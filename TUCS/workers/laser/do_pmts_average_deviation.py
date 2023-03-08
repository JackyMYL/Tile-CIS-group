############################################################
#
# do_pmts_average_deviation.py
#
############################################################
#
# Author: Henric & Ammara
#
# Jan 2018
#
# Goal: Do a plot for difference between the deviation of  
#       two pmt's reading same cell for a runNumber.
#       By default, .png and .C files are produced
#
# Input parameters are:
#
# -> limit: the maximum tolerable variation (in %). Represented by two lines
#           
# -> doEps: provide eps plots in addition to default png graphics
#
# 
#############################################################

from src.GenericWorker import *
from src.oscalls import *
import src.MakeCanvas
import time
from src.region import *
from src.laser.toolbox import *
import ROOT

class do_pmts_average_deviation(GenericWorker):
    
    "Produce nice plot for diff b/t two pmt's reading same cell"

    c1 = None

    def __init__(self, runType='Las', limit=1, doEps = False, span=0.3, iterations=3):
        self.runType  = runType
        self.doEps    = doEps
        self.limit    = limit        
        self.origin   = ROOT.TDatime()
        self.PMTool   = LaserTools()
        self.time_max = 0
        self.time_min = 10000000000000000
        self.span      = span
        self.iter      = iterations
       
        self.hist_pmt0 = ()
        self.hist_pmt1 = ()

        self.outputTag = outputTag # global variable to tag output histogram file name
        self.dir    = getPlotDirectory(subdir=self.outputTag)


    def ProcessStart(self):

        try:
            self.HistFile.cd()
        except:
            self.initHistFile("output/Tucs.HIST{}.root".format(self.outputTag))
        self.HistFile.cd()

        self.dirname = "PMTAverageDiff_span{}_iter{}".format(self.span,self.iter)
        ROOT.gDirectory.mkdir(self.dirname)
        ROOT.gDirectory.cd(self.dirname)
  
        if self.c1==None:
            self.c1 = src.MakeCanvas.MakeCanvas()
            self.c1.SetTitle("PMT Response")
       
        self.hist = ROOT.TH1D("DeltaDeviation", "Combined Method",150, -5., 5.)
                   
        
    def ProcessRegion(self, region):

        # First Retrieve all the relavent pmt infos
        self.mydict = {}
        numbers = region.GetNumber(1)
        
        # Only proceed if the region is a Tile module
        if len(numbers)!=2:
            return region
        [part, module] = region.GetNumber(1)
 
        # Retrieve info about all PMTs in the module
        for pmt in region.GetChildren('readout'):
            cell = pmt.GetCellName()
            # Create the list of cells in the module
            if cell not in self.mydict:
                self.mydict[cell] = []
            self.mydict[cell].append(pmt)

        ncell=0
        cell_list=[]
        deviation_list=[]
        # Loop on cells in the module
        for cell in list(self.mydict.keys()):
            # Create the pair of PMTs reading the cell
            pair = self.mydict[cell]
            if len(pair)!=2:
                continue

            #Very important: force the pair to be ordered always in the same way
            if pair[0].get_channel() > pair[1].get_channel(): 
                pair[0],pair[1] = pair[1],pair[0]
		    
            #print 'cell %s pair %s' % (cell,pair)
            pmt0adc = pair[0].GetChildren('readout')
            pmt1adc = pair[1].GetChildren('readout')		  
            #print "pair[0]", pair[0]
            
            # Loop on gains of 1st PMT of the cell
            deviation_pmt0=0.0
            for adc in pmt0adc:
                # 1st PMT low gain
                if adc.GetNumber(1)[3] == 0:
                    pmt0adclowgain = adc
                    if 'deviation' in adc.data:
                        deviation_pmt0 = adc.data['deviation']
                # 1st PMT high gain
                else:
                    pmt0adchighgain = adc
                    if 'deviation' in adc.data:
                        deviation_pmt0 = adc.data['deviation']
                        #print "%s do_pmt_average_: average %8.5f" %(adc.GetHash(), adc.data['deviation'])
                    
            # Loop on gains of 2nd PMT of the cell 
            deviation_pmt1=0.0
            for adc in pmt1adc:
                # 2nd PMT low gain
                if adc.GetNumber(1)[3] == 0:
                    pmt1adclowgain = adc
                    if 'deviation' in adc.data:
                        deviation_pmt1 = adc.data['deviation'] 
		# 2nd PMT high gain        
                else:
                    pmt1adchighgain = adc
                    if 'deviation' in adc.data:
                        deviation_pmt1 = adc.data['deviation'] 
                        #print "%s do_pmt_average_: average %8.5f" %(adc.GetHash(), adc.data['deviation'])

            #print " cell name" , cell
            #print "deviation_pmt0", deviation_pmt0
            #print "deviation_pmt1", deviation_pmt1
            deviation = deviation_pmt1 - deviation_pmt0
            if deviation_pmt0 !=0 and deviation_pmt1 !=0 :
                if deviation == 0 :
                    print("deviation equal to ", deviation)
                else:
                    #print "deviation diff", deviation
                    self.hist.Fill(deviation)
                    deviation_list.append(deviation)
            # print type(deviation)
            ncell=ncell+1
            #print "ncell", ncell
            #cell_list.append(float(ncell))
            
            
    def ProcessStop(self):

        ROOT.gStyle.SetOptStat(1111)
        ROOT.gStyle.SetStatX(0.7)
        ROOT.gStyle.SetStatY(0.83)
        ROOT.gStyle.SetStatW(.08)
        ROOT.gStyle.SetOptFit(1)
        ROOT.gStyle.SetHistLineColor(2)
        fit = ROOT.TF1("fit", "gaus")
        fit.SetParameter(1,self.hist.GetMean())
        fit.SetParameter(2,max(self.hist.GetRMS(),0.1))
        #if self.hist.GetEntries()>4:
        self.hist.Fit(fit)
          
        self.hist.GetXaxis().SetLabelOffset(0.01)
        self.hist.GetXaxis().SetLabelFont(42)
        self.hist.GetXaxis().SetLabelSize(0.05)
       
        self.hist.GetXaxis().SetTitle("Difference of PMT average deviation")
        self.c1.cd()
        self.c1.SetGridx()
        self.c1.SetGridy()
        self.hist.SetStats(1)
        self.hist.Draw()
        self.HistFile.cd(self.dirname) 
        self.hist.Write()

        self.c1.Print("{}/pmtAveragediff_combined_span{}_iter{}.root".format(self.dir,self.span,self.iter))
        if self.doEps:
            self.c1.Print("{}/pmtAveragediff_combined_span{}_iter{}.eps".format(self.dir,self.span,self.iter))
        else:
            self.c1.Print("{}/pmtAveragediff_combined_span{}_iter{}.pdf".format(self.dir,self.span,self.iter))            























     
