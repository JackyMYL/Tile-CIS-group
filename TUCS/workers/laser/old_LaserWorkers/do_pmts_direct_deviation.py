############################################################
#
# do_pmts_direct_deviation.py
#
############################################################
#
# Author: Ammara with the help of Henric
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
#
#############################################################

from src.GenericWorker import *
from src.oscalls import *
import src.MakeCanvas
import time
from src.region import *
from src.laser.toolbox import *
import ROOT

class do_pmts_direct_deviation(GenericWorker):
    
    "Produce nice plot for diff b/t two pmt's reading same cell"

    c1 = None

    def __init__(self, runType='Las', limit=1, doEps = False, runNumber = 317424):
        self.runType  = runType
        self.doEps    = doEps
        self.limit    = limit        
        self.origin   = ROOT.TDatime()
        self.PMTool   = LaserTools()
        self.time_max = 0
        self.time_min = 10000000000000000
        self.runNumber = runNumber
        self.hist_pmt0 = ()
        self.hist_pmt1 = ()

        self.outputTag = outputTag # global variable to tag output histogram file name
        self.dir    = getPlotDirectory(subdir=self.outputTag)

        try:
            self.HistFile.cd()
        except:
            self.initHistFile("output/Tucs.HIST{}.root".format(self.outputTag))
        self.HistFile.cd()

        self.dirname = "PMTDiff"
        ROOT.gDirectory.mkdir(self.dirname)
        ROOT.gDirectory.cd(self.dirname)
        if self.c1==None:
            self.c1 = src.MakeCanvas.MakeCanvas()
            self.c1.SetTitle("PMT REsponse")


    def ProcessStart(self):
        
        self.hist = ROOT.TH1D("delta deviation", "Direct Method",150, -5., 5.)
        
           
        
    def ProcessRegion(self, region):

# First Retrieve all the relavent pmt infos
        self.mydict = {}
        numbers = region.GetNumber(1)
        if len(numbers)!=2:
            return region
        [part, module] = region.GetNumber(1)
        for pmt in region.GetChildren('readout'):
            cell = pmt.GetCellName()
		    #print 'cell', cell
            if cell not in self.mydict:
                self.mydict[cell] = []
            self.mydict[cell].append(pmt)
        
        dict_cell = {}
        ncell=0
        cell_list=[]
        deviation_list=[]
        
        for cell in list(self.mydict.keys()):
            pair = self.mydict[cell]
            print('pair', pair)
            if len(pair)!=2:
                continue
            print('pair', pair)
		  
            #Very important: force the pair to be ordered always in the same way
            if pair[0].get_channel() > pair[1].get_channel(): 
                pair[0],pair[1] = pair[1],pair[0]
  
            pmt0adc = pair[0].GetChildren('readout')
            pmt1adc = pair[1].GetChildren('readout')
		  
            print("pair[0]", pair[0])
		   
		  #  pmt0_dev = []
            deviation_pmt0=0.0
            for adc in pmt0adc:
		        
                if adc.GetNumber(1)[3] == 0:
                    pmt0adclowgain = adc
                    pmt0adclowgainEvents = adc.GetEvents()                       
                    for event in pmt0adclowgainEvents:
                        if event.run.runNumber == self.runNumber:
                            if event.run.runType=='Las':
                                if 'deviation' in event.data:
                                    deviation_pmt0 = event.data['deviation']
                                    print("event1", pair[0], deviation_pmt0, event.run.runNumber)
                            break
                                
		                           
                else:
                    pmt0adchighgain = adc
                    pmt0adchighgainEvents = adc.GetEvents()
                    for event in pmt0adchighgainEvents:
                        if event.run.runNumber == self.runNumber:
                            if event.run.runType=='Las':
                                if 'deviation' in event.data:
                                    deviation_pmt0 = event.data['deviation']
                                    print("event1", pair[0], deviation_pmt0, event.run.runNumber)
                  
            deviation_pmt1=0.0
            for adc in pmt1adc:
		       
                if adc.GetNumber(1)[3] == 0:
                    pmt1adclowgain = adc
                    pmt1adclowgainEvents = adc.GetEvents()
                    for event in pmt1adclowgainEvents:
                        if event.run.runNumber == self.runNumber:
                            if event.run.runType=='Las':
                                if 'deviation' in event.data:
                                    deviation_pmt1 = event.data['deviation'] 
                                    print("event2", pair[1], deviation_pmt1, event.run.runNumber)
		                          
                else:
                    pmt1adchighgain = adc
                    pmt1adchighgainEvents = adc.GetEvents()
                    for event in pmt1adchighgainEvents:
                        if event.run.runNumber == self.runNumber:
                            if event.run.runType=='Las':
                                if 'deviation' in event.data:
                                    deviation_pmt1 = event.data['deviation'] 
                                    print("event2", pair[1], deviation_pmt1, event.run.runNumber)
		             
		   #     pmt1_dev.append(deviation_pmt1)
            print(" cell name" , cell)
            print("deviation_pmt0", deviation_pmt0)
            print("deviation_pmt1", deviation_pmt1)
            deviation = deviation_pmt1 - deviation_pmt0
            if deviation_pmt0 !=0 and deviation_pmt1 !=0 :
                if deviation == 0 :
                    print("deviation equal to ", deviation)
                else:
                    print("deviation diff", deviation)
                    self.hist.Fill(deviation)
                   # dict_cell[cell] =  deviation
                    deviation_list.append(deviation)
            # print type(deviation)
            ncell=ncell+1
            print("ncell", ncell)
                    
                    
           # cell_list.append(float(ncell))
            
            
    def ProcessStop(self):

        ROOT.gStyle.SetOptStat(1111)
        ROOT.gStyle.SetStatX(0.7)
        ROOT.gStyle.SetStatY(0.83)
        ROOT.gStyle.SetStatW(.08)
        ROOT.gStyle.SetOptFit(1)
        ROOT.gStyle.SetHistLineColor(kRed)
       # ROOT.gstyle.SetFitLineColor(kRed)
        fit = ROOT.TF1("fit", "gaus")
        fit.SetParameter(1,self.hist.GetMean())
        fit.SetParameter(2,max(self.hist.GetRMS(),0.1))
       # if self.hist.GetEntries()>4:
        self.hist.Fit(fit)
          
          
        self.hist.GetXaxis().SetLabelOffset(0.01)
        self.hist.GetXaxis().SetLabelFont(42)
        self.hist.GetXaxis().SetLabelSize(0.05)
   
       
        self.hist.GetXaxis().SetTitle("PMT deviation difference")
        self.c1.cd()
        self.c1.SetGridx()
        self.c1.SetGridy()
        self.hist.SetStats(1)
        self.hist.Draw()
        self.hist.Print('Run:317424')
        self.HistFile.cd(self.dirname) 
        self.hist.Write()
        if self.doEps:
            self.c1.Print("%s/pmtdiff_direct.root" % (self.dir))
              























     
