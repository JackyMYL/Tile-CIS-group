from workers.noise.NoiseWorker import NoiseWorker

import ROOT

class PlotDigiNoise(NoiseWorker):
    '''
    Produces various plots with digi noise
    '''
    def __init__(self, runNumber, runType, output):
        self.runNumber = runNumber
        self.runType = runType
        self.output = output
        self.adcCmpData = {}
        self.adcVariables = ['ped','hfn','lfn','hfnsigma1','hfnsigma2','hfnnorm']

    def ProcessStart(self):
        pass
        
    def ProcessStop(self):
        # ADC data
        adc_histos = {}
        for r in self.adcCmpData:
            datad = self.adcCmpData[r][2]
            if len(datad)==0:
                self.output.print_log("ERROR: No data for '%s'" % r)
                continue
            ctype = self.adcCmpData[r][0]
            gain = 0 if 'lowgain' in r else 1
            gainstr = 'lowgain' if 'lowgain' in r else 'higain'

            if ctype not in adc_histos:
                adc_histos[ctype] = [{},{}]
            for var in self.adcVariables:
                if var not in adc_histos[ctype][gain]:
                    adc_histos[ctype][gain][var] = ROOT.TH1D('adc_'+ctype+'_'+var+'_'+gainstr, 'adc_'+ctype+'_'+var+'_'+gainstr, 200, 0, 5 * (1.0 if gain == 0 else 2.0))
                adc_histos[ctype][gain][var].Fill(datad[var])
        
        # Output
        for ctype in adc_histos:
            for gain in range(0,2):
                gainstr = 'lowgain' if gain==0 else 'higain'
                for var in self.adcVariables:
                    if adc_histos[ctype][gain]:
                        hi = adc_histos[ctype][gain][var]
                        self.output.print_log("%s %s %s entries: %d mean: %f rms: %f" % (ctype, var, gainstr, hi.GetEntries(), hi.GetMean(), hi.GetRMS()))
                        self.output.add_root_object(hi)
                    else:
                        self.output.print_log("ERROR: var '%s' not found ctype: %s gain: %s" % (var, ctype, gainstr))
        print(" ")

    def ProcessRegion(self, region):
        if len(region.GetEvents()) == 0: return
        if 'gain' not in region.GetHash():
            return

        ctype = self.GetCellTypeForADC(region)
        cell = self.GetCellForADC(region, ctype)

        for evt in region.GetEvents():
            if (evt.run.runNumber == self.runNumber) and (evt.run.runType == self.runType):
                if not region.GetHash() in self.adcCmpData:
                    self.adcCmpData[region.GetHash()] = [ctype, region.GetHash(), {}]
                for var in self.adcVariables:
                    if var in evt.data:
                        self.adcCmpData[region.GetHash()][2][var] = evt.data[var]
