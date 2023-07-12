from src.GenericWorker import *
import src.MakeCanvas
import time
import numpy
import src.stats
import math
from src.region import *
from src.run import *
from src.laser.toolbox import *

import matplotlib.pyplot as plt

#if os.environ.get('TUCS'):
#    ROOT.gROOT.LoadMacro("$TUCS/root_macros/AtlasStyle.C")
#    ROOT.SetAtlasStyle()
#    ROOT.gROOT.ForceStyle()


# class to calculate the coefficients for current/inst lumi, a simplified version: check single runs and all cells, average over consecutive lumiblock for a given lumiblock entries
# worker is called by macro getSimpleCoefficient.py
# then we want to plot this for A,B,DC and E cells  against eta
class GetSimpleCoefficient_2015(GenericWorker):
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
                if 'LumiBlock' in list(event.run.data.keys()):# valid entries in run?? some files seem buggy for 2015  
                    self.eventsList.append(event)
                #print 'Run ', event.run.runNumber

    def        ProcessStop(self):
        
        ROOT.gStyle.SetPalette(1)
        ROOT.gROOT.LoadMacro("root_macros/AtlasStyle.C")
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
        etamapLB = {0:0.01,1:0.05,2:0.05,5:0.15,6:0.15,9:0.25,11:0.25,13:0.2,15:0.35,16:0.35,19:0.45,21:0.45,23:0.55,25:0.4,28:0.55,34:0.65,27:0.65,\
33:0.75,37:0.85,40:0.75,39:0.6,44:0.85,46:0.95}
        # e cells added manually                                                                                                                  
        etamapEB = {0:1.30,12:1.05,1:1.50,13:1.15,2:0.85,4:0.95,6:1.15942,8:1.05869,10:1.25867,14:1.15803,16:1.00741,20:1.35795,22:1.25738,32:1.35678,28:1.45728,42:1.4562,36:1.20632,40:1.55665}        
        # histograms
        Acells  = TH1F("Acells","Acells",32,-1.6,1.6 )
        BCcells = TH1F("BCcells","BCcells",30,-1.5,1.5)
        Dcells  = TH1F("Dcells","Dcells",14 , -1.39,1.39)
        Ecells  = TH1F("Ecells", "Ecells", 24,-1.2, 1.2 )

        #2D histograms/profile --> range would depend on the 
        #take note of range!!!
        
        EtaBins_Ecells = [-1.6, -1.4, -1.2, -1.1, -1.0, 0.0, 1.0, 1.1, 1.2, 1.4, 1.6]
        YBins_Ecells = [(x * 4)+0.1 for x in range(0, 401)] 
        EtaBins_Dcells = [-1.39, -1.1, -0.9, -0.7, -0.5, -0.3, -0.1, 0.1, 0.3, 0.5, 0.7, 0.9, 1.1, 1.39]
        YBins_Dcells = [(x * 0.5)+0.01 for x in range(0, 401)] 
        
        currentvseta_A  = ROOT.TH2F("currentvseta_A", '', 32, -1.60, 1.60, 400, 0.0, 200.0)        
        currentvseta_BC = ROOT.TH2F("currentvseta_BC",'', 30, -1.50, 1.50, 400, 0.0, 200.0)        
        #currentvseta_D  = ROOT.TH2F("currentvseta_D", '', 14, -1.39, 1.39, 400, 0.01, 200.01)
        currentvseta_D  = ROOT.TH2F("currentvseta_D", '', 13, array('d',EtaBins_Dcells), 400, array('d',YBins_Dcells))
        currentvseta_E  = ROOT.TH2F("currentvseta_E", '', 10, array('d',EtaBins_Ecells), 400, array('d',YBins_Ecells))
        currentvseta_prof_A  = ROOT.TProfile("currentvseta_prof_A", '', 32, -1.60, 1.60, 'S')    
        currentvseta_prof_BC = ROOT.TProfile("currentvseta_prof_BC",'', 30, -1.50, 1.50, 'S')    
        #currentvseta_prof_D  = ROOT.TProfile("currentvseta_prof_D", '', 14, -1.39, 1.39, 'S')    
        currentvseta_prof_D  = ROOT.TProfile("currentvseta_prof_D", '', 13, array('d',EtaBins_Dcells), 'S')    
        currentvseta_prof_E  = ROOT.TProfile("currentvseta_prof_E", '', 10, array('d',EtaBins_Ecells), 'S')    
        #---2D
        
        # get files with info on inst. lumi for given lumiblock
        filename = os.getenv("TUCS")+"data/ilumicalc_histograms_None_276262-284484.root"
        print(filename)
        file = TFile(filename,'READ' )
        file.cd()

        InstLumiMean = None

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
           
