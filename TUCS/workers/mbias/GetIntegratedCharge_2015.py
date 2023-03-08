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
class GetIntegratedCharge_2015(GenericWorker):
    "A plot worker for MBias"
    
    def __init__(self, LumiBegin=1, LumiRange=20):
        self.dir = getPlotDirectory() #where to save the plots
 
        self.dir      =  os.path.join(src.oscalls.getPlotDirectory(),'mbias2015','ResponseVariation')
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
#        regionsAll = ['A1', 'A2', 'A3', 'A4', 'A5', 'A6', 'A7', 'A8', 'A9', 'A10', 'A12', 'A13', 'A14', 'A15', 'A16', 'BC1', 'BC2', 'BC3', 'BC4', 'BC5', 'BC6', 'BC7', 'BC8', 'B9', 'C10', 'B11', 'B12', 'B13', 'B14', 'B15', 'D0', 'D1', 'D2', 'D3', 'D4', 'D5', 'D6', 'E1', 'E2', 'E3', 'E4']

        #only extended barrel
#        regionsAll = ['A12', 'A13', 'A14', 'A15', 'A16','C10', 'B11', 'B12', 'B13', 'B14', 'B15', 'D4', 'D5', 'D6', 'E1', 'E2', 'E3', 'E4']
        regionsAll = ['E3', 'E2', 'E1', 'E4']
#        regionsAll = ['A12', 'A13', 'A14', 'A15', 'A16']
#        regionsAll = ['C10', 'B11', 'B12', 'B13', 'B14', 'B15']
#        regionsAll = ['E3', 'E4']

        RunNumber = None

        PMTCurrent = None
        LumiBlock = None

        # using mapping from website: only using first pmt                                                                                  
        etamapLB = {0:0.01,1:0.05,2:0.05,5:0.15,6:0.15,9:0.25,11:0.25,13:0.2,15:0.35,16:0.35,19:0.45,21:0.45,23:0.55,25:0.4,28:0.55,34:0.65,27:0.65,\
33:0.75,37:0.85,40:0.75,39:0.6,44:0.85,46:0.95}
        # e cells added manually                                                                                                                  
        etamapEB = {0:1.3,12:1.05,1:1.5,13:1.15,2:0.85,4:0.95,6:1.15942,8:1.05869,10:1.25867,14:1.15803,16:1.00741,20:1.35795,22:1.25738,32:1.35678,28:1.45728,42:1.4562,36:1.20632,40:1.55665}

	
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

            ExtendedBarrel = []
                
            #  we loop over all cells and average over modules, but keeo track of single channels!
            for cell in regionsAll:
                PMTCurrentApmt1 = []
                PMTCurrentApmt2 = []
                PMTCurrentCpmt1 = []
                PMTCurrentCpmt2 = []

                InstLumi = []

                det_reg = self.PMTool.getRegionName2015(cell)
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


                count=0
		#loop over lb entries
                for l in range(self.LumiBegin,self.LumiEnd):
                    cellmeanApmt1 = []
                    cellmeanApmt2 = []
                    cellmeanCpmt1 = []
                    cellmeanCpmt2 = []

                    InstLumi.append(histoFile.GetBinContent(l+1)/1000.)

                    lumi=lumiIndex+count
#                    print lumi
                    count+=1
                    # start with A side 
                    for m in range(len(PMTCurrentHelp[lumi][PartA])):# 
                        specialPMT = []
                        useSpecial = False
                        if m==14 and "E" in cell:# if EBA15
                            specialPMT = self.PMTool.getRegionName2015(cell, True)[1]
                            useSpecial = True
#                        if PMTCurrentHelp[lumi][PartA][m][PMTch[0]]==0 or PMTCurrentHelp[lumi][PartA][m][PMTch[1]]==0: continue
                        if PMTGoodHelp[lumi][PartA][m][PMTch[0]]<1 or PMTGoodHelp[lumi][PartA][m][PMTch[1]]<1: 
                            cellmeanApmt1.append(0.0)
                            cellmeanApmt2.append(0.0)
                            continue
                        if PMTStatusHelp[lumi][PartA][m][PMTch[0]]<1 or PMTStatusHelp[lumi][PartA][m][PMTch[1]]<1: 
                            cellmeanApmt1.append(0.0)
                            cellmeanApmt2.append(0.0)
                            continue
                        if useSpecial:
                            cellmeanApmt1.append(PMTCurrentHelp[lumi][PartA][m][specialPMT[0]])# pmt1                                                                                  
                            cellmeanApmt2.append(PMTCurrentHelp[lumi][PartA][m][specialPMT[1]])# pmt2
                        else:
                            cellmeanApmt1.append(PMTCurrentHelp[lumi][PartA][m][PMTch[0]])# pmt1
                            cellmeanApmt2.append(PMTCurrentHelp[lumi][PartA][m][PMTch[1]])# pmt2

                    # c side
                    for m in range(len(PMTCurrentHelp[lumi][PartC])):# 
                        specialPMT = []
                        useSpecial = False
                        if m==17 and "E" in cell: # if EBC18
                            specialPMT = self.PMTool.getRegionName2015(cell, True)[1]
                            useSpecial = True

#                        if PMTCurrentHelp[lumi][PartC][m][PMTch[0]]==0 or PMTCurrentHelp[lumi][PartC][m][PMTch[1]]==0: continue
                        if PMTGoodHelp[lumi][PartC][m][PMTch[0]]<1 or PMTGoodHelp[lumi][PartC][m][PMTch[1]]<1: 
                            cellmeanCpmt1.append(0.0)
                            cellmeanCpmt2.append(0.0)
                            continue
                        if PMTStatusHelp[lumi][PartC][m][PMTch[0]]<1 or PMTStatusHelp[lumi][PartC][m][PMTch[1]]<1:
                            cellmeanCpmt1.append(0.0)
                            cellmeanCpmt2.append(0.0)
                            continue

                        if useSpecial:
                            cellmeanCpmt1.append(PMTCurrentHelp[lumi][PartC][m][specialPMT[0]])# pmt1
                            cellmeanCpmt2.append(PMTCurrentHelp[lumi][PartC][m][specialPMT[1]])# pmt2
                        else:
                            cellmeanCpmt1.append(PMTCurrentHelp[lumi][PartC][m][PMTch[0]])
                            cellmeanCpmt2.append(PMTCurrentHelp[lumi][PartC][m][PMTch[1]])


                    PMTCurrentApmt1.append(cellmeanApmt1)
                    PMTCurrentApmt2.append(cellmeanApmt2)

                    PMTCurrentCpmt1.append(cellmeanCpmt1)
                    PMTCurrentCpmt2.append(cellmeanCpmt2)

                        
#                    del cellmeanApmt1[:]
 #                   del cellmeanApmt2[:]
  #                  del cellmeanCpmt1[:]
   #                 del cellmeanCpmt2[:]

                #determine averages for instLumi and current and calculate coefficient
                instlumiMean = stats()
                currentApmt1 = stats()
                currentApmt2 = stats()
                currentCpmt1 = stats()
                currentCpmt2 = stats()

                for i in range(len(InstLumi)):
                    instlumiMean.fill(InstLumi[i])
                    
                #lb loop
                for m in range(len(PMTCurrentApmt1[0])):
                    for lb in range(len(PMTCurrentApmt1)):
                        currentApmt1.fill(PMTCurrentApmt1[lb][m])
                        currentApmt2.fill(PMTCurrentApmt2[lb][m])
                        currentCpmt1.fill(PMTCurrentCpmt1[lb][m])
                        currentCpmt2.fill(PMTCurrentCpmt2[lb][m])

                    # now create vector with information: channel,  module, eta, lumiCoeff
                    informationApmt1 = [PMTch[0]+1, m, etaValueA, currentApmt1.mean()/instlumiMean.mean()]
                    informationApmt2 = [PMTch[1]+1, m, etaValueA, currentApmt2.mean()/instlumiMean.mean()]
                    informationCpmt1 = [PMTch[0]+1, m, etaValueC, currentCpmt1.mean()/instlumiMean.mean()]
                    informationCpmt2 = [PMTch[1]+1, m, etaValueC, currentCpmt2.mean()/instlumiMean.mean()]

                    # dump all this information in overall vector
                    ExtendedBarrel.append(informationApmt1)
                    ExtendedBarrel.append(informationApmt2)
                    ExtendedBarrel.append(informationCpmt1)
                    ExtendedBarrel.append(informationCpmt2)
                
        # we need to subtract the laser variation seen...
        # first: read in D5 and E cells components separately, normalize to first run (actually, do this before...)...subtract D5 variation from other cells
        LaserInformation = [] # time, deviation, part mod, chan
        print('reading laser files')
        time_min = 1000000000000.
        with open('Laser_Dcells_v3_variation_2015.txt') as f:
            data = f.readlines()
            for line in data:
                laserinfo = line.split() # time, deviation, part, mod, chan
                if int(laserinfo[4]) ==17: # just use one pmt for now
                    LaserInformation.append(laserinfo)
