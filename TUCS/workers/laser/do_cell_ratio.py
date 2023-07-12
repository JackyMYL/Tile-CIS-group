############################################################
#
# do_cell_ratio.py
#
############################################################
#
# Author: Rute Pedro
#
# Jul 2021, to reply comments on Run 2 laser int note
#
# Goal: Plot the distribution of A=2*A6/(A5+A7) for a given run
#       By default, .root and .pdf files are produced
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

class do_cell_ratio(GenericWorker):
    
    "Produce nice plot for the ratio between 2*A6 and (A5+A7) response"

    c1 = None

    def __init__(self, runType='Las', limit=1, doEps = False):
        self.runType  = runType
        self.doEps    = doEps
        self.limit    = limit        
        self.origin   = ROOT.TDatime()
        self.PMTool   = LaserTools()
        self.time_max = 0
        self.time_min = 10000000000000000
       
        self.outputTag = outputTag # global variable to tag output histogram file name
        self.dir    = getPlotDirectory(subdir=self.outputTag)

        self.run_list = []


    def ProcessStart(self):

        global run_list
        for run in run_list.getRunsOfType('Las'):
            self.run_list.append(run.runNumber)

        try:
            self.HistFile.cd()
        except:
            self.initHistFile("output/Tucs.HIST{}.root".format(self.outputTag))
        self.HistFile.cd()

        self.dirname = "celRatio"
        ROOT.gDirectory.mkdir(self.dirname)
        ROOT.gDirectory.cd(self.dirname)
  
        if self.c1==None:
            self.c1 = src.MakeCanvas.MakeCanvas()
            self.c1.SetTitle("PMT Response")
       
        self.hist  = ROOT.TH1D("CellRatio", "Combined Method",150, -5., 5.)
        self.hist0 = ROOT.TH1D("CellRatioLeft", "Combined Method",150, -5., 5.)
        self.hist1 = ROOT.TH1D("CellRatioRight", "Combined Method",150, -5., 5.)

                   
        
    def ProcessRegion(self, region):

        # Loop over run list
        for run in self.run_list:
            
            print("LOOPING over run list: run number {}".format(run))
            
            # First Retrieve all the relavent pmt infos
            self.mydict = {}
            numbers = region.GetNumber(1)

            # Only proceed if the region is a Tile module
            if len(numbers)!=2:
                return region
            [part, module] = region.GetNumber(1)
            print("\n MODULE {} {} region readout {}".format(region.get_partition(), module, region.GetChildren('readout')))

            # Retrieve info about all PMTs in the module
            for pmt in region.GetChildren('readout'):
                cell = pmt.GetCellName()

                # Create the list of cells for the ratio
                if cell in ['A5','A6','A7']:
                    if cell not in self.mydict:
                        self.mydict[cell] = []
                    self.mydict[cell].append(pmt)
        
            print("module {} {} cell list {}\n".format(part, module, self.mydict.keys()))

            deviation_pmt0 = {}
            deviation_pmt1 = {}

            # Loop on cells in the module
            for cell in list(self.mydict.keys()):
                # Create the pair of PMTs reading the cell
                pair = self.mydict[cell]
                if len(pair)!=2:
                    continue

                #Very important: force the pair to be ordered always in the same way
                if pair[0].get_channel() > pair[1].get_channel(): 
                    pair[0],pair[1] = pair[1],pair[0]
		    
                print("cell {} pair {}".format(cell,pair))
                pmt0adc = pair[0].GetChildren('readout')
                pmt1adc = pair[1].GetChildren('readout')		  
                print ("pair[0]", pair[0])
                print ("pmt0adc", pmt0adc)
   
                # Loop on gains of 1st PMT of the cell
                deviation_pmt0[cell]=0.0
                for adc in pmt0adc:
                    # 1st PMT low gain
                    if adc.GetNumber(1)[3] == 0:
                        pmt0adclowgainEvents = adc.GetEvents()                
                        for event in pmt0adclowgainEvents:
                            if event.run.runNumber == run:
                                if 'deviation' in event.data:
                                    deviation_pmt0[cell] = event.data['deviation']
                                    print("adc {} deviation {}".format(adc, event.data['deviation']))
                                break
                    # 1st PMT high gain
                    else:
                        pmt0adchighgainEvents = adc.GetEvents()                
                        for event in pmt0adchighgainEvents:
                            if event.run.runNumber == run:
                                if 'deviation' in event.data:
                                    deviation_pmt0[cell] = event.data['deviation']
                                    print("adc {} deviation {}".format(adc, event.data['deviation']))
                                break
                    
                # Loop on gains of 2nd PMT of the cell 
                deviation_pmt1[cell]=0.0
                for adc in pmt1adc:
                    # 1st PMT low gain
                    if adc.GetNumber(1)[3] == 0:
                        pmt1adclowgainEvents = adc.GetEvents()                
                        for event in pmt1adclowgainEvents:
                            if event.run.runNumber == run:
                                if 'deviation' in event.data:
                                    deviation_pmt1[cell] = event.data['deviation']
                                    print("adc {} deviation {}".format(adc, event.data['deviation']))
                                break
                    # 1st PMT high gain
                    else:
                        pmt1adchighgainEvents = adc.GetEvents()                
                        for event in pmt1adchighgainEvents:
                            if event.run.runNumber == run:
                                if 'deviation' in event.data:
                                    deviation_pmt1[cell] = event.data['deviation']
                                    print("adc {} deviation {}".format(adc, event.data['deviation']))
                                break

                #print(" cell name {} deviation_pmt0 {} deviation_pmt1 {}".format(cell,deviation_pmt0,deviation_pmt1))
                
                cell_ratio_pmt0 = 0.
                cell_ratio_pmt1 = 0.
            
                if 'A6' in deviation_pmt0.keys() and deviation_pmt0['A6']!=0.0:
                    cell_ratio_pmt0 = 2*deviation_pmt0['A6']/(deviation_pmt0['A5']+deviation_pmt0['A7'])
                    self.hist0.Fill(cell_ratio_pmt0)
                    self.hist.Fill(cell_ratio_pmt0)
                if 'A6' in deviation_pmt1.keys() and deviation_pmt1['A6']!=0.0:
                    cell_ratio_pmt1 = 2*deviation_pmt1['A6']/(deviation_pmt1['A5']+deviation_pmt1['A7'])
                    self.hist1.Fill(cell_ratio_pmt1)
                    self.hist.Fill(cell_ratio_pmt1)

                #print("{} {} (Left)  dev A5 {} A6 {} A7 {} ratio {}".format(part,module,deviation_pmt0['A5'],deviation_pmt0['A6'],deviation_pmt0['A7'],cell_ratio_pmt0))
                #print("{} {} (Right) dev A5 {} A6 {} A7 {} ratio {}".format(part,module,deviation_pmt1['A5'],deviation_pmt1['A6'],deviation_pmt1['A7'],cell_ratio_pmt1))

        ## end run loop





    def ProcessStop(self):


        ROOT.gStyle.SetOptStat(1111)
        #ROOT.gStyle.SetStatX(0.7)
        #ROOT.gStyle.SetStatY(0.83)
        #ROOT.gStyle.SetStatW(.08)
        ROOT.gStyle.SetOptFit(1)
        ROOT.gStyle.SetHistLineColor(2)

        self.c1.cd()
        self.c1.SetGridx()
        self.c1.SetGridy()

        fit = ROOT.TF1("fit", "gaus")
        fit.SetParameter(1,self.hist.GetMean())
        fit.SetParameter(2,max(self.hist.GetRMS(),0.1))
        self.hist.Fit(fit)          
        self.hist.GetXaxis().SetLabelOffset(0.01)
        self.hist.GetXaxis().SetLabelFont(42)
        self.hist.GetXaxis().SetLabelSize(0.05)
        self.hist.GetXaxis().SetTitle("Cell Ratio 2*A6/(A5+A7)")
        self.hist.SetStats(1)
        self.hist.Draw()
        self.c1.Print("{}/cellRatio.root".format(self.dir))
        if self.doEps:
            self.c1.Print("{}/cellRatio.eps".format(self.dir))
        else:
            self.c1.Print("{}/cellRatio.pdf".format(self.dir))

        fit.SetParameter(1,self.hist0.GetMean())
        fit.SetParameter(2,max(self.hist0.GetRMS(),0.1))
        self.hist0.Fit(fit)          
        self.hist0.GetXaxis().SetLabelOffset(0.01)
        self.hist0.GetXaxis().SetLabelFont(42)
        self.hist0.GetXaxis().SetLabelSize(0.05)
        self.hist0.GetXaxis().SetTitle("Cell Ratio 2*A6/(A5+A7) Left PMT")
        self.hist0.SetStats(1)
        self.hist0.Draw()
        self.c1.Print("{}/cellRatioLeft.root".format(self.dir))
        if self.doEps:
            self.c1.Print("{}/cellRatioLeft.eps".format(self.dir))
        else:
            self.c1.Print("{}/cellRatioLeft.pdf".format(self.dir))

        fit.SetParameter(1,self.hist1.GetMean())
        fit.SetParameter(2,max(self.hist1.GetRMS(),0.1))
        self.hist1.Fit(fit)          
        self.hist1.GetXaxis().SetLabelOffset(0.01)
        self.hist1.GetXaxis().SetLabelFont(42)
        self.hist1.GetXaxis().SetLabelSize(0.05)
        self.hist1.GetXaxis().SetTitle("Cell Ratio 2*A6/(A5+A7) Right PMT")
        self.hist1.SetStats(1)
        self.hist1.Draw()
        self.c1.Print("{}/cellRatioRight.root".format(self.dir))
        if self.doEps:
            self.c1.Print("{}/cellRatioRight.eps".format(self.dir))
        else:
            self.c1.Print("{}/cellRatioRight.pdf".format(self.dir))


        self.HistFile.cd(self.dirname) 
        self.hist.Write()
        self.hist0.Write()
        self.hist1.Write()




















     
