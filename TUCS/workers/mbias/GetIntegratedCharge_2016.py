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
class GetIntegratedCharge_2016(GenericWorker):
    "A plot worker for MBias"
    
    def __init__(self, LumiBegin=1, LumiRange=20):
        self.dir = getPlotDirectory() #where to save the plots
 
        self.dir      =  os.path.join(src.oscalls.getPlotDirectory(),'mbias2016','ResponseVariation')
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
        ROOT.gStyle.SetPalette(1)
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
                
            #  we loop over all cells and average over modules, but keep track of single channels!
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

                cellmeanA = stats()
                cellmeanC = stats()
                #determine averages for instLumi and current and calculate coefficient
                instlumiMean = stats()
                currentA = stats() # means of cellmeanA go here
                currentC = stats() # means of cellmeanC go here   
                count=0
		#loop over lb entries
                for l in range(self.LumiBegin,self.LumiEnd):
                    cellmeanApmt1 = []
                    cellmeanApmt2 = []
                    cellmeanCpmt1 = []
                    cellmeanCpmt2 = []

#                    InstLumiMean.fill(histoFile.GetBinContent(l+1)/1000.)
                    lumi=lumiIndex+count
#                    print lumi
                    count+=1
                    # start with A side 
                    for m in range(len(PMTCurrentHelp[lumi][PartA])):# 
                        specialPMT = []
                        useSpecial = False
                        # special cells removed later
#                        if cell.startswith('E1') and (m+1==7 or m+1==25 or m+1==44 or m+1==53): continue #E1merged
#                        if cell.startswith('E1') and (m+1==8 or m+1==24 or m+1==43 or m+1==54): continue #MBTS outer
                        if m==14 and "E" in cell:# if EBA15
                            specialPMT = self.PMTool.getRegionName2015(cell, True)[1]
                            useSpecial = True
                        
                        if PMTCurrentHelp[lumi][PartA][m][PMTch[0]]==0 or PMTCurrentHelp[lumi][PartA][m][PMTch[1]]==0: continue
                        if PMTGoodHelp[lumi][PartA][m][PMTch[0]]<1 or PMTGoodHelp[lumi][PartA][m][PMTch[1]]<1: 
                            cellmeanApmt1.append(0.0)
                            cellmeanApmt2.append(0.0)
                            continue
                        if PMTStatusHelp[lumi][PartA][m][PMTch[0]]<1 or PMTStatusHelp[lumi][PartA][m][PMTch[1]]<1:
                            cellmeanApmt1.append(0.0)
                            cellmeanApmt2.append(0.0)
                            continue
                        if not useSpecial:
                            cellmeanApmt1.append(PMTCurrentHelp[lumi][PartA][m][PMTch[0]])
                            cellmeanApmt2.append(PMTCurrentHelp[lumi][PartA][m][PMTch[1]])
                        else:
                            cellmeanApmt1.append(PMTCurrentHelp[lumi][PartA][m][specialPMT[0]])
                            cellmeanApmt2.append(PMTCurrentHelp[lumi][PartA][m][specialPMT[1]])

                        # end of module loop
                    # c side
                    for m in range(len(PMTCurrentHelp[lumi][PartC])):# 
                        specialPMT = []
                        useSpecial = False
                        if m==17 and "E" in cell: # if EBC18
                            specialPMT = self.PMTool.getRegionName2015(cell, True)[1]
                            useSpecial = True
                        # special cells, removed later
#                        if cell.startswith('E1') and (m==31 or m==33 or m==36): continue #E1 close to saturation                                                                                                                            
#                        if cell.startswith('E4') and (m+1==29 or m+1==32 or m+1==34 or m+1==37): continue #E4p  
#                        if cell.startswith('E1') and (m+1==7 or m+1==25 or m+1==44 or m+1==53): continue #E1merged
#                        if cell.startswith('E1') and (m+1==28 or m+1==31 or m+1==35 or m+1==38): continue #E1merged
#                        if cell.startswith('E1') and (m+1==8 or m+1==24 or m+1==43 or m+1==54): continue #MBTS outer
#                        if cell.startswith('E2') and m==39: continue #E2 saturated 
                        if PMTCurrentHelp[lumi][PartC][m][PMTch[0]]==0 or PMTCurrentHelp[lumi][PartC][m][PMTch[1]]==0: 
                            cellmeanCpmt1.append(0.0)
                            cellmeanCpmt2.append(0.0)
                            continue
                        if PMTGoodHelp[lumi][PartC][m][PMTch[0]]<1 or PMTGoodHelp[lumi][PartC][m][PMTch[1]]<1: 
                            cellmeanCpmt1.append(0.0)
                            cellmeanCpmt2.append(0.0)
                            continue
                        if PMTStatusHelp[lumi][PartC][m][PMTch[0]]<1 or PMTStatusHelp[lumi][PartC][m][PMTch[1]]<1:
                            cellmeanCpmt1.append(0.0)
                            cellmeanCpmt2.append(0.0)
                            continue
                        if not useSpecial:
                            cellmeanCpmt1.append(PMTCurrentHelp[lumi][PartC][m][PMTch[0]])
                            cellmeanCpmt2.append(PMTCurrentHelp[lumi][PartC][m][PMTch[1]])
                        else:
                            cellmeanCpmt1.append(PMTCurrentHelp[lumi][PartC][m][specialPMT[0]])
                            cellmeanCpmt2.append(PMTCurrentHelp[lumi][PartC][m][specialPMT[1]])
                        # end of module loop

                    PMTCurrentApmt1.append(cellmeanApmt1)
                    PMTCurrentApmt2.append(cellmeanApmt2)

                    PMTCurrentCpmt1.append(cellmeanCpmt1)
                    PMTCurrentCpmt2.append(cellmeanCpmt2)
                    

                    # end of lb loop------------------------------------------------------------------------
                InstLumiMean = 0.2011 #Run 298633 , lb 200-230
                currentApmt1 = stats()
                currentApmt2 = stats()
                currentCpmt1 = stats()
                currentCpmt2 = stats()

                #lb loop
                print(len(PMTCurrentCpmt1), len(PMTCurrentCpmt1[0]))
                for m in range(len(PMTCurrentApmt1[0])):
                    for lb in range(len(PMTCurrentApmt1)):
                        currentApmt1.fill(PMTCurrentApmt1[lb][m])
                        currentApmt2.fill(PMTCurrentApmt2[lb][m])
                        currentCpmt1.fill(PMTCurrentCpmt1[lb][m])
                        currentCpmt2.fill(PMTCurrentCpmt2[lb][m])

                    # now create vector with information: channel,  module, eta, lumiCoeff
                    informationApmt1 = [PMTch[0]+1, m, etaValueA, currentApmt1.mean()/InstLumiMean]
                    informationApmt2 = [PMTch[1]+1, m, etaValueA, currentApmt2.mean()/InstLumiMean]
                    informationCpmt1 = [PMTch[0]+1, m, etaValueC, currentCpmt1.mean()/InstLumiMean]
                    informationCpmt2 = [PMTch[1]+1, m, etaValueC, currentCpmt2.mean()/InstLumiMean]

                    currentApmt1.reset()
                    currentApmt2.reset()
                    currentCpmt1.reset()
                    currentCpmt2.reset()

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
        with open('Laser_D6_variation_2016.txt') as f:
            data = f.readlines()
            for line in data:
                laserinfo = line.split() # time, deviation, part, mod, chan
                if int(laserinfo[4]) ==37: # just use one pmt for now
                    LaserInformation.append(laserinfo)
