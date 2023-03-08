from workers.noise.NoiseWorker import NoiseWorker

class CheckSpecialChannels(NoiseWorker):
    '''
    Check cabling for special channels
    '''

    def __init__(self, data = 'DATA', runNumber=1000000000):
        self.runNumber = runNumber
        self.m_special_regions = {}
        if runNumber<222222:
            self.cabling = 'RUN1'
        else:
            if (data == 'MC' and runNumber>=310000) or runNumber>=343000:
                self.cabling = 'RUN2a'
            else:
                self.cabling = 'RUN2'


    def ProcessStart(self):
        pass
        
    def ProcessStop(self):

        regs = {'MBTS': {},
                'E4\'': {},
                'E1m': {},
                'E': {},
                'spC10': {
                'TILECAL_EBA_m39_c05':0,
                'TILECAL_EBA_m40_c05':0,
                'TILECAL_EBA_m41_c05':0,
                'TILECAL_EBA_m42_c05':0,
                'TILECAL_EBA_m55_c05':0,
                'TILECAL_EBA_m56_c05':0,
                'TILECAL_EBA_m57_c05':0,
                'TILECAL_EBA_m58_c05':0,
                'TILECAL_EBC_m39_c05':0,
                'TILECAL_EBC_m40_c05':0,
                'TILECAL_EBC_m41_c05':0,
                'TILECAL_EBC_m42_c05':0,
                'TILECAL_EBC_m55_c05':0,
                'TILECAL_EBC_m56_c05':0,
                'TILECAL_EBC_m57_c05':0,
                'TILECAL_EBC_m58_c05':0
                }
        }

        if self.cabling == 'RUN2' or self.cabling == 'RUN2a':
            regs['MBTS'] = {
                'TILECAL_EBA_m08_c12':0, 
                'TILECAL_EBA_m24_c12':0,
                'TILECAL_EBA_m39_c04':0,
                'TILECAL_EBA_m40_c04':0,
                'TILECAL_EBA_m41_c04':0,
                'TILECAL_EBA_m42_c04':0,
                'TILECAL_EBA_m43_c12':0,
                'TILECAL_EBA_m54_c12':0,
                'TILECAL_EBA_m55_c04':0,
                'TILECAL_EBA_m56_c04':0,
                'TILECAL_EBA_m57_c04':0,
                'TILECAL_EBA_m58_c04':0,
                'TILECAL_EBC_m08_c12':0,
                'TILECAL_EBC_m24_c12':0,
                'TILECAL_EBC_m39_c04':0,
                'TILECAL_EBC_m40_c04':0,
                'TILECAL_EBC_m41_c04':0,
                'TILECAL_EBC_m42_c04':0,
                'TILECAL_EBC_m43_c12':0,
                'TILECAL_EBC_m54_c12':0,
                'TILECAL_EBC_m55_c04':0,
                'TILECAL_EBC_m56_c04':0,
                'TILECAL_EBC_m57_c04':0,
                'TILECAL_EBC_m58_c04':0
                }

            regs['E4\''] = {
                'TILECAL_EBC_m29_c12':0,
                'TILECAL_EBC_m32_c12':0,
                'TILECAL_EBC_m34_c12':0,
                'TILECAL_EBC_m37_c12':0
                }

            regs['E1m'] = {
                'TILECAL_EBA_m07_c12':0, 
                'TILECAL_EBA_m25_c12':0, 
                'TILECAL_EBA_m44_c12':0, 
                'TILECAL_EBA_m53_c12':0,
                'TILECAL_EBC_m07_c12':0, 
                'TILECAL_EBC_m25_c12':0, 
                'TILECAL_EBC_m44_c12':0, 
                'TILECAL_EBC_m53_c12':0,
                'TILECAL_EBC_m28_c12':0, 
                'TILECAL_EBC_m31_c12':0, 
                'TILECAL_EBC_m35_c12':0, 
                'TILECAL_EBC_m38_c12':0
                }

        if self.cabling == 'RUN2a':
            regs['MBTS'].update( {
                'TILECAL_EBA_m03_c12':0,
                'TILECAL_EBA_m20_c12':0,
                'TILECAL_EBA_m46_c12':0,
                'TILECAL_EBA_m59_c12':0,

                'TILECAL_EBC_m03_c12':0,
                'TILECAL_EBC_m19_c12':0,
                'TILECAL_EBC_m46_c12':0,
                'TILECAL_EBC_m59_c12':0
            } )
            regs['E1m'].update( {
                'TILECAL_EBA_m04_c12':0,
                'TILECAL_EBA_m21_c12':0,
                'TILECAL_EBA_m47_c12':0,
                'TILECAL_EBA_m60_c12':0,

                'TILECAL_EBC_m04_c12':0,
                'TILECAL_EBC_m18_c12':0,
                'TILECAL_EBC_m47_c12':0,
                'TILECAL_EBC_m60_c12':0
            } )


        nMapErrors = 0
        reg_by_type = {}
        for sr in self.m_special_regions:
            (region, _cell, ctype) = self.m_special_regions[sr]
            if ctype not in reg_by_type:
                reg_by_type[ctype] = list()
            reg_by_type[ctype].append(region.GetHash())
            print("%s (%s) => %s N: %s L: %s numbers: %s => %s" % (sr, region.GetHash(1), _cell.GetHash(), region.GetCellName(True), region.GetLayerName(), str(region.GetNumber(1)), ctype))
            chan_hash = region.GetParent('physical').GetHash()
            if chan_hash not in regs[ctype]:
                if ctype != 'E':
                    print("ERROR: chan %s (%s) not defined for type %s" % (chan_hash, region.GetHash(), ctype))
            else:
                regs[ctype][chan_hash] += 1
            if ctype=='MBTS' and 'MBTS' not in _cell.GetHash():
                print("ERROR: Wrong cell %s for ADC %s" % (_cell.GetHash(), region.GetHash()))
                nMapErrors += 1

        for ctype in reg_by_type:
            print("ADC:s in cell of type %s:" % ctype)
            print(reg_by_type[ctype])

        # check that all special channels have been seen two times
        for r in regs:
            for part in regs[r]:
                if regs[r][part] != 2:
                    print("ERROR: part %s of type %s seen %d times" % (part, r, regs[r][part]))
                    nMapErrors += 1

        reg2cell = {}
        if self.cabling == 'RUN2' or self.cabling == 'RUN2a':
            reg2cell = {
                        'TILECAL_EBA_m39_c05' : ['spC10', 'TILECAL_EBA_m39_sBC_t09', [3, 39, 1, 9]],
                        'TILECAL_EBA_m40_c05' : ['spC10', 'TILECAL_EBA_m40_sBC_t09', [3, 40, 1, 9]],
                        'TILECAL_EBA_m41_c05' : ['spC10', 'TILECAL_EBA_m41_sBC_t09', [3, 41, 1, 9]],
                        'TILECAL_EBA_m42_c05' : ['spC10', 'TILECAL_EBA_m42_sBC_t09', [3, 42, 1, 9]],
                        'TILECAL_EBA_m55_c05' : ['spC10', 'TILECAL_EBA_m55_sBC_t09', [3, 55, 1, 9]],
                        'TILECAL_EBA_m56_c05' : ['spC10', 'TILECAL_EBA_m56_sBC_t09', [3, 56, 1, 9]],
                        'TILECAL_EBA_m57_c05' : ['spC10', 'TILECAL_EBA_m57_sBC_t09', [3, 57, 1, 9]],
                        'TILECAL_EBA_m58_c05' : ['spC10', 'TILECAL_EBA_m58_sBC_t09', [3, 58, 1, 9]],

                        'TILECAL_EBC_m39_c05' : ['spC10', 'TILECAL_EBC_m39_sBC_t09', [4, 39, 1, 9]],
                        'TILECAL_EBC_m40_c05' : ['spC10', 'TILECAL_EBC_m40_sBC_t09', [4, 40, 1, 9]],
                        'TILECAL_EBC_m41_c05' : ['spC10', 'TILECAL_EBC_m41_sBC_t09', [4, 41, 1, 9]],
                        'TILECAL_EBC_m42_c05' : ['spC10', 'TILECAL_EBC_m42_sBC_t09', [4, 42, 1, 9]],
                        'TILECAL_EBC_m55_c05' : ['spC10', 'TILECAL_EBC_m55_sBC_t09', [4, 55, 1, 9]],
                        'TILECAL_EBC_m56_c05' : ['spC10', 'TILECAL_EBC_m56_sBC_t09', [4, 56, 1, 9]],
                        'TILECAL_EBC_m57_c05' : ['spC10', 'TILECAL_EBC_m57_sBC_t09', [4, 57, 1, 9]],
                        'TILECAL_EBC_m58_c05' : ['spC10', 'TILECAL_EBC_m58_sBC_t09', [4, 58, 1, 9]],

                        'TILECAL_EBA_m39_c04' : ['MBTS', 'TILECAL_EBA_m39_sE_MBTSA2', [3, 39, 3, 15]],
                        'TILECAL_EBA_m40_c04' : ['MBTS', 'TILECAL_EBA_m40_sE_MBTSA3', [3, 40, 3, 15]],
                        'TILECAL_EBA_m41_c04' : ['MBTS', 'TILECAL_EBA_m41_sE_MBTSA4', [3, 41, 3, 15]],
                        'TILECAL_EBA_m42_c04' : ['MBTS', 'TILECAL_EBA_m42_sE_MBTSA5', [3, 42, 3, 15]],
                        'TILECAL_EBA_m55_c04' : ['MBTS', 'TILECAL_EBA_m55_sE_MBTSA6', [3, 55, 3, 15]],
                        'TILECAL_EBA_m56_c04' : ['MBTS', 'TILECAL_EBA_m56_sE_MBTSA7', [3, 56, 3, 15]],
                        'TILECAL_EBA_m57_c04' : ['MBTS', 'TILECAL_EBA_m57_sE_MBTSA0', [3, 57, 3, 15]],
                        'TILECAL_EBA_m58_c04' : ['MBTS', 'TILECAL_EBA_m58_sE_MBTSA1', [3, 58, 3, 15]],

                        'TILECAL_EBC_m39_c04' : ['MBTS', 'TILECAL_EBC_m39_sE_MBTSC2', [4, 39, 3, 15]],
                        'TILECAL_EBC_m40_c04' : ['MBTS', 'TILECAL_EBC_m40_sE_MBTSC3', [4, 40, 3, 15]],
                        'TILECAL_EBC_m41_c04' : ['MBTS', 'TILECAL_EBC_m41_sE_MBTSC4', [4, 41, 3, 15]],
                        'TILECAL_EBC_m42_c04' : ['MBTS', 'TILECAL_EBC_m42_sE_MBTSC5', [4, 42, 3, 15]],
                        'TILECAL_EBC_m55_c04' : ['MBTS', 'TILECAL_EBC_m55_sE_MBTSC6', [4, 55, 3, 15]],
                        'TILECAL_EBC_m56_c04' : ['MBTS', 'TILECAL_EBC_m56_sE_MBTSC7', [4, 56, 3, 15]],
                        'TILECAL_EBC_m57_c04' : ['MBTS', 'TILECAL_EBC_m57_sE_MBTSC0', [4, 57, 3, 15]],
                        'TILECAL_EBC_m58_c04' : ['MBTS', 'TILECAL_EBC_m58_sE_MBTSC1', [4, 58, 3, 15]],

                        'TILECAL_EBA_m08_c12' : ['MBTS', 'TILECAL_EBA_m08_sE_MBTSA', [3,  8, 3, 15]],
                        'TILECAL_EBA_m24_c12' : ['MBTS', 'TILECAL_EBA_m24_sE_MBTSA', [3, 24, 3, 15]],
                        'TILECAL_EBA_m43_c12' : ['MBTS', 'TILECAL_EBA_m43_sE_MBTSA', [3, 43, 3, 15]],
                        'TILECAL_EBA_m54_c12' : ['MBTS', 'TILECAL_EBA_m54_sE_MBTSA', [3, 54, 3, 15]],

                        'TILECAL_EBC_m08_c12' : ['MBTS', 'TILECAL_EBC_m08_sE_MBTSC', [4,  8, 3, 15]],
                        'TILECAL_EBC_m24_c12' : ['MBTS', 'TILECAL_EBC_m24_sE_MBTSC', [4, 24, 3, 15]],
                        'TILECAL_EBC_m43_c12' : ['MBTS', 'TILECAL_EBC_m43_sE_MBTSC', [4, 43, 3, 15]],
                        'TILECAL_EBC_m54_c12' : ['MBTS', 'TILECAL_EBC_m54_sE_MBTSC', [4, 54, 3, 15]],

                        'TILECAL_EBC_m29_c12' : ['E4\'', 'TILECAL_EBC_m29_sE_t10', [4, 29, 3, 10]],
                        'TILECAL_EBC_m32_c12' : ['E4\'', 'TILECAL_EBC_m32_sE_t10', [4, 32, 3, 10]],
                        'TILECAL_EBC_m34_c12' : ['E4\'', 'TILECAL_EBC_m34_sE_t10', [4, 34, 3, 10]],
                        'TILECAL_EBC_m37_c12' : ['E4\'', 'TILECAL_EBC_m37_sE_t10', [4, 37, 3, 10]],

                        'TILECAL_EBA_m07_c12' : ['E1m', 'TILECAL_EBA_m07_sE_t10', [3,  7, 3, 10]],
                        'TILECAL_EBA_m25_c12' : ['E1m', 'TILECAL_EBA_m25_sE_t10', [3, 25, 3, 10]],
                        'TILECAL_EBA_m44_c12' : ['E1m', 'TILECAL_EBA_m44_sE_t10', [3, 44, 3, 10]],
                        'TILECAL_EBA_m53_c12' : ['E1m', 'TILECAL_EBA_m53_sE_t10', [3, 53, 3, 10]],

                        'TILECAL_EBC_m07_c12' : ['E1m', 'TILECAL_EBC_m07_sE_t10', [4,  7, 3, 10]],
                        'TILECAL_EBC_m25_c12' : ['E1m', 'TILECAL_EBC_m25_sE_t10', [4, 25, 3, 10]],
                        'TILECAL_EBC_m44_c12' : ['E1m', 'TILECAL_EBC_m44_sE_t10', [4, 44, 3, 10]],
                        'TILECAL_EBC_m53_c12' : ['E1m', 'TILECAL_EBC_m53_sE_t10', [4, 53, 3, 10]],

                        'TILECAL_EBC_m28_c12' : ['E1m', 'TILECAL_EBC_m28_sE_t10', [4, 28, 3, 10]],
                        'TILECAL_EBC_m31_c12' : ['E1m', 'TILECAL_EBC_m31_sE_t10', [4, 31, 3, 10]],
                        'TILECAL_EBC_m35_c12' : ['E1m', 'TILECAL_EBC_m35_sE_t10', [4, 35, 3, 10]],
                        'TILECAL_EBC_m38_c12' : ['E1m', 'TILECAL_EBC_m38_sE_t10', [4, 38, 3, 10]]
                        }

            if self.cabling == 'RUN2a':
                reg2cell.update({
                        'TILECAL_EBA_m03_c12' : ['MBTS', 'TILECAL_EBA_m03_sE_MBTSA', [3,  3, 3, 15]],
                        'TILECAL_EBA_m20_c12' : ['MBTS', 'TILECAL_EBA_m20_sE_MBTSA', [3, 20, 3, 15]],
                        'TILECAL_EBA_m46_c12' : ['MBTS', 'TILECAL_EBA_m46_sE_MBTSA', [3, 46, 3, 15]],
                        'TILECAL_EBA_m59_c12' : ['MBTS', 'TILECAL_EBA_m59_sE_MBTSA', [3, 59, 3, 15]],

                        'TILECAL_EBC_m03_c12' : ['MBTS', 'TILECAL_EBC_m03_sE_MBTSC', [4,  3, 3, 15]],
                        'TILECAL_EBC_m19_c12' : ['MBTS', 'TILECAL_EBC_m19_sE_MBTSC', [4, 19, 3, 15]],
                        'TILECAL_EBC_m46_c12' : ['MBTS', 'TILECAL_EBC_m46_sE_MBTSC', [4, 46, 3, 15]],
                        'TILECAL_EBC_m59_c12' : ['MBTS', 'TILECAL_EBC_m59_sE_MBTSC', [4, 59, 3, 15]],

                        'TILECAL_EBA_m04_c12' : ['E1m', 'TILECAL_EBA_m04_sE_t10', [3,  4, 3, 10]],
                        'TILECAL_EBA_m21_c12' : ['E1m', 'TILECAL_EBA_m21_sE_t10', [3, 21, 3, 10]],
                        'TILECAL_EBA_m47_c12' : ['E1m', 'TILECAL_EBA_m47_sE_t10', [3, 47, 3, 10]],
                        'TILECAL_EBA_m60_c12' : ['E1m', 'TILECAL_EBA_m60_sE_t10', [3, 60, 3, 10]],

                        'TILECAL_EBC_m04_c12' : ['E1m', 'TILECAL_EBC_m04_sE_t10', [4,  4, 3, 10]],
                        'TILECAL_EBC_m18_c12' : ['E1m', 'TILECAL_EBC_m18_sE_t10', [4, 18, 3, 10]],
                        'TILECAL_EBC_m47_c12' : ['E1m', 'TILECAL_EBC_m47_sE_t10', [4, 47, 3, 10]],
                        'TILECAL_EBC_m60_c12' : ['E1m', 'TILECAL_EBC_m60_sE_t10', [4, 60, 3, 10]]
                        }
                )
        nMapErrorsE = 0
        for sr in self.m_special_regions:
            (region, _cell, ctype) = self.m_special_regions[sr]
            _chan = region.GetParent('physical')
            if _chan.GetHash() not in reg2cell:
                if ctype == 'E':
                    nMapErrorsE += 1
                else:
                    print("Error: Unable to map channel %s" % _chan.GetHash())
                    nMapErrors += 1
            else:
                r2c = reg2cell[_chan.GetHash()]
                if (r2c[0] != ctype) or (_cell.GetHash() != r2c[1]) or (_cell.GetNumber() != r2c[2]):
                    nMapErrors += 1
                    print("Error: Invalid mapping for %s chan: %s" % (region.GetHash(), _chan.GetHash()))
        if nMapErrors==0:
            print("No mapping errors detected!")
        if nMapErrorsE!=0:
            print("Missing mapping for",nMapErrorsE,"E-cell channels (but it's not a problem)")
        print(" ")

    def ProcessRegion(self, region):
        if 'gain' not in region.GetHash():
            return
        ctype = self.GetCellTypeForADC(region)
        _chan = region.GetParent(type='physical')
        _cell = self.GetCellForADC(region, ctype)

        region_hash = region.GetHash()
        if ctype != '':
            self.m_special_regions[region_hash] = (region, _cell, ctype)

        for cell_event in _cell.GetEvents():
            sctype = ctype
            if 'special_cell_type' in cell_event.data:
                evtctype = cell_event.data['special_cell_type']
                if evtctype != ctype:
                    print("ERROR CheckSpecialChannels Cell types mismatch for ADC %s cell %s -- Type defined as '%s' for cell, ADC says '%s'" % (region_hash, _cell.GetHash(), evtctype, ctype))
                    if ctype == '':
                       sctype = evtctype
                       print("Overriding with %s" % sctype)
            cell_event.data['special_cell_type'] = sctype
        
        for adc_event in region.GetEvents():
            adc_event.data['special_cell_type'] = ctype
            for chan_event in _chan.GetEvents():
                chan_event.data['special_cell_type'] = ctype
