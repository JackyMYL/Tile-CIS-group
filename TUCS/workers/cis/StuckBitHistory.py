#################################################################################
# Author: Grey Wilburn <grey.williams.wilburn@cern.ch>                          #
#                                                                               #
# Date: A warm, bright mid-April Monday morning in 2015                         #
#                                                                               #
# Plots stuck bit history as a function of run number. Meant to work with the   #
# StudyFlag.py macro. Based slightly on CISBitMapper.py worker.                 #
#################################################################################

# stdlib imports
import os.path
# 3rd party imports
import ROOT
# TUCS imports
import src.GenericWorker
import src.MakeCanvas
import src.oscalls
# CIS imports
import workers.cis.common as common

class StuckBitHistory(src.GenericWorker.GenericWorker):
	"Creates plots showing the stuck behavior of bits over time"

	def __init__(self, only_all_flags=False, only_chosen_flag=False, DBUpdate=False,
			flagtype =  'DB Deviation', plotdirectory = 'StudyFlag'):
		self.flag = flagtype
		self.only_all_flags = only_all_flags
		self.only_chosen_flag = only_chosen_flag
		self.DBUpdate = DBUpdate
		self.plot_directory = plotdirectory

		if self.only_chosen_flag and self.flag == 'all':
			self.only_all_flags = True
			self.only_chosen_flag = False
			
	def ProcessStart(self):
		self.c1 = src.MakeCanvas.MakeCanvas()
		self.dir = os.path.join(src.oscalls.getPlotDirectory(), 'cis', self.plot_directory,
			'StuckBitHistory', self.flag)
		if self.DBUpdate:
			self.dir =  os.path.join(src.oscalls.getPlotDirectory(), 'cis', 
					'CIS_Update', 'StuckBitHistory')
		src.oscalls.createDir(self.dir)
		
	def ProcessStop(self):
		pass

	def ProcessRegion(self,region):
		if region.GetEvents() == set():
			return

		N = len(region.GetEvents()) # Number of runs
		
		histo = ROOT.TH2F("histo","",N,0,N,10,0,10)
		rlist = [] # For x axis labels

		if self.DBUpdate:
			if not region.GetHash() in stuck_bit_list:
				return
		run_count = 1
		for event in sorted(region.GetEvents(), key=lambda x: x.run.runNumber):
				
			# For various print options controlled by study flag
			if self.only_all_flags:
				if 'moreInfo' not in event.data and not self.all:
					continue
				if not self.all and not event.data['moreInfo']:
					continue
				if self.adc_problems:
					if 'problems' not in event.data and not self.all:
						continue
					if not event.data['problems'] and not self.all:
						continue
			if self.only_chosen_flag:
				global stablist
				self.stablist = stablist
				if region.GetHash() not in self.stablist:
					return

			rlist.append(event.run.runNumber)
			# See if a bit is stuck for this run, at 0 or at 1
			for bit in range(0,10):
				if 'StuckBits' not in event.data:
					continue
				if (type(event.data['StuckBits']['AtOne']) == int) or (type(event.data['StuckBits']['AtZero']) == int):
					continue
				if bit in event.data['StuckBits']['AtOne']:
					histo.SetBinContent(run_count, bit+1, 2)         #red
				elif bit in event.data['StuckBits']['AtZero']:
					histo.SetBinContent(run_count, bit+1, 1)         #blue
				else:
					histo.SetBinContent(run_count, bit+1, 0)         #white
			run_count += 1

		print("Stuck Bit History plot for %s" % region.GetHash())
		self.FormatHisto(histo, rlist) #See next function
		histo.Draw('col')

		# Standard TUCS plot title, w/ both chan and pmt number
		det, partition, module, channel, gain = region.GetHash().split('_')
		pmt = region.GetHash(1)[16:19]
		title = ''.join([partition, module[1:], ' ', channel,'/', pmt,
			' ', gain])

		latex = ROOT.TLatex()
		latex.SetTextAlign(12)
		latex.SetTextSize(0.04)
		latex.SetNDC()
		latex.DrawLatex(0.11,0.975, title)

		# These TBox's aren't drawn. They are just for the legend.
		b1 = ROOT.TBox(0.10,0.10,0.105,0.105)   #stuck at 1
		b1.SetFillColor(2)			#red
		b0 = ROOT.TBox(0.10,0.10,0.105,0.105)   #stuck at 0
		b0.SetFillColor(4)			#blue

		# Format legend
		leg = ROOT.TLegend(0.60, 0.95, 1.0, 1.0, "", "brNDC")
		leg.SetFillColor(0)
		leg.SetBorderSize(0)
		leg.SetNColumns(3)
		leg.AddEntry(b0, "Bit Stuck at 0","f")
		leg.AddEntry(b1, "Bit Stuck at 1","f")
		leg.Draw()
	
		self.c1.Print("%s/StuckBitHistory_%s.png" % (self.dir, region.GetHash()))

	def FormatHisto(self, histo, rlist):
		self.c1.Clear()
		self.c1.SetLeftMargin(0.10)
		self.c1.SetRightMargin(0.037)
		self.c1.SetBottomMargin(.2)
		self.c1.SetGrid(1,1)
		
		# format x axis, set run numbers as labels
		x_axis = histo.GetXaxis()
		for i in range(0,len(rlist)):
			x_axis.SetBinLabel(i+1, str(rlist[i]))
		x_axis.LabelsOption("v")
		x_axis.SetTitle("Run Number")
		x_axis.SetLabelFont(42)
		x_axis.SetTitleFont(42)
		x_axis.SetTitleOffset(1.9)

		# format y axis, set bit numbers as labels
		y_axis = histo.GetYaxis()
		for i in range (0,10):
			y_axis.SetBinLabel(i+1, str(i))
		y_axis.SetLabelSize(.045)
		y_axis.SetTitle("ADC Bit")
		y_axis.SetLabelFont(42)
		y_axis.SetTitleFont(42)
		y_axis.SetTitleOffset(0.8)

		# Set min and max, hack to have only white, blue, and red bins		
		histo.SetMinimum(1)
		histo.SetMaximum(2)
