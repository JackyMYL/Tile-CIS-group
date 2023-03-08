from workers.noise.NoiseWorker import NoiseWorker
import pdb

class NoiseStability(NoiseWorker):
    '''
    Makes timeline histograms that can be used to monitor the stability
    of noise constants over time.
    '''

    def __init__(self, parameter='digi',runType='Ped',plotDetail=3,load_autocr=True,fromDB=False):
        self.initLog()
        self.runType = runType
        self.initNoiseHistFile()
        self.plotDetail = plotDetail
        self.warnThresh  = 0.10
        self.errorThresh = 0.20
        self.fromDB = fromDB

        self.partStr=['LBA','LBC','EBA','EBC']
        
        if self.fromDB: 
            self.suffix='_db'
        else:
            self.suffix=''

        self.parameters = []
        if parameter == 'digi':
            self.type = 'readout'
            self.gainStr=['LG','HG'] 
            self.parameters = ['ped'+self.suffix,'hfn'+self.suffix,'lfn'+self.suffix,'hfnsigma1'+self.suffix,'hfnsigma2'+self.suffix,'hfnnorm'+self.suffix]
            if load_autocr:
                self.parameters += ['autocorr'+str(x) for x in range(6)]
        elif parameter == 'chan':
            self.type = 'readout'
            self.gainStr=['LG','HG'] 
            self.parameters = ['efit_mean','eopt_mean']
        elif parameter == 'cell':
            self.type = 'physical'
            self.gainStr = [""]
            self.parameters = ['cellnoise'+g+self.suffix for g in ['LGLG','LGHG','HGLG','HGHG']]
            #self.parameters += ['pilenoise'+g for g in ['LGLG','LGHG','HGLG','HGHG']]
            self.parameters += ['cellsigma1'+g+self.suffix for g in ['LGLG','LGHG','HGLG','HGHG']]
            self.parameters += ['cellsigma2'+g+self.suffix for g in ['LGLG','LGHG','HGLG','HGHG']]
            self.parameters += ['cellnorm'+g+self.suffix for g in ['LGLG','LGHG','HGLG','HGHG']]
        else:
            self.type = type
            if type=='readout': self.gainStr=['LG','HG']
            else: self.gainStr=[""]
            self.parameters.append(parameter)

        self.cellbins =\
                   [['A00','A01','A02','A03','A04','A05','A06','A07','A08','A09',\
                    'BC00','BC01','BC02','BC03','BC04','BC05','BC06','BC07','BC08','D00','D02','D04','D06'],\
                    ['A00','A01','A02','A03','A04','A05','A06','A07','A08','A09',\
                    'BC00','BC01','BC02','BC03','BC04','BC05','BC06','BC07','BC08','D02','D04','D06'],\
                    ['A11','A12','A13','A14','A15','BC09','BC10','BC11','BC12','BC13','BC14','D08','D10','D12','E10','E11','E13','E15'],\
                    ['A11','A12','A13','A14','A15','BC09','BC10','BC11','BC12','BC13','BC14','D08','D10','D12','E10','E11','E13','E15']]


    def ProcessStart(self):

        ncells_LBA = len(self.cellbins[0])
        ncells_LBC = len(self.cellbins[1])
        ncells_E = len(self.cellbins[2])

        self.h_rmsOverMean1dim = {}
        self.h_rmsOverMean = {}
        self.h_rmsOverMedian = {}
        self.h_difference = {}
        self.h_reldifference = {}
        self.h_changefactor = {}
        self.badRegions = 0
        if self.plotDetail > 0:
            self.dataPart = {}
            self.h_timelinePart = {}
            if self.plotDetail > 1:
                self.h_timelineMod = {}
                self.dataMod = {}
                if self.plotDetail > 2:
                    self.h_timelineCh   = {}
                    self.h_timelineCell = {}
        for p in self.parameters:
            self.h_rmsOverMean1dim[p] = []
            self.h_rmsOverMean[p] = []
            self.h_rmsOverMedian[p] = []
            self.h_difference[p] = []
            self.h_reldifference[p] = []
            self.h_changefactor[p] = []
            if self.plotDetail >0:
                self.dataPart[p] = []
                self.h_timelinePart[p] = []
                if self.plotDetail > 1:
                    self.dataMod[p] = []
                    self.h_timelineMod[p] = []
                    if self.plotDetail > 2:
                        self.h_timelineCh[p]   = []
                        self.h_timelineCell[p] = []
            for g in range(len(self.gainStr)):
                
                self.h_rmsOverMean1dim[p].append(ROOT.TH1F('h_'+p+'_rmsOverMean1dim_'+self.gainStr[g],'RMS over mean, 1 dim, for '+p+' '+self.gainStr[g],120,0,1))
                self.h_rmsOverMean1dim[p][g].SetXTitle('RMS by mean')
                if self.type == 'readout':
                    self.h_rmsOverMean1dim[p][g].SetYTitle('Number of Channels')
                elif self.type == 'physical':
                    self.h_rmsOverMean1dim[p][g].SetYTitle('Number of Cells')
            
            for part in range(4):
                self.h_rmsOverMean[p].append([])
                self.h_rmsOverMedian[p].append([])
                self.h_difference[p].append([])
                self.h_reldifference[p].append([])
                self.h_changefactor[p].append([])
                ncells=len(self.cellbins[part])
                for g in range(len(self.gainStr)):
                    self.h_rmsOverMean[p][part].append(ROOT.TH2F('h_'+p+'_rmsOverMean_'+self.gainStr[g]+'_'+self.partStr[part],'RMS over mean for '+p+' '+self.gainStr[g]+' '+self.partStr[part],64,0,64,48,0,48))
                    self.h_rmsOverMean[p][part][g].SetXTitle('Module')
                    if self.type == 'readout':
                        self.h_rmsOverMean[p][part][g].SetYTitle('Channel')
                    elif self.type == 'physical':
                        self.h_rmsOverMean[p][part][g].SetYTitle('Cell')
                        self.h_rmsOverMean[p][part][g].GetYaxis().Set(ncells,0,ncells-1)
                    self.h_rmsOverMedian[p][part].append(ROOT.TH2F('h_'+p+'_rmsOverMedian_'+self.gainStr[g]+'_'+self.partStr[part],'RMS over median for '+p+' '+self.gainStr[g]+' '+self.partStr[part],64,0,64,48,0,48))
                    self.h_rmsOverMedian[p][part][g].SetXTitle('Module')

                    self.h_difference[p][part].append(ROOT.TH2F('h_'+p+'_difference_'+self.gainStr[g]+'_'+self.partStr[part], 'difference for '+p+' '+self.gainStr[g]+' '+self.partStr[part],64,0,64,48,0,48))
                    self.h_difference[p][part][g].SetXTitle('Module')

                    self.h_reldifference[p][part].append(ROOT.TH2F('h_'+p+'_reldifference_'+self.gainStr[g]+'_'+self.partStr[part], 'relative difference for '+p+' '+self.gainStr[g]+' '+self.partStr[part],64,0,64,48,0,48))
                    self.h_reldifference[p][part][g].SetXTitle('Module')
                    self.h_changefactor[p][part].append(ROOT.TH2F('h_'+p+'_changefactor_'+self.gainStr[    g]+'_'+self.partStr[part], 'change factor for '+p+' '+self.gainStr[g]+' '+self.partStr[part],64,0,64,48,0,48))
                    self.h_changefactor[p][part][g].SetXTitle('Module')
                    if self.type == 'readout':
                        self.h_rmsOverMedian[p][part][g].SetYTitle('Channel')
                        self.h_difference[p][part][g].SetYTitle('Channel')
                        self.h_reldifference[p][part][g].SetYTitle('Channel')
                        self.h_changefactor[p][part][g].SetYTitle('Channel')
                    elif self.type == 'physical':
                        self.h_rmsOverMedian[p][part][g].SetYTitle('Cell')
                        self.h_rmsOverMedian[p][part][g].GetYaxis().Set(ncells,0,ncells-1)
                        self.h_difference[p][part][g].SetYTitle('Cell')
                        self.h_difference[p][part][g].GetYaxis().Set(ncells,0,ncells-1)

                        self.h_reldifference[p][part][g].SetYTitle('Cell')
                        self.h_reldifference[p][part][g].GetYaxis().Set(ncells,0,ncells-1)
                        self.h_changefactor[p][part][g].SetYTitle('Cell')
                        self.h_changefactor[p][part][g].GetYaxis().Set(ncells,0,ncells-1)

                if self.plotDetail >0:
                    self.dataPart[p].append([])
                    self.h_timelinePart[p].append([])
                    for g in range(len(self.gainStr)):
                        self.dataPart[p][part].append({})
                        self.h_timelinePart[p][part].append(ROOT.TGraphErrors())
                        self.h_timelinePart[p][part][g].SetNameTitle('h_'+p+'_timeline_'+self.gainStr[g]+'_'+self.partStr[part],'Timeline of '+p+' '+self.gainStr[g]+' '+self.partStr[part])
                    if self.plotDetail >1:
                        for mod in range(64):
                            self.dataMod[p].append([])
                            self.h_timelineMod[p].append([])
                            for g in range(len(self.gainStr)):
                                self.dataMod[p][part*64+mod].append({})
                                self.h_timelineMod[p][part*64+mod].append(ROOT.TGraphErrors())
                                self.h_timelineMod[p][part*64+mod][g].SetNameTitle('h_'+p+'_timeline_'+self.gainStr[g]+'_'+self.partStr[part]+str(mod+1).zfill(2),'Timeline of '+p+' '+self.gainStr[g]+' '+self.partStr[part]+str(mod+1).zfill(2))
                            if self.plotDetail >2:
                                if self.type=='readout':
                                    for ch in range(48):
                                        self.h_timelineCh[p].append([])
                                        for g in range(len(self.gainStr)):
                                            self.h_timelineCh[p][part*64*48+mod*48+ch].append(ROOT.TGraphErrors())
                                            self.h_timelineCh[p][part*64*48+mod*48+ch][g].SetNameTitle('h_'+p+'_timeline_'+self.gainStr[g]+'_'+self.partStr[part]+str(mod+1).zfill(2)+'_ch'+str(ch).zfill(2),'Timeline of '+p+' '+self.gainStr[g]+' '+self.partStr[part]+str(mod+1).zfill(2)+' ch'+str(ch).zfill(2))
                                elif self.type=='physical':
                                    for ch in range(ncells):
                                        self.h_timelineCell[p].append([])
                                        for g in range(len(self.gainStr)):
                                            if part == 0:
                                                myindex = mod*ncells_LBA + ch
                                            elif part ==1:
                                                myindex = 64*ncells_LBA + mod*ncells_LBC+ ch
                                            elif part ==2:
                                                myindex = 64*ncells_LBA + 64*ncells_LBC + mod*ncells_E+ ch
                                            elif part ==3:
                                                myindex = 64*ncells_LBA + 64*ncells_LBC + 64*ncells_E + mod*ncells_E+ ch


                                            self.h_timelineCell[p][myindex].append(ROOT.TGraphErrors())
                                            self.h_timelineCell[p][myindex][g].SetNameTitle('h_'+p+'_timeline_'+self.gainStr[g]+'_'+self.partStr[part]+str(mod+1).zfill(2)+'_cell'+self.cellbins[part][ch],'Timeline of '+p+' '+self.gainStr[g]+' '+self.partStr[part]+str(mod+1).zfill(2)+' cell '+self.cellbins[part][ch])

    def ProcessStop(self):
        print("no of bad regions = " , self.badRegions)
        
        ncells_LBA = len(self.cellbins[0])
        ncells_LBC = len(self.cellbins[1])
        ncells_E = len(self.cellbins[2])

        self.HistFile.cd()
        ROOT.gDirectory.cd("Noise")
        ROOT.gDirectory.mkdir('Stability').cd()
        for p in self.parameters:
            for h in self.h_rmsOverMean1dim[p]:
                h.Write()
            for part in range(4):
                ncells=len(self.cellbins[part])
                for h in self.h_rmsOverMean[p][part]:
                    h.Write()
                for h in self.h_rmsOverMedian[p][part]:
                    h.Write()
                for h in self.h_difference[p][part]:
                    h.Write()
                for h in self.h_reldifference[p][part]:
                    h.Write()
                for h in self.h_changefactor[p][part]:
                    h.Write()
                if self.plotDetail>0:
                    g=0
                    for h in self.h_timelinePart[p][part]:
                        i=0
                        for  k in sorted(self.dataPart[p][part][g].keys()):
                            h.SetPoint(i,k,getMean(self.dataPart[p][part][g][k]))
                            h.SetPointError(i,0,getRMS(self.dataPart[p][part][g][k]))
                            i+=1
                        h.Write()
                        g+=1
                    if self.plotDetail>1:
                        if not ROOT.gDirectory.GetDirectory(self.partStr[part]):
                            ROOT.gDirectory.mkdir(self.partStr[part])
                        ROOT.gDirectory.cd(self.partStr[part])
                        for mod in range(64):
                            g=0
                            for h in self.h_timelineMod[p][part*64+mod]:
                                i=0
                                for  k in list(self.dataMod[p][part*64+mod][g].keys()):
                                    h.SetPoint(i,k,getMean(self.dataMod[p][part*64+mod][g][k]))
                                    h.SetPointError(i,0,getRMS(self.dataMod[p][part*64+mod][g][k]))
                                    i+=1
                                h.Write()
                                g+=1
                            if self.plotDetail>2:
                                modDir = self.partStr[part]+str(mod+1).zfill(2)
                                if not ROOT.gDirectory.GetDirectory(modDir):
                                    ROOT.gDirectory.mkdir(modDir)
                                ROOT.gDirectory.cd(modDir)
                                if self.type=='readout':
                                    for ch in range(48):
                                        for h in self.h_timelineCh[p][part*64*48+mod*48+ch]:
                                            h.Write()
                                elif self.type == 'physical':
                                    for ch in range(ncells):
                                        if part==0:  #LBA, LBC and EBA,C have different lengths
                                            myindex = mod*ncells_LBA + ch
                                        elif part==1:
                                            myindex = 64*ncells_LBA + mod*ncells_LBC + ch

                                        elif part==2:
                                            myindex = 64*ncells_LBA + 64*ncells_LBC + mod*ncells_E + ch
                                        elif part==3:
                                            myindex = 64*ncells_LBA + 64*ncells_LBC+ 64*ncells_E + mod*ncells_E+ ch
                                            
                                        for h in self.h_timelineCell[p][myindex]:
                                                h.Write()
                                ROOT.gDirectory.cd('../') #Exit Chan/Cell dir
                        ROOT.gDirectory.cd('../') # Exit Mod dir
    
    def ProcessRegion(self, region):
        if len(region.GetEvents()) == 0:
            return
        useRegion = False
        if self.type=='readout' and 'gain' in region.GetHash():
            [part, mod, ch, gain] = region.GetNumber()
            standard_p = 'ped' # quantity we know must =0 for bad data
        elif self.type=='physical' and '_t' in region.GetHash():
            [part, mod, sample, tower] = region.GetNumber()
            sampStr =['A','BC','D','E']
            ncells = len(self.cellbins[part-1])
            ch = self.cellbins[part-1].index(sampStr[sample]+'%02d' % tower)
            standard_p = 'cellnoiseHGHG' # quantity we know must =0 for bad data
        else:
            return
        nPoints = {}
        runList = {}
        data = {}

        for p in self.parameters:
            if self.type=='physical':
                gain = 0
            data[p]    = []
            nPoints[p] = 0
            runList[p] = []
        
        for event in region.GetEvents():
            if event.run.runType != self.runType:
                continue
            for p in self.parameters:
                if p == 'cellnoiseHGHG_db' or p == 'cellnoiseHGHG_db':
                    if event.data[p]>9000:
                        continue
                data[p].append(event.data[p]) # Save data
                nPoints[p] += 1 #increment nPoints that have usable data
                runList[p].append(event.run.runNumber)
                if self.plotDetail >0:
                    if not event.run.runNumber in list(self.dataPart[p][part-1][gain].keys()):
                        self.dataPart[p][part-1][gain][event.run.runNumber] = []
                    self.dataPart[p][part-1][gain][event.run.runNumber].append(event.data[p])

                    if self.plotDetail >1:
                        if not event.run.runNumber in list(self.dataMod[p][(part-1)*64+mod-1][gain].keys()):
                            self.dataMod[p][(part-1)*64+mod-1][gain][event.run.runNumber] = []
                        self.dataMod[p][(part-1)*64+mod-1][gain][event.run.runNumber].append(event.data[p])
                        if self.plotDetail >2:
                            if self.type=='readout':
                                self.h_timelineCh[p][(part-1)*64*48+(mod-1)*48+ch][gain].SetPoint(nPoints[p]-1,event.run.runNumber,event.data[p])
                            elif self.type=='physical':
                                self.h_timelineCell[p][(part-1)*64*ncells+(mod-1)*ncells+ch][gain].SetPoint(nPoints[p]-1,event.run.runNumber,event.data[p])
