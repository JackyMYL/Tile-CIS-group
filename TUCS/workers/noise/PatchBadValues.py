from workers.noise.NoiseWorker import NoiseWorker

class PatchBadValues(NoiseWorker):
    '''
    Patch missing values wih eta-dependent average.  
    standard_p: if this parameter is 0 all parameters at that gain are patched
    '''

    def __init__(self,runType='Ped',type='readout',standard_p='hfnsigma1',useDbValues=False,RUN2=True,maxgain=6,minval=-1e5,maxval=1e5):
        self.initLog()
        self.type = type
        self.runType = runType
        self.standard_p = standard_p
        self.UsePerPartition = False
        self.useDbValues = useDbValues
        self.RegionsToFix = []
        self.partStr=['LBA','LBC','EBA','EBC']
        self.useSpecial = True
        self.RUN2 = RUN2
        self.maxgain = maxgain
        self.minval = minval
        self.maxval = maxval

        self.cellbins =\
                   [['A00','A01','A02','A03','A04','A05','A06','A07','A08','A09',\
                    'BC00','BC01','BC02','BC03','BC04','BC05','BC06','BC07','BC08','D00','D02','D04','D06'],\
                    ['A00','A01','A02','A03','A04','A05','A06','A07','A08','A09',\
                    'BC00','BC01','BC02','BC03','BC04','BC05','BC06','BC07','BC08','D02','D04','D06'],\
                    ['A11','A12','A13','A14','A15','BC09','BC10','BC11','BC12','BC13','BC14','D08','D10','D12','E10','E11','E13','E15','spC09','spD08','spE10'],\
                    ['A11','A12','A13','A14','A15','BC09','BC10','BC11','BC12','BC13','BC14','D08','D10','D12','E10','E11','E13','E15','spC09','spD08','spE10']]
        
        self.parameters = []
        if self.type == 'readout':
            self.sampStr =[]
            self.gainStr=['LG','HG']
            self.parameters = ['ped','hfn','lfn','hfnsigma1','hfnsigma2','hfnnorm']
            self.parameters += ['autocorr'+str(x) for x in range(6)]
            if self.standard_p.endswith('_db'):
                self.useDbValues = True
            elif self.useDbValues:
                self.standard_p += '_db'
        elif self.type == 'physical':
            self.sampStr= ['A','BC','D','E','spC','spD','spE']
            self.gainStr= ['LGLG','LGHG','HGLG','HGHG','HG--','--HG'][:self.maxgain]
            self.gainStrE=['LGLG','LGHG','HGLG','HGHG','HG--','--HG'][:self.maxgain]
            if 'HGLG' in self.gainStrE: self.gainStrE.remove('HGLG')
            if '--HG' in self.gainStrE: self.gainStrE.remove('--HG')
            self.parameters = ['cellnoise'+g   for g in self.gainStr]
            self.parameters += ['pilenoise'+g  for g in self.gainStr]
            self.parameters += ['cellsigma1'+g for g in self.gainStr]
            self.parameters += ['cellsigma2'+g for g in self.gainStr]
            self.parameters += ['cellnorm'+g   for g in self.gainStr]
            if self.standard_p.endswith('_db'):
                self.useDbValues = True
                self.standard_p = self.standard_p[:-3]

        if self.useDbValues:
            for i in range(len(self.parameters)):
                self.parameters[i] += '_db'


    def ProcessStart(self):
        # container for regions to be patched
        # use the same container structure for cells and channels
        self.perPartData = {}
        for p in self.parameters:
            self.perPartData[p]=[]
            for part in range(4):
                self.perPartData[p].append([])
                for ch in range(64):
                    self.perPartData[p][part].append([ [] for gain in (1,2) ])

        print("standard_p is set to",self.standard_p,"and useDbValues to",self.useDbValues)
        print("Will check",len(self.gainStr),"gains")
        print("Will patch the following values:")
        print(self.parameters)
        print(" ")


    def ProcessStop(self):

        if self.UsePerPartition:
            print("Now starting with: " ,self.TopRegion.GetHash())
            for region1 in self.TopRegion.GetChildren(self.type):
                for region2 in region1.GetChildren(self.type):
                    for region3 in region2.GetChildren(self.type):
                        for region4 in region3.GetChildren(self.type):
                            self.SetPerPartition(region4,'')
        elif len(self.RegionsToFix)>0:
            for region,gainStr in self.RegionsToFix:
                print("Attempting to patch constants for: ",region.GetHash())
                self.SetPerPartition(region,gainStr)
        print(" ")
                            

    def ProcessRegion(self, region):
        if region.GetHash() == 'TILECAL':
            print("Setting top region to: ", region.GetHash())
            self.TopRegion = region
            
        if len(region.GetEvents()) == 0:
            return
        
        useRegion = False
        if self.type=='readout' and 'gain' in region.GetHash():
            [part, mod, ch, gain] = region.GetNumber()
        elif self.type=='physical' and ('_t' in region.GetHash() or ('MBTS' in region.GetHash() and self.RUN2)):
            [part, mod, sample, tower] = region.GetNumber()
            if self.useSpecial and part>=3:
                nm=region.GetChildren('readout').pop().GetCellName(True)
                if 'MBTS' in region.GetHash() and nm=='E6': # MBTS channel in special C10
                    sample = 4
                    tower = 9
                elif nm=='E5' or nm=='E6' or nm=='E1m' or nm=='E4\'' or nm=='spC10' or \
                    (sample==2 and tower==8  and ((mod>=15 and mod<=18))):
                    sample+=3
                    if tower>10: tower=10
            ch = self.cellbins[part-1].index(self.sampStr[sample]+'%02d' % tower)
            ncells = len(self.cellbins[part-1])
            gain = 0
        else:
            return
        
        suff = '_db' if self.useDbValues else ''
        for event in region.GetEvents():
            if event.run.runType == self.runType:
                for p in self.parameters:
                    try:
                        self.perPartData[p][part-1][ch][gain].append(event.data[p])
                    except KeyError:
                        self.perPartData[p][part-1][ch][gain].append(0.0)

                if self.type=='readout':
                    val=event.data[self.standard_p]
                    if abs(val) < 10e-4 or val<self.minval or val>self.maxval:
                        print("ATTENTION:  PATHCHING",region.GetHash())
                        self.RegionsToFix.append((region,''))
                elif self.type=='physical':
                    if '_sE' in region.GetHash():
                        for gainStr in self.gainStrE:
                            if not self.standard_p+gainStr+suff in event.data:
                                print("Missing var '%s' for E region %s" % (self.standard_p+gainStr+suff, region.GetHash()))
                            else:
                                if abs(event.data[self.standard_p+gainStr+suff]) < 10e-4:
                                    print("ATTENTION:  PATCHING", region.GetHash(),gainStr)
                                    self.RegionsToFix.append((region,gainStr+suff))
                    else:
                        for gainStr in self.gainStr:
                            if not self.standard_p+gainStr+suff in event.data:
                                print("Missing var '%s' for region %s" % (self.standard_p+gainStr+suff, region.GetHash()))
                            else:
                                if abs(event.data[self.standard_p+gainStr+suff]) < 10e-4:
                                    print("ATTENTION:  PATCHING",region.GetHash(),gainStr)
                                    self.RegionsToFix.append((region,gainStr+suff))
    

    def SetPerPartition(self,region,gainStr):
        '''Sets region value to partition-median value of that region'''
        sample=-1
        if self.type=='readout' and 'gain' in region.GetHash():
            [part, mod, ch, gain] = region.GetNumber()
        elif self.type=='physical' and ('_t' in region.GetHash() or ('MBTS' in region.GetHash() and self.RUN2)):
            [part, mod, sample, tower] = region.GetNumber()
            if self.useSpecial and part>=3:
                nm=region.GetChildren('readout').pop().GetCellName(True)
                if 'MBTS' in region.GetHash() and nm=='E6': # MBTS channel in special C10
                    sample = 4
                    tower = 9
                elif nm=='E5' or nm=='E6' or nm=='E1m' or nm=='E4\'' or nm=='spC10' or \
                    (sample==2 and tower==8  and ((mod>=15 and mod<=18))):
                    sample+=3
                    if tower>10: tower=10
            ch = self.cellbins[part-1].index(self.sampStr[sample]+'%02d' % tower)
            ncells = len(self.cellbins[part-1])
            gain = 0
        else:
            return

        for event in region.GetEvents():
            if event.run.runType == self.runType:
                for p in self.parameters:
                    if p in list(event.data.keys()) and gainStr in p:
                        if 'pile' in p and event.data[p]>0.0:
                            print('Do not patch pileup noise, keep ',p,event.data[p])
                        elif sample==4: # single-channel special C10, take noise from another channel
                            p1=p[:-7]+p[-5:-3]+p[-7:-5]+p[-3:] if p.endswith('_db') else p[:-4]+p[-2:]+p[-4:-2]
                            med=getMedian(self.perPartData[p][part-1][ch][gain])
                            if p1!=p and event.data[p1]>0.0 or med==0.0:
                                print('Special C10 - copy from',p1,'to',p,'replacing',event.data[p],'by',event.data[p1])
                                event.data[p] = event.data[p1]
                            else:
                                print('Special C10 - replacing',p,event.data[p],'by',med)
                                event.data[p] = med
                        elif sample!=3 and sample!=6 and 'G' in p:
                            p1=p[:-7]+p[-5:-3]+p[-7:-5]+p[-3:] if p.endswith('_db') else p[:-4]+p[-2:]+p[-4:-2]
                            med=getMedian(self.perPartData[p][part-1][ch][gain])
                            if p1!=p and event.data[p1]>0.0 or med==0.0:
                                print('Cell with one LG masked - copy from',p1,'to',p,'replacing',event.data[p],'by',event.data[p1])
                                event.data[p] = event.data[p1]
                            else:
                                print('Replacing',p,event.data[p],'by',med)
                                event.data[p] = med
                        else:
                            med=getMedian(self.perPartData[p][part-1][ch][gain])
                            print('Replacing',p,event.data[p],'by',med)
                            event.data[p] = med
