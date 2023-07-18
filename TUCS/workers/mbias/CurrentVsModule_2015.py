from src.GenericWorker import *
import src.MakeCanvas
import time
import numpy
import src.stats
import math
from src.region import *
from src.run import *
from src.laser.toolbox import *



# worker is called by macro getCurrentVsModule2015.py

class CurrentVsModule_2015(GenericWorker):
    "A plot worker for MBias"
    
    def __init__(self, checkCell, LumiBegin=1, LumiRange=20):
        self.dir = getPlotDirectory() #where to save the plots
	    

        self.PMTool         = LaserTools()
	#will be histos later
        self.CurrentVsInstLumi = None
	# used events (one per run)
        self.eventsList = []
	#detector region
	#corresponding name
        self.regionName = None
        self.plot_name = None
        #self.Runnumber = None
        self.LumiBegin = LumiBegin
        self.LumiEnd = LumiBegin+LumiRange
        self.LumiRange = LumiRange
        self.cellName = checkCell

    def ProcessRegion(self, region):
	
        if region.GetEvents() == set():
            return
		
        Name = region.GetHash()
        self.regionName = Name[8:19] # shorter name without TILECAL_ in front
	
        for event in region.GetEvents():
            # and only look at laser runs, for now
            if event.run.runType == 'Las' or event.run.runType == 'Phys':
                if 'LumiBlock' in  list(event.run.data.keys()):# valid entries in run?? some files seem buggy for 2015  
                    self.eventsList.append(event)
                #print 'Run ', event.run.runNumber
		    
		    
    def	ProcessStop(self):

        if os.environ.get('TUCS'):
            ROOT.gROOT.LoadMacro("$TUCS/root_macros/AtlasStyle.C")
            ROOT.SetAtlasStyle()
            ROOT.gROOT.ForceStyle()
	    	    
        ROOT.gStyle.SetPalette(1)
	#self.c1.Clear()
        #self.c1.cd()
        RunNumber = None

        PMTCurrent = None
        LumiBlock = None

        # using mapping from website: only using first pmt                                                                                  
	
        # histogram
        cellA1 = TH1F("cellA1","cellA1",64,0,64 )
        cellA2 = TH1F("cellA2","cellA2",64,0,64 )
        cellC1 = TH1F("cellC1","cellC1",64,0,64 )
        cellC2 = TH1F("cellC2","cellC2",64,0,64 )

        # get files with info on inst. lumi for given lumiblock
        filename = '/afs/cern.ch/user/c/cfischer/TUCS_QT/Tucs/ilumicalc_histograms_None_276262-284484.root'
        print(filename)
        file = TFile(filename,'READ' )
        file.cd()

        for event in self.eventsList:# just one run

            print('Run', event.run.runNumber)
#            if event.run.runNumber==285096 or event.run.runNumber==285354 or event.run.runNumber==285355 or event.run.runNumber==285357: continue
#            if event.run.runNumber>=284484: continue # avoid crash                                                                                                                      
            if event.run.runNumber<276262: continue
            print(len(event.run.data['LumiBlock']))
            if len(event.run.data['LumiBlock'])==0 or event.run.runNumber==206299: #no lumi-file for this run
                continue   

            RunNumber = event.run.runNumber
