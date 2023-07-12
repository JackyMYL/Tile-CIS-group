from workers.noise.NoiseWorker import NoiseWorker

class MakeDigi2Gaus(NoiseWorker):
    '''
    Computes 2 Gaussian digital constants
    from 2 Gaussian cell constants.  Relies on data
    from other calibration systems (Cesium, CIS, LASER)
    to derive the conversion factor from MeV to ADC
    '''

    def __init__(self,digiFromDB=True,cellFromDB=True, OFcoeff=1.14, LGscale=1.0, HGscale=1.0, output=None):
        
        # Ensures region loop is over ADCs not cells
        self.type='readout'
        self.OFcoeff = OFcoeff # extra factor from channel noise to digi noise due to optimal filter
        self.LGscale = LGscale
        self.HGscale = HGscale
        self.output = output

        self.m_n_processed_MBTS = 0
        self.m_n_processed_cells = 0
        self.m_n_processed_E4prime = 0
        self.m_n_processed_E1merged = 0
        self.m_n_processed_spc10 = 0
        self.m_n_processed_E = 0
        self.m_n_processed_bad = 0
        self.m_n_processed_doublebad = 0

        # Where to look for the data
        if digiFromDB:  self.digiSuffix = '_db'
        else:           self.digiSuffix = ''
        
        if cellFromDB:  self.cellSuffix = '_db'
        else:           self.cellSuffix = ''
        
        self.output.print_log("MakeDigi2Gaus Digi suffix: %s cell suffix: %s OFcoeff: %f LGscale: %f HGscale: %f" % (self.digiSuffix, self.cellSuffix, self.OFcoeff, self.LGscale, self.HGscale))
        
    def ProcessStart(self):
        pass
        
    def ProcessStop(self):
        totcells = self.m_n_processed_MBTS + self.m_n_processed_cells + self.m_n_processed_E4prime + self.m_n_processed_E1merged + self.m_n_processed_spc10
        self.output.print_log("MakeDigi2Gaus %d processed normal channels" % self.m_n_processed_cells)
        self.output.print_log("MakeDigi2Gaus %d processed MBTS" % self.m_n_processed_MBTS)
        self.output.print_log("MakeDigi2Gaus %d processed E4prime" % self.m_n_processed_E4prime)
        self.output.print_log("MakeDigi2Gaus %d processed E1merged" % self.m_n_processed_E1merged)
        self.output.print_log("MakeDigi2Gaus %d processed special C10" % self.m_n_processed_spc10)
        self.output.print_log("MakeDigi2Gaus %d processed E" % self.m_n_processed_E)
        self.output.print_log("MakeDigi2Gaus %d processed bad channels" % self.m_n_processed_bad)
        self.output.print_log("MakeDigi2Gaus %d processed double bad channels" % self.m_n_processed_doublebad)
        
        self.output.print_log("MakeDigi2Gaus Total %d cells" % totcells)
        print(" ")
        
    def ProcessRegion(self, region):
        if len(region.GetEvents()) == 0: return
        newEvents = set()
        
        if 'gain' not in region.GetHash():
            return

        ctype = self.GetCellTypeForADC(region)
        cell = self.GetCellForADC(region, ctype)

        region_hash = region.GetHash()

        if ctype in ['MBTS', 'E4\'']:
            for adc_event in region.GetEvents():
                if adc_event.run.runType not in ['Ped','all']:
                    continue
                if adc_event.data['special_cell_type'] != ctype:
                    self.output.print_log("MakeDigi2Gaus ERROR: cell type mismatch ADC: %s event: %s" % (ctype, adc_event.data['special_cell_type']))

                isBad = adc_event.data['isStatusBad']
                if ctype == 'MBTS':
                    self.m_n_processed_MBTS += 1
                    if isBad: self.output.print_log("MakeDigi2Gaus ERROR: Bad MBTS channel: %s" % region_hash)
                if ctype == 'E4\'':
                    self.m_n_processed_E4prime += 1
                    if isBad: self.output.print_log("MakeDigi2Gaus ERROR: Bad E4' channel: %s" % region_hash)

                data = {}
                data['ped'] = adc_event.data['ped'+self.digiSuffix]
                data['hfn'] = adc_event.data['hfn'+self.digiSuffix]
                data['lfn'] = adc_event.data['lfn'+self.digiSuffix]
                data['hfnsigma1'] = adc_event.data['hfn'+self.digiSuffix]
                data['hfnsigma2'] = 0.0
                data['hfnnorm']   = 0.0
                for i in range(6):
                    data['autocorr'+str(i)] = adc_event.data['autocorr'+str(i)+self.digiSuffix]
                
                print("MakeDigi2Gaus %s %s : %f" % (region.GetHash(), ctype, data['hfnsigma1']))

                newEvents.add(Event(Run(adc_event.run.runNumber, 'PedUpdate', adc_event.run.time, adc_event.run.data), data))
            for event in newEvents:
                region.AddEvent(event)
        else:
            adc = region
            
            for adc_event in adc.GetEvents():
                if adc_event.run.runType not in ['Ped','all']:
                    continue
                isBad = adc_event.data['isStatusBad']
                data = {}
                data['ped'] = adc_event.data['ped'+self.digiSuffix]
                data['hfn'] = adc_event.data['hfn'+self.digiSuffix]
                data['lfn'] = adc_event.data['lfn'+self.digiSuffix]
                for i in range(6):
                    data['autocorr'+str(i)] = adc_event.data['autocorr'+str(i)+self.digiSuffix]
                
                # Loop over cell data and match run to digi data
                for cell_event in cell.GetEvents():
                    # print "Processing cell: %s in ADC %s run: %d %d" % (cell.GetHash(), adc.GetHash(), cell_event.run.runNumber, adc_event.run.runNumber)
                    if cell_event.run.runNumber != adc_event.run.runNumber:
                        continue

                    if adc_event.data['special_cell_type'] != ctype or ctype != cell_event.data['special_cell_type']:
                        self.output.print_log("MakeDigi2Gaus ERROR: cell type mismatch ADC: %s cell: %s -- adc event: '%s' event: '%s' cell: '%s'" % (adc.GetHash(), cell.GetHash(), ctype, adc_event.data['special_cell_type'], cell_event.data['special_cell_type']))

                    scale = self.OFcoeff
                    sig1Cell = sig2Cell = norm21Cell = 0
                    ###### Do the calculation (derivation from Jana Novakova) #####
                    try:
                        if 'highgain' in adc.GetHash():
                            sig1Cell   = cell_event.data['cellsigma1HGHG'+self.cellSuffix]
                            sig2Cell   = cell_event.data['cellsigma2HGHG'+self.cellSuffix]
                            norm21Cell = cell_event.data['cellnormHGHG'+self.cellSuffix]
                            scale *= self.HGscale
                        else:
                            sig1Cell   = cell_event.data['cellsigma1LGLG'+self.cellSuffix]
                            sig2Cell   = cell_event.data['cellsigma2LGLG'+self.cellSuffix]
                            norm21Cell = cell_event.data['cellnormLGLG'+self.cellSuffix]
                            scale *= self.LGscale
                    except KeyError as ke:
                        self.output.print_log("MakeDigi2Gaus MakeDigi2Gaus Exception for region '%s' : %s" % (region.GetHash(), str(ke)))

                    ADCoverMeV = adc_event.data['f_cis_db']*adc_event.data['f_cesium_db']*adc_event.data['f_laser_db']*adc_event.data['f_emscale_db']
                    # self.output.print_log("MakeDigi2Gaus MakeDigi2Gaus %s cs: %f cis: %f las: %f emscale: %f mev2adc: %f" % (adc.GetHash(), adc_event.data['f_cesium_db'], adc_event.data['f_cis_db'], adc_event.data['f_laser_db'], adc_event.data['f_emscale_db'], ADCoverMeV))
                    if ctype == 'E1m':
                        self.m_n_processed_E1merged += 1
                        scale *= 0.5
                        if isBad: self.output.print_log("MakeDigi2Gaus ERROR: E1merged channel is bad %s" % region_hash)
                    elif ctype == 'E':
                        self.m_n_processed_E += 1
                        if isBad: self.output.print_log("MakeDigi2Gaus ERROR: E channel is bad %s. s1: %f s2: %f n: %f" % (region_hash, sig1Cell, sig2Cell, norm21Cell))
                        scale *= 1.0
                    elif ctype == 'spC10':
                        self.m_n_processed_spc10 += 1
                        if isBad: self.output.print_log("MakeDigi2Gaus ERROR: spC10 channel is bad %s" % region_hash)
                        scale *= 1.0
                    else:
                        gainstr = 'HG' if 'highgain' in adc.GetHash() else 'LG'
                        n_bad_chan = cell_event.data['n_bad_adcs_'+gainstr]
                        if n_bad_chan == 1:
                            self.m_n_processed_bad += 1
                            scale *= 2.0
                            self.output.print_log("MakeDigi2Gaus Single bad ADC %s" % region_hash)
                        elif n_bad_chan == 2:
                            self.m_n_processed_doublebad += 1
                            scale *= sqrt(2)
                            self.output.print_log("MakeDigi2Gaus Double bad ADCs %s" % region_hash)
                        else:
                            self.m_n_processed_cells += 1
                            scale *= sqrt(2)

                    ADCoverMeV = ADCoverMeV/scale
                    data['hfnsigma1'] = sig1Cell*ADCoverMeV
                    data['hfnsigma2'] = sig2Cell*ADCoverMeV
                    data['hfnnorm']   = norm21Cell
                    newEvents.add(Event(Run(adc_event.run.runNumber, 'PedUpdate', adc_event.run.time, adc_event.run.data), data))

            for event in newEvents:
                adc.AddEvent(event)
                
