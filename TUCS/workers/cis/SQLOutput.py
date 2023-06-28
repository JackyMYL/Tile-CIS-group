#Reads CIS sqlite files and plots the results
#
#Author: Grey Wilburn
#Date: An Autumn afternoon in 2014...
#
# Modified: Jacky Li @ May 2023

from src.GenericWorker import *
import os
import subprocess
import ROOT
from TileCalibBlobPython.TileCalibTools import MINRUN, MINLBK, MAXRUN, MAXLBK, LASPARTCHAN


class SQLOutput(GenericWorker):
	"A worker for plotting the output of CIS SQLite update files"

                #counters

	updated_chan = 0
	masked_chan = 0
	affected_chan = 0
	good_chan =0
	masked_list = []
	affected_list = []
	#plus_5 = 0
	def Increment(counter):
		return counter + 1
		#End Counters

	def __init__(self, schema = 'sqlite://;schema=results/tileSqlite.db;dbname=CONDBR2', 
                     tag = 'RUN2-HLT-UPD1-00', folder = '/TILE/OFL02/CALIB/CIS/LIN', 
                     single_iov = True, plot_directory = "CISUpdate", recalALL = False):
#	def __init__(self, schema = 'sqlite://;schema=results/tileSqlite.db;dbname=CONDBR2',
#                     tag = 'TileOfl02CalibCisLin-RUN2-UPD-16', folder = '/TILE/OFL02/CALIB/CIS/LIN',
#                     single_iov = True, plot_directory = "CISUpdate", recalALL = False):
		self.schema = schema
		self.tag = tag
		self.folder = folder
		self.sql_dict = {}
		self.single_iov = single_iov
		self.plot_directory = plot_directory
		self.latestRun = TileCalibTools.getLastRunNumber()
		self.recalALL = recalALL
		#Compatible with NEW TUCS (NEW = October 2014)
		self.rdir = getResultDirectory('cis/%s' % self.plot_directory)
		self.pdir = os.path.join(getPlotDirectory(), "cis", "CIS_Update")
		createDir(self.pdir)
		createDir(self.rdir)

	def ProcessStart(self):
		arglist = []
		arglist.append("ReadCalibFromCool.py")
		arglist.append(("--tag = %s" % self.tag))
		arglist.append (("--folder = %s" %  self.folder))
		arglist.append(("--schema = %s" % self.schema))
		arglist.append(123456)

		self.c1 = src.MakeCanvas.MakeCanvas()
		self.hist = ROOT.TH1F('percent_difference', '', 100, -4.9, 5.1)

		#For creating output for a single IOV file		
		if self.single_iov:
			self.run_list = [db_run_list[-1]]
			self.last_run = self.run_list[0]
		else:
			self.run_list = db_run_list

		#Run ReadCalibFromCool.py for each run in the run list to read newly-created SQL file
		for run in self.run_list:
			self.sql_dict[run] = {}
			
			arglist[4] = "--run = %i" % run
			command =  "ReadCalibFromCool.py  --tag=%s --folder=%s --schema='%s' --run=%i" % (self.tag, self.folder, self.schema, run)
			out = os.popen(command).read()

			#Format the output of ReadCalibFromCool, and store each channel's new DB constant in a dictionary for this run
			outlist = out.split('\n')
			for line in outlist:
				linelist = line.split()
				if not 'missing' in linelist and len(linelist) == 4:
					part_mod_list = list(linelist[0])
					partition = part_mod_list[0] + part_mod_list[1] + part_mod_list[2]
				
					module = part_mod_list[3] + part_mod_list[4]
					
					
					if len(linelist[1]) == 1:
						channel = '0' + linelist[1]
					elif len(linelist[1]) == 2:
						channel = linelist[1]
					else:
						print("Can't assign channel number: ", linelist)
						print(linelist, len(linelist[2]))

					if linelist[2] == '0':
						gain = "lowgain"
					elif linelist[2] == '1':
						gain = "highgain"
					else:
						print("Can't assign gain: ", linelist)

					if channel and gain:
						adc_name = "TILECAL_" + partition + "_m" + module + "_c" + channel + "_" + gain
