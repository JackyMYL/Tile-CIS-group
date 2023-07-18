from workers.noise.NoiseWorker import NoiseWorker

class EtaDependence(NoiseWorker):
    '''
    Creates root histograms of the eta-dependence of noise.
    '''

    def __init__(self,parameter='digi',runType='Ped',fromDB=True):
        self.initLog
        self.runType=runType
        self.initNoiseHistFile()
        self.fromDB=fromDB

        self.partStr=['LBA','EBA','LBC','EBC']
        self.sideStr=['A','C']
        self.sampStr=['A','BC','D','E']

        self.parameters=[]
        
        if self.fromDB:
            self.suffix='_db'
        else:
            self.suffix=''

        if parameter == 'digi':
            self.type = 'readout'
            selg.gainStr = ['HG','LG']
            self.parameters = ['hfn'+self.suffix,'lfn'+self.suffix]

        elif parameter == 'cell':
            self.type = 'physical'
            self.gainStr = [""]
            self.parameters = []
            for g in ['LGLG','LGHG','HGLG','HGHG']:
                self.parameters += ['cellnoise'+g+self.suffix]
                if self.fromDB:
                    self.parameters += ['pilenoise'+g+self.suffix]

        self.cellbins =\
                    [['A00','A01','A02','A03','A04','A05','A06','A07','A08','A09','A11','A12','A13','A14','A15',\
                    'BC00','BC01','BC02','BC03','BC04','BC05','BC06','BC07','BC08','D00','D02','D04','D06'],\
                    ['A00','A01','A02','A03','A04','A05','A06','A07','A08','A09','A11','A12','A13','A14','A15',\
                    'BC00','BC01','BC02','BC03','BC04','BC05','BC06','BC07','BC08','D02','D04','D06'],\
                    ['A11','A12','A13','A14','A15','BC09','BC10','BC11','BC12','BC13','BC14','D08','D10','D12','E10','E11','E13','E15'],\
                    ['A11','A12','A13','A14','A15','BC09','BC10','BC11','BC12','BC13','BC14','D08','D10','D12','E10','E11','E13','E15']]

        self.newpowermods = ['EBC_m39','LBC_m36','LBC_m40','LBC_m33','LBA_m47']
        self.newpowermods12 = ['LBA_m03','LBA_m08','LBA_m11','LBA_m15','LBA_m19','LBA_m21','LBA_m25','LBA_m27','LBA_m31','LBA_m36','LBA_m39','LBA_m41','LBA_m49','LBA_m53','LBA_m55','LBA_m57','LBA_m62','LBA_m65','LBC_m03','LBC_m06','LBC_m09','LBC_m13','LBC_m15','LBC_m18','LBC_m20','LBC_m24','LBC_m26','LBC_m29','LBC_m41','LBC_m42','LBC_m43','LBC_m44','LBC_m45','LBC_m46','LBC_m47','LBC_m49','LBC_m52','LBC_m57','LBC_m62','LBC_m63']#,'EBA_m39']

        self.digi12 = ['sA_t08','sA_t07','sBC_t07','sD_t06','sA_t09','sBC_t08']

        self.badcell = 'LBC_m62_sA_t06'

    def ProcessStart(self):
        self.h_EtaDep = {}
        self.h_DataList = {}
        self.h_EtaDepNew = {}
        self.h_EtaDepNew12 = {}
        self.h_EtaDepOld = {}
        self.h_RMS1dim = {}
        self.h_RMS1dimall = {}
        self.h_RMS1dimdig12 = {}
        self.h_DataListNew = {}
        self.h_DataListNew12 = {}
        self.h_DataListOld = {}
        for p in self.parameters:
            self.h_EtaDep[p] = []
            self.h_DataList[p] = []
            self.h_EtaDepNew[p] = []
            self.h_EtaDepNew12[p] = []
            self.h_RMS1dim[p] = ROOT.TH1F('h_'+p+'_RMS1Dim','1 dimensional plot of RMS in changed LVPS',100,0,50)
            self.h_RMS1dimall[p] = ROOT.TH1F('h_'+p+'_RMS1Dimall','1 dimensional plot of RMS',100,0,50)
            self.h_RMS1dimdig12[p] = ROOT.TH1F('h_'+p+'_RMS1dimdig12','1 dimensional plot of RMS in Dig 1 and 2',100,0,50)
            self.h_EtaDepOld[p] = []
            self.h_DataListNew[p] = []
            self.h_DataListNew12[p] = []
            self.h_DataListOld[p] = []

            
           # self.h_RMS1dim.append(ROOT.TH1F('h_'+p+'_RMS1Dim','1 dimensional plot of RMS in changed LVPS',170,0,50))


            #for part in xrange(4):
                #self.h_EtaDep[p].append([])
                #self.h_DataList[p].append([])
                #ncells=len(self.cellbins)
            for side in range(2):
                self.h_EtaDep[p].append([])
                self.h_DataList[p].append([])
                self.h_EtaDepNew[p].append([])
                self.h_EtaDepNew12[p].append([])
                self.h_EtaDepOld[p].append([])
                self.h_DataListNew[p].append([])
                self.h_DataListNew12[p].append([])
                self.h_DataListOld[p].append([])
                for sample in range(4):
                #if self.type == 'readout':
                    #self.h_EtaDep[p][part].append([])
                    #self.h_DataList[p][part].append([])
                    #for dataeta in xrange(2):
                        #self.h_DataList[p][part][sample].append([])
                        #for g in xrange(len(self.gainStr)):
                            #self.h_DataList[p][part][sample][dataeta].append({})

                    #for g in xrange(len(self.gainStr)):
                        #self.h_EtaDep[p][part][sample].append(ROOT.TGraphErrors())                
                        #self.h_EtaDep[p][part][sample][g].SetNameTitle('h_'+p+'_EtaDep_'+self.gainStr[g]+'_'+self.sampStr[sample]+'_'+self.partStr[part],'Eta dependence of noise for '+p+' '+self.gainStr[g]+' '+self.sampStr[sample]+' '+self.partStr[part])


     
                    if self.type == 'physical': 
                        self.h_DataList[p][side].append([])
                        self.h_DataListNew[p][side].append([])
                        self.h_DataListNew12[p][side].append([])
                        self.h_DataListOld[p][side].append([])
                        for dataeta in range(2):
                            self.h_DataList[p][side][sample].append([])
                            self.h_DataListNew[p][side][sample].append([])
                            self.h_DataListNew12[p][side][sample].append([])
                            self.h_DataListOld[p][side][sample].append([])
                            for tower in range(17):
                                self.h_DataList[p][side][sample][dataeta].append([])
                                self.h_DataListNew[p][side][sample][dataeta].append([])
                                self.h_DataListNew12[p][side][sample][dataeta].append([])
                                self.h_DataListOld[p][side][sample][dataeta].append([])
                                        #for mod in xrange(64):
                                            #self.h_DataList[p][side][sample][dataeta][tower].append(0)
                                    #self.h_DataList[p][part][sample][dataeta].append({})
                                    #for mod in xrange(64):
                                    #    self.h_DataList[p][part][sample][dataeta][tower][mod] = []

                        self.h_EtaDep[p][side].append(ROOT.TGraph())
                        self.h_EtaDepNew[p][side].append(ROOT.TGraph())
                        self.h_EtaDepNew12[p][side].append(ROOT.TGraph())
                        self.h_EtaDepOld[p][side].append(ROOT.TGraph())
                        self.h_EtaDep[p][side][sample].SetNameTitle('h_'+p+'_EtaDep_'+self.sampStr[sample]+'_'+self.sideStr[side],'Eta dependence of noise for '+p+' '+self.sampStr[sample]+' '+self.sideStr[side])
                        self.h_EtaDepNew[p][side][sample].SetNameTitle('h_'+p+'_EtaDepNew_'+self.sampStr[sample]+'_'+self.sideStr[side],'Eta dependence of new power noise for '+p+' '+self.sampStr[sample]+' '+self.sideStr[side])
                        self.h_EtaDepNew12[p][side][sample].SetNameTitle('h_'+p+'_EtaDepNew12_'+self.sampStr[sample]+'_'+self.sideStr[side],'Eta depenndence of 2012 new power noise for '+p+' '+self.sampStr[sample]+' '+self.sideStr[side])
                        self.h_EtaDepOld[p][side][sample].SetNameTitle('h_'+p+'_EtaDepOld_'+self.sampStr[sample]+'_'+self.sideStr[side],'Eta dependence of old power noise for '+p+' '+self.sampStr[sample]+' '+self.sideStr[side])

    def ProcessStop(self):
        self.HistFile.cd()
        ROOT.gDirectory.cd("Noise")
        ROOT.gDirectory.mkdir('EtaDep').cd()
        for p in self.parameters:
            self.h_RMS1dim[p].Write()
            self.h_RMS1dimall[p].Write()
            self.h_RMS1dimdig12[p].Write()
            #for part in xrange(4):
            for sample in range(4):
                for side in range(2):
                #if self.type == 'readout':
                    #for g in xrange(len(self.gainStr)):
                        #for h in self.h_EtaDep[p][part][sample][g]:
                            #i=0
                            #for k in self.DataList[p][part][sample][0][g]:
                                #h.SetPoint(i,getMean(self.h_DataList[p][part][sample][1][g]),getMean(self.h_DataList[p][part][sample][0][g]))
                                #h.SetPointError(i,getMean(self.h_DataList[p][part][sample][1][g]),getRMS(self.h_DataList[p][part][sample][0][g]))
                                #i+=1
                            #h.Write()
                                    
                    if self.type == 'physical':
                        h = self.h_EtaDep[p][side][sample]
                        i=0
                        for tower in range(17):
                            if self.h_DataList[p][side][sample][1][tower]:
                            #for k in self.h_DataList[p][part][sample][0][tower].keys():
                                #if sample == 3:
                                    #print "parameter = " , p
                                    #print "tower = " , tower
                                    #print "sample = " , sample
                                    #print "side = " , side
                                    #print "length = " , len(self.h_DataList[p][side][sample][0][tower])
                                    #print "i = " , i
                                    #print "eta = ", getMean(self.h_DataList[p][side][sample][1][tower])
                                    #print getMean(self.h_DataList[p][side][sample][0][tower])
                                h.SetPoint(i,getMean(self.h_DataList[p][side][sample][1][tower]),getMean(self.h_DataList[p][side][sample][0][tower]))
                                #h.SetPointError(i,0,getRMS(self.h_DataList[p][side][sample][0][tower]))
                                i+=1
                        h.Write()

                        newh = self.h_EtaDepNew[p][side][sample]
                        j=0
                        for tower in range(17):
                            if self.h_DataListNew[p][side][sample][1][tower]:
                                #print "parameter = " , p
                                #print "tower = " , tower
                                #print "sample = " , sample
                                #print "side = " , side
                                #print "length = " , len(self.h_DataListNew[p][side][sample][0][tower])
                                #print "j = " , j
                                #print "eta = ", getMean(self.h_DataListNew[p][side][sample][1][tower])
                                #print getMean(self.h_DataListNew[p][side][sample][0][tower])

                                newh.SetPoint(j,getMean(self.h_DataListNew[p][side][sample][1][tower]),getMean(self.h_DataListNew[p][side][sample][0][tower]))
                                j+=1
                        newh.Write()

                        newh12 = self.h_EtaDepNew12[p][side][sample]
                        k=0
                        for tower in range(17):
                            if self.h_DataListNew12[p][side][sample][1][tower]:
                                newh12.SetPoint(k,getMean(self.h_DataListNew12[p][side][sample][1][tower]),getMean(self.h_DataListNew12[p][side][sample][0][tower]))
                                k+=1
                        newh12.Write()

                        oldh = self.h_EtaDepOld[p][side][sample]
                        l=0
                        for tower in range(17):
                            if self.h_DataListOld[p][side][sample][1][tower]:
                                oldh.SetPoint(l,getMean(self.h_DataListOld[p][side][sample][1][tower]),getMean(self.h_DataListOld[p][side][sample][0][tower]))
                                l+=1
                        oldh.Write()
                                

    def ProcessRegion(self, region):
        if len(region.GetEvents()) == 0:
            return
        useRegion = False
        
        sampStr = ['A','BC','D','E']

        if self.type == 'readout' and 'gain' in region.GetHash():
            [part,mod,chan,gain] = region.GetNumber()
            adc = region
            cell = adc.GetParent('physical')
            if 'A' in cell.GetName():
                sample = 0
            if 'BC' in cell.GetName():
                sample = 1
            if 'D' in cell.GetName():
                sample = 2
            if 'E' in cell.GetName():
                sample = 3

            (celleta,cellphi) = cell.GetEtaPhi
            standard_p='ped'

        elif self.type == 'physical' and '_t' in region.GetHash():
            [part,mod,sample,tower] = region.GetNumber()
            (celleta,cellphi) = region.GetEtaPhi()
            if sample == 3:
                if tower == 10:
                    celleta = celleta*1.05
                elif tower == 11:
                    celleta = celleta*1.15
                elif tower == 13:
                    celleta = celleta*1.3
                elif tower == 15:
                    celleta = celleta*1.5

            standard_p = 'cellnoiseHGHG'
            if part == 1 or part == 3:
                side = 0
            else:
                side = 1
        
        else:
            return

        for event in region.GetEvents():
            if event.run.runType != self.runType:
                continue
            if self.type == 'physical':
                for p in self.parameters:
                    if event.data[p]:
                        self.h_DataList[p][side][sample][1][tower].append(celleta)
                        #self.h_DataList[p][part-1][sample][0][tower][mod-1].append(event.data[p])
                        self.h_DataList[p][side][sample][0][tower].append(event.data[p])
                        #self.h_DataList[p][part-1][sample][1][tower][mod-1].append(celleta)    
                        self.h_RMS1dimall[p].Fill(event.data[p])
                        newflag = 0

                        for newpower in self.newpowermods: 
                            if newpower in region.GetHash():
                                #print "parameter: " , p
                                #print "side: " , side
                                #print "sample:" , sample
                                #print "module:" , mod
                                #print "noise:" , event.data[p]
                                self.h_DataListNew[p][side][sample][1][tower].append(celleta)
                                self.h_DataListNew[p][side][sample][0][tower].append(event.data[p])
                                
                                newflag = 1

                        for newpower12 in self.newpowermods12:
                            if newpower12 in region.GetHash():
                                if self.badcell not in region.GetHash():
                                    self.h_DataListNew[p][side][sample][1][tower].append(celleta)
                                    self.h_DataListNew[p][side][sample][0][tower].append(event.data[p])
                                    self.h_DataListNew12[p][side][sample][1][tower].append(celleta)
                                    self.h_DataListNew12[p][side][sample][0][tower].append(event.data[p])
                                    self.h_RMS1dim[p].Fill(event.data[p])
                                    for dig12 in self.digi12:
                                        if dig12 in region.GetHash():
                                            self.h_RMS1dimdig12[p].Fill(event.data[p])



                                if p == 'cellnoiseHGHG':
                                    if event.data[p]>25:
                                        print(region.GetHash())
                                        print("side: " , side)
                                        print("sample: ", sample)
                                        print("module: ", mod)
                                        print("tower: ", tower)
                                        print("noise: ", event.data[p])

                                #This flags as old, since there is a need of doing only older PS.
                                #newflag = 1
                        
                        if not newflag:
                            self.h_DataListOld[p][side][sample][1][tower].append(celleta)
                            self.h_DataListOld[p][side][sample][0][tower].append(event.data[p])

                if self.type == 'readout':
                    for p in self.parameters:
                        self.h_DataList[p][part-1][sample][0][gain][chan].append(event.data[p])
                        self.h_DataList[p][part-1][sample][1][gain][chan].append(event.data[p])
                    