#                    if float(laserinfo[0])< time_min:
#                        time_min=float(laserinfo[0])

#        print time_min

        LaserInformationCorr = []

        with open('Laser_Ecells_v3_variation_2015.txt') as f:
            data = f.readlines()
            for line in data:
                laserinfo = line.split()
                for i in range(len(LaserInformation)):
                    D5dev = float(LaserInformation[i][1])
                    # subtract D5 variation:
                    if laserinfo[0]==LaserInformation[i][0] and laserinfo[2]==LaserInformation[i][2] and laserinfo[3]==LaserInformation[i][3]:# channel doesn't need to be the same of course:
                        LaserInformationCorr.append([laserinfo[0],float(laserinfo[1])-D5dev, laserinfo[2], laserinfo[3], laserinfo[4]])
                        break # match found


        
        ## final pair we need to plot: (integrated Charge, response variation)
        pairsEtaE1 = []
        pairsEtaE2 = []
        pairsEtaE3 = []
        pairsEtaE4 = []


        pairsEta11 = []
        pairsEta12 = [] #eta between 1.2 and 1.3
        pairsEta13 = [] # eta between 1.3 and 1.4
        pairsEta14 = [] # eta between 1.4 and 1.5
        pairsEta15 = [] # eta between 1.5 and 1.7

        # now: need to read in information from response variation
        FullInfo = [] # time, variation, eta, lumiCoeff
#        f.open('Mbias_variation_2015.txt','r')

        MbiasInfo = [] # same as in file: time, variation, name, mod

        # part dictionary
        partDict = {"LBA":0, "LBC":1, "EBA":2, "EBC":3}

        print("reading file")
        with open('Mbias_Ecells_variation_2015.txt') as f:
            data = f.readlines()
            for line in data:
                responseinfo = line.split() # this will have  date, variation, channel, module (EBA or EBC)
#                print responseinfo
                # we need to subtract the laser component from mbias first
                channel = int(responseinfo[2][9:11]) # extract channel number (actually PMT)
                # now find the match:
                # nearest run:
                distRun = 1000000000000.
                finalVariation = 20.
                for i in range(len(LaserInformationCorr)):
                    if ("EBA" in responseinfo[2] and LaserInformationCorr[i][2]=="EBA") or ("EBC" in responseinfo[2] and LaserInformationCorr[i][2]=="EBC"):# match EB side
#                        print "Hier??", channel, LaserInformationCorr[i][4]
                        if int(LaserInformationCorr[i][3])-1==int(responseinfo[3]) and channel==self.PMTool.get_PMT_index(partDict[LaserInformationCorr[i][2]],int(LaserInformationCorr[i][3])-1, int(LaserInformationCorr[i][4])):
#                            print "auch noch hier?"
                            if abs(float(LaserInformationCorr[i][0])-float(responseinfo[0]))<distRun:# find closest run
#                                print "und dann?"
                                distRun = abs(float(LaserInformationCorr[i][0])-float(responseinfo[0]))
                                finalVariation = 100.*float(responseinfo[1])-LaserInformationCorr[i][1] # deviation in %
#                finalVariation = 100.*float(responseinfo[1]) # deviation in %
                MbiasInfo.append([float(responseinfo[0]),finalVariation , responseinfo[2],int(responseinfo[3])])
        print("done")

        # match different mbias infos        
        for info in range(len(MbiasInfo)):
            channel =  int(MbiasInfo[info][2][9:11]) # extract channel number (actually PMT)                                                         
            # now match with other information
            for i in range(len(ExtendedBarrel)):
                if "EBA" in MbiasInfo[info][2]:
                    if ExtendedBarrel[i][1]==14 or int(responseinfo[3])==14: continue #temporary fix for EBA15 cabeling
                    if ExtendedBarrel[i][0]==channel and ExtendedBarrel[i][2]>0.0 and ExtendedBarrel[i][1]==MbiasInfo[info][3]:
                            if channel==13 and (ExtendedBarrel[i][1]==28 or ExtendedBarrel[i][1]==31 or ExtendedBarrel[i][1]==33 or ExtendedBarrel[i][1]==36 or ExtendedBarrel[i][1]==7 or ExtendedBarrel[i][1]==23 or ExtendedBarrel[i][1]==42 or ExtendedBarrel[i][1]==53 or ExtendedBarrel[i][1]==6 or ExtendedBarrel[i][1]==24 or ExtendedBarrel[i]==43 or ExtendedBarrel[i][1]==52):#for E1: exclude E' cells, MBTS
                                print("does this happen??")
                                continue
                            if channel==5 and ((ExtendedBarrel[i][1]>=38 and ExtendedBarrel[i][1]<=41) or (ExtendedBarrel[i][1]>=54 and ExtendedBarrel[i][1]<=57)):#special modules C10
                                continue
#                            f = open("E3E4_fullInfo_2015.txt", "a+")
                            FullInfo.append([MbiasInfo[info][0], MbiasInfo[info][1], ExtendedBarrel[i][2], ExtendedBarrel[i][3], MbiasInfo[info][3]])
#                            f.write(" %s %s %s %s %s \n" % (str(MbiasInfo[info][2]), str(MbiasInfo[info][3]), str(MbiasInfo[info][1]), str(ExtendedBarrel[i][3]),str(MbiasInfo[info][0])))
#                            f.close()
                            print("FullInfo EBA")
                            break # search no further
                elif "EBC" in  MbiasInfo[info][2]:
                    if ExtendedBarrel[i][1]==17 or int(responseinfo[3])==17: continue #temporary fix for EBC18 cabeling
                    if ExtendedBarrel[i][0]==channel and ExtendedBarrel[i][2]<0.0 and ExtendedBarrel[i][1]==MbiasInfo[info][3]:
                            if channel==13 and (ExtendedBarrel[i][1]==28 or ExtendedBarrel[i][1]==31 or ExtendedBarrel[i][1]==33 or ExtendedBarrel[i][1]==36 or ExtendedBarrel[i][1]==7 or ExtendedBarrel[i][1]==23 or ExtendedBarrel[i][1]==42 or ExtendedBarrel[i][1]==53 or ExtendedBarrel[i][1]==6 or ExtendedBarrel[i][1]==24 or ExtendedBarrel[i]==43 or ExtendedBarrel[i][1]==52 or ExtendedBarrel[i][1]==27 or ExtendedBarrel[i][1]==30 or ExtendedBarrel[i][1]==34 or ExtendedBarrel[i][1]==37):#for E1: exclude E' cells, MBTS
                                continue
                            if channel==5 and ((ExtendedBarrel[i][1]>=38 and ExtendedBarrel[i][1]<=41) or (ExtendedBarrel[i][1]>=54 and ExtendedBarrel[i][1]<=57)):#special modules C10
                                continue
#                            f = open("E3E4_fullInfo_2015.txt", "a+")
#                            f.write(" %s %s %s %s %s \n" % (str(MbiasInfo[info][2]), str(MbiasInfo[info][3]), str(MbiasInfo[info][1]), str(ExtendedBarrel[i][3]),str(MbiasInfo[info][0])))
                            FullInfo.append([MbiasInfo[info][0], MbiasInfo[info][1], ExtendedBarrel[i][2], ExtendedBarrel[i][3], MbiasInfo[info][3]])