#						print adc_name, linelist[3]
						self.sql_dict[run][adc_name] = float(linelist[3])
	def ProcessStop(self):
	
		#Write the .txt output file	
		file = open("results/CIS_DB_update.txt", "w")	

		#Write database, folder, and tag information at the beginning of the file		
		file.write("Schema: %s \n" % self.schema)
		file.write("Folder: %s \n" % self.folder)
		file.write("Tag: %s \n" % self.tag)
		file.write("\n")

		#Note if there is a single IOV, make a note
		if self.single_iov:
			file.write("USING ONLY 1 IOV\n")
			file.write("IOV: [%i,0] - [%r,%r]\n" % (self.run_list[0], MAXRUN, MAXLBK))
			file.write("\n")

		#Print channel name, new db value, old db value for each run
		pd_dict = {}
		count_dict = {}
		plus_5 =0
		for channel in old_db_dict:
			pd_dict[channel] = 0
			count_dict[channel] = 0
		for run in sorted(self.sql_dict):
			if not run in mod_update_dict:
				continue
			file.write("run %i\n" % run)
			file.write("channel \t\t | \t old DB value \t | \t new DB value \t | \t difference\n")
			for channel in sorted(self.sql_dict[run]):
				chan_list = channel.split('_')
				mod = chan_list[1] + '_' + chan_list[2]
				if mod in mod_update_dict[run]:
					if channel in mod_update_dict[run][mod]:
						if run in old_db_dict[channel]:
							old_db = old_db_dict[channel][run]
						else:
							latest_run =  sorted(old_db_dict[channel])[-1]
							old_db =  old_db_dict[channel][latest_run]
						pd =  ((self.sql_dict[run][channel] - old_db) / old_db)
						pd_dict[channel] += pd
						count_dict[channel] += 1
						file.write("%s \t %r \t %r \t %r\n" % (channel, old_db, self.sql_dict[run][channel], pd))
						if abs(pd) >= 0.05: #checks if the percent difference is greater than 5 percent. If so, increments the counter
							plus_5 += 1


		file.write("updated: %s\t  good: %s\n" % (SQLOutput.updated_chan, SQLOutput.good_chan))
		file.write(">5 percent change: %s\n" %(plus_5))
		file.write("Masked channels: %s\n" % SQLOutput.masked_chan)
		file.write("\n".join("%s" % (masked) for masked in SQLOutput.masked_list))
		file.write("\n Affected channels: %s\n" % SQLOutput.affected_chan)
		file.write("\n".join("%s" % (affected) for affected in SQLOutput.affected_list))
		for channel in pd_dict:
			if count_dict[channel] > 0:
				pd_avg = pd_dict[channel] / count_dict[channel]
				self.hist.Fill(100.0*pd_avg)

		#Create a histogram of the average % change for all of the modules that were recalibrated
		self.c1.Clear()
		
		#format overflow bins
		self.hist.SetBinContent(1, self.hist.GetBinContent(1) + self.hist.GetBinContent(0))
		self.hist.SetBinContent(100, self.hist.GetBinContent(100) + self.hist.GetBinContent(101))

		#format axes
		if self.recalALL:
			self.c1.SetLogy(1)
		if self.single_iov:
			self.hist.GetXaxis().SetTitle('% Change in DB CIS Constant')
		else:
			self.hist.GetXaxis().SetTitle('Avg. % Change in DB CIS Constant')
		self.hist.GetYaxis().SetTitle('Number of ADC\'s')
		ROOT.gStyle.SetOptStat(0)
		
		self.hist.Draw('')
		#h.Draw('')
		path = self.pdir
		filename = "%s/hist.png" % path
		self.c1.Print(filename)		
		
			
	def ProcessRegion(self, region):
		gh = region.GetHash()
		
		#If the adc isn't in the update, or doesn't need to be plotted, then we skip over it
		if (not gh in db_update_list) and (not gh in plot_list):
			return
		if not gh in calib_dict or len(calib_dict[gh]) == 0:
			return
		#print(gh)
		gh_list = gh.split('_')
		mod_name = gh_list[1] + '_' + gh_list[2]

		#Now we create a plot for this channel
		numEvents = 0
		for point, event in enumerate(region.GetEvents()):
			numEvents+=1;
		graph = ROOT.TGraph()
		graphDBO = ROOT.TGraph()
		if not self.single_iov:
			graphDBN = ROOT.TGraph()
		xlist = []
		ylist = []
		cool_list_adc = []
		adc_bad = False
		adc_aff = False
		#print("line 214 here we are")
		calib_list = []

		#Fill the TGraphs
		i = 0
		for event in sorted(region.GetEvents(), key=lambda x:x.run.runNumber):
			run = event.run.runNumber
			if run in calib_dict[gh]: 
				calib = calib_dict[gh][run]
				ylist.append(calib)
				xlist.append(event.run.time_in_seconds)
				old_db = old_db_dict[gh][run]
				graph.SetPoint(i, event.run.time_in_seconds, calib)
				graphDBO.SetPoint(i, event.run.time_in_seconds, old_db)
				if not self.single_iov:
					if gh in self.sql_dict[run]:
						new_db = self.sql_dict[run][gh]
						graphDBN.SetPoint(i, event.run.time_in_seconds, new_db)
					else:
						new_db = old_db_dict[gh][run]
						graphDBN.SetPoint(i, event.run.time_in_seconds, new_db)
			if 'problems' in event.data:
				adc_aff = True
				for problem in event.data['problems']:
					if problem == 'Stuck bit' or problem == 'Severe stuck bit':
						stuck_bit_list.append(gh)
					if not problem in cool_list_adc:
						cool_list_adc.append(problem)
					if problem in ['ADC masked (unspecified)', 'Severe stuck bit', 'Channel masked (unspecified)']:
						adc_bad = True
		
			i += 1
		#format the plot title, using both channel and pmt numbering
		pmt = region.GetHash(1)[16:19]   		
		det, partition, module, channel, gain = region.GetHash().split('_') 
		title = ''.join([partition, module[1:], ' ', channel, '/', pmt,' ', gain])
		# NEW CODE
		if gh in db_update_list:
			SQLOutput.updated_chan += 1
			if adc_bad == True:
				SQLOutput.masked_chan += 1
				SQLOutput.masked_list.append(title)
			elif adc_aff == True:
				SQLOutput.affected_chan += 1
				SQLOutput.affected_list.append(title)
			else:
				   SQLOutput.good_chan += 1
		if not gh in db_update_list:
			if self.recalALL:
				title = title + "(minor change)"
			else:
				title = title + " (not in update)"
		self.c1.Clear()
				
		#Get mean and RMS values
		mean = ROOT.TMath.Mean(len(ylist), array('f', ylist))
		rms = ROOT.TMath.RMS(len(ylist), array('f', ylist))
		# if mean == 0 :
		# 	print("MEAN ALARM")
		# 	mean = 1

		rmsDBO = graphDBO.GetRMS(2)
		meanDBO = graphDBO.GetMean(2)
		if not self.single_iov:
			rmsDBN = graphDBN.GetRMS(2)
			meanDBN = graphDBN.GetMean(2)
			
		#Format the axes
		x_axis = graph.GetXaxis()
		x_axis.SetTimeDisplay(1)
		x_axis.SetTimeFormat('%d/%m/%y%F1970-01-01 00:00:00')
		x_axis.SetLabelSize(0.04)
		x_axis.SetNdivisions(505)
	#	xmax = x_axis.GetXmax()
	#	xmin = x_axis.GetXmin()
		xmin = sorted(xlist)[0] - 259200
		xmax = sorted(xlist)[-1] + 259200
		y_axis = graph.GetYaxis()
		ymin = sorted(ylist)[0]
		ymax = sorted(ylist)[-1]
		if ((ymax - ymin) / ymax) > 0.9:
			ylist_new = []
			for point in ylist:
				if  ((ymax - point) / ymax) < 0.9:
					ylist_new.append(point)
			ymin = sorted(ylist_new)[0]
		#format the calib datapoints, and the enitre plot
		graph.SetMinimum(ymin * 0.9)
		graph.SetMaximum(ymax * 1.1)
		graph.SetMarkerStyle(20)
		graph.SetMarkerSize(1.3)
		graph.GetYaxis().SetTitle('CIS Constant (ADC count/pC)')
		graph.SetMarkerColor(ROOT.kBlack)
		graph.Draw('AP')
		x_axis.SetLimits(xmin, xmax)
			
		#draw boxes around the detector and channel averages
		box2 = ROOT.TBox(xmin, common.DEF_CALIB[gain] * 0.98,xmax, common.DEF_CALIB[gain] * 1.02)
		box2.SetFillColor(ROOT.kRed - 2)
		if (ymin*0.9) < common.DEF_CALIB[gain] < (ymax*1.1): 
			box2.Draw()
			
		box = ROOT.TBox(xmin, mean * 0.99,xmax, mean * 1.01)
		box.SetFillColor(ROOT.kGreen - 5)
		box.Draw()
			
		line = ROOT.TLine()
		line.SetLineWidth(3)
		line.DrawLine(xmin, common.DEF_CALIB[gain],xmax, common.DEF_CALIB[gain])
		line.DrawLine(xmin, mean, xmax, mean)

		#draw points over boxes
		graph.Draw('P')

		#Format the old db points
		graphDBO.SetMarkerStyle(23)
		graphDBO.SetMarkerSize(0.9)
		graphDBO.SetMarkerColor(ROOT.kBlue)
		graphDBO.Draw('psame')

		#Format the new db information
		if not self.single_iov:
			graphDBN.SetMarkerStyle(21)
			graphDBN.SetMarkerSize(0.8)
			graphDBN.SetMarkerColor(ROOT.kMagenta)
			graphDBN.Draw('psame')
		else:
			line_single_iov = ROOT.TLine()
			line_single_iov.SetLineWidth(3)
			line_single_iov.SetLineColor(6)
			if gh in self.sql_dict[self.last_run]:
				new_db = self.sql_dict[self.last_run][gh]
				#line_single_iov.DrawLine(xmin, self.sql_dict[self.last_run][gh], xmax, self.sql_dict[self.last_run][gh])
				#line_single_iov.DrawLine(xmin, mean, xmax, mean)
			else:
				if self.last_run in old_db_dict[gh]:
					#line_single_iov.SetLineColor(4)
					new_db = db_update[gh][self.last_run]
					#line_single_iov.DrawLine(xmin, old_db_dict[gh][self.last_run], xmax, old_db_dict[gh][self.last_run])
					#line_single_iov.DrawLine(xmin, mean, xmax, mean)
					#new_db = self.sql_dict[self.last_run][gh]		
				else:
					latest_run = sorted(old_db_dict[gh])[-1]
					#line_single_iov.SetLineColor(2)
					#new_db = self.sql_dict[latest_run][gh]
					new_db = db_update[gh][latest_run]
					#line_single_iov.DrawLine(xmin, old_db_dict[gh][latest_run], xmax, old_db_dict[gh][latest_run])
					#line_single_iov.DrawLine(xmin, mean, xmax, mean) #this is a test, when used comment out line_single_iov.DrawLine(xmin, new_db, xmax, new_db)
			line_single_iov.DrawLine(xmin, new_db, xmax, new_db)

		#Add the legend
		leg = ROOT.TLegend(0.646, 0.8163636, 0.9485, 1, "", "brNDC")
		#leg = ROOT.TLegend(0.1,0.82,0.4,1, "", "brNDC")
		leg.SetBorderSize(0)
		leg.SetFillColor(0)
		leg.AddEntry(box2, "+/- 2% of detector avg", "f")
		leg.AddEntry(box, "+/- 1% of mean", "f")
		leg.AddEntry(graph, "measured values", "P")
		leg.AddEntry(graphDBO, "old DB values", "P")
		if not self.single_iov:
			leg.AddEntry(graphDBN, "new database values", "P")
		else:
			leg.AddEntry(line_single_iov, "Future database value", "f")
		leg.Draw()
		
		#print mean information, title on the graph		
		latex = ROOT.TLatex()
		latex.SetTextAlign(12)
		latex.SetTextSize(0.04)
		latex.SetNDC()
		
		latex.DrawLatex(0.19, 0.80, "Mean = %0.2f" % mean)
		latex.DrawLatex(0.19, 0.74, "RMS/Mean = %0.4f %%" % (100.0*float(rms) / float (mean)) )
		latex.DrawLatex(0.1670854, 0.9685315, title)
		if gh in final_default_list:
			latex.SetTextColor(2)
			latex.DrawLatex(0.19, 0.85, 'DEFAULT')

		latex.SetTextSize(0.03)
		if len(cool_list_adc) > 0:
			latex.SetTextColor(2)
			if adc_bad:
				latex.DrawLatex(0.02, 0.07, "ADC BAD")
				x_pos = 0.12
			else:
				latex.DrawLatex(0.02, 0.07, "ADC AFFECTED")
				x_pos = 0.19
			if 'problems' in event.data:
				for problem in event.data['problems']:
					if problem == 'Channel masked (unspecified)':
						problem = 'Chan masked (unspec.)'
					if problem == "ADC masked (unspecified)":
						problem = "ADC masked (unspec.)"
					if problem == "Bad CIS calibration":
						problem = "Bad CIS Calib"
					if problem == "No CIS calibration":
						problem = "No CIS Calib."
					if problem == "No cesium calibration":
						problem = "No Cs Calib"
					if problem == "Bad cesium calibration":
						problem = "Bad Cs Calib"
					if problem == "Bad laser calibration":
						problem = "Bad Las Calib"
					if problem == "No laser calibration":
						problem = "No Las Calib"
					latex.DrawLatex(x_pos, 0.07, problem)
					x_pos += 0.22

		if gh in tucs_dict:
			latex.SetTextColor(4)
			latex.DrawLatex(0.02, 0.02, "qflags:")
			x_pos = 0.12
			for problem in tucs_dict[gh]:
				if tucs_dict[gh][problem] < 0.50:
					continue
				if problem == "Large Injection RMS":
					problem = "Large Inj. RMS"
				latex.DrawLatex(x_pos, 0.02, problem)
				x_pos += 0.15 
		#Save Plot
		filename = "CISUpdate_%s.png" % gh	
		savename = "%s/%s" % (self.pdir,filename)		
		self.c1.Print(savename)