#                                if p == 'cellnoiseHGHG_db':
#                                    if event.data[p]>100:
#                                        print "part",part
#                                        print "mod",mod
#                                        print "tower",tower
#                                        print "sample",sample
#                                        print "run",event.run.runNumber
#                                        print event.data[p]

        # don't go any further if no usable data for region
        #if not useRegion:
        #    return

        nzRegion = True

        for p in self.parameters:
           
            for x in data[p]:
                if x == 0:
                    nzRegion = False

            mean   = float(getMean(data[p]))
            rms    = float(getRMS(data[p]))
            median = float(getMedian(data[p]))
            difference = data[p][-1] - data[p][0]
            if data[p][0] != 0:
                reldifference = difference/(data[p][0])
                changefactor = data[p][-1]/(data[p][0])
            else:
                reldifference = data[p][-1]
                changefactor = 0 # "masking"
#            if reldifference<-0.65: #if we want to ignore some really bad values
#                reldifference = 0

            if mean > 0.: 
                variationMean = rms/mean
            else: 
                variationMean = 1.0
            if median > 0.: variationMedian = rms/median
            else: variationMedian = 1.0

            #if variationMedian > self.errorThresh:
            #    self.noiseLog.error('Stability Error: %s has unstable %s with variation of %f%%' % (region.GetHash(),p,variationMedian*100) )
            #    self.noiseLog.error('Median: %f RMS: %f' % (median, rms))
            #elif variationMedian > self.warnThresh:
            #    self.noiseLog.warn('Stability Warning: %s has unstable %s with variation of %f%%' % (region.GetHash(),p,variationMedian*100) )

            if variationMean>1.0:
                variationMean=1.0
            if variationMedian>1.0:
                variationMedian=1.0
            if variationMean > 1.0:
                self.h_rmsOverMean[p][part-1][gain].Fill(mod-1,ch,1.0)
            else:
                self.h_rmsOverMean[p][part-1][gain].Fill(mod-1,ch,variationMean)
                if nzRegion:
                    self.h_rmsOverMean1dim[p][gain].Fill(variationMean)
                    if p == 'hfn':
                        if variationMean>0.3:
                            print("part ",part)
                            print("mod ",mod)
                            print("chan ",ch)
                            print("gain ",gain)
                            print("value ", variationMean)
                else: 
                    self.badRegions += 1
            if variationMedian > 1.0:
                self.h_rmsOverMedian[p][part-1][gain].Fill(mod-1,ch,1.0)
            else:
                self.h_rmsOverMedian[p][part-1][gain].Fill(mod-1,ch,variationMedian)

            self.h_difference[p][part-1][gain].Fill(mod-1,ch,difference)
            self.h_reldifference[p][part-1][gain].Fill(mod-1,ch,reldifference)
            self.h_changefactor[p][part-1][gain].Fill(mod-1,ch,changefactor)