#           InstLumiMean = None
            PMTCurrentHelp = event.run.data['PMTCurrent']
            PMTStatusHelp = event.run.data['PMTStatus']
            PMTGoodHelp = event.run.data['IsGood']

            lumiIndex = 0
            #have to find the right lumi index
            for i in range(len(event.run.data['LumiBlock'])):
                if event.run.data['LumiBlock'][i]==self.LumiBegin:
                    lumiIndex=i
                    break
                
            #  we loop over all cells and average over modules
            for cell in regionsAll:

                det_reg = self.PMTool.getRegionName2015(cell, False)
                PartA = det_reg[0][0] #long barrel or extended barrel
                PartC = det_reg[0][1]
                PMTch = det_reg[1] #pmts belonging to cell, will use my own mapping for channel vs eta
                #eta values:
                etaValueA = 10.
                etaValueC = -10.
                if PartA==1:
                    etaValueA= etamapLB[PMTch[0]]
                else:
                    etaValueA= etamapEB[PMTch[0]]
                etaValueC = -1.*etaValueA
                
                cellmeanA = stats()
                cellmeanC = stats()
                count=0
                #determine averages for instLumi and current and calculate coefficient
                instlumiMean = stats()
                currentA = stats() # means of cellmeanA go here
                currentC = stats() # means of cellmeanC go here
                #loop over lb entries
                for l in range(self.LumiBegin,self.LumiEnd):
                    
                    #2016#instlumiMean.fill(histoFile.GetBinContent(l+1)/1000.)
                    #loop over modules in A and C-side        but save inputs separately )need to average over all modules
                    countA=0
                    countC=0
                    lumi=lumiIndex+count
#                    print lumi
                    count+=1




                    # start with A side and average two PMTs
                    for m in range(len(PMTCurrentHelp[lumi][PartA])):# 
                        if cell=="C10" and ((m>=38 and m<=41)  or (m>=54 and m<=57)):
                            continue
                        if m==14 and "E" in cell: continue#PMTch = self.PMTool.getRegionName2015(cell, True)[1] # special EBA15
                        if cell.startswith('E1') and (m+1==7 or m+1==25 or m+1==44 or m+1==53): continue #E1merged
                        if cell.startswith('E1') and (m+1==8 or m+1==24 or m+1==43 or m+1==54): continue #MBTS outer
                        #For 2D
                        if PMTStatusHelp[lumi][PartA][m][PMTch[0]]==1 and PMTGoodHelp[lumi][PartA][m][PMTch[0]]==1 and PMTCurrentHelp[lumi][PartA][m][PMTch[0]]>0.:                            
                           if cell.startswith('A'):  
                              currentvseta_A.Fill(etaValueA, PMTCurrentHelp[lumi][PartA][m][PMTch[0]])
                              currentvseta_prof_A.Fill(etaValueA, PMTCurrentHelp[lumi][PartA][m][PMTch[0]])
                           if cell.startswith('B') or cell.startswith('C'):
                              currentvseta_BC.Fill(etaValueA, PMTCurrentHelp[lumi][PartA][m][PMTch[0]])
                              currentvseta_prof_BC.Fill(etaValueA, PMTCurrentHelp[lumi][PartA][m][PMTch[0]])
                           if cell.startswith('D'):
                              currentvseta_D.Fill(etaValueA, PMTCurrentHelp[lumi][PartA][m][PMTch[0]])
                              currentvseta_prof_D.Fill(etaValueA, PMTCurrentHelp[lumi][PartA][m][PMTch[0]])
                           if cell.startswith('E'):
                              currentvseta_E.Fill(etaValueA, PMTCurrentHelp[lumi][PartA][m][PMTch[0]])
                              currentvseta_prof_E.Fill(etaValueA, PMTCurrentHelp[lumi][PartA][m][PMTch[0]])
                        if PMTStatusHelp[lumi][PartA][m][PMTch[1]]==1 and PMTGoodHelp[lumi][PartA][m][PMTch[1]]==1 and PMTCurrentHelp[lumi][PartA][m][PMTch[1]]>0.:
                           if cell.startswith('A'):
                              currentvseta_A.Fill(etaValueA, PMTCurrentHelp[lumi][PartA][m][PMTch[1]])
                              currentvseta_prof_A.Fill(etaValueA, PMTCurrentHelp[lumi][PartA][m][PMTch[1]])
                           if cell.startswith('B') or cell.startswith('C'):
                              currentvseta_BC.Fill(etaValueA, PMTCurrentHelp[lumi][PartA][m][PMTch[1]])
                              currentvseta_prof_BC.Fill(etaValueA, PMTCurrentHelp[lumi][PartA][m][PMTch[1]])
                           if cell.startswith('D'):
                              currentvseta_D.Fill(etaValueA, PMTCurrentHelp[lumi][PartA][m][PMTch[1]])
                              currentvseta_prof_D.Fill(etaValueA, PMTCurrentHelp[lumi][PartA][m][PMTch[1]])
                           if cell.startswith('E'):
                              currentvseta_E.Fill(etaValueA, PMTCurrentHelp[lumi][PartA][m][PMTch[1]])
                              currentvseta_prof_E.Fill(etaValueA, PMTCurrentHelp[lumi][PartA][m][PMTch[1]])
                                                      
                        if PMTCurrentHelp[lumi][PartA][m][PMTch[0]]==0 or PMTCurrentHelp[lumi][PartA][m][PMTch[1]]==0: continue
                        if PMTGoodHelp[lumi][PartA][m][PMTch[0]]<1 or PMTGoodHelp[lumi][PartA][m][PMTch[1]]<1: continue
                        if PMTStatusHelp[lumi][PartA][m][PMTch[0]]<1 or PMTStatusHelp[lumi][PartA][m][PMTch[1]]<1: continue
                        countA+=1