#                            f.close()
                            break # search no further


        # and now matching with intergrated lumi:
        intL = 0.0

        intLUMI = TGraph()

        intLUMI.SetPoint(intLUMI.GetN(), (TDatime(2015, 0o6, 0o3, 9, 0, 0)).Convert(), intL)
        intLUMI.SetPoint(intLUMI.GetN(), (TDatime(2015, 0o6, 0o3, 9, 43, 59)).Convert(), intL)
        intL += 0.064;
                
        intLUMI.SetPoint(intLUMI.GetN(), (TDatime(2015, 0o6, 0o3, 9, 44, 0)).Convert(), intL)
        intLUMI.SetPoint(intLUMI.GetN(), (TDatime(2015, 0o6, 0o3, 19, 7, 59)).Convert(), intL)
        intL += 0.064
        intLUMI.SetPoint(intLUMI.GetN(), (TDatime(2015, 0o6, 0o3, 19, 8, 0)).Convert(), intL)
        intLUMI.SetPoint(intLUMI.GetN(), (TDatime(2015, 0o6, 0o4, 19, 30, 59)).Convert(), intL)
        intL += 0.11
        intLUMI.SetPoint(intLUMI.GetN(), (TDatime(2015, 0o6, 0o4, 19, 31, 0)).Convert(), intL)
        intLUMI.SetPoint(intLUMI.GetN(), (TDatime(2015, 0o6, 0o5, 23, 17, 59)).Convert(), intL)
        intL += 0.433
        intLUMI.SetPoint(intLUMI.GetN(), (TDatime(2015, 0o6, 0o5, 23, 18, 0)).Convert(), intL)
        intLUMI.SetPoint(intLUMI.GetN(), (TDatime(2015, 0o6, 0o7, 7, 23, 59)).Convert(), intL)
        intL += 0.332
        intLUMI.SetPoint(intLUMI.GetN(), (TDatime(2015, 0o6, 0o7, 7, 24, 0)).Convert(), intL)
        intLUMI.SetPoint(intLUMI.GetN(), (TDatime(2015, 0o6, 0o7, 19, 10, 59)).Convert(), intL)
        intL += 0.388
        intLUMI.SetPoint(intLUMI.GetN(), (TDatime(2015, 0o6, 0o7, 19, 11, 0)).Convert(), intL)
        intLUMI.SetPoint(intLUMI.GetN(), (TDatime(2015, 0o6, 9, 21, 35, 59)).Convert(), intL)
        intL += 0.0
        intLUMI.SetPoint(intLUMI.GetN(), (TDatime(2015, 0o6, 9, 21, 36, 0)).Convert(), intL)
        intLUMI.SetPoint(intLUMI.GetN(), (TDatime(2015, 0o6, 10, 2, 16, 59)).Convert(), intL)
        intL += 0.0
        intLUMI.SetPoint(intLUMI.GetN(), (TDatime(2015, 0o6, 10, 2, 17, 0)).Convert(), intL)
        intLUMI.SetPoint(intLUMI.GetN(), (TDatime(2015, 0o6, 10, 8, 8, 59)).Convert(), intL)
        intL += 0.001
        intLUMI.SetPoint(intLUMI.GetN(), (TDatime(2015, 0o6, 10, 8, 9, 0)).Convert(), intL)
        intLUMI.SetPoint(intLUMI.GetN(), (TDatime(2015, 0o6, 10, 19, 52, 59)).Convert(), intL)
        intL += 0.002
        intLUMI.SetPoint(intLUMI.GetN(), (TDatime(2015, 0o6, 10, 19, 53, 0)).Convert(), intL)
        intLUMI.SetPoint(intLUMI.GetN(), (TDatime(2015, 0o6, 11, 0, 59, 59)).Convert(), intL)
        intL += 0.006
        intLUMI.SetPoint(intLUMI.GetN(), (TDatime(2015, 0o6, 11, 1, 0, 0)).Convert(), intL)
        intLUMI.SetPoint(intLUMI.GetN(), (TDatime(2015, 0o6, 12, 16, 14, 59)).Convert(), intL)
        intL += 0.006
        intLUMI.SetPoint(intLUMI.GetN(), (TDatime(2015, 0o6, 12, 16, 15, 0)).Convert(), intL)
        intLUMI.SetPoint(intLUMI.GetN(), (TDatime(2015, 0o6, 13, 15, 53, 59)).Convert(), intL)
        intL += 3.569
        intLUMI.SetPoint(intLUMI.GetN(), (TDatime(2015, 0o6, 13, 15, 54, 0)).Convert(), intL)
        intLUMI.SetPoint(intLUMI.GetN(), (TDatime(2015, 0o6, 14, 6, 9, 59)).Convert(), intL)
        intL += 3.258
        intLUMI.SetPoint(intLUMI.GetN(), (TDatime(2015, 0o6, 14, 6, 10, 0)).Convert(), intL)
        intLUMI.SetPoint(intLUMI.GetN(), (TDatime(2015, 0o7, 0o4, 19, 9, 59)).Convert(), intL)
        intL += 0.054
        intLUMI.SetPoint(intLUMI.GetN(), (TDatime(2015, 0o7, 0o4, 19, 10, 0)).Convert(), intL)
        intLUMI.SetPoint(intLUMI.GetN(), (TDatime(2015, 0o7, 0o5, 4, 50, 59)).Convert(), intL)
        intL += 3.511
        intLUMI.SetPoint(intLUMI.GetN(), (TDatime(2015, 0o7, 0o5, 4, 51, 0)).Convert(), intL)
        intLUMI.SetPoint(intLUMI.GetN(), (TDatime(2015, 0o7, 0o5, 22, 30, 59)).Convert(), intL)
        intL += 1.466
        intLUMI.SetPoint(intLUMI.GetN(), (TDatime(2015, 0o7, 0o5, 22, 31, 0)).Convert(), intL)
        intLUMI.SetPoint(intLUMI.GetN(), (TDatime(2015, 0o7, 0o7, 2, 22, 59)).Convert(), intL)
        intL += 2.792
        intLUMI.SetPoint(intLUMI.GetN(), (TDatime(2015, 0o7, 0o7, 2, 23, 0)).Convert(), intL)
        intLUMI.SetPoint(intLUMI.GetN(), (TDatime(2015, 0o7, 0o7, 21, 3, 59)).Convert(), intL)
        intL += 6.376
        intLUMI.SetPoint(intLUMI.GetN(), (TDatime(2015, 0o7, 0o7, 21, 4, 0)).Convert(), intL)
        intLUMI.SetPoint(intLUMI.GetN(), (TDatime(2015, 0o7, 8, 13, 17, 59)).Convert(), intL)
        intL += 8.092
        intLUMI.SetPoint(intLUMI.GetN(), (TDatime(2015, 0o7, 8, 13, 18, 0)).Convert(), intL)
        intLUMI.SetPoint(intLUMI.GetN(), (TDatime(2015, 0o7, 10, 17, 5, 59)).Convert(), intL)
        intL += 13.182
        intLUMI.SetPoint(intLUMI.GetN(), (TDatime(2015, 0o7, 10, 17, 6, 0)).Convert(), intL)
        intLUMI.SetPoint(intLUMI.GetN(), (TDatime(2015, 0o7, 11, 9, 8, 59)).Convert(), intL)
        intL += 0.729
        intLUMI.SetPoint(intLUMI.GetN(), (TDatime(2015, 0o7, 11, 9, 9, 0)).Convert(), intL)
        intLUMI.SetPoint(intLUMI.GetN(), (TDatime(2015, 0o7, 11, 20, 12, 59)).Convert(), intL)
        intL += 0.584
        intLUMI.SetPoint(intLUMI.GetN(), (TDatime(2015, 0o7, 11, 20, 13, 0)).Convert(), intL)
        intLUMI.SetPoint(intLUMI.GetN(), (TDatime(2015, 0o7, 12, 2, 18, 59)).Convert(), intL)
        intL += 16.236
        intLUMI.SetPoint(intLUMI.GetN(), (TDatime(2015, 0o7, 12, 2, 19, 0)).Convert(), intL)
        intLUMI.SetPoint(intLUMI.GetN(), (TDatime(2015, 0o7, 13, 5, 45, 59)).Convert(), intL)
        intL += 20.642
        intLUMI.SetPoint(intLUMI.GetN(), (TDatime(2015, 0o7, 13, 5, 46, 0)).Convert(), intL)
        intLUMI.SetPoint(intLUMI.GetN(), (TDatime(2015, 0o7, 14, 0, 23, 59)).Convert(), intL)
        intL += 18.846
        intLUMI.SetPoint(intLUMI.GetN(), (TDatime(2015, 0o7, 14, 0, 24, 0)).Convert(), intL)
        intLUMI.SetPoint(intLUMI.GetN(), (TDatime(2015, 0o7, 14, 23, 48, 59)).Convert(), intL)
        intL += 0.009
        intLUMI.SetPoint(intLUMI.GetN(), (TDatime(2015, 0o7, 14, 23, 49, 0)).Convert(), intL)
        intLUMI.SetPoint(intLUMI.GetN(), (TDatime(2015, 0o7, 15, 18, 16, 59)).Convert(), intL)
        intL += 0.734
        intLUMI.SetPoint(intLUMI.GetN(), (TDatime(2015, 0o7, 15, 18, 17, 0)).Convert(), intL)
        intLUMI.SetPoint(intLUMI.GetN(), (TDatime(2015, 0o7, 15, 23, 1, 59)).Convert(), intL)
        intL += 7.324
        intLUMI.SetPoint(intLUMI.GetN(), (TDatime(2015, 0o7, 15, 23, 2, 0)).Convert(), intL)
        intLUMI.SetPoint(intLUMI.GetN(), (TDatime(2015, 0o7, 20, 1, 35, 59)).Convert(), intL)
        intL += 2.097
        intLUMI.SetPoint(intLUMI.GetN(), (TDatime(2015, 0o7, 20, 1, 36, 0)).Convert(), intL)
        intLUMI.SetPoint(intLUMI.GetN(), (TDatime(2015, 0o7, 20, 4, 36, 59)).Convert(), intL)
        intL += 3.234
        intLUMI.SetPoint(intLUMI.GetN(), (TDatime(2015, 0o7, 20, 4, 37, 0)).Convert(), intL)
        intLUMI.SetPoint(intLUMI.GetN(), (TDatime(2015, 8, 13, 3, 11, 59)).Convert(), intL)
        intL += 0.54
        intLUMI.SetPoint(intLUMI.GetN(), (TDatime(2015, 8, 13, 3, 12, 0)).Convert(), intL)
        intLUMI.SetPoint(intLUMI.GetN(), (TDatime(2015, 8, 13, 15, 37, 59)).Convert(), intL)
        intL += 5.286
        intLUMI.SetPoint(intLUMI.GetN(), (TDatime(2015, 8, 13, 15, 38, 0)).Convert(), intL)
        intLUMI.SetPoint(intLUMI.GetN(), (TDatime(2015, 8, 14, 9, 5, 59)).Convert(), intL)
        intL += 2.56
        intLUMI.SetPoint(intLUMI.GetN(), (TDatime(2015, 8, 14, 9, 6, 0)).Convert(), intL)
        intLUMI.SetPoint(intLUMI.GetN(), (TDatime(2015, 8, 14, 17, 2, 59)).Convert(), intL)
        intL += 2.964
        intLUMI.SetPoint(intLUMI.GetN(), (TDatime(2015, 8, 14, 17, 3, 0)).Convert(), intL)
        intLUMI.SetPoint(intLUMI.GetN(), (TDatime(2015, 8, 15, 8, 48, 59)).Convert(), intL)
        intL += 1.537
        intLUMI.SetPoint(intLUMI.GetN(), (TDatime(2015, 8, 15, 8, 49, 0)).Convert(), intL)
        intLUMI.SetPoint(intLUMI.GetN(), (TDatime(2015, 8, 15, 13, 49, 59)).Convert(), intL)
        intL += 2.381
        intLUMI.SetPoint(intLUMI.GetN(), (TDatime(2015, 8, 15, 13, 50, 0)).Convert(), intL)
        intLUMI.SetPoint(intLUMI.GetN(), (TDatime(2015, 8, 15, 18, 34, 59)).Convert(), intL)
        intL += 1.671
        intLUMI.SetPoint(intLUMI.GetN(), (TDatime(2015, 8, 15, 18, 35, 0)).Convert(), intL)
        intLUMI.SetPoint(intLUMI.GetN(), (TDatime(2015, 8, 16, 3, 13, 59)).Convert(), intL)
        intL += 7.406
        intLUMI.SetPoint(intLUMI.GetN(), (TDatime(2015, 8, 16, 3, 14, 0)).Convert(), intL)
        intLUMI.SetPoint(intLUMI.GetN(), (TDatime(2015, 8, 16, 17, 17, 59)).Convert(), intL)
        intL += 0.109
        intLUMI.SetPoint(intLUMI.GetN(), (TDatime(2015, 8, 16, 17, 18, 0)).Convert(), intL)
        intLUMI.SetPoint(intLUMI.GetN(), (TDatime(2015, 8, 16, 18, 52, 59)).Convert(), intL)
        intL += 19.3
        intLUMI.SetPoint(intLUMI.GetN(), (TDatime(2015, 8, 16, 18, 53, 0)).Convert(), intL)
        intLUMI.SetPoint(intLUMI.GetN(), (TDatime(2015, 8, 17, 22, 43, 59)).Convert(), intL)
        intL += 0.1
        intLUMI.SetPoint(intLUMI.GetN(), (TDatime(2015, 8, 17, 22, 44, 0)).Convert(), intL)
        intLUMI.SetPoint(intLUMI.GetN(), (TDatime(2015, 8, 18, 2, 14, 59)).Convert(), intL)
        intL += 5.55
        intLUMI.SetPoint(intLUMI.GetN(), (TDatime(2015, 8, 18, 2, 15, 0)).Convert(), intL)
        intLUMI.SetPoint(intLUMI.GetN(), (TDatime(2015, 8, 19, 3, 12, 59)).Convert(), intL)
        intL += 11.054
        intLUMI.SetPoint(intLUMI.GetN(), (TDatime(2015, 8, 19, 3, 13, 0)).Convert(), intL)
        intLUMI.SetPoint(intLUMI.GetN(), (TDatime(2015, 8, 21, 4, 10, 59)).Convert(), intL)
        intL += 12.074
        intLUMI.SetPoint(intLUMI.GetN(), (TDatime(2015, 8, 21, 4, 20, 0)).Convert(), intL)
        intLUMI.SetPoint(intLUMI.GetN(), (TDatime(2015, 8, 21, 20, 1, 59)).Convert(), intL)
        intL += 27.231
        intLUMI.SetPoint(intLUMI.GetN(), (TDatime(2015, 8, 21, 20, 2, 0)).Convert(), intL)
        intLUMI.SetPoint(intLUMI.GetN(), (TDatime(2015, 8, 22, 13, 42, 59)).Convert(), intL)
        intL += 1.003
        intLUMI.SetPoint(intLUMI.GetN(), (TDatime(2015, 8, 22, 13, 43, 0)).Convert(), intL)
        intLUMI.SetPoint(intLUMI.GetN(), (TDatime(2015, 8, 23, 2, 30, 59)).Convert(), intL)
        intL += 2.054
        intLUMI.SetPoint(intLUMI.GetN(), (TDatime(2015, 8, 23, 2, 31, 0)).Convert(), intL)
        intLUMI.SetPoint(intLUMI.GetN(), (TDatime(2015, 8, 23, 14, 20, 59)).Convert(), intL)
        intL += 7.715
        intLUMI.SetPoint(intLUMI.GetN(), (TDatime(2015, 8, 23, 14, 21, 0)).Convert(), intL)
        intLUMI.SetPoint(intLUMI.GetN(), (TDatime(2015, 8, 23, 19, 41, 59)).Convert(), intL)
        intL += 1.048
        intLUMI.SetPoint(intLUMI.GetN(), (TDatime(2015, 8, 23, 19, 42, 0)).Convert(), intL)
        intLUMI.SetPoint(intLUMI.GetN(), (TDatime(2015, 8, 24, 20, 24, 59)).Convert(), intL)
        intL += 0.066
        intLUMI.SetPoint(intLUMI.GetN(), (TDatime(2015, 8, 24, 20, 25, 0)).Convert(), intL)
        intLUMI.SetPoint(intLUMI.GetN(), (TDatime(2015, 8, 25, 11, 11, 59)).Convert(), intL)
        intL += 0.0
        intLUMI.SetPoint(intLUMI.GetN(), (TDatime(2015, 8, 25, 11, 12, 0)).Convert(), intL)
        intLUMI.SetPoint(intLUMI.GetN(), (TDatime(2015, 8, 25, 13, 37, 59)).Convert(), intL)
        intL += 0.02
        intLUMI.SetPoint(intLUMI.GetN(), (TDatime(2015, 8, 25, 13, 38, 0)).Convert(), intL)
        intLUMI.SetPoint(intLUMI.GetN(), (TDatime(2015, 9, 0o6, 19, 43, 59)).Convert(), intL)
        intL += 1.062
        intLUMI.SetPoint(intLUMI.GetN(), (TDatime(2015, 9, 0o6, 19, 44, 0)).Convert(), intL)
        intLUMI.SetPoint(intLUMI.GetN(), (TDatime(2015, 9, 0o7, 0, 12, 59)).Convert(), intL)
        intL += 10.091
        intLUMI.SetPoint(intLUMI.GetN(), (TDatime(2015, 9, 0o7, 0, 13, 0)).Convert(), intL)
        intLUMI.SetPoint(intLUMI.GetN(), (TDatime(2015, 9, 8, 8, 11, 59)).Convert(), intL)
        intL += 28.235
        intLUMI.SetPoint(intLUMI.GetN(), (TDatime(2015, 9, 8, 8, 12, 0)).Convert(), intL)
        intLUMI.SetPoint(intLUMI.GetN(), (TDatime(2015, 9, 9, 6, 8, 59)).Convert(), intL)
        intL += 22.392
        intLUMI.SetPoint(intLUMI.GetN(), (TDatime(2015, 9, 9, 6, 9, 0)).Convert(), intL)
        intLUMI.SetPoint(intLUMI.GetN(), (TDatime(2015, 9, 9, 22, 1, 59)).Convert(), intL)
        intL += 11.561
        intLUMI.SetPoint(intLUMI.GetN(), (TDatime(2015, 9, 9, 22, 2, 0)).Convert(), intL)
        intLUMI.SetPoint(intLUMI.GetN(), (TDatime(2015, 9, 10, 2, 27, 59)).Convert(), intL)
        intL += 2.664
        intLUMI.SetPoint(intLUMI.GetN(), (TDatime(2015, 9, 10, 2, 28, 0)).Convert(), intL)
        intLUMI.SetPoint(intLUMI.GetN(), (TDatime(2015, 9, 11, 16, 3, 59)).Convert(), intL)
        intL += 66.909
        intLUMI.SetPoint(intLUMI.GetN(), (TDatime(2015, 9, 11, 16, 4, 0)).Convert(), intL)
        intLUMI.SetPoint(intLUMI.GetN(), (TDatime(2015, 9, 13, 2, 18, 59)).Convert(), intL)
        intL += 8.586
        intLUMI.SetPoint(intLUMI.GetN(), (TDatime(2015, 9, 13, 2, 19, 0)).Convert(), intL)
        intLUMI.SetPoint(intLUMI.GetN(), (TDatime(2015, 9, 13, 16, 33, 59)).Convert(), intL)
        intL += 22.295
        intLUMI.SetPoint(intLUMI.GetN(), (TDatime(2015, 9, 13, 16, 34, 0)).Convert(), intL)
        intLUMI.SetPoint(intLUMI.GetN(), (TDatime(2015, 9, 14, 3, 28, 59)).Convert(), intL)
        intL += 34.976
        intLUMI.SetPoint(intLUMI.GetN(), (TDatime(2015, 9, 14, 3, 29, 0)).Convert(), intL)
        intLUMI.SetPoint(intLUMI.GetN(), (TDatime(2015, 9, 14, 16, 26, 59)).Convert(), intL)
        intL += 58.832
        intLUMI.SetPoint(intLUMI.GetN(), (TDatime(2015, 9, 14, 16, 27, 0)).Convert(), intL)
        intLUMI.SetPoint(intLUMI.GetN(), (TDatime(2015, 9, 16, 11, 45, 59)).Convert(), intL)
        intL += 1.227
        intLUMI.SetPoint(intLUMI.GetN(), (TDatime(2015, 9, 16, 11, 46, 0)).Convert(), intL)
        intLUMI.SetPoint(intLUMI.GetN(), (TDatime(2015, 9, 16, 23, 40, 59)).Convert(), intL)
        intL += 75.161
        intLUMI.SetPoint(intLUMI.GetN(), (TDatime(2015, 9, 16, 23, 41, 0)).Convert(), intL)
        intLUMI.SetPoint(intLUMI.GetN(), (TDatime(2015, 9, 17, 19, 53, 59)).Convert(), intL)
        intL += 85.152
        intLUMI.SetPoint(intLUMI.GetN(), (TDatime(2015, 9, 17, 19, 54, 0)).Convert(), intL)
        intLUMI.SetPoint(intLUMI.GetN(), (TDatime(2015, 9, 18, 14, 36, 59)).Convert(), intL)
        intL += 8.851
        intLUMI.SetPoint(intLUMI.GetN(), (TDatime(2015, 9, 18, 14, 37, 0)).Convert(), intL)
        intLUMI.SetPoint(intLUMI.GetN(), (TDatime(2015, 9, 19, 3, 55, 59)).Convert(), intL)
        intL += 54.808
        intLUMI.SetPoint(intLUMI.GetN(), (TDatime(2015, 9, 19, 3, 56, 0)).Convert(), intL)
        intLUMI.SetPoint(intLUMI.GetN(), (TDatime(2015, 9, 19, 21, 35, 59)).Convert(), intL)
        intL += 34.174
        intLUMI.SetPoint(intLUMI.GetN(), (TDatime(2015, 9, 19, 21, 36, 0)).Convert(), intL)
        intLUMI.SetPoint(intLUMI.GetN(), (TDatime(2015, 9, 20, 18, 53, 59)).Convert(), intL)
        intL += 1.974
        intLUMI.SetPoint(intLUMI.GetN(), (TDatime(2015, 9, 20, 18, 54, 0)).Convert(), intL)
        intLUMI.SetPoint(intLUMI.GetN(), (TDatime(2015, 9, 21, 0, 34, 59)).Convert(), intL)
        intL += 48.754
        intLUMI.SetPoint(intLUMI.GetN(), (TDatime(2015, 9, 21, 0, 35, 0)).Convert(), intL)
        intL += 91.877
        intLUMI.SetPoint(intLUMI.GetN(), (TDatime(2015, 9, 21, 18, 52, 0)).Convert(), intL)
        intLUMI.SetPoint(intLUMI.GetN(), (TDatime(2015, 9, 24, 0, 33, 59)).Convert(), intL)
        intL += 106.12
        intLUMI.SetPoint(intLUMI.GetN(), (TDatime(2015, 9, 24, 0, 34, 0)).Convert(), intL)
        intLUMI.SetPoint(intLUMI.GetN(), (TDatime(2015, 9, 25, 3, 59, 59)).Convert(), intL)
        intL += 3.674
        intLUMI.SetPoint(intLUMI.GetN(), (TDatime(2015, 9, 25, 4, 0, 0)).Convert(), intL)
        intLUMI.SetPoint(intLUMI.GetN(), (TDatime(2015, 9, 25, 10, 38, 59)).Convert(), intL)
        intL += 105.982
        intLUMI.SetPoint(intLUMI.GetN(), (TDatime(2015, 9, 25, 10, 39, 0)).Convert(), intL)
        intLUMI.SetPoint(intLUMI.GetN(), (TDatime(2015, 9, 26, 8, 36, 59)).Convert(), intL)
        intL += 10.145
        intLUMI.SetPoint(intLUMI.GetN(), (TDatime(2015, 9, 26, 8, 37, 0)).Convert(), intL)
        intLUMI.SetPoint(intLUMI.GetN(), (TDatime(2015, 9, 26, 22, 22, 59)).Convert(), intL)
        intL += 5.787
        intLUMI.SetPoint(intLUMI.GetN(), (TDatime(2015, 9, 26, 22, 23, 0)).Convert(), intL)
        intLUMI.SetPoint(intLUMI.GetN(), (TDatime(2015, 9, 27, 3, 57, 59)).Convert(), intL)
        intL += 84.08
        intLUMI.SetPoint(intLUMI.GetN(), (TDatime(2015, 9, 27, 3, 58, 0)).Convert(), intL)
        intLUMI.SetPoint(intLUMI.GetN(), (TDatime(2015, 9, 27, 23, 6, 59)).Convert(), intL)
        intL += 68.982
        intLUMI.SetPoint(intLUMI.GetN(), (TDatime(2015, 9, 27, 23, 7, 0)).Convert(), intL)
        intLUMI.SetPoint(intLUMI.GetN(), (TDatime(2015, 9, 28, 12, 9, 59)).Convert(), intL)
        intL += 14.653
        intLUMI.SetPoint(intLUMI.GetN(), (TDatime(2015, 9, 28, 12, 10, 0)).Convert(), intL)
        intLUMI.SetPoint(intLUMI.GetN(), (TDatime(2015, 9, 28, 16, 10, 59)).Convert(), intL)
        intL += 29.656
        intLUMI.SetPoint(intLUMI.GetN(), (TDatime(2015, 9, 28, 16, 11, 0)).Convert(), intL)
        intLUMI.SetPoint(intLUMI.GetN(), (TDatime(2015, 9, 29, 3, 58, 59)).Convert(), intL)
        intL += 30.32
        intLUMI.SetPoint(intLUMI.GetN(), (TDatime(2015, 9, 29, 3, 59, 0)).Convert(), intL)
        intLUMI.SetPoint(intLUMI.GetN(), (TDatime(2015, 9, 29, 13, 15, 59)).Convert(), intL)
        intL += 172.709
        intLUMI.SetPoint(intLUMI.GetN(), (TDatime(2015, 9, 29, 13, 16, 0)).Convert(), intL)
        intLUMI.SetPoint(intLUMI.GetN(), (TDatime(2015, 9, 30, 21, 29, 59)).Convert(), intL)
        intL += 60.585
        intLUMI.SetPoint(intLUMI.GetN(), (TDatime(2015, 9, 30, 21, 30, 0)).Convert(), intL)
        intLUMI.SetPoint(intLUMI.GetN(), (TDatime(2015, 10, 0o2, 7, 55, 59)).Convert(), intL)
        intL += 11.155
        intLUMI.SetPoint(intLUMI.GetN(), (TDatime(2015, 10, 0o2, 7, 56, 0)).Convert(), intL)
        intLUMI.SetPoint(intLUMI.GetN(), (TDatime(2015, 10, 0o2, 13, 31, 59)).Convert(), intL)
        intL += 147.743
        intLUMI.SetPoint(intLUMI.GetN(), (TDatime(2015, 10, 0o2, 13, 32, 0)).Convert(), intL)
        intLUMI.SetPoint(intLUMI.GetN(), (TDatime(2015, 10, 0o3, 19, 1, 59)).Convert(), intL)
        intL += 143.206
        intLUMI.SetPoint(intLUMI.GetN(), (TDatime(2015, 10, 0o3, 19, 2, 0)).Convert(), intL)
        intLUMI.SetPoint(intLUMI.GetN(), (TDatime(2015, 10, 0o4, 15, 17, 59)).Convert(), intL)
        intL += 39.362
        intLUMI.SetPoint(intLUMI.GetN(), (TDatime(2015, 10, 0o4, 15, 18, 0)).Convert(), intL)
        intLUMI.SetPoint(intLUMI.GetN(), (TDatime(2015, 10, 0o5, 16, 4, 59)).Convert(), intL)
        intL += 15.009
        intLUMI.SetPoint(intLUMI.GetN(), (TDatime(2015, 10, 0o5, 16, 5, 0)).Convert(), intL)
        intLUMI.SetPoint(intLUMI.GetN(), (TDatime(2015, 10, 0o5, 19, 36, 59)).Convert(), intL)
        intL += 51.164
        intLUMI.SetPoint(intLUMI.GetN(), (TDatime(2015, 10, 0o5, 19, 37, 0)).Convert(), intL)
        intLUMI.SetPoint(intLUMI.GetN(), (TDatime(2015, 10, 0o6, 3, 13, 59)).Convert(), intL)
        intL += 1.571
        intLUMI.SetPoint(intLUMI.GetN(), (TDatime(2015, 10, 0o6, 3, 14, 0)).Convert(), intL)
        intLUMI.SetPoint(intLUMI.GetN(), (TDatime(2015, 10, 0o6, 13, 20, 59)).Convert(), intL)
        intL += 20.781
        intLUMI.SetPoint(intLUMI.GetN(), (TDatime(2015, 10, 0o6, 13, 21, 0)).Convert(), intL)
        intLUMI.SetPoint(intLUMI.GetN(), (TDatime(2015, 10, 0o6, 18, 35, 59)).Convert(), intL)
        intL += 230.172
        intLUMI.SetPoint(intLUMI.GetN(), (TDatime(2015, 10, 0o6, 18, 36, 0)).Convert(), intL)
        intLUMI.SetPoint(intLUMI.GetN(), (TDatime(2015, 10, 9, 10, 19, 59)).Convert(), intL)
        intL += 29.66
        intLUMI.SetPoint(intLUMI.GetN(), (TDatime(2015, 10, 9, 10, 20, 0)).Convert(), intL)
        intLUMI.SetPoint(intLUMI.GetN(), (TDatime(2015, 10, 9, 16, 2, 59)).Convert(), intL)
        intL += 14.98
        intLUMI.SetPoint(intLUMI.GetN(), (TDatime(2015, 10, 9, 16, 3, 0)).Convert(), intL)
        intLUMI.SetPoint(intLUMI.GetN(), (TDatime(2015, 10, 9, 23, 53, 59)).Convert(), intL)
        intL += 197.358
        intLUMI.SetPoint(intLUMI.GetN(), (TDatime(2015, 10, 9, 23, 54, 0)).Convert(), intL)
        intLUMI.SetPoint(intLUMI.GetN(), (TDatime(2015, 10, 11, 13, 54, 59)).Convert(), intL)
        intL += 165.76
        intLUMI.SetPoint(intLUMI.GetN(), (TDatime(2015, 10, 11, 13, 55, 0)).Convert(), intL)
        intLUMI.SetPoint(intLUMI.GetN(), (TDatime(2015, 10, 12, 19, 8, 59)).Convert(), intL)
        intL += 0.0
        intLUMI.SetPoint(intLUMI.GetN(), (TDatime(2015, 10, 12, 19, 9, 0)).Convert(), intL)
        intLUMI.SetPoint(intLUMI.GetN(), (TDatime(2015, 10, 13, 14, 38, 59)).Convert(), intL)
        intL += 0.001
        intLUMI.SetPoint(intLUMI.GetN(), (TDatime(2015, 10, 13, 14, 39, 0)).Convert(), intL)
        intLUMI.SetPoint(intLUMI.GetN(), (TDatime(2015, 10, 15, 1, 2, 59)).Convert(), intL)
        intL += 0.011
        intLUMI.SetPoint(intLUMI.GetN(), (TDatime(2015, 10, 15, 1, 3, 0)).Convert(), intL)
        intLUMI.SetPoint(intLUMI.GetN(), (TDatime(2015, 10, 15, 9, 26, 59)).Convert(), intL)
        intL += 0.038
        intLUMI.SetPoint(intLUMI.GetN(), (TDatime(2015, 10, 15, 9, 27, 0)).Convert(), intL)
        intLUMI.SetPoint(intLUMI.GetN(), (TDatime(2015, 10, 15, 19, 37, 59)).Convert(), intL)
        intL += 0.115
        intLUMI.SetPoint(intLUMI.GetN(), (TDatime(2015, 10, 15, 19, 38, 0)).Convert(), intL)
        intLUMI.SetPoint(intLUMI.GetN(), (TDatime(2015, 10, 16, 20, 15, 59)).Convert(), intL)
        intL += 0.103
        intLUMI.SetPoint(intLUMI.GetN(), (TDatime(2015, 10, 16, 20, 16, 0)).Convert(), intL)
        intLUMI.SetPoint(intLUMI.GetN(), (TDatime(2015, 10, 17, 5, 39, 59)).Convert(), intL)
        intL += 0.28
        intLUMI.SetPoint(intLUMI.GetN(), (TDatime(2015, 10, 17, 5, 40, 0)).Convert(), intL)
        intLUMI.SetPoint(intLUMI.GetN(), (TDatime(2015, 10, 17, 19, 13, 59)).Convert(), intL)
        intL += 0.088
        intLUMI.SetPoint(intLUMI.GetN(), (TDatime(2015, 10, 17, 19, 14, 0)).Convert(), intL)
        intLUMI.SetPoint(intLUMI.GetN(), (TDatime(2015, 10, 18, 2, 13, 59)).Convert(), intL)
        intL += 0.126
        intLUMI.SetPoint(intLUMI.GetN(), (TDatime(2015, 10, 18, 2, 14, 0)).Convert(), intL)
        intLUMI.SetPoint(intLUMI.GetN(), (TDatime(2015, 10, 18, 15, 49, 59)).Convert(), intL)
        intL += 0.002
        intLUMI.SetPoint(intLUMI.GetN(), (TDatime(2015, 10, 18, 15, 50, 0)).Convert(), intL)
        intLUMI.SetPoint(intLUMI.GetN(), (TDatime(2015, 10, 20, 4, 42, 59)).Convert(), intL)
        intL += 13.32
        intLUMI.SetPoint(intLUMI.GetN(), (TDatime(2015, 10, 20, 4, 43, 0)).Convert(), intL)
        intLUMI.SetPoint(intLUMI.GetN(), (TDatime(2015, 10, 20, 9, 44, 59)).Convert(), intL)
        intL += 30.635
        intLUMI.SetPoint(intLUMI.GetN(), (TDatime(2015, 10, 20, 9, 45, 0)).Convert(), intL)
        intLUMI.SetPoint(intLUMI.GetN(), (TDatime(2015, 10, 21, 2, 9, 59)).Convert(), intL)
        intL += 105.713
        intLUMI.SetPoint(intLUMI.GetN(), (TDatime(2015, 10, 21, 2, 10, 0)).Convert(), intL)
        intLUMI.SetPoint(intLUMI.GetN(), (TDatime(2015, 10, 21, 20, 34, 59)).Convert(), intL)
        intL += 13.366
        intLUMI.SetPoint(intLUMI.GetN(), (TDatime(2015, 10, 21, 20, 35, 0)).Convert(), intL)
        intLUMI.SetPoint(intLUMI.GetN(), (TDatime(2015, 10, 22, 23, 48, 59)).Convert(), intL)
        intL += 123.505
        intLUMI.SetPoint(intLUMI.GetN(), (TDatime(2015, 10, 22, 23, 47, 0)).Convert(), intL)
        intLUMI.SetPoint(intLUMI.GetN(), (TDatime(2015, 10, 23, 17, 43, 59)).Convert(), intL)
        intL += 64.794
        intLUMI.SetPoint(intLUMI.GetN(), (TDatime(2015, 10, 23, 17, 44, 0)).Convert(), intL)
        intLUMI.SetPoint(intLUMI.GetN(), (TDatime(2015, 10, 24, 16, 6, 59)).Convert(), intL)
        intL += 33.001
        intLUMI.SetPoint(intLUMI.GetN(), (TDatime(2015, 10, 24, 16, 7, 0)).Convert(), intL)
        intLUMI.SetPoint(intLUMI.GetN(), (TDatime(2015, 10, 26, 2, 59, 59)).Convert(), intL)
        intL += 15.901
        intLUMI.SetPoint(intLUMI.GetN(), (TDatime(2015, 10, 26, 3, 0, 0)).Convert(), intL)
        intLUMI.SetPoint(intLUMI.GetN(), (TDatime(2015, 10, 26, 16, 5, 59)).Convert(), intL)
        intL += 299.626
        intLUMI.SetPoint(intLUMI.GetN(), (TDatime(2015, 10, 26, 16, 6, 0)).Convert(), intL)
        intLUMI.SetPoint(intLUMI.GetN(), (TDatime(2015, 10, 28, 0, 0, 59)).Convert(), intL)
        intL += 161.366
        intLUMI.SetPoint(intLUMI.GetN(), (TDatime(2015, 10, 28, 0, 1, 0)).Convert(), intL)
        intLUMI.SetPoint(intLUMI.GetN(), (TDatime(2015, 10, 29, 1, 57, 59)).Convert(), intL)
        intL += 45.763
        intLUMI.SetPoint(intLUMI.GetN(), (TDatime(2015, 10, 29, 1, 58, 0)).Convert(), intL)
        intLUMI.SetPoint(intLUMI.GetN(), (TDatime(2015, 10, 30, 6, 16, 59)).Convert(), intL)
        intL += 11.654
        intLUMI.SetPoint(intLUMI.GetN(), (TDatime(2015, 10, 30, 6, 17, 0)).Convert(), intL)
        intLUMI.SetPoint(intLUMI.GetN(), (TDatime(2015, 10, 30, 17, 3, 59)).Convert(), intL)
        intL += 221.752
        intLUMI.SetPoint(intLUMI.GetN(), (TDatime(2015, 10, 30, 17, 4, 0)).Convert(), intL)
        intLUMI.SetPoint(intLUMI.GetN(), (TDatime(2015, 10, 31, 18, 4, 59)).Convert(), intL)
        intL += 282.557
        intLUMI.SetPoint(intLUMI.GetN(), (TDatime(2015, 10, 31, 18, 5, 0)).Convert(), intL)
        intLUMI.SetPoint(intLUMI.GetN(), (TDatime(2015, 11, 0o1, 20, 36, 59)).Convert(), intL)
        intL += 68.291
        intLUMI.SetPoint(intLUMI.GetN(), (TDatime(2015, 11, 0o1, 20, 37, 0)).Convert(), intL)
        intLUMI.SetPoint(intLUMI.GetN(), (TDatime(2015, 11, 0o2, 6, 28, 59)).Convert(), intL)
        intL += 39.267
        intLUMI.SetPoint(intLUMI.GetN(), (TDatime(2015, 11, 0o2, 6, 29, 0)).Convert(), intL)
        intLUMI.SetPoint(intLUMI.GetN(), (TDatime(2015, 11, 0o2, 17, 29, 59)).Convert(), intL)
        intL += 183.232
        intLUMI.SetPoint(intLUMI.GetN(), (TDatime(2015, 11, 0o2, 17, 30, 0)).Convert(), intL)
        intLUMI.SetPoint(intLUMI.GetN(), (TDatime(2015, 11, 9, 59, 59, 59)).Convert(), intL)
        intLUMI.SetPoint(intLUMI.GetN(), (TDatime(2015, 11, 10, 0, 0, 0)).Convert(), 0)


        # match the dates to the Tgraph

        pairsOld = []
        pairsOr  = []
        pairsE   = []
        pairsB   = []

        for g in range(intLUMI.GetN()):
            x1 = ROOT.Double(0.)
            y1 = ROOT.Double(0.)
            x2 = ROOT.Double(0.)
            y2 = ROOT.Double(0.)
            intLUMI.GetPoint(g, x1, y1)
            intLUMI.GetPoint(g+1, x2, y2)
            for i in range(len(FullInfo)):
                if FullInfo[i][0]>= x1 and FullInfo[i][0]<x2:
