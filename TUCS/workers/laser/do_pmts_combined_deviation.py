############################################################
#
# do_pmts_combined_deviation.py
#
############################################################
#
# Author: Henric & Ammara & Rute
#
# Nov 2018
#
# Goal: Do a plot for difference between the deviation of  
#       two pmt's reading same cell for a list of runs (default) 
#       or for a single run specified by runNumber.
#       By default, .png and .C files are produced
#
# Input parameters are:
#
# -> limit: the maximum tolerable variation (in %). Represented by two lines
#           
# -> doEps: provide eps plots in addition to default png graphics
#
#############################################################

from src.GenericWorker import *
from src.oscalls import *
import src.MakeCanvas
import time
from src.region import *
from src.laser.toolbox import *
import ROOT

class do_pmts_combined_deviation(GenericWorker):
    
    "Produce nice plot for diff b/t two pmt's reading same cell"

    c1 = None

    def __init__(self, runType='Las', limit=1, doEps = False, runNumber=None, span=0.3, iterations=3):
        self.runType   = runType
        self.doEps     = doEps
        self.limit     = limit        
        self.origin    = ROOT.TDatime()
        self.PMTool    = LaserTools()
        self.time_max  = 0
        self.time_min  = 10000000000000000
        self.run_list  = []
        self.runNumber = runNumber
        self.span      = span
        self.iter      = iterations
     
        self.hist_pmt0 = ()
        self.hist_pmt1 = ()

        self.outputTag = outputTag # global variable to tag output histogram file name
        self.dir       = getPlotDirectory(subdir=self.outputTag)


    def ProcessStart(self):

        # Construct the run list from the run list in Use (if a run number is specified that it will be the only run in the list)
        global run_list
        self.runName = "allRuns"

        if self.runNumber is None:
            for run in run_list.getRunsOfType('Las'):
                self.run_list.append(run.runNumber)
        else:
            self.run_list.append(self.runNumber)
            self.runName = self.runNumber
        print("Run dictionary ", self.run_list)
        
        try:
            self.HistFile.cd()
        except:
            self.initHistFile("output/Tucs.HIST{}.root".format(self.outputTag))
        self.HistFile.cd()

        self.dirname = "PMTDiff_{}_span{}_iter{}".format(self.runName,self.span,self.iter)
        ROOT.gDirectory.mkdir(self.dirname)
        ROOT.gDirectory.cd(self.dirname)

        if self.c1==None:
            self.c1 = src.MakeCanvas.MakeCanvas()
            self.c1.SetTitle("PMT Response")
       
        self.hist = ROOT.TH1D("DeltaDeviation", "Combined Method",150, -5., 5.)
                   
        
    def ProcessRegion(self, region):

        # Loop over run list
        for run in self.run_list:

            #print "LOOPING over run list: run number ", run
            
            # First Retrieve all the relavent pmt infos
            self.mydict = {}
            numbers = region.GetNumber(1)

            # Only proceed if the region is a Tile module
            if len(numbers)!=2:
                return region
            [part, module] = region.GetNumber(1)
            
            # Retrieve info about all PMTs in the module
            for child in region.GetChildren('readout'):
                cell = child.GetCellName()
                # Create the list of cells in the module
                if cell not in self.mydict:
                    self.mydict[cell] = []
                self.mydict[cell].append(child)

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
                        pmt0adclowgainEvents = adc.GetEvents()                       
                        for event in pmt0adclowgainEvents:
                            if event.run.runNumber == run:
                                if 'deviation' in event.data:
                                    deviation_pmt0 = event.data['deviation']
                                    #print "event1", pair[0], deviation_pmt0, event.run.runNumber
                                break

                    # 1st PMT high gain
                    else:
                        pmt0adchighgain = adc
                        pmt0adchighgainEvents = adc.GetEvents()
                        for event in pmt0adchighgainEvents:
                            if event.run.runNumber == run:
                                if 'deviation' in event.data:
                                    deviation_pmt0 = event.data['deviation']
                                    #print "event1", pair[0], deviation_pmt0, event.run.runNumber
                                break

                # Loop on gains of 2nd PMT of the cell
                deviation_pmt1=0.0
                for adc in pmt1adc:
                    # 2nd PMT low gain
                    if adc.GetNumber(1)[3] == 0:
                        pmt1adclowgain = adc
                        pmt1adclowgainEvents = adc.GetEvents()
                        for event in pmt1adclowgainEvents:
                            if event.run.runNumber == run:
                                if 'deviation' in event.data:
                                    deviation_pmt1 = event.data['deviation'] 
                                    #print "event2", pair[1], deviation_pmt1, event.run.runNumber
                                break
		    
                    # 2nd PMT high gain
                    else:
                        pmt1adchighgain = adc
                        pmt1adchighgainEvents = adc.GetEvents()
                        for event in pmt1adchighgainEvents:
                            if event.run.runNumber == run:                       
                                if 'deviation' in event.data:
                                    deviation_pmt1 = event.data['deviation'] 
                                    #print "event2", pair[1], deviation_pmt1, event.run.runNumber                        
                                break
		             
		            #pmt1_dev.append(deviation_pmt1)
                #print " cell name" , cell
                #print "deviation_pmt0", deviation_pmt0
                #print "deviation_pmt1", deviation_pmt1
                deviation = deviation_pmt1 - deviation_pmt0
                if deviation_pmt0 !=0 and deviation_pmt1 !=0 :
                    self.hist.Fill(deviation)
                    deviation_list.append(deviation)
                #print type(deviation)
                ncell=ncell+1
                #print "ncell", ncell
                #cell_list.append(float(ncell))
            
            
    def ProcessStop(self):

        ROOT.gStyle.SetOptStat(1111)
        ROOT.gStyle.SetOptFit(1)
        fit = ROOT.TF1("fit", "gaus")
        fit.SetParameter(1,self.hist.GetMean())
        fit.SetParameter(2,max(self.hist.GetRMS(),0.1))
        #if self.hist.GetEntries()>4:
        #print "Histogram Mean %7.5f +/- %7.5f Std Dev %7.5f +/- %7.5f"%(self.hist.GetMean(), self.hist.GetMeanError(), self.hist.GetStdDev(), self.hist.GetStdDevError())
        self.hist.Fit(fit)

        self.hist.SetLineColor(2)          
        self.hist.GetXaxis().SetLabelOffset(0.01)
        self.hist.GetXaxis().SetLabelFont(42)
        self.hist.GetXaxis().SetLabelSize(0.05)
          
        self.hist.GetXaxis().SetTitle("PMT deviation difference")
        self.c1.cd()
        self.c1.SetGridx()
        self.c1.SetGridy()
        self.hist.SetStats(1)
        self.hist.Draw()
        self.HistFile.cd(self.dirname) 
        self.hist.Write()

        self.c1.Print("{}/pmtdiff_combined_{}_span{}_iter{}.root".format(self.dir,self.runName,self.span,self.iter))
        if self.doEps:
            self.c1.Print("{}/pmtdiff_combined_{}_span{}_iter{}.eps".format(self.dir,self.runName,self.span,self.iter))
        else:
            self.c1.Print("{}/pmtdiff_combined_{}_span{}_iter{}.pdf".format(self.dir,self.runName,self.span,self.iter))


     