#            #first find appropriate lumiblock range to use
#            for i in range(len(event.run.data['LumiBlock'])):
#                # need to use a test channel to see if we have currents (take D5)
#                if event.run.data['PMTCurrent'][i][2][0][16]!=0: # we have currents 
#                    LumiBegin = event.run.data['LumiBlock'][i]
#                    if event.run.data['LumiBlock'][i+10] == LumiBegin+10:
#                        LumiEnd = LumiBegin+10
#                        break
#                    else:
#                        LumiBegin=LumiBegin+10# start over

            histoFile = file.Get('run%s_peaklumiplb' % event.run.runNumber)
	   
            #self.Runnumber = str(event.run.runNumber)
	   
            PMTCurrentA1 = stats()
            PMTCurrentA2 = stats()
            PMTCurrentC1 = stats()
            PMTCurrentC2 = stats()

            InstLumi = stats()
            InstLumiMean = None
            PMTCurrentHelp = event.run.data['PMTCurrent']
            PMTStatusHelp = event.run.data['PMTStatus']
            PMTGoodHelp = event.run.data['IsGood']

            lumiIndex = 0
            #have to find the right lumi index
            for i in range(len(event.run.data['LumiBlock'])):
                if event.run.data['LumiBlock'][i]==self.LumiBegin:
                    lumiIndex=i
                    break

            det_reg = self.PMTool.getRegionName2015(self.cellName)
            PartA = det_reg[0][0] #long barrel or extended barrel
            PartC = det_reg[0][1]
            PMTch = det_reg[1] #pmts belonging to cell, will use my own mapping for channel vs eta
            count=0
            #loop over modules 
            for m in range(64):# 
                # loop over lb entries
                countA1=0
                countA2=0
                countC1=0
                countC2=0
                for l in range(self.LumiBegin,self.LumiEnd):
                    if m==0: InstLumi.fill(histoFile.GetBinContent(l+1)/1000.) #only need to fill this once
                    lumi=lumiIndex+count
                    count+=1
                    print(lumi)
                    if PMTCurrentHelp[lumi][PartA][m][PMTch[0]]!=0 and PMTGoodHelp[lumi][PartA][m][PMTch[0]]==1 and PMTStatusHelp[lumi][PartA][m][PMTch[0]]==1: 
                        countA1+=1
                        print('here')
                        PMTCurrentA1.fill(PMTCurrentHelp[lumi][PartA][m][PMTch[0]])# first PMT
                    if PMTCurrentHelp[lumi][PartA][m][PMTch[1]]!=0 and PMTGoodHelp[lumi][PartA][m][PMTch[1]]==1 and PMTStatusHelp[lumi][PartA][m][PMTch[1]]==1: 
                        countA2+=1
                        PMTCurrentA2.fill(PMTCurrentHelp[lumi][PartA][m][PMTch[1]])# second PMT
                    if PMTCurrentHelp[lumi][PartC][m][PMTch[0]]!=0 and PMTGoodHelp[lumi][PartC][m][PMTch[0]]==1 and PMTStatusHelp[lumi][PartC][m][PMTch[0]]==1:
                        countC1+=1
                        PMTCurrentC1.fill(PMTCurrentHelp[lumi][PartC][m][PMTch[0]])
                    if PMTCurrentHelp[lumi][PartC][m][PMTch[1]]!=0 and PMTGoodHelp[lumi][PartC][m][PMTch[1]]==1 and PMTStatusHelp[lumi][PartC][m][PMTch[1]]==1:
                        countC2+=1
                        PMTCurrentC2.fill(PMTCurrentHelp[lumi][PartC][m][PMTch[1]])

                if countA1!=0:
                    cellA1.SetBinContent(m+1, PMTCurrentA1.mean())
                    cellA1.SetBinError(m+1, PMTCurrentA1.error())
                else:
                    cellA1.SetBinContent(m+1, 0.)
                if countA2!=0:
                    cellA2.SetBinContent(m+1, PMTCurrentA2.mean())
                    cellA2.SetBinError(m+1, PMTCurrentA2.error())
                else:
                    cellA2.SetBinContent(m+1, 0.)

                if countC1!=0:
                    cellC1.SetBinContent(m+1, PMTCurrentC1.mean())
                    cellC1.SetBinError(m+1, PMTCurrentC1.error())
                else:
                    cellC1.SetBinContent(m+1, 0.)
                if countC2!=0:
                    cellC2.SetBinContent(m+1, PMTCurrentC2.mean())
                    cellC2.SetBinError(m+1, PMTCurrentC2.error())
                else:
                    cellC2.SetBinContent(m+1, 0.)

                #reset variables
                PMTCurrentA1.reset()
                PMTCurrentA2.reset()
                PMTCurrentC1.reset()
                PMTCurrentC2.reset()

                count=0
            InstLumiMean = InstLumi.mean()
        
        #now plotting
        c =  TCanvas("c","",800,600)
        c.SetBottomMargin(0.2)
        c.SetLogy()

        cellA1.SetLineColor(kBlue)
        cellA1.SetMarkerColor(kBlue)
        cellA1.SetMarkerStyle(20)
        cellA2.SetLineColor(kBlue+2)
        cellA2.SetMarkerColor(kBlue+2)
        cellA2.SetMarkerStyle(20)

        cellC1.SetLineColor(ROOT.kRed)
        cellC1.SetMarkerColor(ROOT.kRed)
        cellC1.SetMarkerStyle(21)
        cellC2.SetLineColor(ROOT.kRed+2)
        cellC2.SetMarkerColor(ROOT.kRed+2)
        cellC2.SetMarkerStyle(21)

        cellA1.Draw("ep")
        cellA2.Draw("epsame")
        cellC1.Draw("epsame")
        cellC2.Draw("epsame")

        maximum = 0.
        minimum = 1000.
        if (cellA1.GetBinContent(cellA1.GetMaximumBin())>maximum): maximum= cellA1.GetBinContent(cellA1.GetMaximumBin())
        if (cellC1.GetBinContent(cellC1.GetMaximumBin())>maximum): maximum= cellC1.GetBinContent(cellC1.GetMaximumBin())
        if (cellA2.GetBinContent(cellA2.GetMaximumBin())>maximum): maximum= cellA2.GetBinContent(cellA2.GetMaximumBin())
        if (cellC2.GetBinContent(cellC2.GetMaximumBin())>maximum): maximum= cellC2.GetBinContent(cellC2.GetMaximumBin())

        if (cellA1.GetBinContent(cellA1.GetMinimumBin())<minimum): minimum= cellA1.GetBinContent(cellA1.GetMinimumBin())
        if (cellC1.GetBinContent(cellC1.GetMinimumBin())<minimum): minimum= cellC1.GetBinContent(cellC1.GetMinimumBin())
        if (cellA2.GetBinContent(cellA2.GetMinimumBin())<minimum): minimum= cellA2.GetBinContent(cellA2.GetMinimumBin())
        if (cellC2.GetBinContent(cellC2.GetMinimumBin())<minimum): minimum= cellC2.GetBinContent(cellC2.GetMinimumBin())


        cellA1.GetXaxis().SetTitle("module number")
        cellA1.GetYaxis().SetTitle("Current [nA]")
        cellA1.GetYaxis().SetTitleOffset(1.2)
        cellA1.SetMaximum(maximum*1.1)
