from workers.noise.NoiseWorker import NoiseWorker

from ROOT import gROOT,AddressOf
from array import array

class DumpDBtoFile(NoiseWorker):
    """
    Writes DB values to ROOT TTree and save to file.
    Each variable is stored in a single array that is indexed 
    by detector component in the following manner
    For adc's and channels: (partition-1)*64*48*2+(module-1)*48*2+ch*2+gain
    For cells: (partition-1)*64*4*16+(module-1)*4*16+sample*16+tower
    """

    def __init__(self,runNumber,parameter='digi',type='readout',load_autocr=True):

        self.parameters = []
        self.partStr=['LBA','LBC','EBA','EBC']
        self.runNumber = runNumber
        
        if parameter == 'digi':
            self.type = 'readout'
            self.parameters = ['ped','hfn','lfn','hfnsigma1','hfnsigma2','hfnnorm']
            if load_autocr:
                self.parameters += ['autocorr'+str(x) for x in range(6)]

            self.gainStr=['LG','HG'] 
        elif parameter == 'chan':
            self.type = 'readout'
            self.parameters = ['efit_mean','eopt_mean']
            self.gainStr=['LG','HG'] 
        elif parameter == 'cell':
            self.type = 'physical'
            self.gainStr = ['']
            self.parameters = ['cellnoise'+g for g in ['LGLG','LGHG','HGLG','HGHG']]
            self.parameters += ['pilenoise'+g for g in ['LGLG','LGHG','HGLG','HGHG']]
            self.parameters += ['cellsigma1'+g for g in ['LGLG','LGHG','HGLG','HGHG']]
            self.parameters += ['cellsigma2'+g for g in ['LGLG','LGHG','HGLG','HGHG']]
            self.parameters += ['cellnorm'+g for g in ['LGLG','LGHG','HGLG','HGHG']]
        elif parameter == 'onlineADC':
            self.type = 'readout'
            self.parameters += ['noise','pilenoise']
        else:
            self.type = type
            if type=='readout': self.gainStr=['LG','HG']
            else: self.gainStr=['']
            self.parameters.append(parameter)
        
        self.cellbins =\
                   [['A00','A01','A02','A03','A04','A05','A06','A07','A08','A09',\
                    'BC00','BC01','BC02','BC03','BC04','BC05','BC06','BC07','BC08','D00','D02','D04','D06'],\
                    ['A00','A01','A02','A03','A04','A05','A06','A07','A08','A09',\
                    'BC00','BC01','BC02','BC03','BC04','BC05','BC06','BC07','BC08','D02','D04','D06'],\
                    ['A11','A12','A13','A14','A15','BC09','BC10','BC11','BC12','BC13','BC14','D08','D10','D12','E10','E11','E13','E15'],\
                    ['A11','A12','A13','A14','A15','BC09','BC10','BC11','BC12','BC13','BC14','D08','D10','D12','E10','E11','E13','E15']]
   
    def ProcessStart(self):

        self.initNoiseNtupleFile(filename="noise"+str(self.runNumber)+".NTUP.root")
        self.noiseNtupleFile.cd()
        self.dbTree = ROOT.TTree( 'dbTree', 'Tree with DBValues' )
        
        self.dbArray = {}
        self.dbArray['RunNumber'] = array('i',[0])
        self.dbTree.Branch("RunNumber",self.dbArray['RunNumber'],"RunNumber/I")
        
        for p in self.parameters:
            if self.type =='readout':
                maxN = 4*64*48*2
                self.dbArray[p] = array('f',maxN*[-1]) 
                self.dbTree.Branch(p, self.dbArray[p], p+'[%i]/F' % maxN)
            elif self.type == 'physical':
                maxN = 4*64*4*16
                self.dbArray[p] = array('f',maxN*[-1]) 
                self.dbTree.Branch(p, self.dbArray[p], p+'[%i]/F' % maxN)
        if self.type =='readout':
            tmpInt = int(-1)
            self.partArray = array('i',maxN*[tmpInt])
            self.dbTree.Branch('Partition',self.partArray,   'Partition[%i]/I' % maxN)
            self.moduleArray = array('i',maxN*[tmpInt])
            self.dbTree.Branch('Module',   self.moduleArray, 'Module[%i]/I' % maxN)
            self.channelArray = array('i',maxN*[tmpInt])
            self.dbTree.Branch('Channel',   self.channelArray, 'Channel[%i]/I' % maxN)
            self.gainArray = array('i',maxN*[tmpInt])
            self.dbTree.Branch('Gain',   self.gainArray, 'Gain[%i]/I' % maxN)
        elif self.type == 'physical':
            tmpInt = int(-1)
            self.partArray = array('i',maxN*[tmpInt])
            self.dbTree.Branch('Partition',self.partArray,   'Partition[%i]/I' % maxN)
            self.moduleArray = array('i',maxN*[tmpInt])
            self.dbTree.Branch('Module',   self.moduleArray, 'Module[%i]/I' % maxN)
            self.sampleArray = array('i',maxN*[tmpInt])
            self.dbTree.Branch('Sample',   self.sampleArray, 'Sample[%i]/I' % maxN)
            self.towerArray = array('i',maxN*[tmpInt])
            self.dbTree.Branch('Tower',    self.towerArray,  'Tower[%i]/I' % maxN)
            self.hashArray = array('i',maxN*[tmpInt])
            self.dbTree.Branch('CellHash',    self.hashArray,  'CellHash[%i]/I' % maxN)
           
           
    def ProcessStop(self):
        self.noiseNtupleFile.cd()
        self.dbTree.Fill()
        self.dbTree.Write()
        self.noiseNtupleFile.Close()

    def ProcessRegion(self, region):
        if len(region.GetEvents()) == 0:
            return
        useRegion = False
        if self.type=='readout' and 'gain' in region.GetHash():
            [part, mod, ch, gain] = region.GetNumber()
        elif self.type=='physical' and '_t' in region.GetHash():
            [part, mod, sample, tower] = region.GetNumber()
            sampStr =['A','BC','D','E']
            ch = self.cellbins[part-1].index(sampStr[sample]+'%02d' % tower)
            ncells = len(self.cellbins[part-1])
            gain = 0
        else:
            return

        if self.type == 'physical':
            detectorId = 48 # Cool det. ID for TileCal
            cellHash = CaloCondTools.getCellHash(detectorId,part,mod-1,sample,tower)

        for event in region.GetEvents():
            if event.run.runType == 'Ped' and event.run.runNumber == self.runNumber:
            #if event.run.runNumber == self.runNumber:
                self.dbArray['RunNumber'][0] = self.runNumber
                for p in self.parameters:
                    dbVal = event.data[p+'_db']
                    if p == 'cellsigma1HGHG':
                        print(dbVal)
                    if self.type == 'readout':
                        self.partArray[(part-1)*64*48*2+(mod-1)*48*2+ch*2+gain]   = part
                        self.moduleArray[(part-1)*64*48*2+(mod-1)*48*2+ch*2+gain] = mod
                        self.channelArray[(part-1)*64*48*2+(mod-1)*48*2+ch*2+gain]= ch
                        self.gainArray[(part-1)*64*48*2+(mod-1)*48*2+ch*2+gain]   = gain
                        self.dbArray[p][(part-1)*64*48*2+(mod-1)*48*2+ch*2+gain]  = dbVal
                    elif self.type == 'physical':
                        self.partArray[(part-1)*64*4*16+(mod-1)*4*16+sample*16+tower]   = part
                        self.moduleArray[(part-1)*64*4*16+(mod-1)*4*16+sample*16+tower] = mod
                        self.sampleArray[(part-1)*64*4*16+(mod-1)*4*16+sample*16+tower] = sample
                        self.towerArray[(part-1)*64*4*16+(mod-1)*4*16+sample*16+tower]  = tower
                        self.hashArray[(part-1)*64*4*16+(mod-1)*4*16+sample*16+tower]   = cellHash
                        self.dbArray[p][(part-1)*64*4*16+(mod-1)*4*16+sample*16+tower]  = dbVal
                
            else:
                print(event.run.runType)
                print(event.run.runNumber)
