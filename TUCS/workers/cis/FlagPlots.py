#################################################### 
#  FlagPlot.py                                     #
#                                                  #
#  Author: Grey Wilburn                            #
#  grey.williams.wilburn@cern.ch                   #
#                                                  #
#  Date: A dreary winter afternoon in January 2015 #
#                                                  #
#  Meant to partially replace PerformancePlots.py  #
####################################################

from src.GenericWorker import *

class FlagPlots(GenericWorker):
	"Creates a plot showing the number of ADC's failing selected TUCS CIS Quality Flag for each CIS run"

	def ProcessStart(self):
		self.prob_dict = {} #store failure information in this dictionary
		self.time_dict = {} #store run times in this dictionary
		self.TUCS_list = ['DB Deviation', 'Fail Likely Calib.', 'Fail Max. Point', 'Low Chi2', 
                                  'No Response', 'Digital Errors', 'Large Injection RMS']
		self.TUCS_list.append('Outlier')
		#self.TUCS_list.append('Next To Edge Sample')
		#self.TUCS_list.append('Edge Sample')
		self.TUCS_list.append('Stuck Bit')
		self.dir = getPlotDirectory()
		self.dir = '%s/cis/Public_Plots/FlagPlots' % self.dir
		createDir(self.dir)
				
	def ProcessStop(self):
		for run in sorted(self.prob_dict):
			print('\nRun: ', run)
			for prob in sorted(self.prob_dict[run]):
				print(prob, self.prob_dict[run][prob])
		self.ymax = 0
		c1 = src.MakeCanvas.MakeCanvas()
		c1.SetCanvasSize(1250, 750)

		#Set up first TGraph, the one we will use for axes configuration
		DB_graph = self.Fill_Graph('DB Deviation', ROOT.kBlack, 23) #See Fill_Graph function below
		
		x_axis = DB_graph.GetXaxis()
		y_axis = DB_graph.GetYaxis()
	
		#Set of the rest of the TGraphs
		FLC_graph = self.Fill_Graph('Fail Likely Calib.', ROOT.kGreen+3, 23)
		FMP_graph = self.Fill_Graph('Fail Max. Point', ROOT.kBlue, 23)
		LC2_graph = self.Fill_Graph('Low Chi2', ROOT.kGreen-4, 23)
		NR_graph = self.Fill_Graph('No Response', ROOT.kYellow+1, 23)
		DER_graph = self.Fill_Graph('Digital Errors', ROOT. kOrange+7, 23)
		LIR_graph = self.Fill_Graph('Large Injection RMS', ROOT.kMagenta, 23)
		#NES_graph = self.Fill_Graph('Next To Edge Sample', ROOT.kGrey, 23)
		#ES_graph = self.Fill_Graph('Edge Sample', ROOT.kCyan, 23)
		OT_graph = self.Fill_Graph('Outlier', ROOT.kOrange-7, 23)
		SB_graph = self.Fill_Graph('Stuck Bit', ROOT.kGray, 23)
		AF_graph = self.Fill_Graph('Failing Any Flag', ROOT.kRed, 20)

		#Set up legend
		leg = ROOT.TLegend(0.71, 0.15, 0.86, 0.9, "", "brNDC")
		leg.SetBorderSize(0)
		leg.SetTextFont(1)
		leg.SetFillColor(0)
		leg.SetTextSize(0.03)
		#leg.SetNColumns(3)
		
		i = 0
		for graph in [DB_graph, FLC_graph, FMP_graph, LC2_graph, NR_graph, DER_graph, LIR_graph,OT_graph,SB_graph]:
			#Get rid of ES_graph in the above list (and turned off elsewhere)
			if graph == LIR_graph:
				self.TUCS_list[i] = 'Large Inj. RMS'
			legstring = '%s' % self.TUCS_list[i]
			leg.AddEntry(graph, legstring, 'P')
			i += 1
		leg.AddEntry(AF_graph, "FAILING ANY FLAG", "P")

		#Draw graphs onto the same canvas			
		DB_graph.Draw('AP')
		FLC_graph.Draw('psame')
		FMP_graph.Draw('psame')
		LC2_graph.Draw('psame')
		LIR_graph.Draw('psame')
		NR_graph.Draw('psame')
		DER_graph.Draw('psame')
		#NES_graph.Draw('AP')
		#ES_graph.Draw('psame')
		OT_graph.Draw('psame')
		SB_graph.Draw('psame')
		AF_graph.Draw('psame')
		leg.Draw()

		#Format title in a nice way
		tl = ROOT.TLatex()
		tl.SetNDC()
		tl.SetTextSize(0.04)
		tl.DrawLatex(0.33,0.95,"#bf{CIS TUCS Flag Failures by Run}")
		#tl.DrawLatex(0.29,0.95,"#bf{CIS TUCS Flag Failures by Run}")

		#Format axes and plot
		self.Format_Plot(x_axis, y_axis, c1)	#See Format_Plot function below	

		#Set y axis range to include enough room for a legend. Max value
		#calculated in Fill_Graph function
		y_axis.SetRangeUser(0,int(self.ymax * 1.11))

		filename = "%s/TUCS_Flag_History.png" % self.dir
		c1.Print(filename)

	def ProcessRegion(self, region):
		gh = region.GetHash() #region name
		gh_list = gh.split('_')
		
		#If region isn't an adc, then we don't care about it
		if not len(gh_list) == 5:
			return
		
		for event in region.GetEvents():
			runnum = event.run.runNumber
			print(runnum)
			if int(runnum) in [253312, 252636, 248651, 248375]:
				continue
			if not runnum in self.prob_dict:
				self.prob_dict[runnum] = {}
			if not 'Failing Any Flag' in self.prob_dict[runnum]:
				self.prob_dict[runnum]['Failing Any Flag'] = 0
			first_prob = True

			#if str(runnum) in ['248375', '248585', '248651']:
			#	continue

			#Get time of run, for plotting purposes
			if not runnum in self.time_dict:
				self.time_dict[runnum] = event.run.time_in_seconds

			#Add failures to dictionary
			for problem in self.TUCS_list:
				#add an inner dictionary for each run
				if not runnum in self.prob_dict:
					self.prob_dict[runnum] = {}
				#add key for each problem in inner dictionary
				if not problem in self.prob_dict[runnum]:
					self.prob_dict[runnum][problem] = 0
				if event.data['CIS_problems'][problem] == True:
					if first_prob:
						self.prob_dict[runnum]['Failing Any Flag'] += 1
					self.prob_dict[runnum][problem] += 1
					first_prob = False
                                        
		#			if problem == 'Low Chi2':
		#				print gh, runnum

	def Fill_Graph(self, flagname, color, marker):
		tg = ROOT.TGraph()
		i = 0 #Start counting at 1 => bad stuff happens...

		for run in self.prob_dict:
			run_time = self.time_dict[run]
			prob_num = self.prob_dict[run][flagname]
			tg.SetPoint(i, run_time, prob_num)
			i += 1
			
			#Is this point greater than the max
			if prob_num > self.ymax:
				self.ymax = prob_num # if yes, it's the new max

		tg.SetMarkerStyle(marker)
		tg.SetMarkerSize(1)
		tg.SetMarkerColor(color)
		return tg

	def Format_Plot(self, x_axis, y_axis, c):
		#I stole much of this formatting from PerformancePlots.py
		timerange = x_axis.GetXmax() - x_axis.GetXmin()
		xmin =x_axis.GetXmin()
		xmax = x_axis.GetXmin() + int(1.3*timerange)
		if timerange <= (10512000/2): # two months
			nweeks = int(timerange/657000)
			x_axis.SetNdivisions(nweeks, 5, 10, ROOT.kTRUE)
			x_axis.SetTimeDisplay(1)
			x_axis.SetTimeFormat('#splitline{%b %d}{%Y} %F1970-01-01 00:00:00')
			x_axis.SetLabelOffset(0.025)
		elif timerange <= (13140000): # five months
			nbiweeks = int(timerange/(1314000))
			x_axis.SetNdivisions(nbiweeks, 5, 10, ROOT.kTRUE)
			x_axis.SetTimeDisplay(1)
			x_axis.SetTimeFormat('#splitline{%b %d}{%Y} %F1970-01-01 00:00:00')
			x_axis.SetLabelOffset(0.025)
		elif timerange <= (21024000): # 8 months
			nmonths = int(timerange/(2628000))
			x_axis.SetNdivisions(nmonths, 5, 10, ROOT.kTRUE)
			x_axis.SetTimeDisplay(1)
			x_axis.SetTimeFormat('#splitline{%b}{%Y} %F1970-01-01 00:00:00')
			x_axis.SetLabelOffset(0.025)
		else:
			ntwomonths = int((timerange/5256000))
			x_axis.SetNdivisions(ntwomonths, 5, 10, ROOT.kTRUE)
			x_axis.SetTimeDisplay(1)
			x_axis.SetTimeFormat('#splitline{%b}{%Y} %F1970-01-01 00:00:00')
			x_axis.SetLabelOffset(0.025)
		x_axis.SetLabelSize(0.025)
		x_axis.SetTickLength(0.04)
		x_axis.SetLimits(xmin, xmax)  
		
		y_axis.SetTitle('Number of TileCal ADC\'s')		
		y_axis.CenterTitle(True)
		y_axis.SetTitleOffset(1.2)
		y_axis.SetTitleSize()
		y_axis.SetLabelSize(0.03)
		y_axis.SetLabelOffset(0.005)
		y_axis.SetNdivisions(10, 5, 0, ROOT.kTRUE)

		c.SetLeftMargin(0.10)
		c.SetTopMargin(0.07)
		c.SetBottomMargin(0.09)
		c.SetRightMargin(0.09)