#        Acells.SetMinimum(minimum-10)
        cellA1.SetMinimum(0.1)

        legend = TLegend(0.7,0.6,0.9,0.8)
        legend.SetFillStyle(0)
        legend.SetFillColor(0)
        legend.SetBorderSize(0)
        legend.AddEntry(cellA1,"1st PMT A side","ep")
        legend.AddEntry(cellA2,"2nd PMT A side","ep")
        legend.AddEntry(cellC1,"1st PMT C side", "ep")
        legend.AddEntry(cellC2,"2nd PMT C side", "ep")
        legend.Draw()

        l = TLatex()
        l.SetNDC()
        l.SetTextFont(42)
        l.DrawLatex(0.2,0.9, "L= %.2f 10^{33} cm^{-2}s^{-1}" % (InstLumiMean))
        l.DrawLatex(0.2,0.95, self.cellName)

        c.Modified()
        c.Update()

        plotName = "Cell%sCurrent_vs_module_instLumi_2015_%i" % (self.cellName,self.LumiRange)

        # save plot, several formats...
        c.Print("%s/%s_%s.root" % (self.dir,plotName , str(RunNumber) ))
        c.Print("%s/%s_%s.eps" % (self.dir, plotName , str(RunNumber) ))
        c.Print("%s/%s_%s.png" % (self.dir, plotName , str(RunNumber)))

	   
