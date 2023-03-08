from src.ReadGenericCalibration import ReadGenericCalibration
from workers.noise.NoiseWorker import NoiseWorker
from src.oscalls import *

class ReadPileupNoiseFile(ReadGenericCalibration,NoiseWorker):
    '''
    Class to read pileup noise values from text file.
    File should be of form:
       PartitionName CellName PileupNoise
       Ex: LBA BC00 21.6034
    '''

    def __init__(self,processingDir='/afs/cern.ch/user/t/tilecali/w0/ntuples/ped'):
        if processingDir.endswith('.root'):
            self.processingDir=''
            self.filename = processingDir
        else:
            self.processingDir = processingDir
            self.filename = ''
        self.ftDict = {} # Each element is a [TTree, TFile]
        self.type='physical'
        self.Read2Gaus=True
        self.Make2GausEqual1Gaus=False
        self.SetAllToDummy=False
        self.gainStr = ['LGLG','LGHG','HGLG','HGHG']#,'HG--','--HG']
        self.part2side = [-1,0,1,0,1] # [AUX,LBA,LBC,EBA,EBC]
        self.BadEvents = [] # to store runs missing ntuple
        self.Missing2Gaus = [] # to store runs missing 2 gauss branches
       
    def get_index(self, side, mod, samp, tower, gain):
        return side *64*4*17*6\
            + mod      *4*17*6\
            + samp       *17*6\
            + tower         *6\
            + gain

    def ProcessStart(self):
        self.cellDict = {}

        self.cellDict['LBA']  = {}
        self.cellDict['LBC']  = {}
        self.cellDict['EBA']  = {}
        self.cellDict['EBC']  = {}
        self.cellDict['EBAS'] = {}
        self.cellDict['EBCS'] = {}
        # if special modules are sepcified in input file
        self.useSpecial = False

        inFile = open(os.path.join(getResultDirectory(),'pileup.txt'),'r')
        for line in inFile:
            # Skip comments
            if line[0] == '#': continue
            # split line into list of fields
            lineHash = line.split()
            # skip empty fields
            if len(lineHash) < 3:
                continue
           
            if 'S' in lineHash[0]: self.useSpecial = True
            # Fill dictionary with value
            self.cellDict[lineHash[0]][lineHash[1]] = float(lineHash[2])
                
        
        inFile.close()
        print('Pileup noise read from file')
            
        
    def ProcessStop(self):
        pass
        
    def ProcessRegion(self, region):
        if region.GetEvents() == 0:
            return
        
        if '_t' not in region.GetHash():
            return

        for event in region.GetEvents():
            if event.run.runType != 'Ped':
                continue
            
            hash = region.GetHash()
            [part, module, sample, tower] = region.GetNumber()

            partName = hash[hash.find('B')-1:hash.find('_',hash.find('B'))]

            cellName = hash[hash.find('s')+1:hash.find('_',hash.find('s'))]
            cellName += hash[hash.find('t')+1:]
            
            if partName in list(self.cellDict.keys()):
                if cellName in list(self.cellDict[partName].keys()):
                    #print 'Filling pilenoise for: ', partName,cellName
                    if self.useSpecial and 'EB' in partName and ((module>38 and module<43) or (module>54 and module<59)) and cellName == 'BC09':
                        for g in self.gainStr:
                            event.data['pilenoise'+g+'_db'] = self.cellDict[partName+'S'][cellName]
                    else:
                        for g in self.gainStr:
                            event.data['pilenoise'+g+'_db'] = self.cellDict[partName][cellName]
            else:
                print('WARNING: pileup noise not filled for:',region.GetHash())

            # Propagate db values for update
            dbList = [ d for d in list(event.data.keys()) if '_db' in d ]
            for datum in dbList:
                event.data[datum[:-3]] = event.data[datum]
                    
        
