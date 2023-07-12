from workers.noise.NoiseWorker import NoiseWorker

class MakeOnlineADCNoise(NoiseWorker):
    '''
    Prepares online channel noise update from Digital and Cell
    noise DBs.  Calculates two quanitites: Channel RMS noise in ADC
    and pileup noise in MeV.
    '''

    def __init__(self):
        pass

    def ProcessStart(self):
        pass

    def ProcessStop(self):
        pass

    def ProcessRegion(self,region):
        if len(region.GetEvents()) == 0: return
        if 'gain' not in region.GetHash():
            return
        
        [part, mod, chan, gain] = region.GetNumber()
        adc = region
        chan = adc.GetParent()
        cell = chan.GetParent(type='physical')

        data = {}
        # Get RMS noise in ADC counts from adc region
        for adc_event in adc.GetEvents():
            if adc_event.run.runType == 'Ped':
                data['noise']     = adc_event.data['hfn_db']

        # Derive Pileup noise in MeV from cell region
        if '_MBTS' in cell.GetHash(): # no pileup constants for MBTS
            data['pilenoise'] = 0.0
        else:
            for cell_event in cell.GetEvents():
                if cell_event.run.runType == 'Ped':
                    if gain == 0: 
                        if '_sE' in cell.GetHash():
                            data['pilenoise'] = cell_event.data['pilenoiseLGLG_db']
                        else:
                            data['pilenoise'] = cell_event.data['pilenoiseLGLG_db']/sqrt(2.)
                    if gain == 1: 
                        if '_sE' in cell.GetHash():
                            data['pilenoise'] = cell_event.data['pilenoiseHGHG_db']
                        else:
                            data['pilenoise'] = cell_event.data['pilenoiseHGHG_db']/sqrt(2.)
        
        region.AddEvent(Event('PedUpdate',adc_event.run.runNumber,data,adc_event.time))

