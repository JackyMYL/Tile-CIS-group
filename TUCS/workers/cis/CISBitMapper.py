# Created: December 08, 2012
# Author: Noah Wasserman
#
# This worker creates a plot of a channel's CIS status bit history
# as a function of run number. Must be controlled by the StudyFlag.py 
# supermacro. Can also printout time stability plots if the --timestab 
# option is selected in the macro. For more info use the --h option
# of StudyFlag.py.
#
#
# stdlib imports
import os.path
#TUCS imports
import src.oscalls
import src.MakeCanvas
from src.GenericWorker import *
#ROOT
import ROOT

class CISBitMapper(GenericWorker):

    def __init__(self, plotdirectory='StudyFlag', rundate='No_Specified_Date', runType='CIS', all=False, only_all_flags=False,
                 only_chosen_flag=False, adc_problems=None, flagtype='DB Deviation',
                 only_good_events = True, exts=['png'], maskingbits = True, cal_type="measured",
                 printtimestab=False, ratio_threshold=0.5, flaglist = True):
        
        self.runType           = runType
        self.all               = all
        self.only_all_flags    = only_all_flags
        self.only_chosen_flag  = only_chosen_flag
        self.adc_problems      = adc_problems
        self.flag              = flagtype
        self.plotdirectory     = plotdirectory
        self.only_good_events  = only_good_events
        self.exts              = exts
        self.rundate           = rundate
        self.maskingbits       = maskingbits
        self.cal_type          = cal_type
        self.printtimestab     = printtimestab
        self.ratio_threshold   = ratio_threshold
        self.flaglist          = flaglist                
        self.bitlist           = ['all','DB Deviation', 'Outlier', 'No Response', 'Large Injection RMS', 'Low Chi2', 'Fail Likely Calib.']
        self.unstable          = []
        self.entry             = []
        self.cis_flagged       = []
        
        #maskingbits allows user to print plots based 
        #on combination of flags that cis uses for masking
        #must be one of those in self.bitlist
        if self.maskingbits:
            if self.flag not in self.bitlist:
                print('Selected flag, '+str(self.flag)+', incompatible with "Masking Bits" command, setting to false.')
                self.maskingbits = False
        
        if self.only_chosen_flag:
            if self.flag == 'all':
                self.only_all_flags = True
                self.only_chosen_flag = False
                
        if self.adc_problems:
            adc_title = str()
            if len(self.adc_problems) > 1:
                adc_sep = []
                for xiter in range(len(self.adc_problems)):
                    adc_seps.append('_')
                adczip = list(zip(self.adc_problems, adc_seps))
                titlechain = itertools.chain.from_iterable(adczip)
                adc_title = adc_title.join(list(titlechain))
            else:
                adc_title = adc_title.join(self.adc_problems)
        
        #set up plot directories, create different paths if timestab is selected
        if self.printtimestab:
            if self.adc_problems and not 'ADC' in self.flag:
                self.dirbit  = os.path.join(src.oscalls.getPlotDirectory(), 'cis', self.plotdirectory,
                                            'QFlagHistory', self.rundate, '{0}_{1}'.format(self.flag, adc_title))
                self.dirtime = os.path.join(src.oscalls.getPlotDirectory(), 'cis', self.plotdirectory,
                                            'TimeStability', self.rundate, '{0}_{1}'.format(self.flag, adc_title))
            elif not self.adc_problems:
                self.dirbit  = os.path.join(src.oscalls.getPlotDirectory(), 'cis', self.plotdirectory,
                                            'QFlagHistory', self.rundate, self.flag)
                self.dirtime = os.path.join(src.oscalls.getPlotDirectory(), 'cis', self.plotdirectory,
                                            'TimeStability', self.rundate, self.flag)
            elif 'ADC' in self.flag:
                self.dirbit  = os.path.join(src.oscalls.getPlotDirectory(), 'cis', self.plotdirectory,
                                            'QFlagHistory', self.rundate, adc_title)                        
                self.dirtime = os.path.join(src.oscalls.getPlotDirectory(), 'cis', self.plotdirectory,
                                            'TimeStability', self.rundate, adc_title)
                                            
            src.oscalls.createDir(self.dirbit)
            src.oscalls.createDir(self.dirtime)
                          
        else:    
            if self.adc_problems and not 'ADC' in self.flag:
                self.dirbit  = os.path.join(src.oscalls.getPlotDirectory(), 'cis', self.plotdirectory,
                                            'QFlagHistory', self.rundate, '{0}_{1}'.format(self.flag, adc_title))
            
            elif not self.adc_problems:
                self.dirbit  = os.path.join(src.oscalls.getPlotDirectory(), 'cis', self.plotdirectory,
                                            'QFlagHistory', self.rundate, self.flag)                                    
                
            elif 'ADC' in self.flag:     
                self.dirbit  = os.path.join(src.oscalls.getPlotDirectory(), 'cis', self.plotdirectory,
                                            'QFlagHistory', self.rundate, adc_title)
                                            
            src.oscalls.createDir(self.dirbit)                                
        
        #establish canvas for plots
        self.c1 = src.MakeCanvas.MakeCanvas() #bitmap canvas
        self.c2 = src.MakeCanvas.MakeCanvas() #timestab canvas
    def ProcessStart(self):
        pass
    
    def ProcessStop(self):
        print('UNSTABLE CHANNELS:')
        for index in self.unstable:
        	print(index)

    def process_graph_timestab(self, graph, title, filename, graphDB=False,):
        "format and print a time stability graph"
        print("Time Stability Graph")
        gain = title.split()[-1]
        self.c2.Clear()

        rms = graph.GetRMS(2)
        mean = graph.GetMean(2)

        if graphDB:
            rmsDB = graphDB.GetRMS(2)
            meanDB = graphDB.GetMean(2)

        # format the axes
        x_axis = graph.GetXaxis()
        x_axis.SetTimeDisplay(1)
        x_axis.SetTimeFormat('%d/%m/%y%F1970-01-01 00:00:00')
        x_axis.SetLabelSize(0.04)
        x_axis.SetNdivisions(505)
        xmax = x_axis.GetXmax()
        xmin = x_axis.GetXmin()

        y_axis = graph.GetYaxis()
        ymax = y_axis.GetXmax()
        ymin = y_axis.GetXmin()

        # format the graph
        graph.SetMinimum(ymin * 0.9)
        graph.SetMaximum(ymax * 1.1)
        graph.SetMarkerStyle(20)
        graph.SetMarkerSize(1.3)
        graph.GetYaxis().SetTitle('CIS Constant (ADC count/pC)')
        graph.SetMarkerColor(ROOT.kBlack)
        graph.Draw('AP')

        # +/- 2% and 1% lines around detector wide average
        box2 = ROOT.TBox(xmin, common.DEF_CALIB[gain] * 0.98,
                         xmax, common.DEF_CALIB[gain] * 1.02)
        box2.SetFillColor(ROOT.kRed - 2)
        box2.Draw()

        box = ROOT.TBox(xmin, mean * 0.99,
                        xmax, mean * 1.01)
        box.SetFillColor(ROOT.kGreen - 5)
        box.Draw()

        line = ROOT.TLine()
        line.SetLineWidth(3)
        line.DrawLine(xmin, common.DEF_CALIB[gain],
                      xmax, common.DEF_CALIB[gain])
        line.DrawLine(xmin, mean, xmax, mean)

        graph.Draw("P")  # Draw points over box
        
        if graphDB:
            graphDB.SetMarkerStyle(23)
            graphDB.SetMarkerSize(1)
            graphDB.SetMarkerColor(ROOT.kBlue)
            graphDB.Draw('psame')

        # add a legend
        leg = ROOT.TLegend(0.646, 0.8163636, 0.9485, 1, "", "brNDC")
        leg.SetBorderSize(0)
        leg.SetFillColor(0)
        leg.AddEntry(box2, "\pm2% of detector avg", "f")
        leg.AddEntry(box, "\pm1% of mean", "f")
        leg.AddEntry(graph, "calibration", "P")
        leg.AddEntry(graphDB, "database", "P")
        leg.Draw()

        latex = ROOT.TLatex()
        latex.SetTextAlign(12)
        latex.SetTextSize(0.04)
        latex.SetNDC()

        latex.DrawLatex(0.19, 0.78, "Mean = %0.2f" % mean)
        if graphDB:
             latex.DrawLatex(0.39, 0.78, "DB Mean = %0.2f" % meanDB)
             latex.DrawLatex(0.65, 0.78, "Deviation = {0:.2f} %".format(abs(100*(1-float(mean)/float(meanDB)))))


        latex.DrawLatex(0.1670854, 0.9685315, title)

        # print them out
        #if (rms / common.DEF_CALIB[gain] * 100 > 0.1) or self.all:
        if self.printtimestab:
            for ext in self.exts:
                self.c2.Print('{path}/{name}.{ext}'.format(path=self.dirtime,
                                                       name=filename,
                                                       ext=ext))

        return mean, rms

    def process_graph_bitmap(self, histo, title, filename, runindex, ybinlabels, xbinlabels):
        
        self.c1.Clear()
        self.c1.SetLeftMargin(0.24)
        self.c1.SetRightMargin(0.037)        
        self.c1.SetBottomMargin(.2)
        self.c1.SetGrid(1,1)
        
        histo.SetFillColor(ROOT.kRed)
        
        #format x axis
        x_axis = histo.GetXaxis()
        for entry in xbinlabels:
            x_axis.SetBinLabel(entry, str(xbinlabels[entry]))
        x_axis.LabelsOption("v")  #so run numbers don't overlap
        x_axis.SetTitle("Run Number")
        x_axis.SetLabelFont(42)
        x_axis.SetTitleFont(42)
        x_axis.SetTitleOffset(1.9)
        
        #format y axis
        y_axis = histo.GetYaxis()
        for entry in ybinlabels:
            y_axis.SetBinLabel(entry+1, ybinlabels[entry])
        y_axis.SetLabelSize(.045)
        y_axis.SetTitle("CIS Failure Mode")
        y_axis.SetLabelFont(42)
        y_axis.SetTitleFont(42)
        y_axis.SetTitleOffset(2.6)
        
        #draw plots
        histo.Draw('col')
        
        #create a legend
        leg = ROOT.TLegend(0.80, 0.95, 1.0, .99, "", "brNDC")
        leg.SetFillColor(0)
        leg.SetBorderSize(0)
        leg.AddEntry(histo, "Flag failing","f")
        leg.Draw()        
        
        #format text options
        latex = ROOT.TLatex()
        latex.SetTextAlign(12)
        latex.SetTextSize(0.04)
        latex.SetNDC()
        
        #throw a title on it
        latex.DrawLatex(0.24, 0.968, title)
        
        #print graphs out
        for ext in self.exts:
            self.c1.Print('{path}/{name}.{ext}'.format(path=self.dirbit,name=filename,ext=ext))
    
    def is_good(self, event):
        "Returns 'True' if the event should be processed by ProcessedRegion."
        runtype_match = (event.run.runType == self.runType) #true if event's run type is same as selected
        bad_event = event.data['isBad']  #true if event is bad
        return runtype_match and not bad_event #true if runtype matches and not a bad event
    
    def ProcessRegion(self, region):
        "Plot the bit history of a region."

        if 'gain' not in region.GetHash():
            return

        calibs = []
        
        #parse channel name
        det, partition, module, channel, gain = region.GetHash().split('_') 
        pmt = region.GetHash(1)[16:19]

        for event in region.GetEvents(): #To print out a list of unstable channels
        	if event.run.runType == 'CIS' and event.data['CIS_problems']['Fail Likely Calib.'] == False:
        		calibs.append(event.data['calibration'])    
        if len(calibs) > 0:
        	mean = ROOT.TMath.Mean(len(calibs), array('f', calibs))
        	rms  = ROOT.TMath.RMS(len(calibs), array('f', calibs))
        	if rms/mean*100 > 0.389059:
        		self.unstable.append({"region":region.GetHash(), "rms/mean(%)":rms/mean*100})
        
        for event in region.GetEvents(): #loop through all events in specified time period
        
            if (event.run.runType == self.runType and 'calibratableEvent' in event.data):
                
                if self.only_all_flags:
                    if 'moreInfo' not in event.data and not self.all:
                        continue
                    if not self.all and not event.data['moreInfo']:
                        continue
                    if self.adc_problems:
                        if 'problems' not in event.data and not self.all:
                            continue
                        if not event.data['problems'] and not self.all:
                            continue
                            
                if self.only_chosen_flag: #to only print out the requested flag
                    global stablist       #call channel list, stablist, from MapFlagFailure.py
                    self.stablist = stablist
                    if region.GetHash() not in self.stablist:
                        return
                        

