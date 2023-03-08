from src.GenericWorker import *
import src.MakeCanvas
import time
import numpy
import src.stats
import math
from src.region import *
from src.run import *
from src.laser.toolbox import *


# class to calculate the coefficients for current/inst lumi, a simplified version: check single runs and all cells, average over consecutive lumiblock for a given lumiblock entries
# worker is called by macro getSimpleCoefficient.py
# then we want to plot this for A,B,DC and E cells  against eta
class GetSimpleCoefficient_2015permodule(GenericWorker):
    "A plot worker for MBias"
    
    def __init__(self, LumiBegin=1, LumiRange=20):
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
        c = ROOT.TCanvas('c','',1400,500)
		
        # all cells
        regionsAll = ['A1', 'A2', 'A3', 'A4', 'A5', 'A6', 'A7', 'A8', 'A9', 'A10', 'A12', 'A13', 'A14', 'A15', 'A16', 'BC1', 'BC2', 'BC3', 'BC4', 'BC5', 'BC6', 'BC7', 'BC8', 'B9', 'C10', 'B11', 'B12', 'B13', 'B14', 'B15', 'D0', 'D1', 'D2', 'D3', 'D4', 'D5', 'D6', 'E1', 'E2', 'E3', 'E4']

        RunNumber = None

        PMTCurrent = None
        LumiBlock = None

        # using mapping from website: only using first pmt                                                                                  
        etamapLB = {0:0.01,1:0.05,2:0.05,5:0.15,6:0.15,9:0.25,11:0.25,13:0.2,15:0.35,16:0.35,19:0.45,21:0.45,23:0.55,24:0.4,27:0.55,33:0.65,29:0.65,\
35:0.75,36:0.85,39:0.75,41:0.6,42:0.85,45:0.95}
        # e cells added manually                                                                                                                  
        etamapEB = {0:1.05,12:1.05,1:1.15,13:1.15,2:0.85,4:0.95,6:1.15942,8:1.05869,10:1.25867,14:1.15803,16:1.00741,20:1.35795,22:1.25738,30:1.35678,31:1.45728,36:1.4562,37:1.20632,40:1.55665}
	


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
                
            # loop over module
            for m in range(64):
                # histograms
                Acells = TH1F("Acells","Acells",32,-1.6,1.6 )
                BCcells = TH1F("BCcells","BCcells",30,-1.5,1.5)
                Dcells = TH1F("Dcells","Dcells",14 , -1.39,1.39)
                Ecells = TH1F("Ecells", "Ecells", 24,-1.2, 1.2 )
                #  we loop over all cells and average over lumiblock entries
                for cell in regionsAll:
                    PMTCurrentA = []
                    PMTCurrentC = []
                    InstLumi = []

                    det_reg = self.PMTool.getRegionName2015(cell)
                    PartA = det_reg[0][0] #long barrel or extended barrel
                    PartC = det_reg[0][1]
                    PMTch = det_reg[1] #pmts belonging to cell, will use my own mapping for channel vs eta
                    # eta values:
                    etaValueA = 10.
                    etaValueC = -10.
                    if PartA==1:
                        etaValueA= etamapLB[PMTch[0]]
                    else:
                        etaValueA= etamapEB[PMTch[0]]
                    etaValueC = -1.*etaValueA
                    countA=0
                    countC=0                    
                    count=0
		    #loop over lb entries
                    for l in range(self.LumiBegin,self.LumiEnd):
                        InstLumi.append(histoFile.GetBinContent(l+1)/1000.)
                        lumi=lumiIndex+count
                        count+=1
                        # start with A side and average two PMTs
                        if PMTCurrentHelp[lumi][PartA][m][PMTch[0]]!=0 and PMTCurrentHelp[lumi][PartA][m][PMTch[1]]!=0 and PMTGoodHelp[lumi][PartA][m][PMTch[0]]==1 and PMTGoodHelp[lumi][PartA][m][PMTch[1]]==1 and PMTStatusHelp[lumi][PartA][m][PMTch[0]]==1 and PMTStatusHelp[lumi][PartA][m][PMTch[1]]==1:
                            PMTCurrentA.append(0.5*(PMTCurrentHelp[lumi][PartA][m][PMTch[0]]+PMTCurrentHelp[lumi][PartA][m][PMTch[1]]))
                            countA+=1
                        else:
                            PMTCurrentA.append(0.0)
                        # c side
                        if PMTCurrentHelp[lumi][PartC][m][PMTch[0]]!=0 and PMTCurrentHelp[lumi][PartC][m][PMTch[1]]!=0 and PMTGoodHelp[lumi][PartC][m][PMTch[0]]==1 and PMTGoodHelp[lumi][PartC][m][PMTch[1]]==1 and PMTStatusHelp[lumi][PartC][m][PMTch[0]]==1 and PMTStatusHelp[lumi][PartC][m][PMTch[1]]==1:
                            PMTCurrentC.append(0.5*(PMTCurrentHelp[lumi][PartC][m][PMTch[0]]+PMTCurrentHelp[lumi][PartC][m][PMTch[1]]))
                            countC+=1
                        else:
                            PMTCurrentC.append(0.0)

                #determine averages for instLumi and current and calculate coefficient
                    instlumiMean = stats()
                    currentA = stats()
                    currentC = stats()
                    for i in range(len(InstLumi)):
                        currentA.fill(PMTCurrentA[i])
                        currentC.fill(PMTCurrentC[i])
                        instlumiMean.fill(InstLumi[i])

                    print(currentC.mean()," ", countC)
                    if countA!=0:
                        lumiCoeffA = currentA.mean()#/instlumiMean.mean()    
                        lumiCoeffErrA = currentA.error()#math.sqrt((currentA.error()/instlumiMean.mean())**2+(currentA.mean()*instlumiMean.error()/instlumiMean.mean()**2)**2)
                    else:
                        lumiCoeffA= 0.0
                        lumiCeoffErrA = 0.0
                    if countC!=0:
                        lumiCoeffC = currentC.mean()#/instlumiMean.mean()    
                        lumiCoeffErrC = currentC.error()#math.sqrt((currentC.error()/instlumiMean.mean())**2+(currentC.mean()*instlumiMean.error()/instlumiMean.mean()**2)**2)
                    else:
                        lumiCoeffC = 0.0
                        lumiCoeffErrC = 0.0
                    
                    InstLumiMean = instlumiMean.mean()

                        
                    if cell.startswith('A'):
                        Acells.SetBinContent(Acells.FindBin(etaValueA), lumiCoeffA )
                        Acells.SetBinError(Acells.FindBin(etaValueA),lumiCoeffErrA)
                        Acells.SetBinContent(Acells.FindBin(etaValueC), lumiCoeffC )
                        Acells.SetBinError(Acells.FindBin(etaValueC),lumiCoeffErrC)        
                    if cell.startswith('B') or cell.startswith('C'):
                        BCcells.SetBinContent(BCcells.FindBin(etaValueA), lumiCoeffA )
                        BCcells.SetBinError(BCcells.FindBin(etaValueA),lumiCoeffErrA)
                        BCcells.SetBinContent(BCcells.FindBin(etaValueC), lumiCoeffC )
                        BCcells.SetBinError(BCcells.FindBin(etaValueC),lumiCoeffErrC)        
                    if cell.startswith('D'):
                        Dcells.SetBinContent(Dcells.FindBin(etaValueA), lumiCoeffA )
                        Dcells.SetBinError(Dcells.FindBin(etaValueA),lumiCoeffErrA)
                        Dcells.SetBinContent(Dcells.FindBin(etaValueC), lumiCoeffC )
                        Dcells.SetBinError(Dcells.FindBin(etaValueC),lumiCoeffErrC)        
                    if cell.startswith('E'):
                        Ecells.SetBinContent(Ecells.FindBin(etaValueA), lumiCoeffA )
                        Ecells.SetBinError(Ecells.FindBin(etaValueA),lumiCoeffErrA)
                        Ecells.SetBinContent(Ecells.FindBin(etaValueC), lumiCoeffC )
                        Ecells.SetBinError(Ecells.FindBin(etaValueC),lumiCoeffErrC)        

        
                # now plotting for each module
                c =  TCanvas("c","",800,600)
                c.SetBottomMargin(0.2)
        
                Acells.SetLineColor(kBlack)
                Acells.SetMarkerStyle(20)
                Acells.SetMarkerColor(kBlack)
                BCcells.SetLineColor(ROOT.kRed)
                BCcells.SetMarkerStyle(21)
                BCcells.SetMarkerColor(ROOT.kRed)
                Dcells.SetLineColor(kBlue)
                Dcells.SetMarkerStyle(22)
                Dcells.SetMarkerColor(kBlue)
                Ecells.SetLineColor(418)
                Ecells.SetMarkerStyle(23)
                Ecells.SetMarkerColor(418)

                Acells.Draw("ep")
                BCcells.Draw("epsame")
                Dcells.Draw("epsame")
                Ecells.Draw("epsame")

                maximum = 0.
                minimum = 1000.
                if (Acells.GetBinContent(Acells.GetMaximumBin())>maximum): maximum= Acells.GetBinContent(Acells.GetMaximumBin())
                if (BCcells.GetBinContent(BCcells.GetMaximumBin())>maximum): maximum= BCcells.GetBinContent(BCcells.GetMaximumBin())
                if (Dcells.GetBinContent(Dcells.GetMaximumBin())>maximum): maximum= Dcells.GetBinContent(Dcells.GetMaximumBin())
                if (Ecells.GetBinContent(Ecells.GetMaximumBin())>maximum): maximum= Ecells.GetBinContent(Ecells.GetMaximumBin())
                    
                if (Acells.GetBinContent(Acells.GetMinimumBin())<minimum): minimum= Acells.GetBinContent(Acells.GetMinimumBin())
                if (BCcells.GetBinContent(BCcells.GetMinimumBin())<minimum): minimum= BCcells.GetBinContent(BCcells.GetMinimumBin())
                if (Dcells.GetBinContent(Dcells.GetMinimumBin())<minimum): minimum= Dcells.GetBinContent(Dcells.GetMinimumBin())

                Acells.GetXaxis().SetTitle("#eta_{cell}")
