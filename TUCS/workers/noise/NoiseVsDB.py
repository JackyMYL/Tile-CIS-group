from workers.noise.NoiseWorker import NoiseWorker

class NoiseVsDB(NoiseWorker):
    '''
    Takes existing DB values and new calibration input and prepares
    a DB update that can be subsequently written by a Write worker.
    This worker can be used to protect updates from spurious values
    and missing detector components by comparing the new constants to
    the existing DB values.  Also a Kolmogorov-Smirnov test can be used
    to assess whether an update is needed.
    '''

    def __init__(self, parameter='digi',runType='Ped',savePlot=True,updateAll=True,load_autocr=True,RUN2=True):
        self.initLog()
        self.runType = runType
        self.savePlot = savePlot
        if savePlot:
            self.initNoiseHistFile()
        self.warnThresh  = 0.05
        self.errorThresh = 0.10
        self.UpdateTreshold = 2000
        self.doKStest = False
        self.useSpecial = True
        self.RUN2 = RUN2

        #self.updateAll = True
        self.updateAll = updateAll
        if RUN2:
            self.regionList = []; # no special cases for the moment
        else:
            self.regionList = ['EBA_m04_c00','EBA_m13_c00','EBA_m24_c00','EBA_m31_c00','EBA_m36_c00','EBA_m44_c00','EBA_m53_c00','EBA_m61_c00','EBA_m03_c00','EBA_m12_c00','EBA_m23_c00','EBA_m30_c00','EBA_m35_c00','EBA_m45_c00','EBA_m54_c00','EBA_m60_c00','EBC_m05_c00','EBC_m13_c00','EBC_m20_c00','EBC_m28_c00','EBC_m37_c00','EBC_m45_c00','EBC_m55_c00','EBC_m62_c00','EBC_m04_c00','EBC_m12_c00','EBC_m19_c00','EBC_m27_c00','EBC_m36_c00','EBC_m44_c00','EBC_m54_c00','EBC_m61_c00']

        self.partStr=['LBA','LBC','EBA','EBC']
        
        self.parameters = []
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
            self.parameters = ['cellnoise'+g for g in ['LGLG','LGHG','HGLG','HGHG','HG--','--HG']]
            self.parameters += ['pilenoise'+g for g in ['LGLG','LGHG','HGLG','HGHG','HG--','--HG']]
            self.parameters += ['cellsigma1'+g for g in ['LGLG','LGHG','HGLG','HGHG','HG--','--HG']]
            self.parameters += ['cellsigma2'+g for g in ['LGLG','LGHG','HGLG','HGHG','HG--','--HG']]
            self.parameters += ['cellnorm'+g for g in ['LGLG','LGHG','HGLG','HGHG','HG--','--HG']]
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
                    ['A11','A12','A13','A14','A15','BC09','BC10','BC11','BC12','BC13','BC14','D08','D10','D12','E10','E11','E13','E15','spC09','spD08','spE10'],\
                    ['A11','A12','A13','A14','A15','BC09','BC10','BC11','BC12','BC13','BC14','D08','D10','D12','E10','E11','E13','E15','spC09','spD08','spE10']]
        


    def ProcessStart(self):
        self.HistFile.cd()
        ROOT.gDirectory.cd("Noise")
        self.h_hfnFrac = ROOT.TH1F('hfnFrac','hfnFrac',120,-0.1,1.1)
        # Mostly just declaring histograms depending on desired level of detail
        if self.savePlot:
            self.HistFile.cd()
            ROOT.gDirectory.cd("Noise")
            self.h_fracDiff_total = {}
            self.h_fracDiff = {}
            self.h_fracDiffMap = {}
            self.h_diffWarn  = {}
            self.h_diffError = {}
            self.h_runDiffWarn  = {}
            self.h_runDiffError = {}
            self.countWarn  = {}
            self.countError = {}
            if self.type == 'physical':
                self.h_KSvsDB = {}
            for p in self.parameters:
                self.h_fracDiff_total[p] = {}
                self.h_fracDiff[p] = []
                self.h_fracDiffMap[p] = []
                self.h_diffWarn[p] = []
                self.h_diffError[p] = []
                self.h_runDiffWarn[p] = []
                self.h_runDiffError[p] = []
                self.countWarn[p] = 0
                self.countError[p] = 0
                if self.type == 'physical' and 'sigma1' in p:
                    gStr = p[p.find('G')-1:]
                    self.h_KSvsDB[gStr] = {}
                for part in range(4):
                    ncells = len(self.cellbins[part])
                    self.h_fracDiff[p].append([])
                    self.h_fracDiffMap[p].append([])
                    self.h_diffWarn[p].append([])
                    self.h_diffError[p].append([])
                    self.h_runDiffWarn[p].append([])
                    self.h_runDiffError[p].append([])
                    for g in range(len(self.gainStr)):
                        self.h_fracDiff[p][part].append(ROOT.TH1F('h_'+p+'_fracDiff_'+self.gainStr[g]+'_'+self.partStr[part],'Frac Difference from DB for '+p+' '+self.gainStr[g]+' '+self.partStr[part],80,-1,1))
                        self.h_fracDiffMap[p][part].append(ROOT.TH2F('h_'+p+'_fracDiffMap_'+self.gainStr[g]+'_'+self.partStr[part],'Frac Difference from DB for '+p+' '+self.gainStr[g]+' '+self.partStr[part],64,0,64,48,0,48))
                        self.h_diffWarn[p][part].append(ROOT.TH2F('h_'+p+'_diffWarn_'+self.gainStr[g]+'_'+self.partStr[part],'Difference from DB for '+p+' '+self.gainStr[g]+' '+self.partStr[part],64,0,64,48,0,48))
                        self.h_diffError[p][part].append(ROOT.TH2F('h_'+p+'_diffError_'+self.gainStr[g]+'_'+self.partStr[part],'Difference from DB for '+p+' '+self.gainStr[g]+' '+self.partStr[part],64,0,64,48,0,48))
                        self.h_runDiffWarn[p][part].append(ROOT.TH2F('h_'+p+'_runDiffWarn_'+self.gainStr[g]+'_'+self.partStr[part],'Difference from DB (per run) for '+p+' '+self.gainStr[g]+' '+self.partStr[part],64,0,64,48,0,48))
                        self.h_runDiffError[p][part].append(ROOT.TH2F('h_'+p+'_runDiffError_'+self.gainStr[g]+'_'+self.partStr[part],'Difference from DB (per run) for '+p+' '+self.gainStr[g]+' '+self.partStr[part],64,0,64,48,0,48))
                        self.h_fracDiffMap[p][part][g].SetXTitle('Module')
                        self.h_diffWarn[p][part][g].SetXTitle('Module')
                        self.h_diffError[p][part][g].SetXTitle('Module')
                        self.h_runDiffWarn[p][part][g].SetXTitle('Module')
                        self.h_runDiffError[p][part][g].SetXTitle('Module')
                        if self.type == 'readout':
                            self.h_fracDiffMap[p][part][g].SetYTitle('Channel')
                            self.h_diffWarn[p][part][g].SetYTitle('Channel')
                            self.h_diffError[p][part][g].SetYTitle('Channel')
                            self.h_runDiffWarn[p][part][g].SetYTitle('Channel')
                            self.h_runDiffError[p][part][g].SetYTitle('Channel')
                        elif self.type == 'physical':
                            self.h_fracDiffMap[p][part][g].SetYTitle('Cell')
                            self.h_fracDiffMap[p][part][g].GetYaxis().Set(ncells,0,ncells)
                            self.h_diffWarn[p][part][g].SetYTitle('Cell')
                            self.h_diffWarn[p][part][g].GetYaxis().Set(ncells,0,ncells)
                            self.h_diffError[p][part][g].SetYTitle('Cell')
                            self.h_diffError[p][part][g].GetYaxis().Set(ncells,0,ncells)
                            self.h_runDiffWarn[p][part][g].SetYTitle('Cell')
                            self.h_runDiffWarn[p][part][g].GetYaxis().Set(len(self.cellbins[part]),0,len(self.cellbins[part]))
                            self.h_runDiffError[p][part][g].SetYTitle('Cell')
                            self.h_runDiffError[p][part][g].GetYaxis().Set(len(self.cellbins[part]),0,len(self.cellbins[part]))
                            for b in range(len(self.cellbins[part])):
                                self.h_fracDiffMap[p][part][g].GetYaxis().SetBinLabel(b+1,self.cellbins[part][b])
                                self.h_diffWarn[p][part][g].GetYaxis().SetBinLabel(b+1,self.cellbins[part][b])
                                self.h_diffError[p][part][g].GetYaxis().SetBinLabel(b+1,self.cellbins[part][b])
                                self.h_runDiffWarn[p][part][g].GetYaxis().SetBinLabel(b+1,self.cellbins[part][b])
                                self.h_runDiffError[p][part][g].GetYaxis().SetBinLabel(b+1,self.cellbins[part][b])

    def ProcessStop(self):
        hfraction_run = {}
        for p in self.parameters:
            hfraction_run[p] = ROOT.TGraph()
            hfraction_run[p].SetName("h_fracDiffTimeline_"+p)
            rCnt = 0
            for r in list(self.h_fracDiff_total[p].keys()):
                h = self.h_fracDiff_total[p][r] 
                f1 = ROOT.TF1('f1', 'gaus', -0.2, 0.2)
                h.Fit('f1','QR')
                #mean  = f1.GetParameter(1)
                mean = 0.
                #sigma = f1.GetParameter(2)
                sigma= 0.01
                minBin=0
                maxBin=0
                nBins = h.GetNbinsX()
                for b in range(1,nBins+1):
                    if minBin == 0 and h.GetBinCenter(b) > (mean-4*sigma): minBin=b
                    if minBin != 0 and maxBin==0 and h.GetBinCenter(b) > (mean+4*sigma): maxBin=b
                nOutliers = h.Integral(0,minBin)+ h.Integral(maxBin,nBins+1)
                hfraction_run[p].SetPoint(rCnt,r,nOutliers/h.GetEntries())
                rCnt += 1

                self.noiseLog.warn('%s: %i  %i, %f' % (p,r,nOutliers,(nOutliers/h.GetEntries()) ) )
            hfraction_run[p].Write()
                    
        self.HistFile.cd()
        ROOT.gDirectory.cd('/Noise')
        self.h_hfnFrac.Write()
        
        if self.savePlot:
            self.HistFile.cd()
            ROOT.gDirectory.cd('/Noise')
            ROOT.gDirectory.mkdir('Consistency').cd()
            for p in self.parameters:
                for r in list(self.h_fracDiff_total[p].keys()):
                    self.h_fracDiff_total[p][r].Write()
                for part in range(4):
                    for h in self.h_fracDiff[p][part]:
                        h.Write()
                    for h in self.h_fracDiffMap[p][part]:
                        h.Write()
                    for h in self.h_diffWarn[p][part]:
                        h.Write()
                    for h in self.h_diffError[p][part]:
                        h.Write()
                    #for h in self.h_runDiffWarn[p][part]:
                    #    h.Write()
                    #for h in self.h_runDiffError[p][part]:
                    #    h.Write()
            if self.type == 'physical':
                for k in list(self.h_KSvsDB.keys()):
                    for kk in list(self.h_KSvsDB[k].keys()):
                        self.h_KSvsDB[k][kk].Write()
                
                #self.noiseLog.warn('Number of update warnings for %s: %i' % (p,self.countWarn[p]) )
                #self.noiseLog.error('Number of update errors for %s: %i' % (p,self.countError[p]) )
            
    def ProcessRegion(self, region):
        if region.GetHash() == 'TILECAL':
            print("Setting top region to: ", region.GetHash())
            self.TopRegion = region
            
        if len(region.GetEvents()) == 0:
            return

        # parameter that we know is non-zero if region is good
        standard_p=''
        
        useRegion = False
        if self.type=='readout' and 'gain' in region.GetHash():
            standard_p = 'ped'
            [part, mod, ch, gain] = region.GetNumber()
        elif self.type=='physical' and '_t' in region.GetHash():
            standard_p = 'cellnoiseLGLG'
            [part, mod, sample, tower] = region.GetNumber()
            if self.useSpecial and part>=3 and \
               ((sample==1 and tower==9  and ((mod>=39 and mod<=42) or (mod>=55 and mod<=58))) or
                (sample==2 and tower==8  and ((mod>=15 and mod<=18))) or
                (sample==3 and tower==10 and self.RUN2 and
                          ((mod==7 or mod==8 or mod==24 or mod==25 or mod==43 or mod==44 or mod==53 or mod==54) or
                           (part==4 and (mod==28 or mod==29 or mod==31 or mod==32 or mod==34 or mod==35 or mod==37 or mod==38))))):
                sample+=3
            sampStr =['A','BC','D','E','spC','spD','spE']
            ch = self.cellbins[part-1].index(sampStr[sample]+'%02d' % tower)
            ncells = len(self.cellbins[part-1])
            gain = 0
        else:
            return
            
        dbUpdate = {}
        runList = {}
        dataList = {}
        for p in self.parameters:
            runList[p] = []
            dataList[p] = []
            runList[p+'_db'] = []
            dataList[p+'_db'] = []
        
        OutOfReadout = True
        # Get Data for all Ped runs
        for event in region.GetEvents():
            if event.run.runType != self.runType:
                continue
            
            for p in self.parameters:
                runList[p].append(event.run.runNumber)
                #FIXME  fill pileup noise from DB
                # not actually needed, since the same thing is already done in ReadCellNoiseFile.py
                if 'pile' in p:
                    try:
                        event.data[p+'_db']
                    
                        if (event.data[p+'_db']!=0.0): 
                            if (event.data[p] != event.data[p+'_db']):
                                print(p,"pileup fix: replacing",event.data[p],"by",event.data[p+'_db']) 
                            event.data[p] = event.data[p+'_db']

                    except KeyError:
                        print("event.data['"+p+"_db'] not found")
                        event.data[p] = 0.
                        pass

                
                dataList[p].append(event.data[p])
                runList[p+'_db'].append(event.run.runNumber)
                
                try:
                    event.data[p+'_db']
                    
                    dataList[p+'_db'].append(event.data[p+'_db'])

                except KeyError:
                    print("event.data['"+p+"_db'] not found")
                    dataList[p+'_db'].append(0.)
                    pass

            OutOfReadout = (OutOfReadout and (abs(event.data[standard_p]) < 10e-4) )
        
        # Order data by runNumber
        for p in self.parameters:
            if len(runList[p])>0:
                parallelSort(runList[p],dataList[p])
                parallelSort(runList[p+'_db'],dataList[p+'_db'])
            
        
        for p in self.parameters:
            for i in range(len(runList[p])):
                run     = runList[p][i]
                dataVal = dataList[p][i]
                dbVal   = dataList[p+'_db'][i]
                
                
                print(region.GetHash(),p,dbVal,dataVal)
                if abs(dbVal)<10e-4: fracDiff = 1.0
                else: fracDiff = (dataVal-dbVal)/dbVal
                if abs(fracDiff) > 1:
                    fracDiff = fracDiff/abs(fracDiff)

                if self.savePlot:
                    # check if run hist exists, if not create it
                    if run not in list(self.h_fracDiff_total[p].keys()):
                        self.h_fracDiff_total[p][run] = ROOT.TH1F('h_'+p+'_fracDiff_r'+str(run),\
                                'Frac Difference from DB for '+p+' run '+str(run),200,-1,1)
                    self.h_fracDiff_total[p][run].Fill(fracDiff)
                    
                    if  self.doKStest and self.type == 'physical' and 'sigma1' in p:
                        # check if K-S histogram exists for this run
                        gStr = p[p.find('G')-1:]
                        if run not in list(self.h_KSvsDB[gStr].keys()):
                            self.h_KSvsDB[gStr][run] = ROOT.TH1F('h_KSvsDB+_'+gStr+'_r'+str(run),'h_KSvsDB+_'+gStr+'_r'+str(run),5000,0,1)
                        
                        if gStr == 'HGHG' and not OutOfReadout:
                            fitRun = DoubleGaussian("fitRun",dataList['cellsigma1'+gStr][i],dataList['cellnorm'+gStr][i],dataList['cellsigma2'+gStr][i])
                            histRun = ROOT.TH1D("histRun","histRun",10000,-5000,5000)
                            histRun.Add(fitRun)
                            fitDB  = DoubleGaussian("fitDB",dataList['cellsigma1'+gStr+'_db'][i],dataList['cellnorm'+gStr+'_db'][i],dataList['cellsigma2'+gStr+'_db'][i])
                            histDB = ROOT.TH1D("histDB","histDB",10000,-5000,5000)
                            histDB.Add(fitDB)

                            print(region.GetHash(),': ',histRun.KolmogorovTest(histDB))
                            self.h_KSvsDB[gStr][run].Fill(histRun.KolmogorovTest(histDB))
                            del histRun
                            del histDB
                
            # compare list with data
            #i=0
            #for d in data_sub[p]:
            #    if dbVal>10-4:  diff = (1.0*d-dbVal)/dbVal
            #    else: diff = 1000.
            #    if abs(diff) > self.errorThresh:
            #        self.noiseLog.error('%i: %s has %s inconsistent with DB by %.2f%%' % (runList[p][i],region.GetHash(),p,diff*100) )
            #        self.noiseLog.error('DbVal: %f , DataVal: %f' % (1.0*dbVal,1.0*d) )
            #        self.h_runDiffError[p][part-1][gain].Fill(mod-1,ch,1)
            #    elif abs(diff) > self.warnThresh:
            #        self.noiseLog.warn('%i: %s has %s inconsistent with DB by %.2f%%' % (runList[p][i],region.GetHash(),p,diff*100) )
            #        self.noiseLog.warn('DbVal: %f , DataVal: %f' % (1.0*dbVal,1.0*d) )
            #        self.h_runDiffWarn[p][part-1][gain].Fill(mod-1,ch,1)
            #    i += 1

            median = getMedian(dataList[p])
            dbVal = dataList[p+'_db'][-1]
            
            if abs(dbVal)<10e-4: diff = 1.0
            else:         diff = (median-dbVal)/dbVal
           
            if abs(diff) > self.errorThresh:
                #self.noiseLog.error('%s --- %s ---- differs from DB by %.2f%%' % (region.GetHash(),p,diff*100) )
                #self.noiseLog.error('DbVal: %f --- Median DataVal: %f' % (dbVal,median) )
                self.h_diffError[p][part-1][gain].Fill(mod-1,ch,1)
                self.countError[p] += 1
            elif abs(diff) > self.warnThresh:
                #self.noiseLog.warn('%s --- %s ---- differs from DB by %.2f%%' % (region.GetHash(),p,diff*100) )
                #self.noiseLog.warn('DbVal: %f --- Median DataVal: %f' % (dbVal,median) )
                self.h_diffWarn[p][part-1][gain].Fill(mod-1,ch,1)
                self.countWarn[p] += 1

            self.h_fracDiff[p][part-1][gain].Fill(diff)
            tmpRMS=self.h_fracDiff[p][part-1][gain].GetRMS()
            if abs(diff) > (tmpRMS*4) :
                diff = diff/abs(diff) * tmpRMS*4
            self.h_fracDiffMap[p][part-1][gain].Fill(mod-1,ch,diff)
            
            ############## Do the actual update ##################
            #if (self.updateAll or abs(diff) > self.errorThresh) and not OutOfReadout:
            if (self.updateAll or region.GetHash() in self.regionList) and not OutOfReadout:
                dbUpdate[p] = median
            else:
                print("Region: ",region.GetHash()," out of readout; replacing with existing DB value.")
                dbUpdate[p] = dbVal # use existing value
                dbUpdate['_missing'] = True
        
        ## FIXME
        ## FOR MC: look for cells with unbalanced PMTs, fix these cells
        #if '_t' in region.GetHash() and self.FixMissingRegions:
        #    chsHFN = []
        #    for chan in region.GetChildren('readout'):
        #        for adc in chan.GetChildren('readout'):
        #            if 'highgain' in adc.GetHash():
        #                for ev in adc.GetEvents():
        #                    if ev.runType == 'Ped':
        #                        chsHFN.append(ev.data['hfn'])
        #    hfnFrac = 0.
        #    if len(chsHFN) ==2 and abs(chsHFN[0] + chsHFN[1])>0:
        #        hfnFrac = abs(chsHFN[0] - chsHFN[1])/abs(chsHFN[0] + chsHFN[1])
        #    self.h_hfnFrac.Fill(hfnFrac)
        #    if hfnFrac > 0.40:
        #        print 'PMT disparity too high for ',region.GetHash(),': ',hfnFrac,'. Scheduling for patch'
        #        self.RegionsToFix.append(region)

        #if self.FixMissingRegions and OutOfReadout and not region in self.RegionsToFix:
        #    print 'Region ',region.GetHash(),' out of readout, sceduling for patch'
        #    self.RegionsToFix.append(region)
        
        # region.AddEvent(Event('PedUpdate',-1,dbUpdate))
       
        UpdateRun = Run(-1,'PedUpdate',0,dbUpdate)
        region.AddEvent(Event(UpdateRun,dbUpdate))

