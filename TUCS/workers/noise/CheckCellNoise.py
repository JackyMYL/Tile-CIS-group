from workers.noise.NoiseWorker import NoiseWorker

import ROOT

class CheckCellNoise(NoiseWorker):
    IndexData = 2
    IndexMC = 3

    def __init__(self, runNumber, runTypeMC, runTypeData, output):
        self.runNumber = runNumber
        self.runTypeMC = runTypeMC
        self.runTypeData = runTypeData
        self.cmpData = {}
        self.badCells = {}
        self.mappingData = {}
        self.adcCmpData = {}
        self.adcVariables = ['hfn', 'lfn']# ['hfn', 'lfn' ,'hfnsigma1', 'hfnsigma2']
        self.mev2adc_normal = 81.83999*0.001050*1.2/(1.14 * sqrt(2.))
        self.mev2adc_E1m = 81.83999*0.001050*1.2/(1.14 * 0.5)
        self.mev2adc_spc = 81.83999*0.001050*1.2/(1.14)
        self.output = output

    def ProcessStart(self):
        pass
        
    def ProcessStop(self):
        histos = {}
        zeros = {}
        missing = {}
        unique_adcs = {}
        for r in self.cmpData:
            ctype = self.cmpData[r][0]
            # Dump cells with at least one bad ADC
            if r in self.badCells:
                cd = self.badCells[r]
                self.output.print_log("CheckCellNoise %s type: %s has %d bad LG %d HG nvars: %d" % (r, ctype, cd['n_bad_adcs_LG'], cd['n_bad_adcs_HG'], len(self.cmpData[r][self.IndexData])))
                for var in self.cmpData[r][self.IndexData]:
                    mcvalue = self.cmpData[r][self.IndexMC][var]
                    dvalue = self.cmpData[r][self.IndexData][var]
                    self.output.print_log("CheckCellNoise   %s: %f %f ratio: %f" % (var, mcvalue, dvalue, (mcvalue/dvalue if dvalue != 0 else 0)))

            ctype = self.cmpData[r][0]
            if not ctype in histos:
                histos[ctype] = {}
                zeros[ctype] = {}
                missing[ctype] = set()
                unique_adcs[ctype] = set()
                self.output.print_log("CheckCellNoise Creating histo %s" % ctype)

            if (len(self.cmpData[r][self.IndexData]) != 6 or len(self.cmpData[r][self.IndexMC]) != 6):
                self.output.print_log("CheckCellNoise Missing %d %d" % (len(self.cmpData[r][self.IndexData]), len(self.cmpData[r][self.IndexMC])))
                missing[ctype].add(r)
            if ctype != '':
                for reg in self.cmpData[r][4]: 
                    unique_adcs[ctype].add(reg)
            for var in self.cmpData[r][self.IndexData]:
                if var in self.cmpData[r][self.IndexMC]:
                    if not var in histos[ctype]:
                        cmax = 400 if 'LG' in var else 10
                        histos[ctype][var] = {'ratio':ROOT.TH1D('ratio_'+ctype+'_'+var, ctype+'_'+var, 100, 0, 4),
                                              'data':ROOT.TH1D('data_'+ctype+'_'+var, ctype+'_'+var, 100, 0, cmax),
                                              'mc':ROOT.TH1D('mc_'+ctype+'_'+var, ctype+'_'+var, 100, 0, cmax)}
                        zeros[ctype][var] = 0
                    if self.cmpData[r][self.IndexData][var] == 0.0 and self.cmpData[r][self.IndexMC][var] == 0.0:
                        zeros[ctype][var] += 1
                    else:
                        mcvalue = self.cmpData[r][self.IndexMC][var]
                        dvalue = self.cmpData[r][self.IndexData][var]
                        if dvalue != 0.0:
                            ratio = mcvalue/dvalue
                            mev2adc = self.mev2adc_normal
                            if ctype in['E1m', 'E']: mev2adc = self.mev2adc_E1m
                            elif ctype != '': mev2adc = self.mev2adc_spc

                            histos[ctype][var]['ratio'].Fill(ratio)
                            histos[ctype][var]['data'].Fill(dvalue * mev2adc)
                            histos[ctype][var]['mc'].Fill(mcvalue * mev2adc)
                            if 'HGHG' in var and ratio < 0.8:
                                self.output.print_log("CheckCellNoise Chan %s with type %s, ratio %f below 0.8 for variable %s" % (r, ctype, ratio, var))
                        else:
                            print("ERROR: data value is 0 for region '%s'" % r)
                            zeros[ctype][var] += 1
                else:
                    self.output.print_log("CheckCellNoise ERROR: variable '%s' not found for region '%s' in MC" % (var, r))
        
        for r in self.cmpData:
            ctype = self.cmpData[r][0]
            adcs = self.cmpData[r][4]
            if 'MBTS' in r and ctype == '':
                print("Reg marked MBTS: %s connected %s" % (r, str(adcs)))
        # ADC data
        adc_histos = {}
        for r in self.adcCmpData:
            datad = self.adcCmpData[r][self.IndexMC]
            if len(datad)==0:
                self.output.print_log("CheckCellNoise ERROR No data for '%s'" % r)
                continue
            ctype = self.adcCmpData[r][0]
            gain = 0 if 'lowgain' in r else 1
            gainstr = 'lowgain' if 'lowgain' in r else 'higain'

            if ctype not in adc_histos:
                adc_histos[ctype] = [{},{}]
            for var in self.adcVariables:
                if var not in adc_histos[ctype][gain]:
                    adc_histos[ctype][gain][var] = ROOT.TH1D('adc_'+ctype+'_'+var+'_'+gainstr, 'adc_'+ctype+'_'+var+'_'+gainstr, 200, 0, 5)
                adc_histos[ctype][gain][var].Fill(datad[var])
        
        # Output
        for ctype in histos:
            for var in histos[ctype]:
                hir = histos[ctype][var]['ratio']
                self.output.print_log("CheckCellNoise %s %s entries: %d zeros: %d adcs: %s ratio mean: %f rms: %f" % (ctype, var, hir.GetEntries(), zeros[ctype][var], len(unique_adcs[ctype]), hir.GetMean(), hir.GetRMS()))
                self.output.add_root_object(hir)
                self.output.add_root_object(histos[ctype][var]['data'])
                self.output.add_root_object(histos[ctype][var]['mc'])
        for ctype in histos:
            for gain in range(0,2):
                gainstr = 'lowgain' if gain==0 else 'higain'
                for var in self.adcVariables:
                    if adc_histos[ctype][gain]:
                        hi = adc_histos[ctype][gain][var]
                        self.output.print_log("CheckCellNoise %s %s %s entries: %d mean: %f rms: %f" % (ctype, var, gainstr, hi.GetEntries(), hi.GetMean(), hi.GetRMS()))
                        self.output.add_root_object(hir)
                    else:
                        self.output.print_log("CheckCellNoise ERROR: var '%s' not found ctype: %s gain: %s" % (var, ctype, gainstr))
  
        for ctype in histos:
            if ctype and len(missing[ctype]):
                self.output.print_log(" CheckCellNoise  Missing in %s : %s" % (ctype, str(missing[ctype])))

        mbtsadcs = set()
        e4padcs =  set()
        e1madcs = set()
        spc10adcs = set()
        Eadcs = set()

        mbtspmts = set()
        e4ppmts =  set()
        e1mpmts = set()
        spc10pmts = set()
        Epmts = set()

        ncell = 0
        mbtscells = set()
        e4pcells = set()
        e1mcells = set()
        spc10cells = set()
        Ecells = set()

        for r in self.mappingData:
            ctype = self.mappingData[r][0]
            if ctype == 'MBTS': 
                mbtspmts.add(self.mappingData[r][1])
                for c in self.mappingData[r][2]: mbtscells.add(c.GetHash())
                for a in self.mappingData[r][3]: mbtsadcs.add(a)
            elif ctype == 'E4\'': 
                e4ppmts.add(self.mappingData[r][1])
                for c in self.mappingData[r][2]: e4pcells.add(c.GetHash())
                for a in self.mappingData[r][3]: e4padcs.add(a)
            elif ctype == 'E1m': 
                e1mpmts.add(self.mappingData[r][1])
                for c in self.mappingData[r][2]: e1mcells.add(c.GetHash())
                for a in self.mappingData[r][3]: e1madcs.add(a)
            elif ctype == 'spC10': 
                spc10pmts.add(self.mappingData[r][1])
                for c in self.mappingData[r][2]: spc10cells.add(c.GetHash())
                for a in self.mappingData[r][3]: spc10adcs.add(a)
            elif ctype == 'E': 
                Epmts.add(self.mappingData[r][1])
                for c in self.mappingData[r][2]: Ecells.add(c.GetHash())
                for a in self.mappingData[r][3]: Eadcs.add(a)
            else: ncell += 1
            
        self.output.print_log("> MBTS")
        self.output.print_log("   %d adcs : %s" % (len(mbtsadcs), ', '.join(a for a in mbtsadcs)))
        self.output.print_log("   %d chans: %s" % (len(mbtspmts), ', '.join(a for a in mbtspmts)))
        self.output.print_log("   %d cells: %s" % (len(mbtscells), ', '.join(a for a in mbtscells)))
        self.output.print_log('')
        self.output.print_log("> E4prime")
        self.output.print_log("   %d adcs : %s" % (len(e4padcs), ', '.join(a for a in e4padcs)))
        self.output.print_log("   %s chans: %s" % (len(e4ppmts), ', '.join(a for a in e4ppmts)))
        self.output.print_log("   %d cells: %s" % (len(e4pcells), ', '.join(a for a in e4pcells)))
        self.output.print_log('')
        self.output.print_log("> E1merged")
        self.output.print_log("   %d adcs : %s" % (len(e1madcs), ', '.join(a for a in e1madcs)))
        self.output.print_log("   %d chans: %s" % (len(e1mpmts), ', '.join(a for a in e1mpmts)))
        self.output.print_log("   %d cells: %s" % (len(e1mcells), ', '.join(a for a in e1mcells)))
        self.output.print_log('')
        self.output.print_log("> spC10")
        self.output.print_log("   %d adcs : %s" % (len(spc10adcs), ', '.join(a for a in spc10adcs)))
        self.output.print_log("   %d chans: %s" % (len(spc10pmts), ', '.join(a for a in spc10pmts)))
        self.output.print_log("   %d cells: %s" % (len(spc10cells), ', '.join(a for a in spc10cells)))
        self.output.print_log("> E")
        self.output.print_log("   %d adcs" % (len(Eadcs)))
        self.output.print_log("   %d chans" % (len(Epmts)))
        self.output.print_log("   %d cells" % (len(Ecells)))


        self.output.print_log("Number of other channels: %d" % ncell)

        for ctype in ['MBTS', 'E4\'', 'E1m', 'spC10', 'E']:
            self.output.print_log(">>> %s" % ctype)
            for r in self.mappingData:
                if self.mappingData[r][0] == ctype:
                    cells = set(self.mappingData[r][2])
                    if len(cells) != 1:
                        print("ERROR: Multiple mapped cells for %s" % r)
                    cell = cells.pop()
                    self.output.print_log(" %s > %s %s" % (r, cell.GetHash(), str(cell.GetNumber())))
            self.output.print_log('')
        for r in self.mappingData:
                ctype = self.mappingData[r][0]
                if ctype != '':
                    cell = self.mappingData[r][2].pop()
                    print("'%s' : ['%s', '%s', %s], " % (r, ctype, cell.GetHash(), str(cell.GetNumber())))
                
    def ProcessRegion(self, region):
        if len(region.GetEvents()) == 0: return
        if 'gain' not in region.GetHash():
            return
        ctype = self.GetCellTypeForADC(region)

        chan = region.GetParent(type='physical')
        cell = self.GetCellForADC(region, ctype)

        if chan.GetHash() in self.mappingData:
            if ctype != self.mappingData[chan.GetHash()][0] or chan.GetHash(1) != self.mappingData[chan.GetHash()][1]:
                self.output.print_log("CheckCellNoise ERROR: mapping for %s differs, %s %s or %s %s" % (chan.GetHash(), ctype, self.mappingData[chan.GetHash()][0], chan.GetHash(1), self.mappingData[chan.GetHash()][1]))
            self.mappingData[chan.GetHash()][2].add(cell)
            self.mappingData[chan.GetHash()][3].add(region.GetHash())
        else:
            self.mappingData[chan.GetHash()] = [ctype, chan.GetHash(1), set([cell]), set([region.GetHash()])]

        if not cell.GetHash() in self.cmpData:
            # Use cell hash iso ADC hash
            self.cmpData[cell.GetHash()] = [ctype, cell.GetHash(), {}, {}, set()]
        else:
            oldctype = self.cmpData[cell.GetHash()][0]
            if ctype != '' and oldctype == '':
                self.output.print_log("CheckCellNoise Replacing data for cell: %s with type %s" % (cell.GetHash(), ctype))
                self.cmpData[cell.GetHash()] = [ctype, cell.GetHash(), {}, {}, set()]
            elif ctype == '' and oldctype != '':
                self.output.print_log("CheckCellNoise Ignoring data for cell: %s with no type, old type: %s" % (cell.GetHash(), oldctype))
                return
        self.cmpData[cell.GetHash()][4].add(region.GetHash())
        
        for evt in region.GetEvents():
            if (evt.run.runNumber == self.runNumber) and (evt.run.runType in [self.runTypeMC, self.runTypeData]):
                if not region.GetHash() in self.adcCmpData:
                    self.adcCmpData[region.GetHash()] = [ctype, region.GetHash(), {}, {}, set()]
                runTypeADCIdx = self.IndexMC if evt.run.runType == self.runTypeMC else self.IndexData
                for var in self.adcVariables:
                    if var in evt.data:
                        self.adcCmpData[region.GetHash()][runTypeADCIdx][var] = evt.data[var]

                for cell_event in cell.GetEvents():
                    if cell_event.run.runNumber != evt.run.runNumber:
                        continue
                    if cell_event.run.runType != evt.run.runType:
                        continue

                    if 'n_bad_channels' in cell_event.data:
                        if cell_event.data['n_bad_channels'] > 0:
                            self.badCells[cell.GetHash()] = {'n_bad_channels': cell_event.data['n_bad_channels'],
                                                             'n_bad_adcs_LG': cell_event.data['n_bad_adcs_LG'],
                                                             'n_bad_adcs_HG': cell_event.data['n_bad_adcs_HG'] }

                    runTypeIdx = self.IndexMC if cell_event.run.runType == self.runTypeMC else self.IndexData
                    for d in cell_event.data:
                        if 'cellnoise' in d:
                            if d in self.cmpData[cell.GetHash()][runTypeIdx]:
                                if cell_event.data[d] != self.cmpData[cell.GetHash()][runTypeIdx][d]:
                                    self.output.print_log("CheckCellNoise ERROR: value differs for variable %s cell %s, %f != %f" % (cell.GetHash(), d, cell_event.data[d], self.cmpData[cell.GetHash()][runTypeIdx][d]))
                            else:
                                self.cmpData[cell.GetHash()][runTypeIdx][d] = cell_event.data[d]