#        Acells.GetYaxis().SetTitle("Coefficient [nA#times 10^{-33} cm^{2}s]")
                Acells.GetYaxis().SetTitle("Current [nA]")
                Acells.GetYaxis().SetTitleOffset(1.2)
                Acells.SetMaximum(maximum+10)
#        Acells.SetMinimum(minimum-10)



                legend = TLegend(0.5,0.6,0.7,0.8)
                legend.SetFillStyle(0)
                legend.SetFillColor(0)
                legend.SetBorderSize(0)
                legend.AddEntry(Acells,"A cells","ep")
                legend.AddEntry(BCcells,"BC cells", "ep");
                legend.AddEntry(Dcells,"D cells","ep");
                legend.AddEntry(Ecells,"E cells","ep");
                legend.Draw()

                l = TLatex()
                l.SetNDC()
                l.SetTextFont(42)
                l.DrawLatex(0.5,0.96, "L= %.2f 10^{33} cm^{-2}s^{-1}, module %i" % (InstLumiMean, m))

                c.Modified()
                c.Update()

                plotName = "Current_vs_eta_instLumimodule%i_2015_%i" % (m,self.LumiRange)

        # save plot, several formats...
                c.Print("%s/%s_%s.root" % (self.dir,plotName , str(RunNumber) ))
                c.Print("%s/%s_%s.eps" % (self.dir, plotName , str(RunNumber) ))
                c.Print("%s/%s_%s.png" % (self.dir, plotName , str(RunNumber)))

                c.Delete()
                del Acells,BCcells,Dcells,Ecells
	   