#                    if (FullInfo[i][4]==2 and FullInfo[i][2]>0) or (FullInfo[i][4]==29 and FullInfo[i][2]>0) or (FullInfo[i][4]==52 and  FullInfo[i][2]>0) or (FullInfo[i][4]==44 and FullInfo[i][2]<0 ):
#                        pairsE.append([y1*FullInfo[i][3]/1000., FullInfo[i][1]])
#                    elif (FullInfo[i][4]==11 and FullInfo[i][2]>0) or (FullInfo[i][4]==22 and FullInfo[i][2]>0) or (FullInfo[i][4]==43 and FullInfo[i][2]>0) or (FullInfo[i][4]==53 and FullInfo[i][2]<0):
#                        pairsB.append([y1*FullInfo[i][3]/1000., FullInfo[i][1]])
#                    elif (FullInfo[i][4]==34 and FullInfo[i][2]>0) or (FullInfo[i][4]==59 and FullInfo[i][2]>0) or (FullInfo[i][4]==3 and FullInfo[i][2]<0) or (FullInfo[i][4]==12 and FullInfo[i][2]<0) or (FullInfo[i][4]==19 and FullInf#o[i][2]<0) or (FullInfo[i][4]==27 and FullInfo[i][2]<0) or (FullInfo[i][4]==36 and FullInfo[i][2]<0) or (FullInfo[i][4]==48 and FullInfo[i][2]<0) or (FullInfo[i][4]==60 and FullInfo[i][2]<0):
#                        pairsOr.append([y1*FullInfo[i][3]/1000., FullInfo[i][1]])
#                    else:
#                        pairsOld.append([y1*FullInfo[i][3]/1000., FullInfo[i][1]])
#
                    if FullInfo[i][2]==1.05:
                        pairsEtaE1.append([y1*FullInfo[i][3]/1000., FullInfo[i][1]]) # finally fill the pairs
                    elif FullInfo[i][2]==1.15:
                        pairsEtaE2.append([y1*FullInfo[i][3]/1000., FullInfo[i][1]]) # finally fill the pairs
                    elif FullInfo[i][2]==1.3:
                        pairsEtaE3.append([y1*FullInfo[i][3]/1000., FullInfo[i][1]]) # finally fill the pairs
                    elif FullInfo[i][2]==1.5:
                        pairsEtaE4.append([y1*FullInfo[i][3]/1000., FullInfo[i][1]]) # finally fill the pairs
