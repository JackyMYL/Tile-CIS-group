from workers.noise.NoiseWorker import NoiseWorker

class MarkBadCells(NoiseWorker):
    '''
    Check if cells have bad channels
    '''

    def __init__(self, output):
        self.m_found_bad_channels = {}
        self.m_output = output
        self.m_badStatusAttribute = 'isStatusBad'

    def ProcessStart(self):
        pass
        
    def ProcessStop(self):
        print(" ")
    
    def GetNumberOfBadChannels(self, _cell):
        n_bad_chans = 0
        bad_adcs = []
        tot_bad_adcs_LG = 0
        tot_bad_adcs_HG = 0
        for chan in _cell.GetChildren('physical'):
            n_bad_adcs_LG = 0
            n_bad_adcs_HG = 0
            for adc in chan.GetChildren('physical'):
                gain = 'highgain' in adc.GetHash()
                for adc_event in adc.GetEvents():
                    if self.m_badStatusAttribute in adc_event.data and adc_event.data[self.m_badStatusAttribute]:
                        self.m_output.print_log("ADC %s of type: %s is bad: %s" % (adc.GetHash(), adc.GetCellName(True), adc_event.data['problems']))
                        if gain:
                            n_bad_adcs_HG += 1
                        else:
                            n_bad_adcs_LG += 1
                        bad_adcs.append(adc.GetHash())
            if (n_bad_adcs_HG + n_bad_adcs_LG) == 2:
                n_bad_chans += 1
            elif (n_bad_adcs_HG + n_bad_adcs_LG) == 0:
                pass
            else:
                n_bad_chans += 1
            tot_bad_adcs_LG += n_bad_adcs_LG
            tot_bad_adcs_HG += n_bad_adcs_HG
        return n_bad_chans, bad_adcs, tot_bad_adcs_LG, tot_bad_adcs_HG

    def ProcessRegion(self, region):
        if 'gain' not in region.GetHash():
            return
        
        _chan = region.GetParent(type='physical')
        ctype = self.GetCellTypeForADC(region)
        _cell = self.GetCellForADC(region, ctype)

        for cell_event in _cell.GetEvents():
            if not 'n_bad_channels' in cell_event.data:
                nbad_chans, bad_adcs, tot_bad_adcs_LG, tot_bad_adcs_HG = self.GetNumberOfBadChannels(_cell)
                cell_event.data['n_bad_channels'] = nbad_chans
                cell_event.data['n_bad_adcs_LG'] = tot_bad_adcs_LG
                cell_event.data['n_bad_adcs_HG'] = tot_bad_adcs_HG
                if nbad_chans:
                    self.m_output.print_log("Cell %s of type %s has %d bad channels %d LG %d HG: %s" % (_cell.GetHash(), cell_event.data['special_cell_type'], nbad_chans, tot_bad_adcs_LG, tot_bad_adcs_HG, str(bad_adcs)))

        for adc_event in region.GetEvents():
            if self.m_badStatusAttribute in adc_event.data:           
                isBad = adc_event.data[self.m_badStatusAttribute]
            # check if two channels belonging to the same cell are both bad
                if isBad:
                    chan_hash = _chan.GetHash()
                    if chan_hash not in self.m_found_bad_channels:
                        self.m_found_bad_channels[chan_hash] = True
                    else:
                        for c in _cell.GetChildren('readout'):
                            h = c.GetHash()
                            if h != chan_hash and h in self.m_found_bad_channels:
                                self.m_output.print_log("WARNING: Sibling channel %s to %s is also bad! Cell %s type: %s ADC: %s" % (h, chan_hash, adc_event.data['special_cell_type'], _cell.GetHash(), region.GetHash()))

                