#                        cellmeanA.fill(0.5*(PMTCurrentHelp[lumi][PartA][m][PMTch[0]]+PMTCurrentHelp[lumi][PartA][m][PMTch[1]]))#average over two pmts
                        cellmeanA.fill(PMTCurrentHelp[lumi][PartA][m][PMTch[0]])
                        cellmeanA.fill(PMTCurrentHelp[lumi][PartA][m][PMTch[1]])
                    # c side
                    for m in range(len(PMTCurrentHelp[lumi][PartC])):#
                        if cell=="C10" and ((m>=38 and m<=41)  or (m>=54 and m<=57)):
                            continue
                        if m==17 and "E" in cell: continue#PMTch = self.PMTool.getRegionName2015(cell, True)[1] # special EBC18
                        if cell.startswith('E1') and (m==31 or m==33 or m==36): continue #E1 close to saturation
                        if cell.startswith('E4') and (m+1==29 or m+1==32 or m+1==34 or m+1==37): continue #E4p
                        if cell.startswith('E1') and (m+1==7 or m+1==25 or m+1==44 or m+1==53): continue #E1merged
                        if cell.startswith('E1') and (m+1==28 or m+1==31 or m+1==35 or m+1==38): continue #E1merged
                        if cell.startswith('E1') and (m+1==8 or m+1==24 or m+1==43 or m+1==54): continue #MBTS outer
                        if cell.startswith('E2') and m==39: continue #E2 saturated
                        #For 2D
                        if PMTStatusHelp[lumi][PartC][m][PMTch[0]]==1 and PMTGoodHelp[lumi][PartC][m][PMTch[0]]==1 and PMTCurrentHelp[lumi][PartC][m][PMTch[0]]>0.:
                           if cell.startswith('A'):
                              currentvseta_A.Fill(etaValueC, PMTCurrentHelp[lumi][PartC][m][PMTch[0]])
                              currentvseta_prof_A.Fill(etaValueC, PMTCurrentHelp[lumi][PartC][m][PMTch[0]])
                           if cell.startswith('B') or cell.startswith('C'):
                              currentvseta_BC.Fill(etaValueC, PMTCurrentHelp[lumi][PartC][m][PMTch[0]])
                              currentvseta_prof_BC.Fill(etaValueC, PMTCurrentHelp[lumi][PartC][m][PMTch[0]])
                           if cell.startswith('D'):
                              currentvseta_D.Fill(etaValueC, PMTCurrentHelp[lumi][PartC][m][PMTch[0]])
                              currentvseta_prof_D.Fill(etaValueC, PMTCurrentHelp[lumi][PartC][m][PMTch[0]])
                           if cell.startswith('E'):
                              currentvseta_E.Fill(etaValueC, PMTCurrentHelp[lumi][PartC][m][PMTch[0]])
                              currentvseta_prof_E.Fill(etaValueC, PMTCurrentHelp[lumi][PartC][m][PMTch[0]])
                        if PMTStatusHelp[lumi][PartC][m][PMTch[1]]==1 and PMTGoodHelp[lumi][PartC][m][PMTch[1]]==1 and PMTCurrentHelp[lumi][PartC][m][PMTch[1]]>0.:
                           if cell.startswith('A'):
                              currentvseta_A.Fill(etaValueC, PMTCurrentHelp[lumi][PartC][m][PMTch[1]])
                              currentvseta_prof_A.Fill(etaValueC, PMTCurrentHelp[lumi][PartC][m][PMTch[1]])
                           if cell.startswith('B') or cell.startswith('C'):
                              currentvseta_BC.Fill(etaValueC, PMTCurrentHelp[lumi][PartC][m][PMTch[1]])
                              currentvseta_prof_BC.Fill(etaValueC, PMTCurrentHelp[lumi][PartC][m][PMTch[1]])
                           if cell.startswith('D'):
                              currentvseta_D.Fill(etaValueC, PMTCurrentHelp[lumi][PartC][m][PMTch[1]])
                              currentvseta_prof_D.Fill(etaValueC, PMTCurrentHelp[lumi][PartC][m][PMTch[1]])
                           if cell.startswith('E'):
                              #if cell=="E1" and PMTCurrentHelp[lumi][PartC][m][PMTch[1]]>100.:
                              #   print cell, " ", etaValueC, " ", PMTCurrentHelp[lumi][PartC][m][PMTch[1]], " ", m, " ", PMTch
                              #if cell=="E2" and PMTCurrentHelp[lumi][PartC][m][PMTch[1]]>200.:
                              #   print cell, " ", etaValueC, " ", PMTCurrentHelp[lumi][PartC][m][PMTch[1]], " ", m, " ", PMTch
                              currentvseta_E.Fill(etaValueC, PMTCurrentHelp[lumi][PartC][m][PMTch[1]])
                              currentvseta_prof_E.Fill(etaValueC, PMTCurrentHelp[lumi][PartC][m][PMTch[1]])
                                                      
                        if PMTCurrentHelp[lumi][PartC][m][PMTch[0]]==0 or PMTCurrentHelp[lumi][PartC][m][PMTch[1]]==0: continue
                        if PMTGoodHelp[lumi][PartC][m][PMTch[0]]<1 or PMTGoodHelp[lumi][PartC][m][PMTch[1]]<1: continue
                        if PMTStatusHelp[lumi][PartC][m][PMTch[0]]<1 or PMTStatusHelp[lumi][PartC][m][PMTch[1]]<1: continue
                        countC+=1