#                    if FullInfo[i][2]>0 and FullInfo[i][4]==38 and FullInfo[i][2]==1.05: # check special channel --> is it outlier?
#                        pairsE.append([y1*FullInfo[i][3]/1000., FullInfo[i][1]])
#                    if FullInfo[i][2]>0 and FullInfo[i][4]==18 and FullInfo[i][2]==1.3: # check special channel --> is it outlier?
#                        pairsB.append([y1*FullInfo[i][3]/1000., FullInfo[i][1]])

##                    if FullInfo[i][2]>=1.2 and FullInfo[i][2]<1.3:
#                    if FullInfo[i][2]>=1.0 and FullInfo[i][2]<1.1:
#                        pairsEta11.append([y1*FullInfo[i][3]/1000., FullInfo[i][1]])
##                    if FullInfo[i][2]>=1.3 and FullInfo[i][2]<1.4:
#                    if FullInfo[i][2]>=1.1 and FullInfo[i][2]<1.2:
#                        pairsEta12.append([y1*FullInfo[i][3]/1000., FullInfo[i][1]])
##                    if FullInfo[i][2]>=1.4 and FullInfo[i][2]<1.5:
#                    if FullInfo[i][2]>=1.2 and FullInfo[i][2]<1.3:
#                        pairsEta13.append([y1*FullInfo[i][3]/1000., FullInfo[i][1]])
##                    if FullInfo[i][2]>=1.5 and FullInfo[i][2]<1.7:
#                    if FullInfo[i][2]>=1.3 and FullInfo[i][2]<1.4:
#                        pairsEta14.append([y1*FullInfo[i][3]/1000., FullInfo[i][1]])
#                    if FullInfo[i][2]>=1.4 and FullInfo[i][2]<1.5:
#                        pairsEta15.append([y1*FullInfo[i][3]/1000., FullInfo[i][1]])

