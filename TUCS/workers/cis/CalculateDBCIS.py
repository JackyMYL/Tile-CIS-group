#################################################################################
#Author: Grey Wilburn <grey.williams.wilburn@cern.ch>
#
#Date: A brisk autumn day in 2014...
#
'''
This worker recalibrates the Database CIS constant values for regions specified
in the Grey_Update macro. It is controlled by that macro.
'''
#
#################################################################################

# stdlib imports
import os.path
import itertools
import math
# 3rd party imports
import ROOT
# TUCS imports
import src.GenericWorker
import src.MakeCanvas
import src.oscalls
import src.Get_Consolidation_Date

# CIS imports
import workers.cis.common as common

class CalculateDBCIS(src.GenericWorker.GenericWorker):
    "Recalibrates the DB CIS const. values using time averages w/ various data quality cuts"

    def __init__(self, run_window = 2, threshold = 0.005):
        
        self.run_window = run_window
        self.threshold = threshold

        self.cool_list = ['ADC masked (unspecified)', 'Bad CIS calibration', 'Stuck bit', #'No CIS calibration',
                    'Severe stuck bit', 'Channel masked (unspecified)']
        self.qflag_list = ['Large Injection RMS', 'Stuck Bit', 'Fail Likely Calib.', 'Low Chi2',
                    'Fail Max. Point', 'Digital Errors']            
    def ProcessStart(self):

        print("now running new calulateDBCIS.py")

    def ProcessStop(self):
        print("db_update: ", len(db_update))
        print("DONEZO!")

    def ProcessRegion(self,region):
        
        #By default, we won't create a plot for this channel
        plot = False

        #get the name of the channel
        gh = region.GetHash()
        
        #check and see if there is any data 
        if region.GetEvents() == set():
            return
        #Fix bug where data are not properly cleared out 
        #elif region.GetEvents() == [0.0]:
        #    return
        #NOW THAT YOU HAVE FOUND OLD DB VALS AND ALL THE CHANNELS WITH PROBLEMS, YOU CAN CALC THRESHHOLD VALUE:
        #Calculating the threshhold for determining "too low" cis constants - we do this by looking at the current database values
        #     and then doing cutoff = (mean - 3*rms)/2
        #Now we will find the average CIS constant value over the time interval for each channel, excluding some small values in our average.
        avgsum = 0
        count = 0
                
        for run in calib_dict[region.GetHash()]:
            #Exclude "low runs" w/ cis contsants less than 20% of gain average
            if 'hi' in gh and  calib_dict[gh][run] > 16.0:
                avgsum += calib_dict[gh][run]
                count += 1
            elif 'lo' in gh and calib_dict[region.GetHash()][run] > 0.250:
                avgsum += calib_dict[gh][run]
                count += 1

        #calculate measured avg.
        lowavg = False
        if count > 0:
            avg = avgsum / count
            zero_count = False
            if ('hi' in gh and avg < hi_threshold) or ('lo' in gh and avg < lo_threshold): #recall that you changed this line
                lowavg = True   

        #For channels with all "low runs"
        else:
            avg = 0
            zero_count = True
            print("ZERO AVG: ", gh, avg)

        #Count number of bad runs. We define 'bad' runs as those w/ CIS const. that vary from the channel average by more than 1%. 1% is the approx. uncertainty of our calibration
        nBadRuns = 0
        runcount = 0
        for run in calib_dict[region.GetHash()]:
            runcount += 1
            if avg > 0:
                perdif = (calib_dict[gh][run] - avg) / avg
            else:
                perdif = 100

            if abs(perdif) > self.threshold:
                nBadRuns += 1

        #For channels with VERY low cis constants for all runs, just use the old DB value
        if zero_count:
            plot = True
            db_default = True

        # # DEFAULT VALUE METHOD # #        
        #Channels failing certain TUCS flas for > 50 % of the runs will have a default value for ALL runs
        elif lowavg and(tucs_dict[gh]['Fail Max. Point'] > 0.5 or tucs_dict[gh]['Fail Likely Calib.'] > 0.5): #test 1
                if tucs_dict[gh]['Low Chi2'] > 0.5 or tucs_dict[gh]['Large Injection RMS'] > 0.5 or tucs_dict[gh]['Digital Errors'] > 0.5: #test2
                    db_default = True #channels failing tests 1 AND 2 get a default value
                else:
                    db_default = False
        else:
            db_default = False

        if db_default:
            #Make plots and note the default value!
            final_default_list.append(gh)
            plot_list.append(gh)
            print("plot list giving default")
            print(gh)
            for run in calib_dict[gh]:
                if 'hi' in gh:
                    last_run = sorted(old_db_dict[gh])[-1]
                    db_update[gh][run] = old_db_dict[gh][last_run]
                    #db_update[gh][run] = 81.84
                else:
                    last_run = sorted(old_db_dict[gh])[-1]
                    db_update[gh][run] = old_db_dict[gh][last_run]
                    #db_update[gh][run] = 1.279

        # # AVERAGE VALUE METHOD # #
        #If the number of 'bad' runs is small, just use the channel average as the new db value for each run
        elif float(nBadRuns / runcount) < 0.1 and nBadRuns < 3:
            for run in calib_dict[region.GetHash()]:
                db_update[gh][run] = avg

        # # "PIECEWISE" AVERAGE VALUE METHOD
        #This rather complicated process calculates new DB values for channels with fulctiating measured CIS constants. It could easily be changed. Suggestions welcome!
        elif not db_default:
            plot_list.append(gh)
            prev_db = 0
            #Always creae plots for fluctuating channels!
            plot = True
            meansum = 0
            goodcount = 0
            mean = 0
            badcount = 0
            tot_count = 0
            total_run_list = []
            runlist = []
            avglist = []
            badrunlist = []
            perdif_dict = {}

            #Loop for calculating local averages, determining local time periods 
    
            for run in sorted(calib_dict[gh]):
                # print(f"Run {run}")
                # print(f"Goodcount{goodcount}")
                # print(f"badcount {badcount}")
                # print(f"total_run_list {total_run_list}")
                # print(f"total count {tot_count}")
                # print(f"calib_dict value{calib_dict[gh][run]}")

                total_run_list.append(run)
                tot_count += 1
                run_index = tot_count-1

                if run_index == 0:
                    perdif_dict[run] = 0
                else:
                    if calib_dict[gh][run] != 0:
                        print("Calibration value is 0 for {}\t{}\n".format(gh, run))
                        pd = (calib_dict[gh][run]-calib_dict[gh][total_run_list[-2]])/calib_dict[gh][run]
                        perdif_dict[run] = pd
                
                #If number of "good" runs is 2 or more, we need to consider "bad" runs
                if goodcount >= self.run_window/2: # >=2 for default run_window size 
                    perdif = ((calib_dict[gh][run] - mean) / mean)
                    print(f"perdif {perdif}")

                    #If the run's measured CIS const. is atleast \pm 0.5 percent away from local average, it is bad
                    if abs(perdif)  > self.threshold:
                        if ('hi' in gh and calib_dict[gh][run] > 15.0) or ('lo' in gh and calib_dict[gh][run] > 0.25): #Don't count really low values as "bad"
                            badcount += 1
                        badrunlist.append(run)

                        #If we have reached run_window-many "bad" runs, time to start a new local average
                        if badcount >= self.run_window :
                            prev_db = mean
                        
                            #Assign all runs in the local time period the local mean 
                            for grun in runlist:    
                                db_update[gh][grun] = mean
                            meansum = calib_dict[gh][run]
                            
                            #Reset goodcount and badcount for new local averaging
                            goodcount = 1
                            runlist = [run] 
                            badcount = 0
                            avglist.append(mean)

                        else:
                            runlist.append(run)

                    #If the run is "good", increase goodcont by 1, recalculate the local avg.                                       
                    else:
                        runlist.append(run)
                        goodcount += 1
                        meansum += calib_dict[gh][run]  


                #If number of "good" runs is small, don't worry about "bad" runs yet (small sample size => what defines "bad"???)   
                else:
                    runlist.append(run)
                    # if run_index > 0:
                    #     perdif = ((calib_dict[gh][run] - mean) / mean)
                    #     if abs(perdif)  > self.threshold:
                    #         if ('hi' in gh and calib_dict[gh][run] > 15.0) or ('lo' in gh and calib_dict[gh][run] > 0.25): #Don't count really low values as "bad"
                    #             badcount += 1
                    #         badrunlist.append(run)
                    if 'hi' in gh and calib_dict[gh][run] > 15.0:
                        goodcount += 1
                        meansum += calib_dict[gh][run]
                    elif 'lo' in gh and calib_dict[gh][run] > 0.25:
                        meansum += calib_dict[gh][run]
                        goodcount += 1

                #Calculate the local average
                if goodcount > 0:       
                    mean = meansum / goodcount
                else:
                    mean = float(0)

                # print(f"mean {mean}")
                # print(f"meansum {meansum}")
                #print(f"avglist {avglist}")
                #Assign values once we have reached the end of the run period
                if tot_count == len(calib_dict[gh]):

                    #If number of good runs has reached 3, we will assign all runs in the local time period the local average
                    if prev_db == 0 or goodcount > self.run_window/2:
                        for grun in runlist:
                            db_update[gh][grun] = mean
                            avglist.append(mean)

                    #If the number of good runs is small, use the previous local average
                    else:
                        for grun in runlist:
                            db_update[gh][grun] = prev_db
                            avglist.append(prev_db)
            # print(f"Perdif list \n\n {perdif_dict}\n\n")
            # Extra bad runs should include those for which there is a single miscalibration 
            # Maybe we should just exclude it from the IOV?
            i=0
            extra_bad_runs = []
            temp_run_list = []
            for run in sorted(perdif_dict):
                temp_run_list.append(run)
                if i !=0:
                    if abs(perdif_dict[int(temp_run_list[-2])]) > self.threshold and abs(perdif_dict[int(temp_run_list[-1])]) > self.threshold:
                        extra_bad_runs.append(temp_run_list[-2])
                i+=1
            #Make sure the "Bad" runs have the most accurate local average value by looking at nearest "good" neighboring runs
            #Doesn't work for wildly fluctuating channels, but they should be masked anyways...
            #print(f"bad run list {badrunlist}") 
            #print(f"Extra bad runs {extra_bad_runs}")     
            badrunlist = badrunlist + list(set(extra_bad_runs)-set(badrunlist))   
            #print(f"Merged lists containing now all bad runs {badrunlist}")
            i = -1
            for run in sorted(calib_dict[gh]):
                print("Starting bad run resolition")
                i += 1
                if not run in badrunlist:
                    continue
                #find first previous good run
                previous_run_good = False
                j = 1
                while previous_run_good == False:
                    #make sure we haven't reached the begininng of update period
                    if (i - j) < 0:
                        previous_run_good = True 
                        previous_run = run
                    elif total_run_list[i-j] not in badrunlist:
                        previous_run_good = True
                        previous_run = total_run_list[i-j]
                    j += 1
                
                #look at future runs
                future_run_good = False
                k = 1
                while future_run_good == False:
                    #make sure we haven't reached the end of 
                    #the update period
                    if (i + k) > (len(total_run_list)-1):
                        future_run_good = True
                        future_run = run
                    elif total_run_list[i+k] not in badrunlist:
                        future_run_good = True
                        future_run = total_run_list[i+k]
                    k += 1
                future_diff = abs(calib_dict[gh][run] - db_update[gh][future_run])
                previous_diff = abs(calib_dict[gh][run] - db_update[gh][previous_run])
                if future_diff < previous_diff:
                    db_update[gh][run] = db_update[gh][future_run]
                else:
                    db_update[gh][run] = db_update[gh][previous_run]
                badrunlist.pop(badrunlist.index(run))
            print(db_update[gh])
            
        #If the number of runs with new DB values doesn't equal the number of runs with measured values, something went wrong!
        # if len(db_update[gh]) != len(calib_dict[gh]):   
        #     print("BAD CALIBRATION: ", gh)
        #     print(db_update[gh])
        #     print(calib_dict[gh])

