from src.ReadGenericCalibration import ReadGenericCalibration
from workers.noise.NoiseWorker import NoiseWorker

class ReadCellNoiseFile(ReadGenericCalibration,NoiseWorker):
    '''
    Reads cell noise values from calibration ntuple (RawCh_NoiseCalib)
    '''

    def __init__(self,runType='Ped',processingDir='', pedNr = '', doOnlineOnly = False, Read2Gaus=True, Make2GausEqual1Gaus=False, verbose=False):
        self.processingDir = '/afs/cern.ch/user/t/tilecali/w0/ntuples/ped'
        self.filename = ''
        if processingDir.endswith('.root'):
            self.filename = processingDir
            if self.filename[0] == "/": self.processingDir=''
        elif len(processingDir)>0:
            self.processingDir = processingDir
        self.runType=runType
        self.pedNr=pedNr
        self.doOnlineOnly=doOnlineOnly
        self.ftDict = {} # Each element is a [TTree, TFile]
        self.type='physical'
        self.Read2Gaus = Read2Gaus
        self.Make2GausEqual1Gaus = Make2GausEqual1Gaus
        self.SetAllToDummy=False
        self.gainStr = ['LGLG','LGHG','HGLG','HGHG','HG--','--HG']
        self.part2side = [-1,0,1,0,1] # [AUX,LBA,LBC,EBA,EBC]
        self.BadEvents = [] # to store runs missing ntuple
        self.Missing2Gaus = [] # to store runs missing 2 gauss branches
        self.verbose = verbose
       
    #cell index
    def get_index(self, side, mod, samp, tower, gain):
        return side *64*4*17*6\
            + mod      *4*17*6\
            + samp       *17*6\
            + tower         *6\
            + gain

    #index for single channel variables
    def get_index_chan(self, part, mod, chan, gain):
        return part   *64*48*2\
            + mod        *48*2\
            + chan          *2\
            + gain

    def addTree(self,runNumber):
            if runNumber in list(self.ftDict.keys()):
                return True
            if self.filename == '':
                print("filename empty")

                if self.pedNr == '':
                    filename = 'RawCh_NoiseCalib_1_%s_%s.root' % (runNumber,'Ped')
                else:
                    filename = 'RawCh_NoiseCalib_Ped.'+str(self.pedNr)+'_tnf1_%s_%s.root' % (runNumber, 'Ped')

                print('Attempting to use file:',filename)
                f, t = self.getFileTree(filename, 'RawCh_NoiseCalib')
                if [f, t] == [None, None]:
                    f, t = self.getFileTree('RawCh_NoiseCalib_%s_%s.root' % (runNumber,'Phys'), 'RawCh_NoiseCalib')
            else:
                print("we have a filename: ", self.filename)
                f, t = self.getFileTree(self.filename, 'RawCh_NoiseCalib')
            if f==None:
                print('File missing for run: ',runNumber)
                print("Removing run from job")
                return False    #Should exit script here
            elif t==None:
                print('Tree missing for run: ',runNumber)
                print("Removing run from job")
                return False
            else:
                print("Opened file: ",f.GetName()) 
                print("Loading run ",runNumber)
                t.SetBranchStatus("*",0)
                t.SetBranchStatus("efixed_rms",1)
                t.SetBranchStatus("ecell_rms",1)
                t.SetBranchStatus("ecell_gsigma1",1)
                t.SetBranchStatus("ecell_gsigma2",1)
                t.SetBranchStatus("ecell_gnorm",1)
                t.GetEntry(0)
                self.ftDict[runNumber] = [f, t]
                return True
            

    def ProcessStart(self):
        if self.Read2Gaus == self.Make2GausEqual1Gaus:
            print("ERROR: Ambigous settings")
            print(" ")
        if self.Make2GausEqual1Gaus:
            print("*************************************")
            print("WARNING: Running in single gaus mode!")
            print("*************************************")
            print(" ")
        
    def ProcessStop(self):
        print(" ")
        
    def ProcessRegion(self, region):
        if len(region.GetEvents()) == 0:
            return

        #Particular case for online single channel noise for folder
        #/TILE/ONL01/NOISE/OFNI
        #
        if self.doOnlineOnly:
            print(region.GetHash())
            for event in region.GetEvents():
                        
                if event.run.runNumber in self.BadEvents or (self.Read2Gaus and event.run.runNumber in self.Missing2Gaus):
                    continue
                if event.run.runType == self.runType:
                    if 'gain' not in region.GetHash():
                        return
                    if not self.addTree(event.run.runNumber):
                        self.BadEvents.append(event.run.runNumber) # file/ttree missing, don't repeat for each run
                        continue
                # Using 2gauss and not in ntuple => skip run
                    elif self.Read2Gaus and not self.ftDict[event.run.runNumber][1].FindBranch('ecell_gsigma1'):
                        print("Missing 2 gauss branches in file for run: ",event.runNumber)
                        print("Removing run from job")
                        self.Missing2Gaus.append(event.run.runNumber)
                        continue

                    self.checkForExistingData(event.data)

                    # Get data from noise tree
                    t = self.ftDict[event.run.runNumber][1]
                    print("t.GetEntries()   = ", t.GetEntries())
                    print("region.GetNumber = ", region.GetNumber())    

                    [part, mod, chan, gain] = region.GetNumber() # Get indices
                    index = self.get_index_chan(part, mod - 1, chan, gain)
                    print(t.efixed_rms[index])
                    event.data['efixed_rms']   =  t.efixed_rms[index]
                        
            return