#                        cellmeanC.fill(0.5*(PMTCurrentHelp[lumi][PartC][m][PMTch[0]]+PMTCurrentHelp[lumi][PartC][m][PMTch[1]]))
                        cellmeanC.fill(PMTCurrentHelp[lumi][PartC][m][PMTch[0]])
                        cellmeanC.fill(PMTCurrentHelp[lumi][PartC][m][PMTch[1]])
###----- for Cora to check
                    if cellmeanA.mean(): currentA.fill(cellmeanA.mean(), 1.0)
                    if cellmeanC.mean(): currentC.fill(cellmeanC.mean(), 1.0)
#                    currentA.fill(cellmeanA.mean(), 1./pow(cellmeanA.error() ,2)) # use mean error --> standard deviation
#                    currentC.fill(cellmeanC.mean(), 1./pow(cellmeanC.error() ,2)) # use mean error --> standard deviation
###-----

#                    if countA==0: currentA.(0.0)
#                    else: PMTCurrentA.append(cellmeanA.mean())
#                    if countC==0: PMTCurrentC.append(0.0)
#                    else: PMTCurrentC.append(cellmeanC.mean())
                    cellmeanA.reset()
                    cellmeanC.reset()

#                print currentA.mean()
                ###----- for Cora to check
                lumiCoeffA = currentA.mean()#/instlumiMean.mean()    
                #lumiCoeffErrA = currentA.weighterr()#math.sqrt((currentA.error()/instlumiMean.mean())**2+(currentA.mean()*instlumiMean.error()/instlumiMean.mean()**2)**2)
                if currentA.weighterr(): lumiCoeffErrA = currentA.weighterr()
                else: lumiCoeffErrA = 0.0
                lumiCoeffC = currentC.mean()#/instlumiMean.mean()    
                #lumiCoeffErrC = currentC.weighterr()#math.sqrt((currentC.error()/instlumiMean.mean())**2+(currentC.mean()*instlumiMean.error()/instlumiMean.mean()**2)**2)
                if currentC.weighterr(): lumiCoeffErrC = currentC.weighterr()  
                else: lumiCoeffErrC = 0.0
                ###------

                #2016#InstLumiMean = instlumiMean.mean()
                
                if cell.startswith('A'):
                    Acells.SetBinContent(Acells.FindBin(etaValueA), lumiCoeffA )
                    Acells.SetBinError(Acells.FindBin(etaValueA),   lumiCoeffErrA)
                    Acells.SetBinContent(Acells.FindBin(etaValueC), lumiCoeffC )
                    Acells.SetBinError(Acells.FindBin(etaValueC),   lumiCoeffErrC)        
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
                ####----- for Cora to check
                #if cell.startswith('E'):
                #    Ecells.SetBinContent(Ecells.FindBin(etaValueA), lumiCoeffA )
                #    Ecells.SetBinError(Ecells.FindBin(etaValueA),lumiCoeffErrA)
                #    Ecells.SetBinContent(Ecells.FindBin(etaValueC), lumiCoeffC )
                #    Ecells.SetBinError(Ecells.FindBin(etaValueC),lumiCoeffErrC)  
                ####---- for Cora to check      

        
        ###2016 arelycg
        #InstLumiMean = 0.1762 #Run 297730
        InstLumiMean = 0.2011 #Run 298633
        #InstLumiMean = 0.2011 #Run 298591
        #InstLumiMean = 0.1513 #Run 298609
        
        #Now plotting
        c =  TCanvas("c","",800,600)
        c.SetBottomMargin(0.2)
        legend = TLegend(0.45,0.65,0.7,0.85)
        legend.SetFillStyle(0)
        legend.SetFillColor(0)
        legend.SetBorderSize(0)
        legendE = TLegend(0.45,0.58,0.7,0.85)
        legendE.SetFillStyle(0)
        legendE.SetFillColor(0)
        legendE.SetBorderSize(0)

        l = TLatex()
        l.SetNDC()
        l.SetTextFont(42)
        
        #From SCAT
        
        #Format
        currentvseta_A.SetMarkerStyle(1)
        currentvseta_BC.SetMarkerStyle(1)
        currentvseta_D.SetMarkerStyle(1)
        currentvseta_E.SetMarkerStyle(1)
        currentvseta_A.SetMarkerColor(kGray)
        currentvseta_BC.SetMarkerColor(ROOT.kRed-9)
        currentvseta_D.SetMarkerColor(kBlue-9)
        currentvseta_E.SetMarkerColor(kGreen-9)
        currentvseta_A.GetXaxis().SetTitle("#eta_{cell}")
        currentvseta_A.GetXaxis().SetTitleSize(0.06)
        currentvseta_A.GetYaxis().SetTitle("Current [nA]")
        currentvseta_A.GetYaxis().SetTitleOffset(1.2)
        currentvseta_E.GetXaxis().SetTitle("#eta_{cell}")
        currentvseta_E.GetXaxis().SetTitleSize(0.06)
        currentvseta_E.GetYaxis().SetTitle("Current [nA]")
        currentvseta_E.GetYaxis().SetTitleOffset(1.2)
        currentvseta_prof_A.GetXaxis().SetTitle("#eta_{cell}")
        currentvseta_prof_A.GetXaxis().SetTitleSize(0.06)
        currentvseta_prof_A.GetYaxis().SetTitle("Current [nA]")
        currentvseta_prof_A.GetYaxis().SetTitleOffset(1.2)
        currentvseta_prof_E.GetXaxis().SetTitle("#eta_{cell}")
        currentvseta_prof_E.GetXaxis().SetTitleSize(0.06)
        currentvseta_prof_E.GetYaxis().SetTitle("Current [nA]")
        currentvseta_prof_E.GetYaxis().SetTitleOffset(1.2)
        
        currentvseta_prof_A.SetLineColor(kBlack)
        currentvseta_prof_BC.SetLineColor(ROOT.kRed)
        currentvseta_prof_D.SetLineColor(kBlue)
        currentvseta_prof_E.SetLineColor(kGreen+2)
        
        currentvseta_prof_A.SetMarkerColor(kBlack)
        currentvseta_prof_BC.SetMarkerColor(ROOT.kRed)
        currentvseta_prof_D.SetMarkerColor(kBlue)
        currentvseta_prof_E.SetMarkerColor(kGreen+2)
        
        currentvseta_prof_A.SetMarkerStyle(kFullCircle)
        currentvseta_prof_BC.SetMarkerStyle(kFullSquare)
        currentvseta_prof_D.SetMarkerStyle(kFullTriangleUp)
        currentvseta_prof_E.SetMarkerStyle(kFullTriangleDown)
        
        currentvseta_prof_A.SetMarkerSize(1.1)
        currentvseta_prof_BC.SetMarkerSize(1.1)
        currentvseta_prof_D.SetMarkerSize(1.1)
        currentvseta_prof_E.SetMarkerSize(1.1)
        
        
        #Draw
        prof_maxYbin = (int) (1.5 * currentvseta_prof_A.GetMaximum())
        currentvseta_A.GetYaxis().SetRange(1,2*prof_maxYbin)
        currentvseta_A.Draw("SCAT")
        currentvseta_BC.Draw("SCATsame")
        currentvseta_D.Draw("SCATsame")
        currentvseta_prof_A.Draw("same")
        currentvseta_prof_BC.Draw("same")
        currentvseta_prof_D.Draw("same")
        
        legend.Clear()
        legend.AddEntry(currentvseta_prof_A, "A cells",  "lep")
        legend.AddEntry(currentvseta_prof_BC,"BC cells", "lep");
        legend.AddEntry(currentvseta_prof_D, "D cells",  "lep");
        legend.Draw()

        l.SetTextFont(72)
        l.DrawLatex(0.2,0.88, "ATLAS")
        l.SetTextFont(42)
        l.DrawLatex(0.33,0.88, "Internal")
        l.DrawLatex(0.2,0.83, "Tile Calorimeter")
        l.DrawLatex(0.2,0.78, "Data 2016")
        l.DrawLatex(0.5,0.85, "#scale[0.9]{#sqrt{s} = 13 TeV, L = %.1f#times10^{33} cm^{-2}s^{-1}}" % (InstLumiMean))

        c.Modified()
        c.Update()

        plotName = "Current_vs_eta_SCAT_instLumi_2016_%i" % (self.LumiRange)

        # save plot, several formats...
        c.Print("%s/%s_%s.root" % (self.dir,plotName , str(RunNumber) ))
        c.Print("%s/%s_%s.eps" % (self.dir, plotName , str(RunNumber) ))
        c.Print("%s/%s_%s.png" % (self.dir, plotName , str(RunNumber) ))
        
        currentvseta_prof_A.SetMaximum(prof_maxYbin)
        currentvseta_prof_A.Draw()
        currentvseta_prof_BC.Draw("same")
        currentvseta_prof_D.Draw("same")
        
        legend.Clear()
        legend.AddEntry(currentvseta_prof_A, "A cells",  "lep")
        legend.AddEntry(currentvseta_prof_BC,"BC cells", "lep");
        legend.AddEntry(currentvseta_prof_D, "D cells",  "lep");
        legend.Draw()
        
        l.SetTextFont(72)
        l.DrawLatex(0.2,0.88, "ATLAS")
        l.SetTextFont(42)
        l.DrawLatex(0.33,0.88, "Internal")
        l.DrawLatex(0.2,0.83, "Tile Calorimeter")
        l.DrawLatex(0.2,0.78, "Data 2016")
        l.DrawLatex(0.5,0.85, "#scale[0.9]{#sqrt{s} = 13 TeV, L = %.1f#times10^{33} cm^{-2}s^{-1}}" % (InstLumiMean))

        c.Modified()
        c.Update()

        plotName = "Current_vs_eta_PROF_instLumi_2016_%i" % (self.LumiRange)

        # save plot, several formats...
        c.Print("%s/%s_%s.root" % (self.dir,plotName , str(RunNumber) ))
        c.Print("%s/%s_%s.eps" % (self.dir, plotName , str(RunNumber) ))
        c.Print("%s/%s_%s.png" % (self.dir, plotName , str(RunNumber) ))
        
        
        ##Now include E-cells.
        #Draw
        prof_EmaxYbin = (int) (0.25 * 100. * currentvseta_prof_E.GetMaximum())
        currentvseta_prof_E.SetMaximum(4.0*prof_EmaxYbin)
        currentvseta_prof_E.SetMinimum(0.01)
        #currentvseta_E.GetYaxis().SetRange(1,prof_EmaxYbin)
        
        currentvseta_prof_E.Draw()
        currentvseta_E.Draw("SCATsame")
        currentvseta_A.Draw("SCATsame")
        currentvseta_BC.Draw("SCATsame")
        currentvseta_D.Draw("SCATsame")
        currentvseta_prof_A.Draw("same")
        currentvseta_prof_BC.Draw("same")
        currentvseta_prof_D.Draw("same")
        currentvseta_prof_E.Draw("same")
        
        legendE.Clear()
        legendE.AddEntry(currentvseta_prof_A, "A cells",  "lep")
        legendE.AddEntry(currentvseta_prof_BC,"BC cells", "lep");
        legendE.AddEntry(currentvseta_prof_D, "D cells",  "lep");
        legendE.AddEntry(currentvseta_prof_E, "E cells",  "lep");
        legendE.Draw()

        l.SetTextFont(72)
        l.DrawLatex(0.2,0.88, "ATLAS")
        l.SetTextFont(42)
        l.DrawLatex(0.33,0.88, "Internal")
        l.DrawLatex(0.2,0.83, "Tile Calorimeter")
        l.DrawLatex(0.2,0.78, "Data 2016")
        l.DrawLatex(0.5,0.85, "#scale[0.9]{#sqrt{s} = 13 TeV, L = %.1f#times10^{33} cm^{-2}s^{-1}}" % (InstLumiMean))

        c.SetLogy(1)
        c.Modified()
        c.Update()

        plotName = "Current_vs_eta_logSCAT_instLumi_2016_%i" % (self.LumiRange)

        # save plot, several formats...
        c.Print("%s/%s_%s.root" % (self.dir,plotName , str(RunNumber) ))
        c.Print("%s/%s_%s.eps" % (self.dir, plotName , str(RunNumber) ))
        c.Print("%s/%s_%s.png" % (self.dir, plotName , str(RunNumber) ))
        
        #prof_EmaxYbin = (int) (0.25 * 100. * currentvseta_prof_E.GetMaximum())
        #currentvseta_prof_E.SetMaximum(4.0*prof_EmaxYbin)
        #currentvseta_prof_E.SetMinimum(0.01)
        currentvseta_prof_E.Draw()
        currentvseta_prof_A.Draw("same")
        currentvseta_prof_BC.Draw("same")
        currentvseta_prof_D.Draw("same")
        
        legendE.Clear()
        legendE.AddEntry(currentvseta_prof_A, "A cells",  "lep")
        legendE.AddEntry(currentvseta_prof_BC,"BC cells", "lep");
        legendE.AddEntry(currentvseta_prof_D, "D cells",  "lep");
        legendE.AddEntry(currentvseta_prof_E, "E cells",  "lep");
        legendE.Draw()
        
        l.SetTextFont(72)
        l.DrawLatex(0.2,0.88, "ATLAS")
        l.SetTextFont(42)
        l.DrawLatex(0.33,0.88, "Internal")
        l.DrawLatex(0.2,0.83, "Tile Calorimeter")
        l.DrawLatex(0.2,0.78, "Data 2016")
        l.DrawLatex(0.5,0.85, "#scale[0.9]{#sqrt{s} = 13 TeV, L = %.1f#times10^{33} cm^{-2}s^{-1}}" % (InstLumiMean))

        c.SetLogy(1)
        c.Modified()
        c.Update()

        plotName = "Current_vs_eta_logPROF_instLumi_2016_%i" % (self.LumiRange)

        # save plot, several formats...
        c.Print("%s/%s_%s.root" % (self.dir,plotName , str(RunNumber) ))
        c.Print("%s/%s_%s.eps" % (self.dir, plotName , str(RunNumber) ))
        c.Print("%s/%s_%s.png" % (self.dir, plotName , str(RunNumber) ))
        
        
        ###COEFF
        c.SetLogy(0)
        currentvseta_prof_A.GetYaxis().SetTitle("Luminosity Coefficient [#times10^{-33}nA#timescm^{2}s]")
        currentvseta_prof_A.Scale(1.0/InstLumiMean)
        for i in range(currentvseta_prof_A.GetNbinsX()):
            print(currentvseta_prof_A.GetBinContent(i+1))
        currentvseta_prof_BC.Scale(1.0/InstLumiMean)
        currentvseta_prof_D.Scale(1.0/InstLumiMean)
        currentvseta_prof_A.SetMaximum((1.0/InstLumiMean)*prof_maxYbin)
        currentvseta_prof_E.SetMinimum(0.1)
        currentvseta_prof_A.Draw()
        currentvseta_prof_BC.Draw("same")
        currentvseta_prof_D.Draw("same")
        
        legend.Clear()
        legend.AddEntry(currentvseta_prof_A, "A cells",  "lep")
        legend.AddEntry(currentvseta_prof_BC,"BC cells", "lep");
        legend.AddEntry(currentvseta_prof_D, "D cells",  "lep");
        legend.Draw()
        
        l.SetTextFont(72)
        l.DrawLatex(0.2,0.88, "ATLAS")
        l.SetTextFont(42)
        l.DrawLatex(0.33,0.88, "Internal")
        l.DrawLatex(0.2,0.83, "Tile Calorimeter")
        l.DrawLatex(0.2,0.78, "Data 2016")
        l.DrawLatex(0.76,0.85, "#scale[0.9]{#sqrt{s} = 13 TeV}")

        c.Modified()
        c.Update()

        plotName = "Coeff_vs_eta_PROF_instLumi_2016_%i" % (self.LumiRange)

        # save plot, several formats...
        c.Print("%s/%s_%s.root" % (self.dir,plotName , str(RunNumber) ))
        c.Print("%s/%s_%s.eps" % (self.dir, plotName , str(RunNumber) ))
        c.Print("%s/%s_%s.png" % (self.dir, plotName , str(RunNumber) ))

        
        ###COEFF with E-cells
        currentvseta_prof_E.GetYaxis().SetTitle("Luminosity Coefficient [#times10^{-33}nA#timescm^{2}s]")
        currentvseta_prof_E.Scale(1.0/InstLumiMean)
        for i in range(currentvseta_prof_E.GetNbinsX()):
            print("E cells: ", currentvseta_prof_E.GetBinContent(i+1))
        currentvseta_prof_E.SetMaximum((1.0/InstLumiMean)*4.0*prof_EmaxYbin)
        currentvseta_prof_E.Draw()
        currentvseta_prof_A.Draw("same")
        currentvseta_prof_BC.Draw("same")
        currentvseta_prof_D.Draw("same")
        
        legendE.Clear()
        legendE.AddEntry(currentvseta_prof_A, "A cells",  "lep")
        legendE.AddEntry(currentvseta_prof_BC,"BC cells", "lep");
        legendE.AddEntry(currentvseta_prof_D, "D cells",  "lep");
        legendE.AddEntry(currentvseta_prof_E, "E cells",  "lep");
        legendE.Draw()
        
        l.SetTextFont(72)
        l.DrawLatex(0.2,0.88, "ATLAS")
        l.SetTextFont(42)
        l.DrawLatex(0.33,0.88, "Internal")
        l.DrawLatex(0.2,0.83, "Tile Calorimeter")
        l.DrawLatex(0.2,0.78, "Data 2016")
        l.DrawLatex(0.76,0.85, "#scale[0.9]{#sqrt{s} = 13 TeV}")

        c.SetLogy(1)
        c.Modified()
        c.Update()

        plotName = "Coeff_vs_eta_logPROF_instLumi_2016_%i" % (self.LumiRange)

        # save plot, several formats...
        c.Print("%s/%s_%s.root" % (self.dir,plotName , str(RunNumber) ))
        c.Print("%s/%s_%s.eps" % (self.dir, plotName , str(RunNumber) ))
        c.Print("%s/%s_%s.png" % (self.dir, plotName , str(RunNumber) ))        
        
        
        ##From stat()
        c.SetLogy(0)
        
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
#        Ecells.Draw("epsame")

        maximum = 0.
        minimum = 1000.
        if (Acells.GetBinContent(Acells.GetMaximumBin())>maximum): maximum= Acells.GetBinContent(Acells.GetMaximumBin())
        if (BCcells.GetBinContent(BCcells.GetMaximumBin())>maximum): maximum= BCcells.GetBinContent(BCcells.GetMaximumBin())
        if (Dcells.GetBinContent(Dcells.GetMaximumBin())>maximum): maximum= Dcells.GetBinContent(Dcells.GetMaximumBin())