#                    if float(laserinfo[0])< time_min:
#                        time_min=float(laserinfo[0])

#        print time_min

        LaserInformationCorr = []

        with open('Laser_A13Ecells_variation_2016.txt') as f:
            data = f.readlines()
            for line in data:
                laserinfo = line.split()
                for i in range(len(LaserInformation)):
                    D5dev = float(LaserInformation[i][1])
                    # subtract D6 variation:
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
        with open('Mbias_NewEcells_variation_2015_29aug16_wrtD6.txt') as f:
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
                                print("und dann?")
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
                            if channel==14 and ExtendedBarrel[i][1]==39: # E2,m39 saturated
                                continue
#                            f = open("E3E4_fullInfo_2015.txt", "a+")
#                            f.write(" %s %s %s %s %s \n" % (str(MbiasInfo[info][2]), str(MbiasInfo[info][3]), str(MbiasInfo[info][1]), str(ExtendedBarrel[i][3]),str(MbiasInfo[info][0])))
                            FullInfo.append([MbiasInfo[info][0], MbiasInfo[info][1], ExtendedBarrel[i][2], ExtendedBarrel[i][3], MbiasInfo[info][3]])
#                            f.close()
                            break # search no further


        # and now matching with intergrated lumi:
        intL = 0.0

        intLUMI = TGraph()

        tmp_Datime_str = "2016-04-22 22:39:00"
        tmp_Datime = TDatime(tmp_Datime_str)
        intLUMI.SetPoint(intLUMI.GetN(), (tmp_Datime).Convert()-1.0+13927, intL)
        intL +=0.062
        intLUMI.SetPoint(intLUMI.GetN(), (tmp_Datime).Convert()+13927, intL)
        tmp_Datime_str = "2016-04-23 04:52:00"
        tmp_Datime = TDatime(tmp_Datime_str)
        intLUMI.SetPoint(intLUMI.GetN(), (tmp_Datime).Convert()-1.0+9288.6, intL)
        intL +=0.048
        intLUMI.SetPoint(intLUMI.GetN(), (tmp_Datime).Convert()+9288.6, intL)
        tmp_Datime_str = "2016-04-23 23:00:00" 
        tmp_Datime = TDatime(tmp_Datime_str)
        intLUMI.SetPoint(intLUMI.GetN(), (tmp_Datime).Convert()-1.0+30324.2, intL)
        intL +=0.578
        intLUMI.SetPoint(intLUMI.GetN(), (tmp_Datime).Convert()+30324.2, intL)
        tmp_Datime_str = "2016-04-24 22:53:00"
        tmp_Datime = TDatime(tmp_Datime_str)
        intLUMI.SetPoint(intLUMI.GetN(), (tmp_Datime).Convert()-1.0+30318.2, intL)
        intL +=0.8
        intLUMI.SetPoint(intLUMI.GetN(), (tmp_Datime).Convert()+30318.2, intL)
        tmp_Datime_str = "2016-04-27 01:14:00"
        tmp_Datime = TDatime(tmp_Datime_str)
        intLUMI.SetPoint(intLUMI.GetN(), (tmp_Datime).Convert()-1.0+20468.2, intL)
        intL +=0.633
        intLUMI.SetPoint(intLUMI.GetN(), (tmp_Datime).Convert()+20468.2, intL)
        tmp_Datime_str = "2016-04-28 20:57:00"
        tmp_Datime = TDatime(tmp_Datime_str)
        intLUMI.SetPoint(intLUMI.GetN(), (tmp_Datime).Convert()-1.0+25533.8, intL)
        intL +=4.027
        intLUMI.SetPoint(intLUMI.GetN(), (tmp_Datime).Convert()+25533.8, intL)
        tmp_Datime_str = "2016-05-06 21:30:00" 
        tmp_Datime = TDatime(tmp_Datime_str)
        intLUMI.SetPoint(intLUMI.GetN(), (tmp_Datime).Convert()-1.0+5246.2, intL)
        intL +=0.034
        intLUMI.SetPoint(intLUMI.GetN(), (tmp_Datime).Convert()+5246.2, intL)
        tmp_Datime_str = "2016-05-07 01:20:00" 
        tmp_Datime = TDatime(tmp_Datime_str)
        intLUMI.SetPoint(intLUMI.GetN(), (tmp_Datime).Convert()-1.0+8264.9, intL)
        intL +=1.182
        intLUMI.SetPoint(intLUMI.GetN(), (tmp_Datime).Convert()+8264.9, intL)
        tmp_Datime_str = "2016-05-07 06:13:00" 
        tmp_Datime = TDatime(tmp_Datime_str)
        intLUMI.SetPoint(intLUMI.GetN(), (tmp_Datime).Convert()-1.0+17008.7, intL)
        intL +=2.353
        intLUMI.SetPoint(intLUMI.GetN(), (tmp_Datime).Convert()+17008.7, intL)
        tmp_Datime_str = "2016-05-07 17:19:00" 
        tmp_Datime = TDatime(tmp_Datime_str)
        intLUMI.SetPoint(intLUMI.GetN(), (tmp_Datime).Convert()-1.0+40815, intL)
        intL +=6.663
        intLUMI.SetPoint(intLUMI.GetN(), (tmp_Datime).Convert()+40815, intL)
        tmp_Datime_str = "2016-05-08 12:04:00" 
        tmp_Datime = TDatime(tmp_Datime_str)
        intLUMI.SetPoint(intLUMI.GetN(), (tmp_Datime).Convert()-1.0+27796.8, intL)
        intL +=22.064
        intLUMI.SetPoint(intLUMI.GetN(), (tmp_Datime).Convert()+27796.8, intL)
        tmp_Datime_str = "2016-05-08 23:38:00" 
        tmp_Datime = TDatime(tmp_Datime_str)
        intLUMI.SetPoint(intLUMI.GetN(), (tmp_Datime).Convert()-1.0+2494.5, intL)
        intL +=1.812
        intLUMI.SetPoint(intLUMI.GetN(), (tmp_Datime).Convert()+2494.5, intL)
        tmp_Datime_str = "2016-05-09 22:43:00" 
        tmp_Datime = TDatime(tmp_Datime_str)
        intLUMI.SetPoint(intLUMI.GetN(), (tmp_Datime).Convert()-1.0+9282.9, intL)
        intL +=8.695
        intLUMI.SetPoint(intLUMI.GetN(), (tmp_Datime).Convert()+9282.9, intL)
        tmp_Datime_str = "2016-05-10 03:36:00" 
        tmp_Datime = TDatime(tmp_Datime_str)
        intLUMI.SetPoint(intLUMI.GetN(), (tmp_Datime).Convert()-1.0+9749.5, intL)
        intL +=9.024
        intLUMI.SetPoint(intLUMI.GetN(), (tmp_Datime).Convert()+9749.5, intL)
        tmp_Datime_str = "2016-05-10 18:37:00"
        tmp_Datime = TDatime(tmp_Datime_str)
        intLUMI.SetPoint(intLUMI.GetN(), (tmp_Datime).Convert()-1.0+29857.2, intL)
        intL +=26.875
        intLUMI.SetPoint(intLUMI.GetN(), (tmp_Datime).Convert()+29857.2, intL)
        tmp_Datime_str = "2016-05-11 19:21:00"
        tmp_Datime = TDatime(tmp_Datime_str)
        intLUMI.SetPoint(intLUMI.GetN(), (tmp_Datime).Convert()-1.0+33415.2, intL)
        intL +=56.21
        intLUMI.SetPoint(intLUMI.GetN(), (tmp_Datime).Convert()+33415.2, intL)
        tmp_Datime_str = "2016-05-12 20:34:00"
        tmp_Datime = TDatime(tmp_Datime_str)
        intLUMI.SetPoint(intLUMI.GetN(), (tmp_Datime).Convert()-1.0+32198.8, intL)
        intL +=51.592
        intLUMI.SetPoint(intLUMI.GetN(), (tmp_Datime).Convert()+32198.8, intL)
        tmp_Datime_str = "2016-05-13 23:42:00"
        tmp_Datime = TDatime(tmp_Datime_str)
        intLUMI.SetPoint(intLUMI.GetN(), (tmp_Datime).Convert()-1.0+22739.1, intL)
        intL +=32.125
        intLUMI.SetPoint(intLUMI.GetN(), (tmp_Datime).Convert()+22739.1, intL)
        tmp_Datime_str = "2016-05-14 10:55:00"
        tmp_Datime = TDatime(tmp_Datime_str)
        intLUMI.SetPoint(intLUMI.GetN(), (tmp_Datime).Convert()-1.0+18517.7, intL)
        intL +=29.524
        intLUMI.SetPoint(intLUMI.GetN(), (tmp_Datime).Convert()+18517.7, intL)
        tmp_Datime_str = "2016-05-14 18:26:00"
        tmp_Datime = TDatime(tmp_Datime_str)
        intLUMI.SetPoint(intLUMI.GetN(), (tmp_Datime).Convert()-1.0+41581.4, intL)
        intL +=97.595
        intLUMI.SetPoint(intLUMI.GetN(), (tmp_Datime).Convert()+41581.4, intL)
        tmp_Datime_str = "2016-05-16 08:06:00"
        tmp_Datime = TDatime(tmp_Datime_str)
        intLUMI.SetPoint(intLUMI.GetN(), (tmp_Datime).Convert()-1.0+16743.2, intL)
        intL +=31.282
        intLUMI.SetPoint(intLUMI.GetN(), (tmp_Datime).Convert()+16743.2, intL)
        tmp_Datime_str = "2016-05-16 19:43:00"
        tmp_Datime = TDatime(tmp_Datime_str)
        intLUMI.SetPoint(intLUMI.GetN(), (tmp_Datime).Convert()-1.0+37858, intL)
        intL +=72.319
        intLUMI.SetPoint(intLUMI.GetN(), (tmp_Datime).Convert()+37858, intL)
        tmp_Datime_str = "2016-05-18 05:34:00"
        tmp_Datime = TDatime(tmp_Datime_str)
        intLUMI.SetPoint(intLUMI.GetN(), (tmp_Datime).Convert()-1.0+13041, intL)
        intL +=38.666
        intLUMI.SetPoint(intLUMI.GetN(), (tmp_Datime).Convert()+13041, intL)
        tmp_Datime_str = "2016-05-18 14:19:00"
        tmp_Datime = TDatime(tmp_Datime_str)
        intLUMI.SetPoint(intLUMI.GetN(), (tmp_Datime).Convert()-1.0+27385.6, intL)
        intL +=0.044
        intLUMI.SetPoint(intLUMI.GetN(), (tmp_Datime).Convert()+27385.6, intL)
        tmp_Datime_str = "2016-05-20 01:16:00"
        tmp_Datime = TDatime(tmp_Datime_str)
        intLUMI.SetPoint(intLUMI.GetN(), (tmp_Datime).Convert()-1.0+127728, intL)
        intL +=263.896
        intLUMI.SetPoint(intLUMI.GetN(), (tmp_Datime).Convert()+127728, intL)
        tmp_Datime_str = "2016-05-27 01:26:00"
        tmp_Datime = TDatime(tmp_Datime_str)
        intLUMI.SetPoint(intLUMI.GetN(), (tmp_Datime).Convert()-1.0+5578.1, intL)
        intL +=9.812
        intLUMI.SetPoint(intLUMI.GetN(), (tmp_Datime).Convert()+5578.1, intL)
        tmp_Datime_str = "2016-05-27 05:57:00"
        tmp_Datime = TDatime(tmp_Datime_str)
        intLUMI.SetPoint(intLUMI.GetN(), (tmp_Datime).Convert()-1.0+22490.4, intL)
        intL +=0.051
        intLUMI.SetPoint(intLUMI.GetN(), (tmp_Datime).Convert()+22490.4, intL)
        tmp_Datime_str = "2016-05-27 21:37:00"
        tmp_Datime = TDatime(tmp_Datime_str)
        intLUMI.SetPoint(intLUMI.GetN(), (tmp_Datime).Convert()-1.0+2273.9, intL)
        intL +=7.199
        intLUMI.SetPoint(intLUMI.GetN(), (tmp_Datime).Convert()+2273.9, intL)
        tmp_Datime_str = "2016-05-28 10:06:00" 
        tmp_Datime = TDatime(tmp_Datime_str)
        intLUMI.SetPoint(intLUMI.GetN(), (tmp_Datime).Convert()-1.0+28868.8, intL)
        intL +=105.367
        intLUMI.SetPoint(intLUMI.GetN(), (tmp_Datime).Convert()+28868.8, intL)
        tmp_Datime_str = "2016-05-29 00:07:00" 
        tmp_Datime = TDatime(tmp_Datime_str)
        intLUMI.SetPoint(intLUMI.GetN(), (tmp_Datime).Convert()-1.0+1608.3, intL)
        intL +=7.527
        intLUMI.SetPoint(intLUMI.GetN(), (tmp_Datime).Convert()+1608.3, intL)
        tmp_Datime_str = "2016-05-29 18:32:00" 
        tmp_Datime = TDatime(tmp_Datime_str)
        intLUMI.SetPoint(intLUMI.GetN(), (tmp_Datime).Convert()-1.0+33588.5, intL)
        intL +=143.474
        intLUMI.SetPoint(intLUMI.GetN(), (tmp_Datime).Convert()+33588.5, intL)
        tmp_Datime_str = "2016-05-30 13:36:00"
        tmp_Datime = TDatime(tmp_Datime_str)
        intLUMI.SetPoint(intLUMI.GetN(), (tmp_Datime).Convert()-1.0+45092, intL)
        intL +=206.618
        intLUMI.SetPoint(intLUMI.GetN(), (tmp_Datime).Convert()+45092, intL)
        tmp_Datime_str = "2016-05-31 04:36:00"
        tmp_Datime = TDatime(tmp_Datime_str)
        intLUMI.SetPoint(intLUMI.GetN(), (tmp_Datime).Convert()-1.0+29401, intL)
        intL +=159.56
        intLUMI.SetPoint(intLUMI.GetN(), (tmp_Datime).Convert()+29401, intL)
        tmp_Datime_str = "2016-06-01 01:56:00"
        tmp_Datime = TDatime(tmp_Datime_str)
        intLUMI.SetPoint(intLUMI.GetN(), (tmp_Datime).Convert()-1.0+9840.5, intL)
        intL +=59.627
        intLUMI.SetPoint(intLUMI.GetN(), (tmp_Datime).Convert()+9840.5, intL)
        tmp_Datime_str = "2016-06-01 13:55:00"
        tmp_Datime = TDatime(tmp_Datime_str)
        intLUMI.SetPoint(intLUMI.GetN(), (tmp_Datime).Convert()-1.0+41047.2, intL)
        intL +=250.425
        intLUMI.SetPoint(intLUMI.GetN(), (tmp_Datime).Convert()+41047.2, intL)
        tmp_Datime_str = "2016-06-02 04:33:00"
        tmp_Datime = TDatime(tmp_Datime_str)
        intLUMI.SetPoint(intLUMI.GetN(), (tmp_Datime).Convert()-1.0+63561, intL)
        intL +=355.708
        intLUMI.SetPoint(intLUMI.GetN(), (tmp_Datime).Convert()+63561, intL)
        tmp_Datime_str = "2016-06-03 12:41:00"
        tmp_Datime = TDatime(tmp_Datime_str)
        intLUMI.SetPoint(intLUMI.GetN(), (tmp_Datime).Convert()-1.0+1357, intL)
        intL +=8.822
        intLUMI.SetPoint(intLUMI.GetN(), (tmp_Datime).Convert()+1357, intL)
        tmp_Datime_str = "2016-06-03 18:08:00"
        tmp_Datime = TDatime(tmp_Datime_str)
        intLUMI.SetPoint(intLUMI.GetN(), (tmp_Datime).Convert()-1.0+51050.1, intL)
        intL +=314.551
        intLUMI.SetPoint(intLUMI.GetN(), (tmp_Datime).Convert()+51050.1, intL)
        tmp_Datime_str = "2016-06-04 20:02:00"
        tmp_Datime = TDatime(tmp_Datime_str)
        intLUMI.SetPoint(intLUMI.GetN(), (tmp_Datime).Convert()-1.0+64163.8, intL)
        intL +=362.589
        intLUMI.SetPoint(intLUMI.GetN(), (tmp_Datime).Convert()+64163.8, intL)
        tmp_Datime_str = "2016-06-05 18:33:00"
        tmp_Datime = TDatime(tmp_Datime_str)
        intLUMI.SetPoint(intLUMI.GetN(), (tmp_Datime).Convert()-1.0+39851.4, intL)
        intL +=240.423
        intLUMI.SetPoint(intLUMI.GetN(), (tmp_Datime).Convert()+39851.4, intL)
        tmp_Datime_str = "2016-06-11 08:18:00"
        tmp_Datime = TDatime(tmp_Datime_str)
        intLUMI.SetPoint(intLUMI.GetN(), (tmp_Datime).Convert()-1.0+25027.8, intL)
        intL +=45.824
        intLUMI.SetPoint(intLUMI.GetN(), (tmp_Datime).Convert()+25027.8, intL)
        tmp_Datime_str = "2016-06-11 22:33:00"
        tmp_Datime = TDatime(tmp_Datime_str)
        intLUMI.SetPoint(intLUMI.GetN(), (tmp_Datime).Convert()-1.0+76375.4, intL)
        intL +=437.638
        intLUMI.SetPoint(intLUMI.GetN(), (tmp_Datime).Convert()+76375.4, intL)
        tmp_Datime_str = "2016-06-13 01:26:00"
        tmp_Datime = TDatime(tmp_Datime_str)
        intLUMI.SetPoint(intLUMI.GetN(), (tmp_Datime).Convert()-1.0+98390.6, intL)
        intL +=495.108
        intLUMI.SetPoint(intLUMI.GetN(), (tmp_Datime).Convert()+98390.6, intL)
        tmp_Datime_str = "2016-06-14 15:52:00"
        tmp_Datime = TDatime(tmp_Datime_str)
        intLUMI.SetPoint(intLUMI.GetN(), (tmp_Datime).Convert()-1.0+66120.5, intL)
        intL +=418.425
        intLUMI.SetPoint(intLUMI.GetN(), (tmp_Datime).Convert()+66120.5, intL)
        tmp_Datime_str = "2016-06-15 13:18:00"
        tmp_Datime = TDatime(tmp_Datime_str)
        intLUMI.SetPoint(intLUMI.GetN(), (tmp_Datime).Convert()-1.0+31038.1, intL)
        intL +=209.425
        intLUMI.SetPoint(intLUMI.GetN(), (tmp_Datime).Convert()+31038.1, intL)
        tmp_Datime_str = "2016-06-16 21:37:00"
        tmp_Datime = TDatime(tmp_Datime_str)
        intLUMI.SetPoint(intLUMI.GetN(), (tmp_Datime).Convert()-1.0+32093.1, intL)
        intL +=208.168
        intLUMI.SetPoint(intLUMI.GetN(), (tmp_Datime).Convert()+32093.1, intL)
        tmp_Datime_str = "2016-06-17 13:12:00"
        tmp_Datime = TDatime(tmp_Datime_str)
        intLUMI.SetPoint(intLUMI.GetN(), (tmp_Datime).Convert()-1.0+88179.6, intL)
        intL +=411.319
        intLUMI.SetPoint(intLUMI.GetN(), (tmp_Datime).Convert()+88179.6, intL)
        tmp_Datime_str = "2016-06-18 16:24:00"
        tmp_Datime = TDatime(tmp_Datime_str)
        intLUMI.SetPoint(intLUMI.GetN(), (tmp_Datime).Convert()-1.0+31887.6, intL)
        intL +=212.511
        intLUMI.SetPoint(intLUMI.GetN(), (tmp_Datime).Convert()+31887.6, intL)
        tmp_Datime_str = "2016-06-19 05:52:00"
        tmp_Datime = TDatime(tmp_Datime_str)
        intLUMI.SetPoint(intLUMI.GetN(), (tmp_Datime).Convert()-1.0+15581.6, intL)
        intL +=113.024
        intLUMI.SetPoint(intLUMI.GetN(), (tmp_Datime).Convert()+15581.6, intL)
        tmp_Datime_str = "2016-06-19 14:42:00"
        tmp_Datime = TDatime(tmp_Datime_str)
        intLUMI.SetPoint(intLUMI.GetN(), (tmp_Datime).Convert()-1.0+20859.2, intL)
        intL +=152.542
        intLUMI.SetPoint(intLUMI.GetN(), (tmp_Datime).Convert()+20859.2, intL)
        tmp_Datime_str = "2016-06-20 00:12:00"
        tmp_Datime = TDatime(tmp_Datime_str)
        intLUMI.SetPoint(intLUMI.GetN(), (tmp_Datime).Convert()-1.0+104529, intL)
        intL +=537.284
        intLUMI.SetPoint(intLUMI.GetN(), (tmp_Datime).Convert()+104529, intL)
        tmp_Datime_str = "2016-06-23 23:59:00"
        tmp_Datime = TDatime(tmp_Datime_str)
        intLUMI.SetPoint(intLUMI.GetN(), (tmp_Datime).Convert()-1.0+11790.8, intL)
        intL +=90.64
        intLUMI.SetPoint(intLUMI.GetN(), (tmp_Datime).Convert()+11790.8, intL)
        tmp_Datime_str = "2016-06-25 03:49:00"
        tmp_Datime = TDatime(tmp_Datime_str)
        intLUMI.SetPoint(intLUMI.GetN(), (tmp_Datime).Convert()-1.0+96022.5, intL)
        intL +=554.3
        intLUMI.SetPoint(intLUMI.GetN(), (tmp_Datime).Convert()+96022.5, intL)
        tmp_Datime_str = "2016-06-26 12:33:00"
        tmp_Datime = TDatime(tmp_Datime_str)
        intLUMI.SetPoint(intLUMI.GetN(), (tmp_Datime).Convert()-1.0+133330, intL)
        intL +=719.459
        intLUMI.SetPoint(intLUMI.GetN(), (tmp_Datime).Convert()+133330, intL)
        tmp_Datime_str = "2016-06-28 09:10:00"
        tmp_Datime = TDatime(tmp_Datime_str)
        intLUMI.SetPoint(intLUMI.GetN(), (tmp_Datime).Convert()-1.0+35842.8, intL)
        intL +=259.13
        intLUMI.SetPoint(intLUMI.GetN(), (tmp_Datime).Convert()+35842.8, intL)
        tmp_Datime_str = "2016-06-29 02:11:00"
        tmp_Datime = TDatime(tmp_Datime_str)
        intLUMI.SetPoint(intLUMI.GetN(), (tmp_Datime).Convert()-1.0+55500, intL)
        intL +=368.351
        intLUMI.SetPoint(intLUMI.GetN(), (tmp_Datime).Convert()+55500, intL)
        tmp_Datime_str = "2016-06-30 00:45:00"
        tmp_Datime = TDatime(tmp_Datime_str)
        intLUMI.SetPoint(intLUMI.GetN(), (tmp_Datime).Convert()-1.0+2259.5, intL)
        intL +=20.341
        intLUMI.SetPoint(intLUMI.GetN(), (tmp_Datime).Convert()+2259.5, intL)
        tmp_Datime_str = "2016-06-30 15:38:00"
        tmp_Datime = TDatime(tmp_Datime_str)
        intLUMI.SetPoint(intLUMI.GetN(), (tmp_Datime).Convert()-1.0+11637.2, intL)
        intL +=104.205
        intLUMI.SetPoint(intLUMI.GetN(), (tmp_Datime).Convert()+11637.2, intL)
        tmp_Datime_str = "2016-06-30 22:19:00"
        tmp_Datime = TDatime(tmp_Datime_str)
        intLUMI.SetPoint(intLUMI.GetN(), (tmp_Datime).Convert()-1.0+15226.2, intL)
        intL +=128.352
        intLUMI.SetPoint(intLUMI.GetN(), (tmp_Datime).Convert()+15226.2, intL)
        tmp_Datime_str = "2016-07-02 03:14:00"
        tmp_Datime = TDatime(tmp_Datime_str)
        intLUMI.SetPoint(intLUMI.GetN(), (tmp_Datime).Convert()-1.0+92067.7, intL)
        intL +=578.141
        intLUMI.SetPoint(intLUMI.GetN(), (tmp_Datime).Convert()+92067.7, intL)
        tmp_Datime_str = "2016-07-03 16:44:00"
        tmp_Datime = TDatime(tmp_Datime_str)
        intLUMI.SetPoint(intLUMI.GetN(), (tmp_Datime).Convert()-1.0+50576.8, intL)
        intL +=377.218
        intLUMI.SetPoint(intLUMI.GetN(), (tmp_Datime).Convert()+50576.8, intL)
        tmp_Datime_str = "2016-07-04 10:23:00"
        tmp_Datime = TDatime(tmp_Datime_str)
        intLUMI.SetPoint(intLUMI.GetN(), (tmp_Datime).Convert()-1.0+23943.6, intL)
        intL +=183.802
        intLUMI.SetPoint(intLUMI.GetN(), (tmp_Datime).Convert()+23943.6, intL)
        tmp_Datime_str = "2016-07-04 22:01:00"
        tmp_Datime = TDatime(tmp_Datime_str)
        intLUMI.SetPoint(intLUMI.GetN(), (tmp_Datime).Convert()-1.0+85482.6, intL)
        intL +=521.515
        intLUMI.SetPoint(intLUMI.GetN(), (tmp_Datime).Convert()+85482.6, intL)
        tmp_Datime_str = "2016-07-06 02:34:00"
        tmp_Datime = TDatime(tmp_Datime_str)
        intLUMI.SetPoint(intLUMI.GetN(), (tmp_Datime).Convert()-1.0+91126.7, intL)
        intL +=549.931
        intLUMI.SetPoint(intLUMI.GetN(), (tmp_Datime).Convert()+91126.7, intL)
        tmp_Datime_str = "2016-07-07 11:58:00"
        tmp_Datime = TDatime(tmp_Datime_str)
        intLUMI.SetPoint(intLUMI.GetN(), (tmp_Datime).Convert()-1.0+82279.9, intL)
        intL +=531.755
        intLUMI.SetPoint(intLUMI.GetN(), (tmp_Datime).Convert()+82279.9, intL)
        tmp_Datime_str = "2016-07-08 14:10:00"
        tmp_Datime = TDatime(tmp_Datime_str)
        intLUMI.SetPoint(intLUMI.GetN(), (tmp_Datime).Convert()-1.0+80566, intL)
        intL +=460.595
        intLUMI.SetPoint(intLUMI.GetN(), (tmp_Datime).Convert()+80566, intL)
        tmp_Datime_str = "2016-07-09 16:36:00"
        tmp_Datime = TDatime(tmp_Datime_str)
        intLUMI.SetPoint(intLUMI.GetN(), (tmp_Datime).Convert()-1.0+49962.3, intL)
        intL +=352.655
        intLUMI.SetPoint(intLUMI.GetN(), (tmp_Datime).Convert()+49962.3, intL)
        tmp_Datime_str = "2016-07-10 11:55:00"
        tmp_Datime = TDatime(tmp_Datime_str)
        intLUMI.SetPoint(intLUMI.GetN(), (tmp_Datime).Convert()-1.0+80683.8, intL)
        intL +=486.825
        intLUMI.SetPoint(intLUMI.GetN(), (tmp_Datime).Convert()+80683.8, intL)
        tmp_Datime_str = "2016-07-12 00:16:00"
        tmp_Datime = TDatime(tmp_Datime_str)
        intLUMI.SetPoint(intLUMI.GetN(), (tmp_Datime).Convert()-1.0+43642.3, intL)
        intL +=284.782
        intLUMI.SetPoint(intLUMI.GetN(), (tmp_Datime).Convert()+43642.3, intL)
        tmp_Datime_str = "2016-07-12 20:09:00"
        tmp_Datime = TDatime(tmp_Datime_str)
        intLUMI.SetPoint(intLUMI.GetN(), (tmp_Datime).Convert()-1.0+91563, intL)
        intL +=526.722
        intLUMI.SetPoint(intLUMI.GetN(), (tmp_Datime).Convert()+91563, intL)
        tmp_Datime_str = "2016-07-14 02:52:00"
        tmp_Datime = TDatime(tmp_Datime_str)
        intLUMI.SetPoint(intLUMI.GetN(), (tmp_Datime).Convert()-1.0+92054.2, intL)
        intL +=533.264
        intLUMI.SetPoint(intLUMI.GetN(), (tmp_Datime).Convert()+92054.2, intL)
        tmp_Datime_str = "2016-07-15 07:04:00"
        tmp_Datime = TDatime(tmp_Datime_str)
        intLUMI.SetPoint(intLUMI.GetN(), (tmp_Datime).Convert()-1.0+83485.2, intL)
        intL +=490.469
        intLUMI.SetPoint(intLUMI.GetN(), (tmp_Datime).Convert()+83485.2, intL)
        tmp_Datime_str = "2016-07-16 09:06:00"
        tmp_Datime = TDatime(tmp_Datime_str)
        intLUMI.SetPoint(intLUMI.GetN(), (tmp_Datime).Convert()-1.0+79646.4, intL)
        intL +=509.094
        intLUMI.SetPoint(intLUMI.GetN(), (tmp_Datime).Convert()+79646.4, intL)
        tmp_Datime_str = "2016-07-17 21:39:00"
        tmp_Datime = TDatime(tmp_Datime_str)
        intLUMI.SetPoint(intLUMI.GetN(), (tmp_Datime).Convert()-1.0+19577.7, intL)
        intL +=169.794
        intLUMI.SetPoint(intLUMI.GetN(), (tmp_Datime).Convert()+19577.7, intL)
        tmp_Datime_str = "2016-07-18 07:11:00"
        tmp_Datime = TDatime(tmp_Datime_str)
        intLUMI.SetPoint(intLUMI.GetN(), (tmp_Datime).Convert()-1.0+76952.2, intL)
        intL +=507.328
        intLUMI.SetPoint(intLUMI.GetN(), (tmp_Datime).Convert()+76952.2, intL)
        tmp_Datime_str = "2016-07-19 18:07:00"
        tmp_Datime = TDatime(tmp_Datime_str)
        intLUMI.SetPoint(intLUMI.GetN(), (tmp_Datime).Convert()-1.0+98573.7, intL)
        intL +=605.228
        intLUMI.SetPoint(intLUMI.GetN(), (tmp_Datime).Convert()+98573.7, intL)
        tmp_Datime_str = "2016-07-21 02:23:00"
        tmp_Datime = TDatime(tmp_Datime_str)
        intLUMI.SetPoint(intLUMI.GetN(), (tmp_Datime).Convert()-1.0+66801.8, intL)
        intL +=463.683
        intLUMI.SetPoint(intLUMI.GetN(), (tmp_Datime).Convert()+66801.8, intL)
        tmp_Datime_str = "2016-07-22 00:54:00"
        tmp_Datime = TDatime(tmp_Datime_str)
        intLUMI.SetPoint(intLUMI.GetN(), (tmp_Datime).Convert()-1.0+21908.5, intL)
        intL +=184.633
        intLUMI.SetPoint(intLUMI.GetN(), (tmp_Datime).Convert()+21908.5, intL)
        tmp_Datime_str = "2016-07-22 10:33:00"
        tmp_Datime = TDatime(tmp_Datime_str)
        intLUMI.SetPoint(intLUMI.GetN(), (tmp_Datime).Convert()-1.0+16398.3, intL)
        intL +=139.611
        intLUMI.SetPoint(intLUMI.GetN(), (tmp_Datime).Convert()+16398.3, intL)
        tmp_Datime_str = "2016-07-22 17:54:00"
        tmp_Datime = TDatime(tmp_Datime_str)
        intLUMI.SetPoint(intLUMI.GetN(), (tmp_Datime).Convert()-1.0+60703.9, intL)
        intL +=382.114
        intLUMI.SetPoint(intLUMI.GetN(), (tmp_Datime).Convert()+60703.9, intL)
        tmp_Datime_str = "2016-07-23 13:10:00"
        tmp_Datime = TDatime(tmp_Datime_str)
        intLUMI.SetPoint(intLUMI.GetN(), (tmp_Datime).Convert()-1.0+4134.1, intL)
        intL +=32.611
        intLUMI.SetPoint(intLUMI.GetN(), (tmp_Datime).Convert()+4134.1, intL)
        tmp_Datime_str = "2016-07-23 17:37:00"
        tmp_Datime = TDatime(tmp_Datime_str)
        intLUMI.SetPoint(intLUMI.GetN(), (tmp_Datime).Convert()-1.0+61606, intL)
        intL +=451.951
        intLUMI.SetPoint(intLUMI.GetN(), (tmp_Datime).Convert()+61606, intL)
        tmp_Datime_str = "2016-07-24 13:27:00"
        tmp_Datime = TDatime(tmp_Datime_str)
        intLUMI.SetPoint(intLUMI.GetN(), (tmp_Datime).Convert()-1.0+11054.2, intL)
        intL +=108.519
        intLUMI.SetPoint(intLUMI.GetN(), (tmp_Datime).Convert()+11054.2, intL)
        tmp_Datime_str = "2016-07-25 00:09:00"
        tmp_Datime = TDatime(tmp_Datime_str)
        intLUMI.SetPoint(intLUMI.GetN(), (tmp_Datime).Convert()-1.0+16169.3, intL)
        intL +=152.84
        intLUMI.SetPoint(intLUMI.GetN(), (tmp_Datime).Convert()+16169.3, intL)
        tmp_Datime_str = "2016-07-25 19:08:00"
        tmp_Datime = TDatime(tmp_Datime_str)
        intLUMI.SetPoint(intLUMI.GetN(), (tmp_Datime).Convert()-1.0+6221.8, intL)
        intL +=61.114
        intLUMI.SetPoint(intLUMI.GetN(), (tmp_Datime).Convert()+6221.8, intL)
        tmp_Datime_str = "2016-08-01 03:16:00"
        tmp_Datime = TDatime(tmp_Datime_str)
        intLUMI.SetPoint(intLUMI.GetN(), (tmp_Datime).Convert()-1.0+4971.1, intL)
        intL +=0.043
        intLUMI.SetPoint(intLUMI.GetN(), (tmp_Datime).Convert()+4971.1, intL)
        tmp_Datime_str = "2016-08-01 12:06:00"
        tmp_Datime = TDatime(tmp_Datime_str)
        intLUMI.SetPoint(intLUMI.GetN(), (tmp_Datime).Convert()-1.0+23748.7, intL)
        intL +=12.941
        intLUMI.SetPoint(intLUMI.GetN(), (tmp_Datime).Convert()+23748.7, intL)
        tmp_Datime_str = "2016-08-01 23:29:00"
        tmp_Datime = TDatime(tmp_Datime_str)
        intLUMI.SetPoint(intLUMI.GetN(), (tmp_Datime).Convert()-1.0+40029.6, intL)
        intL +=336.201
        intLUMI.SetPoint(intLUMI.GetN(), (tmp_Datime).Convert()+40029.6, intL)
        tmp_Datime_str = "2016-08-03 17:41:00"
        tmp_Datime = TDatime(tmp_Datime_str)
        intLUMI.SetPoint(intLUMI.GetN(), (tmp_Datime).Convert()-1.0+53125.7, intL)
        intL +=313.486
        intLUMI.SetPoint(intLUMI.GetN(), (tmp_Datime).Convert()+53125.7, intL)
        tmp_Datime_str = "2016-08-04 11:28:00"
        tmp_Datime = TDatime(tmp_Datime_str)
        intLUMI.SetPoint(intLUMI.GetN(), (tmp_Datime).Convert()-1.0+3762.7, intL)
        intL +=34.332
        intLUMI.SetPoint(intLUMI.GetN(), (tmp_Datime).Convert()+3762.7, intL)
        tmp_Datime_str = "2016-08-04 16:09:00"
        tmp_Datime = TDatime(tmp_Datime_str)
        intLUMI.SetPoint(intLUMI.GetN(), (tmp_Datime).Convert()-1.0+46660.1, intL)
        intL +=324.299
        intLUMI.SetPoint(intLUMI.GetN(), (tmp_Datime).Convert()+46660.1, intL)
        tmp_Datime_str = "2016-08-05 17:35:00"
        tmp_Datime = TDatime(tmp_Datime_str)
        intLUMI.SetPoint(intLUMI.GetN(), (tmp_Datime).Convert()-1.0+3224.3, intL)
        intL +=28.827
        intLUMI.SetPoint(intLUMI.GetN(), (tmp_Datime).Convert()+3224.3, intL)
        tmp_Datime_str = "2016-08-05 20:36:00"
        tmp_Datime = TDatime(tmp_Datime_str)
        intLUMI.SetPoint(intLUMI.GetN(), (tmp_Datime).Convert()-1.0+2343.8, intL)
        intL +=20.633
        intLUMI.SetPoint(intLUMI.GetN(), (tmp_Datime).Convert()+2343.8, intL)
        tmp_Datime_str = "2016-08-06 11:51:00"
        tmp_Datime = TDatime(tmp_Datime_str)
        intLUMI.SetPoint(intLUMI.GetN(), (tmp_Datime).Convert()-1.0+59754.8, intL)
        intL +=401.912
        intLUMI.SetPoint(intLUMI.GetN(), (tmp_Datime).Convert()+59754.8, intL)
        tmp_Datime_str = "2016-08-07 11:19:00"
        tmp_Datime = TDatime(tmp_Datime_str)
        intLUMI.SetPoint(intLUMI.GetN(), (tmp_Datime).Convert()-1.0+16301.2, intL)
        intL +=138.458
        intLUMI.SetPoint(intLUMI.GetN(), (tmp_Datime).Convert()+16301.2, intL)
        tmp_Datime_str = "2016-08-07 23:37:00"
        tmp_Datime = TDatime(tmp_Datime_str)
        intLUMI.SetPoint(intLUMI.GetN(), (tmp_Datime).Convert()-1.0+48256.2, intL)
        intL +=339.504
        intLUMI.SetPoint(intLUMI.GetN(), (tmp_Datime).Convert()+48256.2, intL)
        tmp_Datime_str = "2016-08-08 17:26:00"
        tmp_Datime = TDatime(tmp_Datime_str)
        intLUMI.SetPoint(intLUMI.GetN(), (tmp_Datime).Convert()-1.0+37350.9, intL)
        intL +=288.6
        intLUMI.SetPoint(intLUMI.GetN(), (tmp_Datime).Convert()+37350.9, intL)
        tmp_Datime_str = "2016-08-09 16:47:00"
        tmp_Datime = TDatime(tmp_Datime_str)
        intLUMI.SetPoint(intLUMI.GetN(), (tmp_Datime).Convert()-1.0+34385.9, intL)
        intL +=271.605
        intLUMI.SetPoint(intLUMI.GetN(), (tmp_Datime).Convert()+34385.9, intL)
        tmp_Datime_str = "2016-08-13 06:54:00"
        tmp_Datime = TDatime(tmp_Datime_str)
        intLUMI.SetPoint(intLUMI.GetN(), (tmp_Datime).Convert()-1.0+18949, intL)
        intL +=168.023
        intLUMI.SetPoint(intLUMI.GetN(), (tmp_Datime).Convert()+18949, intL)
        tmp_Datime_str = "2016-08-13 14:50:00"
        tmp_Datime = TDatime(tmp_Datime_str)
        intLUMI.SetPoint(intLUMI.GetN(), (tmp_Datime).Convert()-1.0+58987.6, intL)
        intL +=408.585
        intLUMI.SetPoint(intLUMI.GetN(), (tmp_Datime).Convert()+58987.6, intL)
        tmp_Datime_str = "2016-08-14 10:26:00"
        tmp_Datime = TDatime(tmp_Datime_str)
        intLUMI.SetPoint(intLUMI.GetN(), (tmp_Datime).Convert()-1.0+77312.1, intL)
        intL +=480.86
        intLUMI.SetPoint(intLUMI.GetN(), (tmp_Datime).Convert()+77312.1, intL)
        tmp_Datime_str = "2016-08-15 22:29:00"
        tmp_Datime = TDatime(tmp_Datime_str)
        intLUMI.SetPoint(intLUMI.GetN(), (tmp_Datime).Convert()-1.0+32714.7, intL)
        intL +=208.598
        intLUMI.SetPoint(intLUMI.GetN(), (tmp_Datime).Convert()+32714.7, intL)
        tmp_Datime_str = "2016-08-16 11:13:00"
        tmp_Datime = TDatime(tmp_Datime_str)
        intLUMI.SetPoint(intLUMI.GetN(), (tmp_Datime).Convert()-1.0+9779.9, intL)
        intL +=97.17
        intLUMI.SetPoint(intLUMI.GetN(), (tmp_Datime).Convert()+9779.9, intL)
        tmp_Datime_str = "2016-08-16 21:04:00"
        tmp_Datime = TDatime(tmp_Datime_str)
        intLUMI.SetPoint(intLUMI.GetN(), (tmp_Datime).Convert()-1.0+3685.3, intL)
        intL +=36.878
        intLUMI.SetPoint(intLUMI.GetN(), (tmp_Datime).Convert()+3685.3, intL)
        tmp_Datime_str = "2016-08-17 00:37:00"
        tmp_Datime = TDatime(tmp_Datime_str)
        intLUMI.SetPoint(intLUMI.GetN(), (tmp_Datime).Convert()-1.0+12473.3, intL)
        intL +=114.638
        intLUMI.SetPoint(intLUMI.GetN(), (tmp_Datime).Convert()+12473.3, intL)
        tmp_Datime_str = "2016-08-17 06:41:00"
        tmp_Datime = TDatime(tmp_Datime_str)
        intLUMI.SetPoint(intLUMI.GetN(), (tmp_Datime).Convert()-1.0+53496.2, intL)
        intL +=393.809
        intLUMI.SetPoint(intLUMI.GetN(), (tmp_Datime).Convert()+53496.2, intL)
        tmp_Datime_str = "2016-08-18 22:32:00"
        tmp_Datime = TDatime(tmp_Datime_str)
        intLUMI.SetPoint(intLUMI.GetN(), (tmp_Datime).Convert()-1.0+15456.7, intL)
        intL +=103.648
        intLUMI.SetPoint(intLUMI.GetN(), (tmp_Datime).Convert()+15456.7, intL)
        tmp_Datime_str = "2016-08-19 15:04:00"
        tmp_Datime = TDatime(tmp_Datime_str)
        intLUMI.SetPoint(intLUMI.GetN(), (tmp_Datime).Convert()-1.0+4711.6, intL)
        intL +=26.882
        intLUMI.SetPoint(intLUMI.GetN(), (tmp_Datime).Convert()+4711.6, intL)
        tmp_Datime_str = "2016-08-19 21:26:00"
        tmp_Datime = TDatime(tmp_Datime_str)
        intLUMI.SetPoint(intLUMI.GetN(), (tmp_Datime).Convert()-1.0+4171.2, intL)
        intL +=15.058
        intLUMI.SetPoint(intLUMI.GetN(), (tmp_Datime).Convert()+4171.2, intL)
        tmp_Datime_str = "2016-08-20 22:03:00"
        tmp_Datime = TDatime(tmp_Datime_str)
        intLUMI.SetPoint(intLUMI.GetN(), (tmp_Datime).Convert()-1.0+20574.4, intL)
        intL +=160.656
        intLUMI.SetPoint(intLUMI.GetN(), (tmp_Datime).Convert()+20574.4, intL)
        tmp_Datime_str = "2016-08-24 19:32:00"
        tmp_Datime = TDatime(tmp_Datime_str)
        intLUMI.SetPoint(intLUMI.GetN(), (tmp_Datime).Convert()-1.0+5933.7, intL)
        intL +=0.023
        intLUMI.SetPoint(intLUMI.GetN(), (tmp_Datime).Convert()+5933.7, intL)
        tmp_Datime_str = "2016-08-25 03:56:00"
        tmp_Datime = TDatime(tmp_Datime_str)
        intLUMI.SetPoint(intLUMI.GetN(), (tmp_Datime).Convert()-1.0+11181.8, intL)
        intL +=28.742
        intLUMI.SetPoint(intLUMI.GetN(), (tmp_Datime).Convert()+11181.8, intL)
        tmp_Datime_str = "2016-08-25 19:07:00"
        tmp_Datime = TDatime(tmp_Datime_str)
        intLUMI.SetPoint(intLUMI.GetN(), (tmp_Datime).Convert()-1.0+27407.1, intL)
        intL +=228.453
        intLUMI.SetPoint(intLUMI.GetN(), (tmp_Datime).Convert()+27407.1, intL)
        tmp_Datime_str = "2016-08-26 14:20:00"
        tmp_Datime = TDatime(tmp_Datime_str)
        intLUMI.SetPoint(intLUMI.GetN(), (tmp_Datime).Convert()-1.0+58308.3, intL)
        intL +=414.525
        intLUMI.SetPoint(intLUMI.GetN(), (tmp_Datime).Convert()+58308.3, intL)
        tmp_Datime_str = "2016-08-27 08:23:00"
        tmp_Datime = TDatime(tmp_Datime_str)
        intLUMI.SetPoint(intLUMI.GetN(), (tmp_Datime).Convert()-1.0+23236.5, intL)
        intL +=198.845
        intLUMI.SetPoint(intLUMI.GetN(), (tmp_Datime).Convert()+23236.5, intL)
        tmp_Datime_str = "2016-08-27 22:14:00"
        tmp_Datime = TDatime(tmp_Datime_str)
        intLUMI.SetPoint(intLUMI.GetN(), (tmp_Datime).Convert()-1.0+9334.2, intL)
        intL +=89.473
        intLUMI.SetPoint(intLUMI.GetN(), (tmp_Datime).Convert()+9334.2, intL)
        tmp_Datime_str = "2016-08-28 03:40:00"
        tmp_Datime = TDatime(tmp_Datime_str)
        intLUMI.SetPoint(intLUMI.GetN(), (tmp_Datime).Convert()-1.0+53720.8, intL)
        intL +=400.455
        intLUMI.SetPoint(intLUMI.GetN(), (tmp_Datime).Convert()+53720.8, intL)
        tmp_Datime_str = "2016-08-28 22:19:00"
        tmp_Datime = TDatime(tmp_Datime_str)
        intLUMI.SetPoint(intLUMI.GetN(), (tmp_Datime).Convert()-1.0+54099.9, intL)
        intL +=386.018
        intLUMI.SetPoint(intLUMI.GetN(), (tmp_Datime).Convert()+54099.9, intL)
        tmp_Datime_str = "2016-08-29 20:08:00"
        tmp_Datime = TDatime(tmp_Datime_str)
        intLUMI.SetPoint(intLUMI.GetN(), (tmp_Datime).Convert()-1.0+70673.3, intL)
        intL +=489.768
        intLUMI.SetPoint(intLUMI.GetN(), (tmp_Datime).Convert()+70673.3, intL)
        
        intLUMI.SetPoint(intLUMI.GetN(), (TDatime(2016, 9, 1, 59, 59, 59)).Convert(), intL)
        intLUMI.SetPoint(intLUMI.GetN(), (TDatime(2016, 9, 2, 0, 0, 0)).Convert(), 0)

        print("total integrated Lumi: ", intL)

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
        Leg1.DrawLatex(0.19,0.75, "#scale[1.2]{#sqrt{s}=13 TeV, 2016 data}")

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


        c.Print("ChargeMLaser_Ecells2016.root" )
        c.Print("ChargeMLaser_Ecells2016.png" )
        c.Print("ChargeMLaser_Ecells2016.C" )



        #c.Print("%s/ChargeLaserPlot_Acells2015.root" % (self.dir) )
        #c.Print("%s/ChargeLaserPlot_Acells2015.eps" % (self.dir) )
        #c.Print("%s/ChargeLaserPlot_Acells2015.png" % (self.dir) )