#        for event in region.GetEvents():
#            if event.run.runType == self.runType:
#                if event.data.has_key('CIS_problems'):    
#                    if event.data['CIS_problems']['Outlier'] == true:
#                        print 'Channel '+str(region.GetHash())+' is failing Outlier flag in run '+str(event.run.runNumber)
#                    if event.data['CIS_problems']['No Response'] == true:
#                        print 'Channel '+str(region.GetHash())+' is failing No Response flag in run '+str(event.run.runNumber)
#                    if (event.data['CIS_problems']['Default Calibration'] == true and event.data['CIS_problems']['DB Deviation'] == True):
#                        print 'Channel '+str(region.GetHash())+' is failing DB Deviation but not Default Calibration in run '+str(event.run.runNumber)
#                    if (event.data['CIS_problems']['Low Chi2'] == True and event.data['CIS_problems']['Large Injection RMS'] == True and event.data['CIS_problems']['Fail Likely Calib.'] == True):
#                        print 'Channel '+str(region.GetHash())+' is failing THREE FLAGS!!!! in run '+str(event.run.runNumber)
#                print 'Channel '+str(region.GetHash())+' for run '+str(event.run.runNumber)+' is failing:'
#                for problem in event.data['CIS_problems']:
#                    print problem, event.data['CIS_problems'][problem]

        #Get number of events in the region to determine y-axis length
        
        N = len(region.GetEvents())  #number of events in the region

        histo = ROOT.TH2F("histo","",N,0,N,14,0,14)  #Set up histogram
        printout = 0   #create bit for determining if histogram should be saved/printed


        runmap=[] #stores a run number with bit failure info for each run
        for event in region.GetEvents():  
            if event.run.runType != self.runType:
                continue
            if not self.is_good(event) and self.only_good_events: #uses is_good function to determine if region should be processed
                continue
            if 'CIS_problems' in event.data:

                problemsvector=[] #stores boolean associated with each flag

                for index,problem in enumerate(event.data['CIS_problems']): #loop through status bits

                    problemsvector.append((problem, event.data['CIS_problems'][problem])) #stores flag name and boolean of problem
                
                runmap.append((event.run.runNumber, problemsvector)) #stores run number with flag info
                                                               
                printout = 1 #print this region

        #create counters to calculate percentage of specific flag failures for masking procedure only            
        [self.nRuns, self.nLowChi2, self.nLargeInjectionRMS, self.nFailLikelyCalib] = [0, 0, 0, 0]
        [self.nFlag , self.nOutlier, self.nDBDev, self.nNoResponse] = [0, 0, 0, 0]
        
        if self.maskingbits: #run for masking procedure
            
            #first set of flag failures for masking
            if self.flag == 'Low Chi2' or self.flag == 'Large Injection RMS' or self.flag == 'Fail Likely Calib.':

                for run in runmap: #loops through pair of run number (run[0]) and flag failure info (run[1])

                    for problemvector in run[1]: #loops through status of each flag for a given run number

                        if problemvector[0] == 'Low Chi2' and problemvector[1] == True: #check for LowChi2 failure
                            self.nLowChi2 += 1 #increment counter if failed

                        if problemvector[0] == 'Large Injection RMS' and problemvector[1] == True: #check for LargeRMS failure
                            self.nLargeInjectionRMS += 1 #increment counter if failed

                        if problemvector[0] == 'Fail Likely Calib.' and problemvector[1] == True: #check for LikelyCalib failure
                            self.nFailLikelyCalib += 1 #increment counter if failed
                            
                    self.nRuns += 1 #keep track of total number of runs looked at
                    
                if self.nRuns > 0: #only look at counters for regions with runs
                    LowChi2Ratio = float(self.nLowChi2)/float(self.nRuns) #LowChi2 failure percentage
                    LargeInjectionRMSRatio = float(self.nLargeInjectionRMS)/float(self.nRuns) #LargeRMS failure percentage
                    FailLikelyCalibRatio = float(self.nFailLikelyCalib)/float(self.nRuns) #LikelyCalib failure percentage
                  
                    #print plot only if all three flags fail for more than %50 of runs
                    if LowChi2Ratio >= self.ratio_threshold and LargeInjectionRMSRatio >= self.ratio_threshold and FailLikelyCalibRatio >= self.ratio_threshold:
                        printout = 1
                        
                    else:
                        printout = 0
                
                #if no runs don't print channel       
                else:
                    printout = 0
            
            #Outlier, DB Deviation, or No Response individually comprise the other 3 masking scenarios
            elif self.flag == 'Outlier' or self.flag == 'DB Deviation' or self.flag == 'No Response':
                
                for run in runmap: #loop through runs and flag failure info stored for each run
                
                    for problemvector in run[1]: #loop through all flags in a given run
                    
                        if problemvector[0] == self.flag and problemvector[1] ==True: #checks if flag is failed
                            self.nFlag += 1
                            
                    self.nRuns += 1
                        
                if self.nRuns > 0:
                    FlagRatio = float(self.nFlag)/float(self.nRuns) #percentage of failure for given flag
                    
                    if FlagRatio >= self.ratio_threshold: #must fail >50% (default, can be changed with --tstab argument in StudyFlag.py macro) of time to print
                        printout = 1
            
                    else:
                        printout = 0
            
                else:
                    printout = 0
            
            #determines if any of the above scenarios are failing (LowChi2, LargeRMS, and Likely Calib. simultaneous,
            #or one of Outlier, DB Deviation, or No Response individually   
            elif self.flag == 'all':
            
                for run in runmap:
                
                    for problemvector in run[1]:
                    
                        if problemvector[0] == 'Low Chi2' and problemvector[1] == True:
                            self.nLowChi2 += 1

                        if problemvector[0] == 'Large Injection RMS' and problemvector[1] == True:
                            self.nLargeInjectionRMS += 1

                        if problemvector[0] == 'Fail Likely Calib.' and problemvector[1] == True:
                            self.nFailLikelyCalib += 1                                
    
                        if problemvector[0] == 'Outlier' and problemvector[1] == True:
                            self.nOutlier += 1
                         
                        if problemvector[0] == 'DB Deviation' and problemvector[1] == True:
                            self.nDBDev += 1
                            
                        if problemvector[0] == 'No Response' and problemvector[1] == True:
                            self.nNoResponse += 1
                         
                    self.nRuns += 1
                    
                if self.nRuns > 0:
                    
                    LowChi2Ratio = float(self.nLowChi2)/float(self.nRuns)
                    LargeInjectionRMSRatio = float(self.nLargeInjectionRMS)/float(self.nRuns)
                    FailLikelyCalibRatio = float(self.nFailLikelyCalib)/float(self.nRuns)
                    OutlierRatio = float(self.nOutlier)/float(self.nRuns)
                    DBDevRatio = float(self.nDBDev)/float(self.nRuns)
                    NoResponseRatio = float(self.nNoResponse)/float(self.nRuns)

                    if LowChi2Ratio >= self.ratio_threshold and LargeInjectionRMSRatio >= self.ratio_threshold and FailLikelyCalibRatio >= self.ratio_threshold:
                        printout = 1
                                        
                    elif OutlierRatio >= self.ratio_threshold:
                        printout = 1
                    
                    elif DBDevRatio >= self.ratio_threshold:
                        printout = 1
                        
                    elif NoResponseRatio >= self.ratio_threshold:
                        printout = 1
                        
                    else:
                        printout = 0
                        
                else:
                    printout = 0
          
            else:
                printout = 0

        # Check to see if channels fail each of the flags specified with --flaglist fail at least the threshold
        # percentage of runs for a given run interval.
        if self.flaglist:
            # initialize counter for total number of runs           
            self.nRuns = 0
            #create counters to calculate percentage of specific flag failures            
            [self.nLowChi2, self.nLargeInjectionRMS, self.nFailLikelyCalib, self.nMeanDeviation] = [0, 0, 0, 0]
            [self.nOutlier, self.nDBDev, self.nNoResponse, self.nStuckBit] = [0, 0, 0, 0]
            [self.nDigErrors, self.nMaxPoint, self.nNext2Edge, self.nEdge] = [0, 0, 0, 0]
            possible_flags     = ['Digital Errors', 'Large Injection RMS', 'Low Chi2', 
                'Fail Max. Point', 'Fail Likely Calib.', 'Next To Edge Sample', 'Mean Deviation'
                'Edge Sample', 'DB Deviation', 'No Response', 'Outlier', 'Unstable', 'Stuck Bit', 'all']
            for i in range(len(self.flaglist)):   
                if self.flaglist[i] not in possible_flags:  #Check if valid flags were specified with the --flaglist option
                    print('WARNING: INVALID FLAG SPECIFIED WITH --FLAGLIST. NOT PRINTING PLOTS')
                    printout = 0

            for run in runmap: #loops through pair of run number (run[0]) and flag failure info (run[1])

                for problemvector in run[1]: #loops through status of each flag for a given run number

                    if problemvector[0] in self.flaglist and problemvector[1] == True: #check for flag failure for flags in self.flaglist
                        if problemvector[0] == 'Digital Errors':
                            self.nDigErrors += 1   #increment counter if Digital Errors is in specified flaglist and failed
                        if problemvector[0] == 'Large Injection RMS':
                            self.nLargeInjectionRMS += 1   #increment counter if Large Injection RMS is in specified flaglist and failed
                        if problemvector[0] == 'Low Chi2':
                            self.nLowChi2 += 1   #increment counter if Low Chi2 is in specified flaglist and failed    
                        if problemvector[0] == 'Fail Max. Point':
                            self.nMaxPoint += 1   #increment counter if Fail Max. Point is in specified flaglist and failed
                        if problemvector[0] == 'Fail Likely Calib.':
                            self.nFailLikelyCalib += 1   #increment counter if Fail Likely Calib. is in specified flaglist and failed
                        if problemvector[0] == 'Next To Edge Sample':
                            self.nNext2Edge += 1   #increment counter if Next To Edge Sample is in specified flaglist and failed
                        if problemvector[0] == 'Edge Sample':
                            self.nEdge += 1   #increment counter if Edge Sample is in specified flaglist and failed
                        if problemvector[0] == 'DB Deviation':
                            self.nDBDev += 1   #increment counter if DB Deviation is in specified flaglist and failed
                        if problemvector[0] == 'No Response':
                            self.nNoResponse += 1   #increment counter if No Response is in specified flaglist and failed
                        if problemvector[0] == 'Outlier':
                            self.nOutlier += 1   #increment counter if Outlier is in specified flaglist and failed
                        if problemvector[0] == 'Mean Deviation':
                            self.nMeanDeviation += 1   #increment counter if Mean Deviation is in specified flaglist and failed
                        if problemvector[0] == 'Stuck Bit':
                            self.nStuckBit += 1   #increment counter if Stuck Bit is in specified flaglist and failed
 

                        
                self.nRuns += 1 #keep track of total number of runs looked at
                    
            if self.nRuns > 0: #only look at counters for regions with runs
                #Calculate percentage of failed runs 
                DigErrorsRatio = float(self.nDigErrors)/float(self.nRuns) #Digital Errors failure percentage
                LargeInjectionRMSRatio = float(self.nLargeInjectionRMS)/float(self.nRuns) #LargeRMS failure percentage
                LowChi2Ratio = float(self.nLowChi2)/float(self.nRuns) #LowChi2 failure percentage
                MaxPointRatio = float(self.nMaxPoint)/float(self.nRuns) #Max. Point failure percentage
                FailLikelyCalibRatio = float(self.nFailLikelyCalib)/float(self.nRuns) #LikelyCalib failure percentage
                Next2EdgeRatio = float(self.nNext2Edge)/float(self.nRuns) #Next To Edge Sample failure percentage
                EdgeRatio = float(self.nEdge)/float(self.nRuns) #Edge Sample failure percentage
                DBDevRatio = float(self.nDBDev)/float(self.nRuns) #DB Deviation failure percentage
                NoResponseRatio = float(self.nNoResponse)/float(self.nRuns) #No Response failure percentage
                OutlierRatio = float(self.nOutlier)/float(self.nRuns) #Outlier failure percentage
                MeanDeviationRatio = float(self.nMeanDeviation)/float(self.nRuns) #Mean Dev failure percentage
                StuckBitRatio = float(self.nStuckBit)/float(self.nRuns) #Stuck Bit failure percentage
                  
                #print plot only if all specified flags fail for more than %50 of runs
                counter = 0
                if DigErrorsRatio >= self.ratio_threshold:
                    counter += 1
                if LargeInjectionRMSRatio >= self.ratio_threshold:
                    counter += 1
                if LowChi2Ratio >= self.ratio_threshold:
                    counter += 1
                if MaxPointRatio >= self.ratio_threshold:
                    counter += 1
                if FailLikelyCalibRatio >= self.ratio_threshold:
                    counter += 1
                if Next2EdgeRatio >= self.ratio_threshold:
                    counter += 1
                if EdgeRatio >= self.ratio_threshold:
                    counter += 1
                if DBDevRatio >= self.ratio_threshold:
                    counter += 1
                if NoResponseRatio >= self.ratio_threshold:
                    counter += 1
                if OutlierRatio >= self.ratio_threshold:
                    counter += 1
                if MeanDeviationRatio >= self.ratio_threshold:
                    counter += 1
                if StuckBitRatio >= self.ratio_threshold:
                    counter += 1
                if counter == len(self.flaglist):    #Make sure all specified flags in flaglist are failing at least the threshold percentage of runs
                    printout = 1
                        
                else:
                    printout = 0
            #if no runs don't print channel       
            else:
                printout = 0

            
        sorted_runmap = sorted(runmap) #sort run and flag failure info by run number so plots format in chronological order
         
        xbinlabels=dict()
        ybinlabels=dict()
       
        if printout == 1:
            self.entry = {"partition" : partition, "module" : int(module[1:]), "channel" : int(channel[1:]), "gain" : gain}
            self.cis_flagged.append(self.entry)
            global bad_cis_list
            bad_cis_list = self.cis_flagged
 
            for run_index, run in enumerate(sorted_runmap):
                xbinlabels[run_index+1]=run[0] #associate each run to a number (has to be +1 to account for initial plotting at 0)
                                               #for labeling y axis
            
                for problem_index, problemvector in enumerate(run[1]):
 
                    if len(ybinlabels) < 14: #stop after all flags enumerated since all channels have same number of flags by definition
                        ybinlabels[problem_index] = problemvector[0]
 