#        if (Ecells.GetBinContent(Ecells.GetMaximumBin())>maximum): maximum= Ecells.GetBinContent(Ecells.GetMaximumBin())

        if (Acells.GetBinContent(Acells.GetMinimumBin())<minimum): minimum= Acells.GetBinContent(Acells.GetMinimumBin())
        if (BCcells.GetBinContent(BCcells.GetMinimumBin())<minimum): minimum= BCcells.GetBinContent(BCcells.GetMinimumBin())
        if (Dcells.GetBinContent(Dcells.GetMinimumBin())<minimum): minimum= Dcells.GetBinContent(Dcells.GetMinimumBin())

        Acells.GetXaxis().SetTitle("#eta_{cell}")
        Acells.GetXaxis().SetTitleSize(0.06)
#        Acells.GetYaxis().SetTitle("Coefficient [nA#times 10^{-33} cm^{2}s]")
        Acells.GetYaxis().SetTitle("Current [nA]")
        Acells.GetYaxis().SetTitleOffset(1.2)
        Acells.SetMaximum(maximum+10)
#        Acells.SetMinimum(minimum-10)



        legend.Clear()
        legend.AddEntry(Acells,"A cells","ep")
        legend.AddEntry(BCcells,"BC cells", "ep");
        legend.AddEntry(Dcells,"D cells","ep");
#        legend.AddEntry(Ecells,"E cells","ep");
        legend.Draw()

        l.SetTextFont(72)
        l.DrawLatex(0.2,0.88, "ATLAS")
        l.SetTextFont(42)
        l.DrawLatex(0.33,0.88, "Internal")
        l.DrawLatex(0.2,0.83, "Tile Calorimeter")
        l.DrawLatex(0.2,0.78, "Data 2016")
        l.DrawLatex(0.4,0.85, "L= %.1f#times10^{33} cm^{-2}s^{-1}" % (InstLumiMean))

        c.Modified()
        c.Update()

        plotName = "Current_vs_eta_instLumi_2016_%i" % (self.LumiRange)

        # save plot, several formats...
        #c.Print("%s/%s_%s.root" % (self.dir,plotName , str(RunNumber) ))
        #c.Print("%s/%s_%s.eps" % (self.dir, plotName , str(RunNumber) ))
        #c.Print("%s/%s_%s.png" % (self.dir, plotName , str(RunNumber)))

           
