############################################################
#
# getLaserFlags.py
#
############################################################
#
# Author: Rute Pedro (rute.pedro@cern.ch)
#
# July 2013
#
# Goal:
# -> Get laser flags
#
# Input parameters are:
# -> event.data['deviation']
#
# Ouput:
# -> bitmap per module with laser flags info
# NOTE: the bitmap will only be created for modules with flagged channels
#
# NOTE:February 2015, Arthur Chomont (arthur.chomont@cern.ch) addition of :  -  a global variable, Flag_Chan which stocks in a dictionary channels::Flag associated
#                                                   -  a flag which groups cases where several channels even or odd from the same partition is having a flag simultaneously (problem with the fiber)
#
# For more info on the LASER system : http://atlas-tile-laser.web.cern.ch
#
#############################################################

from src.GenericWorker import *
from src.laser.toolbox import *
from src.oscalls import *
from array import *
import numpy
import math
import ROOT
import src.MakeCanvas
import os.path

class getLaserFlags(GenericWorker):
    "This worker attributes channel flags with laser data"

    def __init__(self, Region='LBA LBC EBA EBC', includeDQ=False, plotdirectory=None, flag=['all'],doPlots = False):
        self.run_dict      = {}
        self.run_list      = []
        self.PMTool        = LaserTools()
        self.includeDQ     = includeDQ
        self.plotdirectory = plotdirectory
        self.doplot        = doPlots
        self.lasflag       = flag
        self.problems      = set()
        self.entry         = []
        self.las_flagged   = []
        self.region        = []

        self.outputTag = outputTag # global variable to tag output histogram file name
        self.dir    = getPlotDirectory(subdir=self.outputTag)        

        # The following lines are useful to define the region of study ans so limit the time used by this worker (coming from the lines 109-111)      
        if len(Region)>0:			                # CHECK WHETHER REGION IS SPECIFIED
            if ' ' in Region: 					# IF REGION IS A LIST OF REGIONS
                self.region = Region.split(' ')			# SEPERATE THE DIFFERENT SPECIFIED REGIONS
            elif isinstance(Region,str): 			# A SINGLE REGION IS SPECIFIED AS STRING
                self.region = [Region]				# SAVE REGION AS A LIST
            elif isinstance(region,list):			# MULTIPLE REGIONS ARE SPECIFIED AS LIST
                self.region = Region               
        self.Flag_Region   = self.Build_Regions(self.region)

        if self.doplot:
            if self.plotdirectory: 
                self.dir = os.path.join(self.dir, 'LaserFlags', self.plotdirectory)
            else:
                self.dir = os.path.join(self.dir, 'LaserFlags')
            src.oscalls.createDir(self.dir)

    def ProcessStart(self):     

        global run_list
        for run in run_list.getRunsOfType('Las'):
            self.run_list.append(run)
            self.run_dict[run.runNumber] = []

        run_dis=self.run_list[0]
        test=1
        while test!=0:
            if self.run_list[test].runNumber<run_dis.runNumber:
                if test==len(self.run_list)-1:
                    self.run_list.insert(test,self.run_list.pop(0))
                    test=0
                else:
                    test+=1
            else:
                self.run_list.insert(test-1,self.run_list.pop(0))
                test=0

        #self.run_list.sort()
        print(self.run_list)
       
        self.date = self.run_list[0].time.split(' ')[:1][0]
        self.enddate = self.run_list[len(self.run_list)-1].time.split(' ')[:1][0]
                
        self.run_list.sort()
        
    def ProcessRegion(self, region):
        REGion=str(region)
        if (REGion.find('c')==-1 and REGion.find('m')==-1):
            print(REGion)
        # Use only selected region
        use_region = False
        for key in self.Flag_Region:
            if key in region.GetHash():
                use_region = True
        if not use_region:
            return

        # This is the DQ status list that affect laser data
        DQstatus_list = ['No HV','Wrong HV','ADC masked (unspecified)','ADC dead','Data corruption','Severe data corruption','Severe stuck bit','Large LF noise','Very large LF noise','Channel masked (unspecified)','Bad timing']
        # loop on events
        for event in region.GetEvents():


