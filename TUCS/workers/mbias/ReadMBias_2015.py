#
#class to read mbias files
#
#
from xml.dom import minidom
from src.ReadGenericCalibration import *
from src.GenericWorker import *
from src.region import *
from src.run import *
from src.laser.toolbox import *
import random
import time, datetime
import os
from os import listdir
from os.path import isfile, join
from array import *

class ReadMBias_2015(ReadGenericCalibration):
    "read mbias data and print"
   
    doSingleRun = None
   
    #def __init__(self,processingDir='/afs/cern.ch/user/t/tilecali/w0/ntuples/mbias/2016/first_data/', doSingleRun = False, doRatio = False, um = 64, detector_region = None, checkCell=False, detector_side=False, refCell="D5", singleChannel=False):
    def __init__(self,processingDir='/afs/cern.ch/work/t/tilmbias/public/2016/', doSingleRun = False, doRatio = False, modnum = 64, detector_region = None, checkCell=False, detector_side=False, refCell="D6", singleChannel=False):
        # directory where ROOT ntuples are
        self.processingDir  = processingDir
        self.run_dict       = {}
        self.run_list       = []
        self.counter        = 0
        self.doSingleRun    = doSingleRun # if only single run: all PMT info can be stored, but critical for more runs, too much memory umption
        self.doRatio        = doRatio # if all runs, but also ratio A13/D5 is required, special treatment
        self.checkCell      = checkCell # information of whole cell over all modules, A and C-side is stored
        self.part           = None
        self.mod            = None
        self.chan           = None
        self.modnum         = modnum #if doRatio: look at how many modules?
        self.PMTool         = LaserTools()
        self.detector_region = detector_region # only relevant for ratio building
        self.side           = detector_side #A or C side, False means both
        self.refCell        = refCell #only, if ratios are considered
        self.singleChannel  = singleChannel # if ratio: same process, only considering single given channel
       
    def ProcessStart(self):
        print(self.processingDir)
        print(self.detector_region)
           
        onlyfiles = [f for f in listdir(self.processingDir) if isfile(join(self.processingDir,f))]#read all files in directory and put in list 
        useFiles = []
       
        # get files with runNumber in name (without exact date time tag)
        for run in run_list:
            print("Run in run list", run)
            for file in onlyfiles:
                if str(run.runNumber) in file:
                    filename = "%s/%s" % (self.processingDir, file)
                    if "csv" not in filename:
                        useFiles.append(filename)
                        self.run_list.append(run)
                        run.data['filename'] = os.path.basename(filename)
                        self.run_dict[run.runNumber] = []
                        print("filename =", filename)
                    #filename = "%s/%s" % (self.processingDir, file)
                    #useFiles.append(filename)
                    #self.run_list.append(run)
                    #run.data['filename'] = os.path.basename(filename)
                    #self.run_dict[run.runNumber] = []
                    #print "filename =", filename                               
       
       
    def ProcessRegion(self, region):
       
        if not self.detector_region:
            self.detector_region=region.GetHash()
            print(region.GetNumber())
        # copied from ReadLaser.py   
        for event in region.GetEvents():
            if (event.run.runType == 'Las' or event.run.runType == 'Phys') and 'filename' in event.run.data:
                self.run_dict[event.run.runNumber].append(event)
                #print "time", event.run.time
                if len(region.GetNumber())==4:
                    self.part, self.mod, self.chan, dummy = region.GetNumber() # get region coordinates
                if len(region.GetNumber())==3:
                    self.part, self.mod, self.chan        = region.GetNumber() 

                #need to modify partition index for mbias files for 2015 data
                if self.part==1: #LBA is index 2#
                    self.part=2
                elif self.part==2: #LBC is index 3
                    self.part=3
                elif self.part==3: #EBA is index 1
                    self.part=1
                    #EBC is index 3 for both conventions       

