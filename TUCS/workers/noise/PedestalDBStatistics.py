from src.GenericWorker import GenericWorker
import os
import ROOT
import datetime
from bisect import bisect

class PedestalDBStatistics(GenericWorker):
    '''
    Gather and report statistics about pedestal updates
    '''

    def __init__(self, output, pedestal_thresholds, supress_number_of_changed, check_bad=False, verbose=False, print_details=False, phys_runs=None, low_stat_runs=None, warn_threshold=0.8):
        self.m_output = output
        self.m_pedestal_thresholds = pedestal_thresholds
        self.m_changes_per_adc = {}
        self.m_changes_per_possibly_bad_adc = {}
        self.m_changes_per_bad_adc = {}
        self.m_changes_per_ok_adc = {}
        self.m_supress_number_of_changed = supress_number_of_changed
        self.m_check_bad = check_bad
        self.m_verbose = verbose
        self.m_print_details = print_details
        self.m_phys_runs = phys_runs
        self.m_low_stat_runs = low_stat_runs
        self.m_warn_threshold = warn_threshold
    
    def _PrintChanges(self, change_map):
        for didx in range(len(self.m_pedestal_thresholds)):
            self.m_output.print_log("** Changes above %f ADC counts **" % self.m_pedestal_thresholds[didx])
            adc_vs_changes = {}
            for adcid in change_map:
                ch = change_map[adcid][didx]
                if ch > 0:
                    if ch in adc_vs_changes:
                        adc_vs_changes[ch].append(adcid)
                    else:
                        adc_vs_changes[ch] = [adcid]
            for nch in sorted(adc_vs_changes, reverse=True):
                if len(adc_vs_changes[nch]) > self.m_supress_number_of_changed:
                    self.m_output.print_log("%d : %d ADC:s" % (nch, len(adc_vs_changes[nch])))
                else:
                    self.m_output.print_log("%d : %s" % (nch, ' '.join(adc_vs_changes[nch])))

    # ---- Implementation of Worker ----

    def ProcessStart(self):
        pass

    def ProcessStop(self):
        if self.m_check_bad:
            self.m_output.print_log("*************************************************")
            self.m_output.print_log("Changes to channels never masked");
            self._PrintChanges(self.m_changes_per_adc)
            
            self.m_output.print_log("*************************************************")
            self.m_output.print_log("Changes to channels masked bad at some point");
            self._PrintChanges(self.m_changes_per_possibly_bad_adc)

            self.m_output.print_log("*************************************************")
            self.m_output.print_log("Changes to channels when bad");
            self._PrintChanges(self.m_changes_per_bad_adc)
            
            self.m_output.print_log("*************************************************")
            self.m_output.print_log("Changes to channels when OK");
            self._PrintChanges(self.m_changes_per_ok_adc)
        else:
            self.m_output.print_log("*************************************************")
            self.m_output.print_log("Changes to channels");
            self._PrintChanges(self.m_changes_per_adc)

    def ProcessRegion(self, region):
        # only consider ADC:s
        rhash = region.GetHash()
        if 'gain' not in rhash:
            return

        # remove 'TILECAL_'
        rhash = rhash[8:]

        # ignore ADC:s wo data
        if not region.GetEvents():
            return

        if self.m_verbose:
            self.m_output.print_log("ADC: %s" % rhash)

        # get the pedestal for each run, do not assume ordering by run number
        ped_vs_run = {}
        is_bad_at_some_point = False
        for event in region.GetEvents():
            if self.m_check_bad and ('isStatusBad' in event.data) and event.data['isStatusBad']:
                is_bad_at_some_point = True
                ped_vs_run[event.run.runNumber] = [event.data['ped_db'], True]
            else:
                ped_vs_run[event.run.runNumber] = [event.data['ped_db'], False]

        if self.m_verbose:
            self.m_output.print_log("%s : %s" % (rhash, str(ped_vs_run)))

        # sort the values by run
        pedestal_values = []
        pedestal_runs = []
        channel_is_bad = []
        for runnr in sorted(ped_vs_run):
            pedestal_values.append(ped_vs_run[runnr][0])
            pedestal_runs.append(runnr)
            channel_is_bad.append(ped_vs_run[runnr][1])
        
        # count number of changes above the thresholds
        changes_above_threshold = [0 for __z in self.m_pedestal_thresholds]
        changes_above_threshold_bad = [0 for __z in self.m_pedestal_thresholds]
        changes_above_threshold_ok = [0 for __z in self.m_pedestal_thresholds]
        has_changes = False
        for idx in range(1, len(pedestal_values)):
            pdiff = abs(pedestal_values[idx] - pedestal_values[idx-1])
            bad_junction = channel_is_bad[idx] or channel_is_bad[idx-1]
            if self.m_verbose:
                self.m_output.print_log(" %d -> %d  = %f  bad: %s" % (pedestal_runs[idx-1], pedestal_runs[idx], pedestal_values[idx] - pedestal_values[idx-1], bad_junction))
            for didx in range(len(self.m_pedestal_thresholds)):
                if pdiff > self.m_pedestal_thresholds[didx]:
                    changes_above_threshold[didx] += 1
                    has_changes = True
                    if self.m_check_bad:
                        if bad_junction:
                            changes_above_threshold_bad[didx] += 1
                        else:
                            changes_above_threshold_ok[didx] += 1
            if self.m_print_details and pdiff > self.m_warn_threshold:
                r1 = pedestal_runs[idx-1]
                r2 = pedestal_runs[idx]
                pr1 = bisect(self.m_phys_runs, r1)
                pr2 = bisect(self.m_phys_runs, r2)
                if pr1 < pr2:
                    self.m_output.print_log("%s bad: %s %d -> %d  = %f " % (rhash, bad_junction, r1, r2, pedestal_values[idx] - pedestal_values[idx-1]))
                    for i in range(pr1, pr2):
                        self.m_output.print_log("phys %d" % self.m_phys_runs[i])
                    lsr1 = bisect(self.m_low_stat_runs, r1)
                    lsr2 = bisect(self.m_low_stat_runs, r2)
                    for i in range(lsr1, lsr2):
                        self.m_output.print_log("low stat %d" % self.m_low_stat_runs[i])
                
        # if there are any updates above the thresholds, store
        if has_changes:
            if is_bad_at_some_point:
                self.m_changes_per_possibly_bad_adc[rhash] = changes_above_threshold
            else:
                self.m_changes_per_adc[rhash] = changes_above_threshold

            if self.m_check_bad:
                self.m_changes_per_bad_adc[rhash] = changes_above_threshold_bad
                self.m_changes_per_ok_adc[rhash] = changes_above_threshold_ok

            if self.m_verbose:
                self.m_output.print_log("%s is bad at some point: %s diffs: %s diffs when ok: %s bad: %s" % (rhash, str(is_bad_at_some_point), str(changes_above_threshold), str(changes_above_threshold_ok), str(changes_above_threshold_bad)))
