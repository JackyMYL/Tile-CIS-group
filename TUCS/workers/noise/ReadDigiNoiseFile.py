from src.ReadGenericCalibration import ReadGenericCalibration
from workers.noise.NoiseWorker import NoiseWorker

class ReadDigiNoiseFile(NoiseWorker,ReadGenericCalibration):
    '''
    Reads digital noise values from calibration ntuple (Digi_NoiseCalib)
    '''

    def __init__(self,processingDir='',load_autocr=True, pedNr=''):
        self.processingDir = '/afs/cern.ch/user/t/tilecali/w0/ntuples/ped'
        self.filename = ''
        if processingDir.endswith('.root'):
            self.filename = processingDir
            if self.filename[0] == "/": self.processingDir=''
        elif len(processingDir)>0:
            self.processingDir = processingDir
        self.ftDict = {} # Each element is a [TTree, TFile]
        self.load_autocr = load_autocr
        self.pedNr=pedNr


    def addTree(self,runNumber):
            if runNumber in list(self.ftDict.keys()):
                return True

            if self.filename == '':
                print("filename empty")

                if self.pedNr == '':
                    filename = 'Digi_NoiseCalib_1_%s_%s.root' % (runNumber,'Ped')
                else:
                    filename = 'Digi_NoiseCalib_Ped.'+str(self.pedNr)+'_tnf1_%s_%s.root' % (runNumber, 'Ped')

                print('Attempting to use file:',filename)
                f, t = self.getFileTree(filename, 'Digi_NoiseCalib')
                if [f, t] == [None, None]:
                    f, t = self.getFileTree('Digi_NoiseCalib_%s_%s.root' % (runNumber,'Phys'), 'Digi_NoiseCalib')
            else:
                print("we have a filename: ", self.filename)
                f, t = self.getFileTree(self.filename, 'Digi_NoiseCalib')
            if f==None:
                print('File missing for run: ',runNumber)
                print("Removing run from job")
                return False
            elif t==None:
                print('Tree missing for run: ',runNumber)
                print("Removing run from job")
                return False
            else:
                print("Opened file: ",f.GetName()) 
                print("Loading run ",runNumber)
                t.SetBranchStatus("*",0)
                t.SetBranchStatus("ped",1)
                t.SetBranchStatus("hfn",1)
                t.SetBranchStatus("lfn",1)
                t.SetBranchStatus("hfnsigma1",1)
                t.SetBranchStatus("hfnsigma2",1)
                t.SetBranchStatus("hfnnorm",1)
                t.SetBranchStatus("auto_corr",1)
                t.GetEntry(0)
                self.ftDict[runNumber] = [f, t]
                return True

    def ProcessStart(self):
        pass
        
    def ProcessStop(self):
        print(" ")
        
    def ProcessRegion(self, region):
        if region.GetEvents() == 0:
            return
        newevents = set()
        # only interested in adc level
        if 'gain' not in region.GetHash():
        #    for event in region.GetEvents():
        #        if event.runType != 'staging':
        #            newevents.add(event)
        #    region.SetEvents(newevents)
            return
        
        # check if Ped event exists (if so, use them). if staging events exist, convert to ped
        for event in region.GetEvents():
            if event.run.runType == 'Ped':
                if self.addTree(event.run.runNumber):
                    newevents.add(event)
            if event.run.runType == 'all':
                if self.addTree(event.run.runNumber):
                    newevents.add(Event('Ped', event.run.runNumber, event.data, event.time))
                
        for event in newevents:
            self.checkForExistingData(event.data)
            # Get indices 
            [part, mod, chan, gain] = region.GetNumber()
            index = self.get_index(region.GetType(),part, mod - 1, chan, gain)
            event.data['calibration'] = 0.0
            # Get data from noise tree
            [f, t] = self.ftDict[event.run.runNumber]
            event.data['ped'] =  t.ped[index]
            event.data['hfn'] =  t.hfn[index]
            event.data['lfn'] =  t.lfn[index]
            
            try:
                event.data['hfnsigma1'] =  t.hfnsigma1[index]
            except AttributeError:
                event.data['hfnsigma1'] =  0.0
            try:
                event.data['hfnsigma2'] =  t.hfnsigma2[index]
            except AttributeError:
                event.data['hfnsigma2'] =  0.0
            try:
                event.data['hfnnorm']   =  t.hfnnorm[index]
            except AttributeError:
                event.data['hfnnorm'] =  0.0
            
            if self.load_autocr:
                for x in range(6):
                    event.data['autocorr'+str(x)] = t.auto_corr[36*index+x]
        region.SetEvents(newevents)
