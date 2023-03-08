from src.ReadGenericCalibration import ReadGenericCalibration
from workers.noise.NoiseWorker import NoiseWorker
import os
import ROOT

class ReadDigiNoiseDQMF(NoiseWorker,ReadGenericCalibration):
    '''
    Reads digital noise values from DQMF
    '''

    def __init__(self, output, user_name, stream, run_type='Ped', do_load_low_gain=False):
        self.m_output = output
        self.m_user_name = user_name
        self.m_run_type = run_type
        self.m_stream = stream
        self.m_do_load_low_gain = do_load_low_gain
        # for each run/partition/gain store histograms
        self.m_data_cache = {}
        # the suffixes for the DQM histograms
        self.m_histogram_suffixes = ['ped', 'lfn', 'hfn']

    def _IsADC(self, region):
        return 'gain' in region.GetHash()

    def _GetDrawerStr(self, region):
        if int(region.get_module()) % 2 == 0:
            return ''
        return ('%s%s' if (int(region.get_module())) > 9 else '%s0%s') % (region.get_partition(), str(int(region.get_module())))

    def _GetChannelStr(self, region):
        return 'ch%d' % int(region.get_channel())

    # ---- Implementation of Worker ----

    def ProcessStart(self):
        conn_str = 'https://%s:%s@atlasdqm.cern.ch' % (self.m_user_name, os.getenv('DQMPWD'))
        try:
            self.m_proxy = xmlrpclib.ServerProxy(conn_str)
        except:
            self.m_output.print_log("ReadDigiNoiseDQMF Error: Unable to open connection")

    def ProcessStop(self):
        self.m_data_cache = None
        self.m_proxy = None
        
    def ProcessRegion(self, region):
        if not self._IsADC(region):
            return
        pedEvent = None

        for event in region.GetEvents():
            if event.run.runType == self.m_run_type:
                pedEvent = event

        if not pedEvent:
            self.m_output.print_log("ReadDigiNoise DQMF Error: No run of type %s found" % self.m_run_type)
            return

        run_number = pedEvent.run.runNumber
        [part, mod, chan, gain] = region.GetNumber()
        
        # try to get the histograms from the cache
        if not run_number in self.m_data_cache:
            self.m_data_cache[run_number] = {}
        if not part in self.m_data_cache[run_number]:
            self.m_data_cache[run_number][part] = {}
        if not gain in self.m_data_cache[run_number][part]:
            self.m_data_cache[run_number][part][gain] = {}
        histos = self.m_data_cache[run_number][part][gain]

        if self.m_do_load_low_gain or (gain == 1):
            # if histograms not found, get them from DQM
            if not 'ped' in histos:
                run_spec = {'stream': self.m_stream, 'source':'tier0', 'run_list': [run_number] }
        
                gain_str = 'lo' if gain == 0 else 'hi'
                part_str = region.get_partition()
                run_str = str(run_number)
                for histogram_suffix in self.m_histogram_suffixes:
                    histo_name = 'TileCal/Noise/Digit/noisemap_%s_%s_%s' % (part_str, gain_str, histogram_suffix)
                    self.m_output.print_log("ReadDigiNoiseDQMF: Reading histogram %s" % histo_name)
                    try:
                        res = self.m_proxy.get_hist_objects(run_spec, histo_name)
                        histogram = ROOT.TBufferXML.ConvertFromXML(res[run_str])
                        histos[histogram_suffix] = histogram
                        self.m_output.print_log("ReadDigiNoiseDQMF: histogram '%s' read'" % histogram.GetName())
                    except Exception as ex:
                        self.m_output.print_log("ReadDigiNoiseDQMF Error: Unable to get DQMF data for histogram '%s' : %s" % (histo_name, str(ex)))
        
        if len(histos) == 3:
            for histogram_suffix in self.m_histogram_suffixes:
                hi = histos[histogram_suffix]
                val = hi.GetBinContent(mod, chan + 1)
                
                pedEvent.data[histogram_suffix] = val + (pedEvent.data['ped_db'] if histogram_suffix=='ped' else 0.0)
                # cross check
                mod_label = hi.GetXaxis().GetBinLabel(mod)
                chan_label = hi.GetYaxis().GetBinLabel(chan + 1)
                if (mod_label != self._GetDrawerStr(region)) or (self._GetChannelStr(region) not in chan_label):
                    self.m_output.print_log("ReadDigiNoiseDQMF Error: Invalid region '%s' %s %s > %s %s : %s" % (region.GetHash(), self._GetDrawerStr(region), self._GetChannelStr(region), mod_label, chan_label, str(val)))
        else:
            for histogram_suffix in self.m_histogram_suffixes:
                pedEvent.data[histogram_suffix] =  0.0
        pedEvent.data['hfnsigma1'] =  0.0
        pedEvent.data['hfnsigma2'] =  0.0
        pedEvent.data['hfnnorm'] =  0.0