#        if not self.part:# temporary fix
#            print self.detector_region
#            part = self.detector_region[0:3]
#            self.mod = int(self.detector_region[5:7])
#            self.chan = int(self.detector_region[9:11])
#            if part == 'EBC': self.part = 4
#            elif part == 'EBA': self.part = 1
#            elif part == 'LBA': self.part = 2
#            elif part == 'LBC': self.part = 3
           
        return 
                               
                               
    def ProcessStop(self):
        #copied from ReadLaser.py

        xmlGRL = minidom.parse(os.getenv('TUCS')+'data/data16_13TeV.periodAllYear_HEAD_DQDefects-00-02-04_PHYS_StandardGRL_Atlas_Ready_Only_Sep22.xml')

        LBCollList = xmlGRL.getElementsByTagName("LumiBlockCollection")

        for run in sorted(self.run_list, key=lambda run: run.runNumber):
            f, t = self.getFileTree(run.data['filename'], 'CurrentTree')
            print("FileName: ",run.data['filename'])     
            if [f, t] == [None, None]:
                print('Failed for run ',run.runNumber)
                continue

            lumiblock = []
            iscollision = []       
            pmtcurrent = []
            pmtstatus = []
            isgoodPMT = []
           
            LBStart = []
            LBEnd = []
           
            lbRun = False
           
            for LBColl in LBCollList:
                RunNumber = LBColl.getElementsByTagName("Run")[0]
                #print("Run: %s" % (RunNumber.firstChild.data))
                if run.runNumber==int(RunNumber.firstChild.data):
                    lbRun =True
                    lbList = LBColl.getElementsByTagName("LBRange")
                    for lb in lbList:
                        lbStart = lb.getAttribute("Start")     
                        lbEnd   = lb.getAttribute("End")
                        LBStart.append(int(lbStart))
                        LBEnd.append(int(lbEnd)) 
                   
           
            #PMTC = std.vector(std.vector(std.vector('float')))()
            #PMTCurrent = numpy.empty((4,64,48),'float')
           
            #t.SetBranchAddress('PMTCurrent', PMTCurrent)
           
            for i in range(t.GetEntries()):
                t.GetEntry(i)
               
                if(t.IsCollision==1):
                       
                    if not lbRun: continue     
                    inLumiRange=False
                    for lb in range(len(LBStart)):     
                        if t.LumiBlock>LBStart[lb] and t.LumiBlock<LBEnd[lb]:
                            inLumiRange =True   
                    if not inLumiRange: continue       
               
                    lumiblock.append(t.LumiBlock)       
                    iscollision.append(t.IsCollision)
                   
                   
                    # only for single runs store whole array, otherwise too memory intensive
                    currentarray = numpy.array(t.PMTCurrent) # test with cesium currents
                    statusarray = numpy.array(t.PMTStatus)
                    isgood = numpy.array(t.IsGood)
                       
                    PMTCurrent = None
                    PMTStatus = None
                    PMTGood = None
                       
                    Current = currentarray.reshape((4,64,48))
                    Status = statusarray.reshape((4,64,48))
                    GoodPMT = isgood.reshape((4,64,48)) 
                   
                    if self.doSingleRun:
                       
                        PMTCurrent = Current
                        PMTStatus = Status
                        PMTGood = GoodPMT

                    # special strorage for ratio plot, has to be made more general in future   
                    elif self.doRatio:
                           
                        #reference cell
                        Part = None
                        PMTch = None
                        ModN = None
                        Tilecal = False
                        #reference cell
                        PartRef = None
                        pmtRef = None 
                        PartMap = {"EBA":0,"LBA":1,"LBC":2,"EBC":3}
                           
                           
                        #now: indices of reference cell specified
                           
                        refReg  = self.PMTool.getRegionName2015(self.refCell, False)
                        PartRef = refReg[0]
                        pmtRef  = refReg[1]

                        if self.detector_region.startswith('TILECAL') or 'm' in self.detector_region:# individual channels
                            if not self.detector_region.startswith('TILECAL'):
                                Part = [PartMap[self.detector_region[0:3]]]
                                ModN = int(self.detector_region[5:7])
                                PMTch = [int(self.detector_region[9:11])-1]
                            else:
                                Part = [PartMap[self.detector_region[8:11]]]
                                ModN = int(self.detector_region[13:15])
                                PMTch = [int(self.detector_region[17:19])-1]
                            Tilecal = True
                            if PartRef[0]==0:##ref:extended barrel
                                if Part[0]==0 or Part[0]==1: PartRef=[0] #probe LBA, EBA
                                if Part[0]==2 or Part[0]==3: PartRef=[3] #probe LBC, EBC                               
                            else:##ref: long barrel
                                if Part[0]==0 or Part[0]==1: PartRef=[1] #probe LBA, EBA
                                if Part[0]==2 or Part[0]==3: PartRef=[2] #probe LBC, EBC