#                    break # value found
                    
        chargeE1 = array('f',[])
        variationE1 = array('f',[])
        for i in range(len(pairsEtaE1)):
            chargeE1.append(pairsEtaE1[i][0])
            variationE1.append(pairsEtaE1[i][1])

        chargeE2 = array('f',[])
        variationE2 = array('f',[])
        for i in range(len(pairsEtaE2)):
            chargeE2.append(pairsEtaE2[i][0])
            variationE2.append(pairsEtaE2[i][1])
            
        chargeE3 = array('f',[])
        variationE3 = array('f',[])
        for i in range(len(pairsEtaE3)):
            chargeE3.append(pairsEtaE3[i][0])
            variationE3.append(pairsEtaE3[i][1])

        chargeE4 = array('f',[])
        variationE4 = array('f',[])
        for i in range(len(pairsEtaE4)):
            chargeE4.append(pairsEtaE4[i][0])
            variationE4.append(pairsEtaE4[i][1])

#        charge11 = array('f',[])
#        variation11 = array('f',[])
#        for i in range(len(pairsEta11)):
#            charge11.append(pairsEta11[i][0])
#            variation11.append(pairsEta11[i][1])


#        charge12 = array('f',[])
#        variation12 = array('f',[])
#        for i in range(len(pairsEta12)):
#            charge12.append(pairsEta12[i][0])
#            variation12.append(pairsEta12[i][1])

