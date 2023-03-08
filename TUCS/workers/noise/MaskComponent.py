from workers.noise.NoiseWorker import NoiseWorker

class MaskComponent(NoiseWorker):
    '''
    Replaces DB values with very large values.  This is useful
    for masking cells from the topoclustering algorithm by making it
    impossible for them to supply a 4-sigma seed.
    '''

    def __init__(self, parameter='digi',components=['']):
        self.initLog()
        
        self.partStr=['LBA','LBC','EBA','EBC']
        
        self.parameters = []
        if parameter == 'digi':
            self.type = 'readout'
            self.parameters = ['hfn','ped']
            self.gainStr=['LG','HG'] 
        elif parameter == 'chan':
            self.type = 'readout'
            self.parameters = ['efit_mean','eopt_mean']
            self.gainStr=['LG','HG'] 
        elif parameter == 'cell':
            self.type = 'physical'
            self.gainStr = ['']
            self.parameters = ['cellnoise'+g for g in ['LGLG','LGHG','HGLG','HGHG']]
            #self.parameters += ['pilenoise'+g for g in ['LGLG','LGHG','HGLG','HGHG']]
            self.parameters += ['cellsigma1'+g for g in ['LGLG','LGHG','HGLG','HGHG']]
            self.parameters += ['cellsigma2'+g for g in ['LGLG','LGHG','HGLG','HGHG']]
            self.parameters += ['cellnorm'+g for g in ['LGLG','LGHG','HGLG','HGHG']]
        else:
            self.type = type
            if type=='readout': self.gainStr=['LG','HG']
            else: self.gainStr=['']
            self.parameters.append(parameter)
        
        self.components = []
        for c in components:
            if c[0] == 'H':
                self.components.append(ConvertCellHash2TucsHash(int(c[1:])))
            else:
                self.components.append(c)
                
        self.cellbins =\
                   [['A00','A01','A02','A03','A04','A05','A06','A07','A08','A09',\
                    'BC00','BC01','BC02','BC03','BC04','BC05','BC06','BC07','BC08','D00','D02','D04','D06'],\
                    ['A00','A01','A02','A03','A04','A05','A06','A07','A08','A09',\
                    'BC00','BC01','BC02','BC03','BC04','BC05','BC06','BC07','BC08','D02','D04','D06'],\
                    ['A11','A12','A13','A14','A15','BC09','BC10','BC11','BC12','BC13','BC14','D08','D10','D12','E10','E11','E13','E15'],\
                    ['A11','A12','A13','A14','A15','BC09','BC10','BC11','BC12','BC13','BC14','D08','D10','D12','E10','E11','E13','E15']]
        


    def ProcessStart(self):
        pass

    def ProcessStop(self):
        pass
           
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
            
        pedUpdateFound = False
        for event in region.GetEvents():
            if event.run.runType == 'PedUpdate':
                pedUpdateFound = True
            
                for p in self.parameters:
                    for comp in self.components:
                        if comp in region.GetHash():
                            event.data[p] = 9999.
                            break
        
        if not pedUpdateFound:
            dbUpdate = {}
            for event in region.GetEvents():
                for p in self.parameters:
                    dbUpdate[p] = event.data[p+'_db']
                
                    for comp in self.components:
                        if comp in region.GetHash():
                            dbUpdate[p] = 9999.
       
            region.AddEvent(Event('PedUpdate',-1,dbUpdate,0))