#            [part_num, imodule, chan, igain] = self.PMTool.GetNumber(event.data['region'])
#            pmt = self.PMTool.get_PMT_index(part_num,imodule-1,chan)
            [part_num, imodule, pmt, igain] = event.region.GetNumber(1)
            
            # Exclude non instrumented channels
            if pmt < 0: continue

            # Exclude events with HVset = 0
            if event.data['HVSet'] == 0: continue

            # By default, exclude events with problematic DQ status
            if not self.includeDQ:
                if 'problems' in event.data:
                    for problem in event.data['problems']:
                        if problem in DQstatus_list: continue

            # Exclude events for which the gain variation from HV is greater than 15%
            if math.fabs(6.9*(event.data['HV']-event.data['HVSet'])/event.data['HVSet']) > 0.15: continue

            # Exclude non OK and masked channels and channels with no deviation (reference<0)
            if event.data['is_OK'] and (not event.data['status']&0x4) and (not event.data['status']&0x10) and 'deviation' in event.data:
                self.run_dict[event.run.runNumber].append(event)

    def InitiateHisto(self):
        print('InitiateHisto')
        self.c1 = src.MakeCanvas.MakeCanvas()
        self.c1.SetGrid(1,1)
        self.c1.SetLeftMargin(0.20)

        histo  = ROOT.TH2F("histo","",48,0,48,6,0,6)
        histo.SetStats(0)
        histo.SetFillColor(ROOT.kRed)
        labels = ["Fast Drift","Erratic Gain","Gain Jump","HL Incompatible","Same DMU","Same Digitizer"]
        for i in range(6):
            histo.GetYaxis().SetBinLabel(i+1,labels[i])

        for i in range(48):
            if i%5 == 0: histo.GetXaxis().SetBinLabel(i+1,str(i))

        histo.GetXaxis().LabelsOption("h")
        title = "%s to %s"%(self.date,self.enddate)
        if self.includeDQ:
            title += ": included events with DQ flags"
        else:
            title += ": excluded events with DQ flags"
        histo.SetTitle(title)

        return histo

    def ProcessStop(self):

        global Flag_Chan                            #dictionary containing channels and flag correponding to given flag
        Flag_Chan={}

        n_runs = len(self.run_list)

        lasref       = numpy.ones((12288,n_runs))   # pmt laser reference per run
        deviation    = numpy.zeros((12888,n_runs))  # deviation per pmt per run
        run_info     = numpy.ones((n_runs,3))       # run info-> per run index: gain, day, time_in_seconds

        if n_runs < 20: n_runs = 25
        derivative_lg = numpy.ones((12288,n_runs))   # derivative per pmt per run for low gain
        derivative_hg = numpy.ones((12288,n_runs))   # derivative per pmt per run for high gain
        high_low_dif = numpy.ones((12288,n_runs))   # difference in response to high and low gain
        no_response_lg  = [0 for x in range(12288)]    # flag to handle with channels with no response for low gain
        no_response_hg  = [0 for x in range(12288)]    # flag to handle with channels with no response for high gain

        irun = 0 # run counter
        # loop on runs to calculate derivatives and hl differences
        for run in sorted(self.run_list, key=lambda run: run.runNumber):

            print("Loop on events RUN: ", run.runNumber,'\n')
            iday  = int(run.time.split(' ')[:1][0].rsplit('-')[2:][0])
            itime = run.time_in_seconds
            igain = 0

            for event in self.run_dict[run.runNumber]:

                [part_num, imodule, chan, igain] = event.region.GetNumber()
                pmt_nr = self.PMTool.get_index(part_num-1,imodule-1,chan,igain)
                pmt_nr = (pmt_nr-pmt_nr%2)/2

                # compute the derivative between present run and last run from different day, same gain and same reference
                if irun != 0:
                    for i in range(irun):
                        i+= 1

                        if igain == run_info[irun-i][0] and deviation[pmt_nr][irun-i]!=0 and iday != run_info[irun-i][1] and event.data['lasref_db'] == lasref[pmt_nr][irun-i]:
                            # derivative in % per day
                            if igain == 0: derivative_lg[pmt_nr][irun] = (event.data['deviation']-deviation[pmt_nr][irun-i])/(itime-run_info[irun-i][2])*3600*24
                            if igain == 1: derivative_hg[pmt_nr][irun] = (event.data['deviation']-deviation[pmt_nr][irun-i])/(itime-run_info[irun-i][2])*3600*24
                            break

                # compute low and high gain difference between two consecutive runs from same day
                if irun!=0 and igain!=run_info[irun-1][0] and iday==run_info[irun-1][1] and deviation[pmt_nr][irun-1]!=0:

                    high_low_dif[pmt_nr][irun] = math.fabs(event.data['deviation'] - deviation[pmt_nr][irun-1])
                
                # check if the channel has 'no response' problem
                if 'problems' in event.data:
                    if 'no response' in event.data['problems']: 
                        print('no response')
                        if igain==0: no_response_lg[pmt_nr] = 1
                        if igain==1: no_response_hg[pmt_nr] = 1

                # keep the info needed for the next run
                deviation[pmt_nr][irun] = event.data['deviation']
                lasref[pmt_nr][irun] = event.data['lasref_db']

            run_info[irun][0] = igain
            run_info[irun][1] = iday
            run_info[irun][2] = itime
            irun += 1

        # Compute the variables for flag attribution for each pmt:
        # compute the derivative mean and RMS values and HL dif mean for a 10 run period
        # repeat with a 5 runs offset
        # At the end keep, for each pmt:
        derivative_mean_lg = [0. for x in range(12288)] # maximum derivative mean for low gain
        derivative_rms_lg  = [0. for x in range(12288)] # maximum derivative RMS for low gain
        max_derivative_lg  = [0. for x in range(12288)] # maximum derivative for low gain
	
        derivative_mean_hg = [0. for x in range(12288)] # maximum derivative mean for high gain
        derivative_rms_hg  = [0. for x in range(12288)] # maximum derivative RMS for high gain
        max_derivative_hg  = [0. for x in range(12288)] # maximum derivative for high gain
        
        high_low_mean   = [0. for x in range(12288)] # maximum HL dif mean

        for pmt in range(12288):
            for irun in range(n_runs-20):

                if irun%5 != 0: continue

                ider_mean_lg = 0.
                ider_rms_lg  = 0.
                n_der_lg = 0
		
                ider_mean_hg = 0.
                ider_rms_hg  = 0.
                n_der_hg = 0
		
                ihl_mean  = 0.
                n_hl  = 0

                for i in range(20):
                    if derivative_lg[pmt][irun+i] != 1:

                        ider_mean_lg += derivative_lg[pmt][irun+i]
                        ider_rms_lg  += derivative_lg[pmt][irun+i]*derivative_lg[pmt][irun+i]
                        n_der_lg     += 1
			
                        max_derivative_lg[pmt] = max(max_derivative_lg[pmt],math.fabs(derivative_lg[pmt][irun+i]))
			
                    if derivative_hg[pmt][irun+i] != 1:

                        ider_mean_hg += derivative_hg[pmt][irun+i]
                        ider_rms_hg  += derivative_hg[pmt][irun+i]*derivative_hg[pmt][irun+i]
                        n_der_hg     += 1
			
                        max_derivative_hg[pmt] = max(max_derivative_hg[pmt],math.fabs(derivative_hg[pmt][irun+i]))

                    if high_low_dif[pmt][irun+i] != 1: 

                        ihl_mean += high_low_dif[pmt][irun+i]
                        n_hl     += 1

                if n_der_lg != 0:

                    ider_mean_lg = ider_mean_lg/n_der_lg
                    ider_rms_lg  = math.sqrt(ider_rms_lg/n_der_lg)

                    derivative_mean_lg[pmt] = max(derivative_mean_lg[pmt], math.fabs(ider_mean_lg))
                    derivative_rms_lg[pmt]  = max(derivative_rms_lg[pmt] , ider_rms_lg)
		    
                if n_der_hg != 0:

                    ider_mean_hg = ider_mean_hg/n_der_hg
                    ider_rms_hg  = math.sqrt(ider_rms_hg/n_der_hg)

                    derivative_mean_hg[pmt] = max(derivative_mean_hg[pmt], math.fabs(ider_mean_hg))
                    derivative_rms_hg[pmt]  = max(derivative_rms_hg[pmt] , ider_rms_hg)

                if n_hl != 0:
                    ihl_mean = ihl_mean/n_hl
                    high_low_mean[pmt] = max(high_low_mean[pmt], math.fabs(ihl_mean))

        # Attribute flags
        cut_hl = 5.
        cut_fast = 3.
        cut_low = 2.5
        cut_erratic = 12.
        cut_jump = 10.

        histo = self.InitiateHisto()

        for part_num in range(4):
            for imodule in range(64):

                flagged_digitizer = [0 for x in range(9)]
                pmts_per_dig      = [0 for x in range(9)]
                flagged_dmu = [0 for x in range(16)]
                pmts_per_dmu      = [0 for x in range(16)]
                for chan in range(48):

                    pmt_nr = self.PMTool.get_index(part_num,imodule,chan,0)
                    pmt_nr = (pmt_nr-pmt_nr%2)/2
                    pmt = self.PMTool.get_PMT_index(part_num,imodule,chan)
                    channel_name = self.PMTool.get_channel_name(part_num, imodule,chan)
                    part_name =self.PMTool.get_module_name(part_num,imodule)

                    # Jump non instrumented channels
                    if pmt < 0: continue

                    flagged  = 0
                    flagged2 = 0
                    gain     = ''
                    digitizer = self.PMTool.getDigitizer(part_num,pmt)
                    pmts_per_dig[digitizer] += 1
                    dmu = self.PMTool.getDMU(chan)
                    pmts_per_dmu[dmu] += 1

                    if ('all' in self.lasflag or 'fast' in self.lasflag) and cut_low < derivative_mean_lg[pmt_nr] < cut_fast and cut_low < derivative_mean_hg[pmt_nr] < cut_fast:
                        flagged = 1

                    if ('all' in self.lasflag or 'hl' in self.lasflag) and high_low_mean[pmt_nr] > cut_hl:
                        histo.SetBinContent(chan+1,4,1)
                        flagged  = 1
                        flagged2 = 1
                        print("%15s: %s"%(histo.GetYaxis().GetBinLabel(4),channel_name))
                        if channel_name in Flag_Chan:                                                      # Add the flag to the entry corresponding to a given channel
                            Flag_Chan[channel_name].append(histo.GetYaxis().GetBinLabel(4))                # For each channels there is a list of all the flags affected to it
                        else:
                            Flag_Chan[channel_name]=[histo.GetYaxis().GetBinLabel(4)]
                        gain = "both"
			
                    if ('all' in self.lasflag or 'fast' in self.lasflag) and ( derivative_mean_lg[pmt_nr] > cut_fast or derivative_mean_hg[pmt_nr] > cut_fast ):
                        histo.SetBinContent(chan+1,1,1)
                        flagged  = 1
                        flagged2 = 1
                        if derivative_mean_lg[pmt_nr] > cut_fast and derivative_mean_hg[pmt_nr] <= cut_fast:
                            print("%15s: %s"%(histo.GetYaxis().GetBinLabel(1),channel_name+" low gain"))
                            if (channel_name+" low gain") in Flag_Chan:                                     # Add the flag to the entry corresponding to a given channel
                                Flag_Chan[channel_name+" low gain"].append(histo.GetYaxis().GetBinLabel(1))
                            else:
                                Flag_Chan[channel_name+" low gain"]=[histo.GetYaxis().GetBinLabel(1)]
                            gain = "lowgain"
                        elif derivative_mean_hg[pmt_nr] > cut_fast and derivative_mean_lg[pmt_nr] <= cut_fast: 
                            print("%15s: %s"%(histo.GetYaxis().GetBinLabel(1),channel_name+" high gain"))
                            if (channel_name+" high gain") in Flag_Chan:                                     # Add the flag to the entry corresponding to a given channel
                                Flag_Chan[channel_name+" high gain"].append(histo.GetYaxis().GetBinLabel(1))
                            else:
                                Flag_Chan[channel_name+" high gain"]=[histo.GetYaxis().GetBinLabel(1)]
                            gain = "highgain"
                        elif derivative_mean_lg[pmt_nr] > cut_fast and derivative_mean_hg[pmt_nr] > cut_fast:
                            print("%15s: %s"%(histo.GetYaxis().GetBinLabel(1),channel_name+" low gain"))
                            print("%15s: %s"%(histo.GetYaxis().GetBinLabel(1),channel_name+" high gain"))
                            if channel_name in Flag_Chan:                                                   # Add the flag to the entry corresponding to a given channel
                                Flag_Chan[channel_name].append(histo.GetYaxis().GetBinLabel(1))
                            else:
                                Flag_Chan[channel_name]=[histo.GetYaxis().GetBinLabel(1)]
                            gain = 'both'
			
                    if ('all' in self.lasflag or 'erratic' in self.lasflag) and ( derivative_rms_lg[pmt_nr] > cut_erratic or derivative_rms_hg[pmt_nr] > cut_erratic):
                        histo.SetBinContent(chan+1,2,1)
                        flagged  = 1
                        flagged2 = 1
                        if derivative_rms_lg[pmt_nr] > cut_erratic and derivative_rms_hg[pmt_nr] <= cut_erratic:
                            print("%15s: %s"%(histo.GetYaxis().GetBinLabel(2),channel_name+" low gain"))
                            if (channel_name+" low gain") in Flag_Chan:                                                   # Add the flag to the entry corresponding to a given channel
                                Flag_Chan[channel_name+" low gain"].append(histo.GetYaxis().GetBinLabel(2))
                            else:
                                Flag_Chan[channel_name+" low gain"]=[histo.GetYaxis().GetBinLabel(2)]
                            gain = "lowgain"
                        elif derivative_rms_hg[pmt_nr] > cut_erratic and derivative_rms_lg[pmt_nr] <= cut_erratic:
                            print("%15s: %s"%(histo.GetYaxis().GetBinLabel(2),channel_name+" high gain"))
                            if (channel_name+" high gain") in Flag_Chan:                                                   # Add the flag to the entry corresponding to a given channel
                                Flag_Chan[channel_name+" high gain"].append(histo.GetYaxis().GetBinLabel(2))
                            else:
                                Flag_Chan[channel_name+" high gain"]=[histo.GetYaxis().GetBinLabel(2)]
                            gain = "highgain"
                        elif derivative_rms_lg[pmt_nr] > cut_erratic and derivative_rms_hg[pmt_nr] > cut_erratic:
                            print("%15s: %s"%(histo.GetYaxis().GetBinLabel(2),channel_name+" low gain"))
                            print("%15s: %s"%(histo.GetYaxis().GetBinLabel(2),channel_name+" high gain"))
                            if channel_name in Flag_Chan:                                                   # Add the flag to the entry corresponding to a given channel
                                Flag_Chan[channel_name].append(histo.GetYaxis().GetBinLabel(2))
                            else:
                                Flag_Chan[channel_name]=[histo.GetYaxis().GetBinLabel(2)]
                            gain = 'both'
			
                    if ('all' in self.lasflag or 'jump' in self.lasflag) and ( max_derivative_lg[pmt_nr] > cut_jump or max_derivative_hg[pmt_nr] > cut_jump ):
                        histo.SetBinContent(chan+1,3,1)
                        flagged  = 1
                        flagged2 = 1
                        if max_derivative_lg[pmt_nr] > cut_jump and max_derivative_hg[pmt_nr] <= cut_jump:
                            print("%15s: %s"%(histo.GetYaxis().GetBinLabel(3),channel_name+" low gain"))
                            if (channel_name+" low gain") in Flag_Chan:                                                   # Add the flag to the entry corresponding to a given channel
                                Flag_Chan[channel_name+" low gain"].append(histo.GetYaxis().GetBinLabel(3))
                            else:
                                Flag_Chan[channel_name+" low gain"]=[histo.GetYaxis().GetBinLabel(3)]
                            gain = "lowgain"
                        elif max_derivative_hg[pmt_nr] > cut_jump and max_derivative_lg[pmt_nr] <= cut_jump:
                            print("%15s: %s"%(histo.GetYaxis().GetBinLabel(3),channel_name+" high gain"))
                            if (channel_name+" high gain") in Flag_Chan:                                                   # Add the flag to the entry corresponding to a given channel
                                Flag_Chan[channel_name+" high gain"].append(histo.GetYaxis().GetBinLabel(3))
                            else:
                                Flag_Chan[channel_name+" high gain"]=[histo.GetYaxis().GetBinLabel(3)]
                            gain = "highgain"
                        elif max_derivative_lg[pmt_nr] > cut_jump and max_derivative_hg[pmt_nr] > cut_jump:
                            print("%15s: %s"%(histo.GetYaxis().GetBinLabel(3),channel_name+" low gain"))
                            print("%15s: %s"%(histo.GetYaxis().GetBinLabel(3),channel_name+" high gain"))
                            if channel_name in Flag_Chan:                                                   # Add the flag to the entry corresponding to a given channel
                                Flag_Chan[channel_name].append(histo.GetYaxis().GetBinLabel(3))
                            else:
                                Flag_Chan[channel_name]=[histo.GetYaxis().GetBinLabel(3)]
                            gain = 'both'
			
                    if ('all' in self.lasflag or 'noResponse' in self.lasflag) and (no_response_lg[pmt_nr] == 1 or no_response_hg[pmt_nr] == 1):
                        histo.SetBinContent(chan+1,3,1)
                        flagged  = 1
                        flagged2 = 1
                        if no_response_lg[pmt_nr] > cut_jump and no_response_hg[pmt_nr] <= cut_jump:
                            print("%15s: %s"%("No response",channel_name+" low gain"))
                            if (channel_name+" low gain") in Flag_Chan:                                                   # Add the flag to the entry corresponding to a given channel
                                Flag_Chan[channel_name+" low gain"].append("No response")
                            else:
                                Flag_Chan[channel_name+" low gain"]=["No response"]
                            gain = "lowgain"
                        elif no_response_hg[pmt_nr] > cut_jump and no_response_lg[pmt_nr] <= cut_jump:
                            print("%15s: %s"%("No response",channel_name+" high gain"))
                            if (channel_name+" low gain") in Flag_Chan:                                                   # Add the flag to the entry corresponding to a given channel
                                Flag_Chan[channel_name+" high gain"].append("No response")
                            else:
                                Flag_Chan[channel_name+" high gain"]=["No response"]
                            gain = "highgain"
                        elif no_response_lg[pmt_nr] > cut_jump and no_response_hg[pmt_nr] > cut_jump:
                            print("%15s: %s"%("No response",channel_name+" low gain"))
                            print("%15s: %s"%("No response",channel_name+" high gain"))
                            if (channel_name+" low gain") in Flag_Chan:                                                   # Add the flag to the entry corresponding to a given channel
                                Flag_Chan[channel_name].append("No response")
                            else:
                                Flag_Chan[channel_name]=["No response"]
                            gain = 'both'
                            
                    # For SuperStudyFlags macro
                    global bad_las_list
                    if flagged2 == 1 and gain == 'both':
                        self.entry_lo = {"partition" : part_name[:3], "module" : imodule+1, "channel" : chan, "gain" : 'lowgain'}
                        self.entry_hi = {"partition" : part_name[:3], "module" : imodule+1, "channel" : chan, "gain" : 'highgain'}
                        self.las_flagged.append(self.entry_lo)
                        self.las_flagged.append(self.entry_hi)
                        bad_las_list = self.las_flagged
                    elif flagged2 == 1 and 'gain' in gain:
                        self.entry = {"partition" : part_name[:3], "module" : imodule+1, "channel" : chan, "gain" : gain}
                        self.las_flagged.append(self.entry)
                        bad_las_list = self.las_flagged

                    flagged_digitizer[digitizer] += flagged
                    flagged_dmu[dmu] += flagged

                dig_title = []
                for dig in range(9):
                    if dig == 0: continue
                    if flagged_digitizer[dig] == 0: continue

                    if flagged_digitizer[dig] > pmts_per_dig[dig] - 2:

                        dig_name = "#color[2]{Dig%d}"%dig
                        x_coord = histo.GetXaxis().GetBinCenter((8-dig)*6+2)
                        y_coord = histo.GetYaxis().GetBinCenter(6)
                        dig_title.append(ROOT.TLatex(x_coord,y_coord,dig_name))
                        #print 'dig_name ',dig_name

                dmu_title = []
                for dmu in range(16):

                    if flagged_dmu[dmu] == 0: continue

                    if flagged_dmu[dmu] > pmts_per_dmu[dmu] - 1:

                        dmu_name = "#bf{#color[2]{#scale[0.55]{DMU%d}}}"%dmu
                        x_coord = histo.GetXaxis().GetBinCenter((dmu)*3+1)
                        y_coord = histo.GetYaxis().GetBinCenter(5)*(1-.05*(dmu%2))
                        dmu_title.append(ROOT.TLatex(x_coord,y_coord,dmu_name))
                        #print 'dmu_name ',dmu_name

                if histo.GetEntries() != 0:
                    histo.GetXaxis().SetTitle("%s Channel"%(part_name))
                    histo.Draw("col")

                    for dig in range(len(dig_title)):
                        dig_title[dig].Draw("same")
                    for dmu in range(len(dmu_title)):
                        dmu_title[dmu].Draw("same")
                    if self.doplot:
                        self.c1.Print("%s/%s.png" % (self.dir, part_name))

                histo.Reset()
                self.c1.Clear()

        return 


    def Build_Regions(self, region_list):
        'Re-formats user-created run list to computer-readable runlist'

        Useable_Regions = []
        print(region_list)
        for region in region_list:
            print(region)
            if not '_m' in region:
                for mod in range(1,65):
                    for chan in range(48):
                        Useable_Regions.append('{0}_m{1:02d}_c{2:02d}'.format(region, mod, chan))
            elif not '_c' in region:
                for chan in range(48):
                    Useable_Regions.append('{0}_c{1:02d}'.format(region, chan))
            else:
                Useable_Regions.append(region)
 
        return Useable_Regions