#                           ##ref:LBA,LBC, probe=EBA --> use LBA
#                           if Part[0]==0 and PartRef[0]!=0:
#                               PartRef=[1]
#                           ##ref EBA. EBC, probe==EBA -->use EBA
#                           if Part[0]==0 and PartRef[0]==0:
#                               PartRef=[0]     
#                           ##ref LBA, LBC, probe=EBC -->use LBC
#                           if Part[0]==3 and PartRef[1]!=3:
#                               PartRef=[2]
#                           ##ref  EBA, EBC, probe=EBC --> use EBC
#                           if Part[0]==3 and PartRef[1]==3:
#                               PartRef=[3] #we only check one side in EB
                        else:
                            det_reg = self.PMTool.getRegionName2015(self.detector_region, False)
                            Part = det_reg[0] #long barrel or extended barrel
                            PMTch = det_reg[1] #pmts belonging to cell
                       
                        phiCurrent = []
                        phiStatus = []
                        phiGood = []
                       
                        #if only one side required, only needs to be asked, if cell is given, otherwise, side is already in region name
                        if self.side and not Tilecal:
                            if self.side=='A': 
                                Part = [Part[0]]
                                PartRef = [PartRef[0]]
                            if self.side=='C':
                                Part = [Part[1]]
                                PartRef = [PartRef[1]]
                               
                                                       
                        #need information from all modules
                        #loop over A-side and C-side/or only one side
                        for p in range(len(Part)):
                            if Tilecal:#use only a specific module
                                #if len(PMTch)==1:#cell equipped with only one pmt/or only selected_region specified in script
                                for m in range(self.modnum):
                                    if not self.singleChannel:
                                        if Current[PartRef[0]][ModN][pmtRef[0]]>0. and Current[PartRef[0]][ModN][pmtRef[1]]>0 and Current[Part[p]][ModN][PMTch[0]]>0. and GoodPMT[PartRef[p]][ModN][pmtRef[0]] and GoodPMT[Part[p]][ModN][PMTch[0]] and GoodPMT[PartRef[p]][ModN][pmtRef[1]]:
                                            phiCurrent.append(Current[Part[p]][ModN][PMTch[0]]/(0.5*(Current[PartRef[0]][ModN][pmtRef[0]]+Current[PartRef[0]][ModN][pmtRef[1]])))# current ratio wrt ref cell
                                            phiStatus.append(Status[Part[p]][ModN][PMTch[0]]) #ref cell status (not important)
                                            phiGood.append(GoodPMT[Part[p]][ModN][PMTch[0]])
                                        else:
                                            phiCurrent.append(0.0)
                                            phiStatus.append(0.0)
                                            phiGood.append(0)   
                                        break # we only need to go once in loop
                                    else:# we want to loop for single channel
                                        #print "arelycg: ", Part[p], " ", m, " ", GoodPMT[2][m][26]
                                        #print "arelycg: ", pmtRef[0], ", ", pmtRef[1], ", ", PMTch[0]
                                        #print "         ", Current[PartRef[p]][m][pmtRef[0]], " ", Current[PartRef[p]][m][pmtRef[1]], " ", ent[Part[p]][m][PMTch[0]]
                                        #print "         ", GoodPMT[PartRef[p]][m][pmtRef[0]], " ", GoodPMT[PartRef[p]][m][pmtRef[1]], " ", PMT[Part[p]][m][PMTch[0]]
                                        if Current[PartRef[p]][m][pmtRef[0]]>0. and Current[PartRef[p]][m][pmtRef[1]]>0 and Current[Part[p]][m][PMTch[0]]>0. and GoodPMT[PartRef[p]][m][pmtRef[0]] and GoodPMT[Part[p]][m][PMTch[0]] and GoodPMT[PartRef[p]][m][pmtRef[1]]:
                                            phiCurrent.append(Current[Part[p]][m][PMTch[0]]/(0.5*(Current[PartRef[p]][m][pmtRef[0]]+Current[PartRef[p]][m][pmtRef[1]])))# current ratio wrt ref cell
                                            phiStatus.append(Status[Part[p]][m][PMTch[0]]) #ref cell status (not important)
                                            phiGood.append(GoodPMT[Part[p]][m][PMTch[0]])
                                        else:
                                            phiCurrent.append(0.0)
                                            phiStatus.append(0.0)
                                            phiGood.append(0)
                                       
                                continue # should be ok (len(Part)=1) for Tilecal true ->we should leave the loop here 
                            # loop over modules
                            for m in range(self.modnum):
                                if len(PMTch)==1:#cell equipped with only one pmt/or only selected_region specified in script
                                     if Current[PartRef[p]][m][pmtRef[0]]>0. and Current[Part[p]][m][PMTch[0]]>0.  and Current[PartRef[p]][m][pmtRef[1]]>0 and GoodPMT[PartRef[p]][m][pmtRef[0]] and GoodPMT[Part[p]][m][PMTch[0]] and GoodPMT[PartRef[p]][m][pmtRef[1]]:
                                         phiCurrent.append(Current[Part[p]][m][PMTch[0]]/(0.5*(Current[PartRef[p]][m][pmtRef[0]]+Current[PartRef[p]][m][pmtRef[1]])))# current ratio wrt ref cell
                                         #phiCurrent.append(Current[p][m][PMTch[0]]/Current[p][m][17])
                                         phiStatus.append(Status[PartRef[p]][m][pmtRef[0]]) #D5 status (not important)
                                         phiGood.append(GoodPMT[p][m][16])
                                     else:
                                         phiCurrent.append(0.0)
                                         phiStatus.append(0.0)   
                                         phiGood.append(0) 
                                else:# use both up and down side pmts
                                    if Current[PartRef[p]][m][pmtRef[0]]>0. and Current[Part[p]][m][PMTch[0]]>0. and Current[PartRef[p]][m][pmtRef[1]]>0. and Current[Part[p]][m][PMTch[1]]>0 and GoodPMT[PartRef[p]][m][pmtRef[0]] and GoodPMT[Part[p]][m][PMTch[0]] and GoodPMT[PartRef[p]][m][pmtRef[1]] and GoodPMT[Part[p]][m][PMTch[1]]:
                                        phiCurrent.append((Current[Part[p]][m][PMTch[0]]+Current[Part[p]][m][PMTch[1]])/(Current[PartRef[p]][m][pmtRef[0]]+Current[PartRef[p]][m][pmtRef[1]]))# current ratio wrt ref cell
                                        #print "here"
                                        phiStatus.append(Status[PartRef[p]][m][pmtRef[0]]) #ref cell status (not important)
                                        phiGood.append(GoodPMT[p][m][16])
                                    else:
                                        phiCurrent.append(0.0)
                                        phiStatus.append(0.0)
                                        phiGood.append(0)                               
                           
                        PMTCurrent = phiCurrent
                        PMTStatus = phiStatus
                        PMTGood = phiGood
                           
                        del phiCurrent, phiStatus
                 
                    #store Cell info for all modules and both A and C-side (average over PMTs)
                    elif self.checkCell:
                           
                        Part = None
                        PMTch = None
                           
                        det_reg = self.PMTool.getRegionName2015(self.checkCell, False)
                        Part = det_reg[0] #long barrel or extended barrel
                        PMTch = det_reg[1] #pmts belonging to cell
                       
                        phiCurrent = []
                        phiStatus =  []
                        phiGood = []
                        #need information from all modules
                        #loop over A-side and C-side
                        for p in range(len(Part)):
                            # loop over modules
                            for m in range(self.modnum):
