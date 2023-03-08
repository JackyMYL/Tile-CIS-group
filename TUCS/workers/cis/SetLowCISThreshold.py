#Written by Ellie Rath, 14 Jan 2020
#this worker will calculate a threshold for deciding low CIS constants, using distribution of current databases values
#here goes nothing lol :)


# stdlib imports  - all copied and pased from CalculateDBCIS
import os.path
import itertools
# 3rd party imports
import ROOT
# TUCS imports
import src.GenericWorker
import src.MakeCanvas
import src.oscalls
import src.Get_Consolidation_Date

# CIS imports
import workers.cis.common as common


class SetLowCISThreshold(src.GenericWorker.GenericWorker):
    "Calculate a threshold for deciding low CIS constants, using distribution of current databases values"

    def __init__(self, run_window = 2, threshold = 0.005):
 
        self.run_window = run_window
        self.threshold = threshold

        self.cool_list = ['ADC masked (unspecified)', 'Bad CIS calibration', 'Stuck bit', #'No CIS calibration',
                    'Severe stuck bit', 'Channel masked (unspecified)']
        self.qflag_list = ['Large Injection RMS', 'Stuck Bit', 'Fail Likely Calib.', 'Low Chi2',
                    'Fail Max. Point', 'Digital Errors']            
    def ProcessStart(self):
        self.cal_type = 'CIS'
        self.dev_db_dict = {}
        self.c1 = src.MakeCanvas.MakeCanvas()

        # Create global objects to be used in subsequent workers    
        global db_run_list, db_update, db_update_list, plot_list, tucs_dict, mod_update_dict, final_default_list
        db_run_list = []
        db_update = {}
        db_update_list = []
        plot_list = []
        final_default_list = []
        tucs_dict = {}
        mod_update_dict = {}
        global calib_dict, old_db_dict, stuck_bit_list
        calib_dict = {}
        old_db_dict = {}
        stuck_bit_list = []
    #   db_dict = {}

        global hg_old_cis
        global lg_old_cis
        hg_old_cis = []
        lg_old_cis = [] 

    def ProcessStop(self):
        if len(hg_old_cis):
            hi_old_avg = ROOT.TMath.Mean(len(hg_old_cis), array('f', hg_old_cis))
            hi_old_rms = ROOT.TMath.RMS(len(hg_old_cis), array('f', hg_old_cis))
        else:
            hi_old_avg = 0
            hi_old_rms = 0
        if len(lg_old_cis):
            lo_old_avg = ROOT.TMath.Mean(len(lg_old_cis), array('f', lg_old_cis))
            lo_old_rms = ROOT.TMath.RMS(len(lg_old_cis), array('f', lg_old_cis))
        else:
            lo_old_avg = 0
            lo_old_rms = 0
        
        global hi_threshold, lo_threshold
        hi_threshold = (hi_old_avg - 3*hi_old_rms)/2
        lo_threshold = (lo_old_avg - 3*lo_old_rms)/2

        print("high gain threshold: ", hi_threshold)
        print("low gain threshold: ", lo_threshold)

    def ProcessRegion(self,region):
        #By default, we won't create a plot for this channel
        plot = False
        lo_threshold = 0.6
        #get the name of the channel
        gh = region.GetHash()
        
        #check and see if there is any data 
        if region.GetEvents() == set():
            return

        #Set up inner dictionary. Each key of the outer dictionary is a channel name, and its value is an inner dictionary. The inner dictionary maps cis constants to run numbers
        calib_dict[gh] = {}
        db_update[gh] = {}
        old_db_dict[gh] = {}
        tucs = {}
        run_count = 0
        Tucs = False
        Cool = False #by default, we don't care about ADC's w/o specific issues in COOL

        #Get the measured and old database CIS constant values, put in the appropriate inner dictionaries
        calib_list = [] #for calculating RMS
        for event in sorted(region.GetEvents(), key = lambda x: x.run.runNumber):
            if event.run.runType == 'CIS' and "calibration" in event.data:
                run_count += 1
                calib_dict[gh][event.run.runNumber] = event.data['calibration']
                calib_list.append(event.data['calibration'])
                old_db_dict[gh][event.run.runNumber] = event.data['f_cis_db']
                if not event.run.runNumber in db_run_list:
                    db_run_list.append(int(event.run.runNumber))
                if 'problems' in event.data and not Cool:
                    for problem in event.data['problems']:
                        if 'No HV' in event.data['problems']:
                            continue
                        if problem in self.cool_list:
                            Cool = True
                            plot_list.append(gh)
                        if problem == 'Stuck bit' or problem == 'Severe stuck bit':
                            stuck_bit_list.append(gh)
                            continue    
                #Retrieve TUCS qflag info
                for problem, value in event.data['CIS_problems'].items():
                    if not problem in tucs:
                        tucs[problem] = 0
                    if value:
                        tucs[problem] += 1
        #Calculate "truncated" mean and RMS, to see if we should
        #make a plot for this ADC
        if run_count > 2:
            calib_list.pop(calib_list.index(max(calib_list)))
            calib_list.pop(calib_list.index(min(calib_list)))
            mean_trunc = ROOT.TMath.Mean(len(calib_list), array('f', calib_list))
            #### Problem here when dividing by mean_trunc = 0 ??? Patch this as well ???
            if mean_trunc == 0:
                mean_trunc = 1
                print(f"Problem with mean_trunc in SetLowCISThreshold.py ({gh})")
            ####
            rms_trunc = ROOT.TMath.RMS(len(calib_list), array('f', calib_list))
            if 100*(float(rms_trunc) / float(mean_trunc)) > 0.389:
                plot_list.append(gh)
        #Analyze frequency of failed qflags

        tucs_dict[gh] = {}
        for problem in tucs:
            if not problem in self.qflag_list:
                continue
            per = float(tucs[problem]) / float(run_count)
            tucs_dict[gh][problem] = per
            if per > .50 and not gh in plot_list and not problem == 'Low Chi2':
                plot_list.append(gh)
                if problem == 'Stuck Bit':
                    stuck_bit_list.append(gh)
 
        #NOW THAT YOU HAVE FOUND OLD DB VALS AND ALL THE CHANNELS WITH PROBLEMS, YOU CAN CALC THRESHHOLD VALUE:
        #Calculating the threshhold for determining "too low" cis constants - we do this by looking at the current database values
        #     and then doing cutoff = (mean - 3*rms)/2
        n_channels = 0
        if gh not in plot_list:
            #print(old_db_dict[gh])
            if len(old_db_dict[gh]) != 0:
                last_run = sorted(old_db_dict[gh])[-1]
                old_cis = old_db_dict[gh][last_run]
                    
                if 'hi' in gh:
                    hg_old_cis.append(old_cis)
                if 'lo' in gh:
                    lg_old_cis.append(old_cis)
            else:
                # with open(os.path.join(src.oscalls.getResultDirectory(),'output/cis/Processing/ProcessingErrors.log'), 'a') as error_logfile:
                #     error_logfile.write("{}\t{}\n".format(gh,"No dict values stored"))
                print("{}\t{}\n".format(gh,"No dict values stored"))
       