#                    if problemvector[0] == 'Default Calibration':
# 
#                        if problemvector[1] == True:
#                            histo.SetBinContent(run_index+1, problem_index+1, 0) #passes flag then no marker if histogram
#                        else:
#                            histo.SetBinContent(run_index+1, problem_index+1, 1) #fill bin if flag is failed
 
#                    else:
 
                    if problemvector[1] == True: #flag 'Default Calibration' is defined oppositely
                        histo.SetBinContent(run_index+1, problem_index+1, 1) #if flag is passed (i.e. channel is not defaulted) fill bin
                    else:
                        histo.SetBinContent(run_index+1, problem_index+1, 0) 
                        
                                        
            title = ''.join([partition, module[1:], ' ', channel,'/', pmt,
                            ' ', gain])
            self.process_graph_bitmap(histo, title, 'QFlagHistory_%s' % region.GetHash(), run_index, 
                                ybinlabels, xbinlabels)
            
            #print time stability plots if timestab selected
            if self.printtimestab:
                print("Time Stability Graph")
                graph = ROOT.TGraph()
                graphDB = ROOT.TGraph()
        
                # fill the graph
                for point, event in enumerate(region.GetEvents()):

                    if event.run.runType != self.runType:
                        continue
                    if not self.is_good(event) and self.only_good_events:
                        continue
                    if self.cal_type == "database":
                        calib = event.data['f_cis_db'] #cis db value
                    elif self.cal_type == "measured":
                        calib = event.data['calibration'] #cis calibration constant
                    elif self.cal_type == "composite":
                        calib_DB = event.data['f_cis_db']
                        calib = event.data['calibration']
                        
                    if self.cal_type == 'composite':
                        print("Set Point Enter")
                        graph.SetPoint(point, event.run.time_in_seconds, calib)
                        graphDB.SetPoint(point, event.run.time_in_seconds, calib_DB)
                        print("Set Poit Exit")
                    else:
                        graph.SetPoint(point, event.run.time_in_seconds, calib)
                
                title = ''.join([partition, module[1:], ' ', channel, '/', pmt, ' ', gain])
                mean, rms = self.process_graph_timestab(graph, title, 'TimeStability_%s' % region.GetHash(),
                                                        graphDB=graphDB)
                                                        
                        
                        