#####################################


        # only interested in cell level
        if not ('_t' in region.GetHash() or 'MBTS' in region.GetHash()):
        #    for event in region.GetEvents():
        #        if event.runType != 'staging':
        #            newevents.add(event)
        #    region.SetEvents(newevents)
            return
   
        for event in region.GetEvents():
            if event.run.runNumber in self.BadEvents or (self.Read2Gaus and event.run.runNumber in self.Missing2Gaus):
                continue
            if event.run.runType == self.runType:
                if not self.addTree(event.run.runNumber):
                    self.BadEvents.append(event.run.runNumber) # file/ttree missing, don't repeat for each run
                    continue
                # Using 2gauss and not in ntuple => skip run
                elif self.Read2Gaus and not self.ftDict[event.run.runNumber][1].FindBranch('ecell_gsigma1'):
                    print("Missing 2 gauss branches in file for run: ",event.runNumber)
                    print("Removing run from job")
                    self.Missing2Gaus.append(event.run.runNumber)
                    continue
                        
                self.checkForExistingData(event.data)
                # Get data from noise tree
                t = self.ftDict[event.run.runNumber][1]
                    
                [part, mod, samp, tower] = region.GetNumber() # Get indices
                # print region.GetHash()
                ngain=len(self.gainStr)
                for gain in range(ngain):
                    
                    index = self.get_index(self.part2side[part], mod - 1, samp, tower, gain)
                    
                    event.data['calibration'] = 0.0

                    if self.SetAllToDummy:
                        event.data['cellnoise'+self.gainStr[gain]]   =  9999.
                        event.data['cellsigma1'+self.gainStr[gain]]  =  9999.
                        event.data['cellsigma2'+self.gainStr[gain]]  =  9999.
                        event.data['cellnorm'+self.gainStr[gain]]    =  9999.
                    else:
                        event.data['cellnoise'+self.gainStr[gain]]   =  t.ecell_rms[index]
                        if self.verbose:
                            print(part, mod, samp, tower, event.data['cellnoise'+self.gainStr[gain]])
                        if self.Read2Gaus:
                            event.data['cellsigma1'+self.gainStr[gain]]  =  t.ecell_gsigma1[index]
                            if (t.ecell_gsigma1[index] <= 5.0 and self.gainStr[gain] == 'HGHG') or \
                               (t.ecell_gsigma1[index] <= 100.0 and self.gainStr[gain] == 'LGLG') :
                                print("ReadCellNoiseFile: Read2Gaus",region.GetHash(),'cellsigma1',self.gainStr[gain],t.ecell_gsigma1[index])
                            event.data['cellsigma2'+self.gainStr[gain]]  =  t.ecell_gsigma2[index]
                            event.data['cellnorm'+self.gainStr[gain]]    =  t.ecell_gnorm[index]
                        elif self.Make2GausEqual1Gaus:
                            event.data['cellsigma1'+self.gainStr[gain]]  =  t.ecell_rms[index]
                            event.data['cellsigma2'+self.gainStr[gain]]  =  t.ecell_rms[index] 
                            event.data['cellnorm'+self.gainStr[gain]]    =  0.

                    dbkey='pilenoise' + self.gainStr[0] + '_db'
                    if dbkey in event.data:
                        event.data['pilenoise' + self.gainStr[gain]] = event.data[dbkey] 
                    else:
                        # print "WARNING: ADC %s has no val: %s" % (region.GetHash(), dbkey)
                        event.data['pilenoise' + self.gainStr[gain]] = 0.0

#                    try:
#                        event.data['pilenoise' + self.gainStr[gain]] = 0. 
#                        event.data['pilenoise' + self.gainStr[gain]] = event.data['pilenoise' + self.gainStr[0] + '_db'] 
#                    except Exception as x:
#                        if self.verbose:
#                            print "ERROR %s Unable to find key '%s' : %s" % (region.GetHash(), 'pilenoise' + self.gainStr[0] + '_db', x)
#                        event.data['pilenoise' + self.gainStr[gain]] = 0.0

                    if self.verbose:
                        print(index/ngain, gain, self.gainStr[gain], \
                            event.data['cellnoise'+self.gainStr[gain]], \
                            event.data['pilenoise' + self.gainStr[gain]], \
                            event.data['cellsigma1'+self.gainStr[gain]], \
                            event.data['cellsigma2'+self.gainStr[gain]], \
                            event.data['cellnorm'+self.gainStr[gain]])