#        charge13 = array('f',[])
#        variation13 = array('f',[])
#        for i in range(len(pairsEta13)):
#            charge13.append(pairsEta13[i][0])
#            variation13.append(pairsEta13[i][1])

#        charge14 = array('f',[])
#        variation14 = array('f',[])
#        for i in range(len(pairsEta14)):
#            charge14.append(pairsEta14[i][0])
#            variation14.append(pairsEta14[i][1])

#        charge15 = array('f',[])
#        variation15 = array('f',[])
#        for i in range(len(pairsEta15)):
#            charge15.append(pairsEta15[i][0])
#            variation15.append(pairsEta15[i][1])

#        chargeE = array('f',[])
#        variationE = array('f',[])
#        for i in range(len(pairsE)):
#            chargeE.append(pairsE[i][0])
#            variationE.append(pairsE[i][1])

#        chargeB = array('f',[])
#        variationB = array('f',[])
#        for i in range(len(pairsB)):
#            chargeB.append(pairsB[i][0])
#            variationB.append(pairsB[i][1])

#        chargeOr = array('f',[])
#        variationOr = array('f',[])
#        for i in range(len(pairsOr)):
#            chargeOr.append(pairsOr[i][0])
#            variationOr.append(pairsOr[i][1])

#        chargeOld = array('f',[])
#        variationOld = array('f',[])
#        for i in range(len(pairsOld)):
#            chargeOld.append(pairsOld[i][0])
#            variationOld.append(pairsOld[i][1])