#                               if m==8 or m==9 or m==41 or m==20 or m==28 or m==39: continue   
                                if len(PMTch)==1:#cell equipped with only one pmt/or only selected_region specified in script   
                                     if Current[Part[p]][m][PMTch[0]]>0. and GoodPMT[Part[p]][m][PMTch[0]]:
                                         phiCurrent.append(Current[Part[p]][m][PMTch[0]]) # current of PMT
                                         phiStatus.append(Status[Part[p]][m][PMTch[0]]) #status
                                         phiGood.append(GoodPMT[Part[p]][m][PMTch[0]]) #isGood
                                     else:
                                         phiCurrent.append(0.0)
                                         phiStatus.append(1.0)
                                         phiGood.append(1.0)
                                else:# use both up and down side pmts
                                    if Current[Part[p]][m][PMTch[0]]>0.  and Current[Part[p]][m][PMTch[1]]>0. and GoodPMT[Part[p]][m][PMTch[1]] and GoodPMT[Part[p]][m][PMTch[0]]:
                                        phiCurrent.append(0.5*(Current[Part[p]][m][PMTch[0]]+Current[Part[p]][m][PMTch[1]])) # current of both 
                                        phiStatus.append(Status[Part[p]][m][PMTch[0]]+Status[Part[p]][m][PMTch[1]]) #status
                                        phiGood.append(GoodPMT[Part[p]][m][PMTch[0]]+GoodPMT[Part[p]][m][PMTch[1]]) #status
                                    else:
                                        phiCurrent.append(0.0)
                                        phiStatus.append(1.0)
                                        phiGood.append(1.0)
                           
                        PMTCurrent = phiCurrent
                        PMTStatus = phiStatus
                        PMTGood = phiGood
                           
                        del phiCurrent, phiStatus, phiGood
                                                         
                    elif not self.doSingleRun and not self.doRatio and not self.checkCell:
                           
                        PMTCurrent = Current[self.part-1][self.mod-1][self.chan-1]     
#                        print "current ", PMTCurrent, '---------------------------------------------------------------------------'
                        PMTStatus = Status[self.part-1][self.mod-1][self.chan-1]
                        PMTGood = GoodPMT[self.part-1][self.mod-1][self.chan-1]
                           
                        #if t.LumiBlock==100:
                            #print "PMTCurrent 100", PMTCurrent
                        #if t.LumiBlock==99:
                            #print "PMTCurrent 99", PMTCurrent
       
                        del Current, Status, GoodPMT
                                               
                    pmtcurrent.append(PMTCurrent)
                    pmtstatus.append(PMTStatus)
                    isgoodPMT.append(PMTGood)
                       
                    del PMTCurrent, PMTStatus, currentarray, statusarray, isgood, PMTGood
                               
            run.data['LumiBlock']       = lumiblock     
            run.data['IsCollision']     = iscollision
            run.data['PMTCurrent']      = pmtcurrent
            run.data['PMTStatus']       = pmtstatus
            run.data['IsGood']          = isgoodPMT

            print(list(run.data.keys()))
            print(run.data['PMTCurrent'][:5])
           
            f.Close()
         