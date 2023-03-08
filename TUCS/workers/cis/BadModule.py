#Author: Grey Wilburn <gwwilburn@uchicago.edu>
#October, 2014
"""
This worker investigates the behavior of TileCal Modules.
For a given channel, a 'bad' run is defined as one where
a channel's CIS constant deviates from the channel avg.
by more than 3%. For a module, a 'bad' run is defined as
as one for which more than 4 channels are bad. Please 
see https://indico.cern.ch/event/332881/ for more 
information on bad runs.
Two output plots are produced. 1 is a 2D Histogram of
the fraction of bad runs for each module. The other is 
a 2D histogram displaying the total runs with ANY data
for each module.
"""

import ROOT
import os.path

#TUCS imports
import src.GenericWorker
import src.MakeCanvas
import src.oscalls
import src.Get_Consolidation_Date
import workers.cis.common as common

class BadModule(src.GenericWorker.GenericWorker):

	def __init__(self, datenum = 2, start_date = " ", end_date = " "):
		self.start_date = start_date
		self.end_date = end_date
		self.datenum = datenum  	

	def ProcessStart(self):
		self.mod_count = {}
		self.mod_dict = {}
		self.mod_run_total = {}
		self.mod_list = []
		self.c1 = src.MakeCanvas.MakeCanvas()
		self.numrun = 0
		self.runlist = []

		self.dir = os.path.join(getPlotDirectory(), "cis", "Investigate", 'WholeDetector')			
		createDir(self.dir)

	def ProcessHisto(self, min, max, title):
		#Set up histogram and TCanvas
		c = src.MakeCanvas.MakeCanvas()
		h = ROOT.TH2F(title, '', 64, 1, 65, 4, 0,4 )

		#Since the formating of the multiple 2D histograms is virtually identical, I wrote the formating into a subroutine
		x_axis = h.GetXaxis()
		y_axis = h.GetYaxis()

		#Set max and min
		h.SetMaximum(max)
		h.SetMinimum(min)

		#Set y axis tick labels to partition names
		count = 1
		for part in ['LBA', 'LBC', 'EBA', 'EBC']:
			y_axis.SetBinLabel(count, part)
			count += 1
		
		#Format y axis
		y_axis.SetTitle('Partition')
		y_axis.CenterTitle()
		y_axis.SetRange(1,4)

		#Format x axis
		x_axis.SetTitle('Module Number')
		x_axis.SetNdivisions(13)	

		#Draw a grid and adjust margins for increased readability
		c.SetGrid(1,1)
		c.SetTopMargin(3)
		c.SetLeftMargin(5)
		c.SetRightMargin(0.9)

		#Add a title
		pt = ROOT.TPaveText(0.10,0.91,0.90,0.999, "brNDC")
		pt.SetBorderSize(0)
		pt.SetFillColor(0)		
		pt.AddText(title)
		
		return c, h, pt

	def ProcessStop(self):

		#Set up  histogram titles
		if self.datenum == 2:
			title_1 = "Fraction of Bad CIS Runs by Module: %s to %s" % (self.start_date, self.end_date)
			title_2 = "Number of CIS Data Runs by Module: %s to %s" % (self.start_date, self.end_date)
		else:
			title_1 = "Fraction of Bad CIS Runs by Module: %s" % self.start_date
			title_2 = "Number of CIS Data Runs by Module: %s" % self.start_date

		c1, h1, pt1 = self.ProcessHisto(0.0, 1.0, title_1) #set up "bad run" histogram
		c2, h2, pt2 = self.ProcessHisto(0.0, len(Use_run_list), title_2) #set up "total run" histogram

		c1.cd()
		
		#Fill the Histograms, and print out information on problematic runs
		print("The following modules have at least 4 bad channels or were turned offfor at least 1 run:")
		print(" ")
		for mod in self.mod_dict:
			badsum = 0
			for run in self.runlist:
				if run in self.mod_dict[mod]:
					#If there are mmore than 4 bad channels in a modue for a given run, then consider the run to be bad
					if self.mod_dict[mod][run] > 4:
						print("\nBAD MODULE: ", mod)
						print("Run number: ", run)
						print("Number of bad chan.: ", self.mod_dict[mod][run])
						badsum += 1
				else:
					print("\nMODULE OFF: ", mod)
					print("Run Number: ", run)
					badsum += 1
			#In preparation for our 2D histogram, determine the partition name and module number for each module
			modlist = mod.split('_')
			partition = modlist[0]
			modnumlist = list(modlist[1])
			modnum = int(modnumlist[1] + modnumlist[2])
			if partition == 'LBA':
				yi = 1
			elif partition == 'LBC':
				yi = 2
			elif partition == 'EBA':
				yi = 3
			elif partition == 'EBC':
				yi = 4			
	
			#Add the fraction of bad runs to the 'bad fraction' 2D histogram
			badfrac = float( float(badsum) / float(self.numrun))
			h1.SetBinContent(modnum, yi, badfrac)
			
			#Add the total number of runs with ANY data to the "total run" 2D histo
			h2.SetBinContent(modnum, yi, len(self.mod_run_total[mod]))
			
		if self.datenum == 2:
			title_1 = "Fraction of Bad Runs by Module: %s to %s" % (self.start_date, self.end_date)
		else:
			title_1 = "Fraction of Bad Runs by Module: %s" % self.start_date

		#Print "bad run" histogram
		h1.Draw("colz")
		pt1.Draw()
		filename = '%s/badrunmap.png' % self.dir
		c1.Print(filename)

		#print "total run" histogram		
		c2.cd()
		h2.Draw("colz")
		pt2.Draw()
		filename2 = '%s/totalrunmap.png' % self.dir
		c2.Print(filename2)
		
	def ProcessRegion(self, region):

		# Make sure this region is a single ADC
		if not "hi" in region.GetHash() and not 'lo' in region.GetHash():
			return
		#Determine which module a channel belongs to, and add that module to our 'number of bad channels for each run' dictionary if it isn't there yet		
		gh = region.GetHash()
		ghl = gh.split("_")
		mod_name = ghl[1] + "_" + ghl[2]
		if not mod_name in self.mod_dict:
			self.mod_dict[mod_name] = {}
			self.mod_run_total[mod_name] = [] #Used for "Total run" histo

		#Calculate the channel mean
		rcount = 0
		csum = 0
		region_run_list = []
		
		#Find runs with CIS data for this ADC, and then calculate the avg. CIS const.			
		for event in region.GetEvents():
			region_run_list.append(event.run.runNumber)
			if event.run.runNumber not in self.runlist:
				self.runlist.append(event.run.runNumber)
			if not event.run.runNumber in self.mod_run_total[mod_name]: #Add run to dictionary used for total run histo
				self.mod_run_total[mod_name].append(event.run.runNumber)	 
			calib = event.data['calibration']
			if ('hi' in gh and calib > 7.5) or ('lo' in gh and calib > 0.125): #i.e., if this ADC has good data for this run, include it in the average
				rcount += 1
				csum += calib
			if not event.run.runNumber in self.mod_dict[mod_name]:
				self.mod_dict[mod_name][event.run.runNumber] = 0
		#Average calculated here
		if rcount > 0:
			cavg = csum / rcount
		else:
			zero = True
			print("ZERO GOOD RUNS: ", gh)
			cavg = 0
		#Append the number of runs each module recorded data to the 
		self.mod_count[mod_name] = rcount

		#Determine the total number of runs (probably not the most efficient way of doing this)
		if rcount > self.numrun:
			self.numrun = rcount

		#If a channel's CIS constant for a run is more than 3% away from the channel mean, consider that channel to be bad for that run
		for event in region.GetEvents():
			calib = event.data['calibration']
			if cavg > 0:
				if abs( (calib - cavg) / cavg) > 0.03:
					self.mod_dict[mod_name][event.run.runNumber] +=1

		#If the channel has no data for a specific run, consider the channel bad for said run
		for run in Use_run_list:
			if not run in region_run_list:
				if not run in self.mod_dict[mod_name]:
					self.mod_dict[mod_name][run] = 0
				self.mod_dict[mod_name][run] +=1