#        FinalGraphE11 = TGraph(len(charge15), charge15, variation15)
#        FinalGraphE11.SetMarkerColor(kGreen)
#        FinalGraphE11.SetMarkerSize(0.2)
#        FinalGraphB = TGraph(len(chargeB), chargeB, variationB)
#        FinalGraphB.SetMarkerColor(kMagenta)
#        FinalGraphB.SetMarkerSize(0.2)

#        FinalHistoE11 = TH1F()
#        FinalHistoE11.SetLineColor(kGreen)
#        FinalHistoB = TH1F()
#        FinalHistoB.SetLineColor(kMagenta)
        FinalHistoE1 = TH1F()
        FinalHistoE1.SetLineColor(kBlack)
        FinalHistoE2 = TH1F()
        FinalHistoE2.SetLineColor(ROOT.kRed)
        FinalHistoE3 = TH1F()
        FinalHistoE3.SetLineColor(kBlue)
        FinalHistoE4 = TH1F()
        FinalHistoE4.SetLineColor(428)

#        FinalGraphE1 = TGraph(len(charge11), charge11, variation11)
        FinalGraphE1 = TGraph(len(chargeE1), chargeE1, variationE1)
        FinalGraphE1.SetMarkerSize(0.2)
 #       FinalGraphE2 = TGraph(len(charge12), charge12, variation12)
        FinalGraphE2 = TGraph(len(chargeE2), chargeE2, variationE2)
        FinalGraphE2.SetMarkerColor(ROOT.kRed)
        FinalGraphE2.SetMarkerSize(0.2)
 #       FinalGraphE3 = TGraph(len(charge13), charge13, variation13)
        FinalGraphE3 = TGraph(len(chargeE3), chargeE3, variationE3)
        FinalGraphE3.SetMarkerColor(kBlue)
        FinalGraphE3.SetMarkerSize(0.2)
 #       FinalGraphE4 = TGraph(len(charge14), charge14, variation14)
        FinalGraphE4 = TGraph(len(chargeE4), chargeE4, variationE4)
        FinalGraphE4.SetMarkerColor(428)
        FinalGraphE4.SetMarkerSize(0.2)

        c = TCanvas("c","c", 800,600)
        FinalGraphE4.Draw("ap")
#        FinalGraphE1.GetXaxis().SetRangeUser(0,10000.)
#        FinalGraphE1.SetMaximum(20.)
#        FinalGraphE1.SetMinimum(-20.)
        FinalGraphE2.Draw("samep")
        FinalGraphE3.Draw("samep")
        FinalGraphE1.Draw("samep")
#        FinalGraphE11.Draw("samep")
#        FinalGraphB.Draw("samep")
        FinalGraphE4.GetXaxis().SetTitle("Integrated Charge [mC]")
        FinalGraphE4.GetYaxis().SetTitle("Scintillator Irradiation Effect [%]")

        


        legend = TLegend(0.74,0.75,0.92,0.92)
        legend.SetHeader("E cells, EB")
#        legend.AddEntry(FinalGraphE11, "1.0#leq#eta<1.1","p")
        legend.AddEntry(FinalHistoE1, "1.0#leq|#eta|<1.1","l")
        legend.AddEntry(FinalHistoE2, "1.1#leq|#eta|<1.2","l")
        legend.AddEntry(FinalHistoE3, "1.2#leq|#eta|<1.4","l")
        legend.AddEntry(FinalHistoE4, "1.4#leq|#eta|<1.6","l")
#        legend.AddEntry(FinalHistoE11, "E1, EBA, m39","l")
#        legend.AddEntry(FinalHistoB, "E3, EBA, m19","l")


#        legend.AddEntry(FinalHistoE1, "1.0#leq#eta<1.1","l")
#        legend.AddEntry(FinalHistoE2, "1.1#leq#eta<1.2","l")
#        legend.AddEntry(FinalHistoE3, "1.2#leq#eta<1.3","l")
#        legend.AddEntry(FinalHistoE4, "1.3#leq#eta<1.4","l")
#        legend.AddEntry(FinalHistoE11, "1.4#leq#eta<1.5","l")
        legend.SetFillColor(0)
        legend.SetFillStyle(0)
        legend.SetBorderSize(0)

        legend.Draw()


        Leg1 = TLatex()
        Leg1.SetNDC()
        Leg1.SetTextAlign( 11 )
        Leg1.SetTextFont( 42 )
        Leg1.SetTextSize( 0.035 )
        Leg1.SetTextColor( 1 )
        Leg1.DrawLatex(0.19,0.75, "#scale[1.2]{#sqrt{s}=13 TeV, 4.34 fb^{-1}}")

        Leg2 =  TLatex()
        Leg2.SetNDC()
        Leg2.SetTextAlign( 11 )
        Leg2.SetTextSize( 0.05 )
        Leg2.SetTextColor( 1 )
        Leg2.SetTextFont(42)
        Leg2.DrawLatex(0.32,0.88," Internal")

        Leg2.DrawLatex(0.19,0.82, "Tile Calorimeter")

        atlasLabel =  TLatex()
        atlasLabel.SetNDC()
        atlasLabel.SetTextFont( 72 )
        atlasLabel.SetTextColor( 1 )
        atlasLabel.SetTextSize( 0.05 )
        atlasLabel.DrawLatex(0.19,0.88, "ATLAS")


        c.Print("ChargeMLaser_newref_Ecells2015.root" )
#        c.Print("ChargeMLaser_newrefPMT16_BCcells2015.png" )
        c.Print("ChargeMLaser_newref_Ecells2015.C" )



        #c.Print("%s/ChargeLaserPlot_Acells2015.root" % (self.dir) )
        #c.Print("%s/ChargeLaserPlot_Acells2015.eps" % (self.dir) )
        #c.Print("%s/ChargeLaserPlot_Acells2015.png" % (self.dir) )
