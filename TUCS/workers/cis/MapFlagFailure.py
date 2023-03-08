# Author: Andrew Hard <ahard@uchicago.edu>
#
# August 19, 2010

"""
This worker plots the frequency for which channels fail a certain flag from the CISFlagProcedure.py worker. It creates a 2D histogram for each partition and gain that includes all of the modules and channels. The worker is called by the StudyFlag.py macro.  By default, the worker looks at channels failing the next to edge flag, but this can easily be changed.
"""

from src.GenericWorker import *
from src.oscalls import *
from src.ReadGenericCalibration import *
from src.region import *
from math import *
import src.MakeCanvas

class MapFlagFailure(GenericWorker):
    "This macro tracks the flag failure rate for each channel"

    def __init__(self, dbCheck=True, flagtype='', path1='output/temp_flag_{0}.log', rundate='NoDateSpecified', path2='', date2='',
                 exclude_other_flags=False, from_studyflag=False, plotdirectory='StudyFlag', adc_problems=None, threshold=False):
        
        self.from_studyflag      = from_studyflag
        self.exclude_other_flags = exclude_other_flags
        self.plotdirectory       = plotdirectory
        self.flagtype            = flagtype
        self.adc_problems        = adc_problems
        self.stablist            = []
        self.threshold           = threshold
        # The folder is defined by the flag studied and the exclude_flags parameter.
        if not self.flagtype:
            raise NameError('The Flag variable has not been passed to MapFlagFailure')
            
        firstpath_date = rundate
        if self.plotdirectory == 'StudyFlag':
            self.dir = os.path.join(getPlotDirectory(), "cis", self.plotdirectory, "QFlagMaps", '{0}_{1}_{2}'.format(
                                        self.flagtype.replace(" ","_"),exclude_other_flags, firstpath_date))
        else:
            self.dir = os.path.join(getPlotDirectory(), "cis", self.plotdirectory, "QFlagMaps",
                                    '{0}_{1}_{2}_plots'.format(self.flagtype.replace(" ","_"),exclude_other_flags, firstpath_date))
        
        createDir(self.dir)
        self.c1 = src.MakeCanvas.MakeCanvas()
        self.dbCheck = dbCheck
        self.fail_chan_list = fail_chan_list
        createDir(os.path.join(getResultDirectory(),'flaglogs/'))
        self.debugtxt = open(os.path.join(getResultDirectory(),'flaglogs/debug.log'), 'w')

    def ProcessStart(self):
        # Declare the 2D histograms showing channel failure rate.
        self.graphs0 = [ROOT.TH2D('graphs0','',64,1,65,48,0,48) for i in range(4)]
        self.graphs1 = [ROOT.TH2D('graphs1','',64,1,65,48,0,48) for i in range(4)]

        # Default values for all calculations are set in the following lists.
        [self.nCalTotal,self.nCalFlag,self.nCalFailFlag] = [0,0,0]
        [self.nChanTotal,self.nChanFlag,self.nChanOtherFlags] = [0,0,0]
        [self.requiredCalibs,self.FailedChan,self.problems] = [1,0,0]
        [self.previousflags,self.entries,self.totals,self.ratios] = [[],{},{},{}]

        # Retrieves info on the flag to be studied.
        # print 'Important list', self.fail_chan_list
        
        self.allflags = ['Digital Errors', 'Large Injection RMS', 'Low Chi2', 'Fail Max. Point', 'Fail Likely Calib.', 
                        'Next To Edge Sample', 'Edge Sample', 'DB Deviation', 'No Response', 'Outlier', 'Unstable', 
                        'Mean Deviation', 'Stuck Bit']
        
        #self.allflags = ['Digital Errors', 'Large Injection RMS', 'Low Chi2', 'Fail Max. Point', 'Fail Likely Calib.']

        
        # Generates list of prior flags in the CIS procedure.
        if (self.exclude_other_flags == True and not self.flagtype in self.allflags and 'ADC' not in self.flagtype):
            print('exclude other flags option not valid when looking at all flags')
            self.debugtxt.write('exclude other flags option ignored because flag not in allflags\
                                possibly because all flags option was also selected \n')
        if (self.exclude_other_flags == True and self.flagtype in self.allflags and self.flagtype ):
            i = 0
            while i < self.allflags.index(self.flagtype):
                stringy = self.allflags[i]
                self.previousflags.append(stringy)
                i += 1
        if self.exclude_other_flags and 'ADC' in self.flagtype:
            self.previousflags = self.allflags
        print('Previous flags in the CIS procedure = ', self.previousflags)

        # Check whether TimingFlag.py is being run.
        try:
            timing_option
            self.timing_option = True
            self.examine = examine
        except:
            self.timing_option = False
                
    def ProcessStop(self):

        self.debugtxt.close()
        # Histogram formatting
        self.c1.cd()
        ROOT.gStyle.SetPalette(1)
        ROOT.gStyle.SetOptStat(0)
        self.c1.SetLeftMargin(0.14)
        self.c1.SetRightMargin(0.14)

        for i in range(4):
            if   i == 0: name = 'LBA'
            elif i == 1: name = 'LBC'
            elif i == 2: name = 'EBA'
            elif i == 3: name = 'EBC'

            graph0 = self.graphs0[i]
            graph0.SetMaximum(1.0)
            graph0.GetXaxis().SetTitle("Module")
            graph0.GetYaxis().SetTitle("Channel number")
            graph0.Draw("COLZ")

            leg1 = ROOT.TLegend(0.6190,0.96,1.0,1.0)
            leg1.SetBorderSize(0)
            leg1.SetFillColor(0)
            leg1.AddEntry(graph0, "failed calibrations / total calibrations","P")          
            leg1.Draw()
        
            pt = ROOT.TPaveText(0.1017812,0.96,0.3053435,1.0, "brNDC")
            pt.AddText("%s Low Gain Status" % name)
            pt.SetBorderSize(0)
            pt.SetFillColor(0)
            pt.Draw()

            self.c1.Print("%s/%sFlagTrack_low.eps" % (self.dir, name)) 
                       
            graph1 = self.graphs1[i]
            graph1.SetMaximum(1.0)
            graph1.SetFillColor(0)
            graph1.GetXaxis().SetTitle("Module")
            graph1.GetYaxis().SetTitle("Channel number")
            graph1.Draw("COLZ")
                                        
            leg2 = ROOT.TLegend(0.6190,0.96,1.0,1.0)
            leg2.SetBorderSize(0)
            leg2.SetFillColor(0)
            leg2.AddEntry(graph1, "failed calibrations / total calibrations","P")
            leg2.Draw()
        
            pt = ROOT.TPaveText(0.1017812,0.96,0.3053435,1.0, "brNDC")
            pt.AddText("%s High Gain Status" % name)
            pt.SetBorderSize(0)
            pt.SetFillColor(0)
            pt.Draw()

            self.c1.Print("%s/%sFlagTrack_high.eps" % (self.dir, name))
                        
        self.c1.Clear()
        

        # Counting the problematic channels discovered in the run list.
        print(' ')
        print('LISTING PROBLEMATIC CHANNELS IN THE SELECTED RUNS AND REGIONS.')
        print(' ')    
        for key in self.ratios:
            a = self.ratios.get(key)
            ## print flag
            ## print key
            if self.threshold:
                if a >= self.threshold:
                    self.stablist.append(key)
                if a == 1:
                    print('  Always failing:')
                    print('     region       = ', key)
                    print('     failure rate = ', a)
                    # if timing_option is true, list is made for GetSamples.py.
                    if self.timing_option == True:
                        self.examine.append(key)
                    self.FailedChan += 1
                    self.problems   += 1
                elif a >= 0.5:
                    print('  Failing over 50% of runs:')
                    print('     region       = ', key)
                    print('     failure rate = ', a)
                    if self.timing_option == True:
                        self.examine.append(key)
                    self.problems += 1
    
                elif a != 0:
                    self.problems += 1
                    ## self.stablist.append(key)
            else:
                if a == 1:
                    print('  Always failing:')
                    print('     region       = ', key)
                    print('     failure rate = ', a)
                    # if timing_option is true, list is made for GetSamples.py.
                    if self.timing_option == True:
                        self.examine.append(key)
                    self.FailedChan += 1
                    self.problems   += 1
                    self.stablist.append(key)
                elif a >= 0.5:
                    print('  Failing over 50% of runs:')
                    print('     region       = ', key)
                    print('     failure rate = ', a)
                    if self.timing_option == True:
                        self.examine.append(key)
                    self.problems += 1
                    self.stablist.append(key)

                elif a != 0:
                    self.problems += 1
                    ## self.stablist.append(key)
                    ## print >> tempfile, '  Failing at least one of the runs:'
                    ## print >> tempfile, '     region       = ', key
                    ## print >> tempfile, '     failure rate = ', a
                
    # Prints a summary of the results.
        print(' ')       
        print('TOTAL CHANNELS EXPERIENCING PROBLEMS  =  ', self.problems)
        print(' ')
        if self.exclude_other_flags == True:
            print('Only considering events that were not failed by prior flags in the CIS procedure.')
        else:
            print('Considering all events that failed the selected flag.')
        print(' ')
        if self.adc_problems and 'ADC' in self.flagtype:
            print('Calibration Data for ', self.adc_problems, ' flag:')
        elif self.adc_problems and not 'ADC' in self.flagtype:
            print('Calibration Data for ', self.flagtype, 'and', self.adc_problems, ' flag:')
        else:
            print('Calibration Data for ', self.flagtype, ' flag:')
        print('     Total Number of Calibrations              =  ', self.nCalTotal)
        print('     Calibrations Passing Flag                 =  ', self.nCalFlag)
        print('     Calibrations Failing Flag                 =  ', self.nCalFailFlag) 
        print(' ')
        if self.adc_problems and 'ADC' in self.flagtype:
            print('Channel Data for ', self.adc_problems, ' flag:')
        elif self.adc_problems and not 'ADC' in self.flagtype:
            print('Channel Data for ', self.flagtype, 'and', self.adc_problems, ' flag:')
        else:
            print('Channel Data for ', self.flagtype, ' flag:')
        print('     Total Number of Channels                  =  ', self.nChanTotal)

        if self.exclude_other_flags == True:
            print('     Chan pass prior flags                     =  ', self.nChanOtherFlags)
            print('     Chan pass prior flags and chosen flag     =  ', self.nChanFlag)
            print('     Chan pass prior flags & fail chosen flag  =  ', self.nChanOtherFlags - self.nChanFlag, ' = ', self.FailedChan)
            
        elif self.exclude_other_flags == False:
            print('     Total channels passing selected flag      =  ', self.nChanFlag)
            print('     Total channels failing selected flag      =  ', self.nChanOtherFlags - self.nChanFlag, ' = ', self.FailedChan)
        print(' ')

        if self.timing_option == True:
            global examine
            examine = self.examine
        global stablist
        stablist = self.stablist
        print(stablist)
        
    def ProcessRegion(self, region):
        if 'gain' not in region.GetHash():
            return

        newevents = set()
        numberCalibs = self.requiredCalibs
        max_progress = 0

        # x: partition, y: module, z: channel, w: gain.
        [x, y, z, w] = region.GetNumber()
        x = x - 1

        # Data formatting
        namelist = ['LBA','LBC','EBA','EBC']
        modname = namelist[x]
        gainlist = ['lowgain','highgain']
        gainname = gainlist[w]

        if y/10 < 1: y1 = '0%d' % y
        else: y1 = y

        if z/10 < 1: z1 = '0%d' % z
        else: z1 = z

        # Just defining an index format that includes all location information.
        channel_index = 'TILECAL_%s_m%s_c%s_%s' % (modname, y1, z1, gainname)

        # This section plots no data channels and failing channels (flags=all feature).
        if self.flagtype == 'all':
            
            if region.GetHash() in self.fail_chan_list:
                self.debugtxt.write(region.GetHash()+ '  is on the fail_chan_list \n')
                if w == 0:
                    self.graphs0[x].SetBinContent(y, z+1, 1)
                if w == 1:
                    self.graphs1[x].SetBinContent(y, z+1, 1)

            try: self.totals[channel_index]
            except:
                ## print 'we are in the except block'
                self.entries[channel_index] = 0
                self.ratios[channel_index] = 0
                self.totals[channel_index] = 0
            for event in region.GetEvents():
                goodEvent = False
                progress = 0
                ratio0 = 0
                ratio1 = 0

                self.nCalTotal += 1
                ## print self.nCalTotal

                if event.run.runType == 'CIS':
                    assert('CIS_problems' in event.data)
                    assert(isinstance(event.data['CIS_problems'], dict))
                    CIS_problems = event.data['CIS_problems']
                    progress = 1
                    self.totals[channel_index] += 1


                    if self.exclude_other_flags == False:
                        progress = 2
                        adcfailpoint = False
                        failpoint = True
                        for keys in self.allflags:
                            if keys not in CIS_problems:
                                print((region.GetHash()+' does not have {0} key, setting to True'.format(keys)))
                                self.debugtxt.write(region.GetHash()+'  missing problem key {0} \n'.format(keys))
                                CIS_problems[keys] = True
                            if not CIS_problems[keys]:
                                progress = 3
                                failpoint = False
                        
                        if self.adc_problems:
                            if 'problems' in event.data:
                                assert(isinstance(event.data['problems'], set))
                                adcproblems = event.data['problems']
                                adcfailpoint = True
                                for piter in range(len(self.adc_problems)):
                                    if not self.adc_problems[piter] in adcproblems:
                                        adcfailpoint = False
                                        progress = 3
                        

                        if not failpoint and not adcfailpoint:
                            self.nCalFlag += 1
                        elif failpoint or adcfailpoint:
                            self.nCalFailFlag += 1
                            self.entries[channel_index] += 1


                        if self.totals[channel_index] != 0:
                            ## Print 'we are adding to the totals'
                            self.ratios[channel_index] = float(self.entries[channel_index])/float(self.totals[channel_index])
                            ## Fills the 2D histograms with the most recent fractions.
                            ## Print self.ratios[channel_index]
                            if w == 0:
                                self.graphs0[x].SetBinContent(y, z+1, self.ratios[channel_index])
                            if w == 1:
                                self.graphs1[x].SetBinContent(y, z+1, self.ratios[channel_index])

                    if progress >max_progress:
                        max_progress = progress
                    if max_progress == 3:
                        goodEvent = True
                    event.data['goodEvent'] = goodEvent
                    event.data['flag_progress'] = progress   
                    newevents.add(event)

                if max_progress >= 1:
                    self.nChanTotal += 1 
                if max_progress >= 2:
                    self.nChanOtherFlags += 1
                if max_progress == 3:
                    self.nChanFlag += 1

        ## This section plots channels failing particular flags.
        elif self.flagtype in self.allflags:
             try: self.totals[channel_index]
             except:
                 self.totals[channel_index] = 0 
                 self.entries[channel_index] = 0
                 self.ratios[channel_index] = 0

             for event in region.GetEvents():
                 #if event.data['CIS_problems'].has_key('Unstable'):
                 #    print region.GetHash(), event.run.runNumber, event.data['CIS_problems']['Unstable']
                 goodEvent = False
                 progress = 0
                 ratio0 = 0
                 ratio1 = 0

                 self.nCalTotal += 1

                 if event.run.runType == 'CIS':
                     
                     if 'CIS_problems' not in event.data:
                        print(event.run.runNumber, event.region.GetHash(), region.GetHash())
                        continue
                     assert(isinstance(event.data['CIS_problems'], dict))
                     CIS_problems = event.data['CIS_problems']
                     if self.flagtype not in CIS_problems:
                         print((region.GetHash()+' does not have this key, setting to True'))
                         self.debugtxt.write(region.GetHash()+'  missing problem key {0} \n'.format(self.flagtype))
                         CIS_problems[self.flagtype] = True
                         continue
                     progress = 1
                     self.totals[channel_index] += 1

                     if self.exclude_other_flags == True:
                         val = 0
                  
                         for r in self.previousflags:
                             if not CIS_problems[r]:
                                 val += 1

                         ## This selects runs that passed prior flags.
                         if val == self.allflags.index(self.flagtype):
                             progress = 2

                         if progress == 2 and not CIS_problems[self.flagtype]:
                            adcpasspoint = True
                            if self.adc_problems:
                                if 'problems' in event.data:
                                    assert(isinstance(event.data['problems'], set))
                                    for piter in range(len(self.adc_problems)):
                                        if self.adc_problems[piter] in event.data['problems']:
                                            adcpasspoint = False
                            if adcpasspoint:
                                progress = 3
                                self.nCalFlag += 1
                            else:
                                self.nCalFailFlag += 1
                                self.entries[channel_index] += 1

                         elif progress == 2 and CIS_problems[self.flagtype]:
                             self.nCalFailFlag += 1
                             self.entries[channel_index] += 1
                             

                     elif self.exclude_other_flags == False:
                         progress = 2
                  
                         if not CIS_problems[self.flagtype]:
                             adcpasspoint2 = True
                             if self.adc_problems:
                                 if 'problems' in event.data:
                                     assert(isinstance(event.data['problems'], set))
                                     for piter in range(len(self.adc_problems)):
                                         if self.adc_problems[piter] in event.data['problems']:
                                             adcpasspoint2 = False
                             if adcpasspoint2:
                                progress = 3
                                self.nCalFlag += 1
                             else:
                                self.nCalFailFlag += 1
                                self.entries[channel_index] += 1
                                        
                         elif CIS_problems[self.flagtype]:
                             self.nCalFailFlag += 1
                             self.entries[channel_index] += 1

         
                     if self.totals[channel_index] != 0:
                         self.ratios[channel_index] = float(self.entries[channel_index])/float(self.totals[channel_index])
                         # Fills the 2D histograms with the most recent fractions.
                         if w == 0:
                             self.graphs0[x].SetBinContent(y, z+1, self.ratios[channel_index])
                         if w == 1:
                             self.graphs1[x].SetBinContent(y, z+1, self.ratios[channel_index])

                 event.data['goodEvent'] = goodEvent
                 event.data['flag_progress'] = progress   
                 if progress >max_progress:
                     max_progress = progress
                 newevents.add(event)
           
             if max_progress >= 1:
                 self.nChanTotal += 1 
             if max_progress >= 2:
                 self.nChanOtherFlags += 1
             if max_progress == 3:
                 self.nChanFlag += 1
                 
#######################################################################
######################### OTHER COOL BITS #############################
#######################################################################
        elif 'ADC' in self.flagtype:
             try: self.totals[channel_index]
             except:
                 self.totals[channel_index] = 0 
                 self.entries[channel_index] = 0
                 self.ratios[channel_index] = 0

             for event in region.GetEvents():
                 goodEvent = False
                 progress = 0
                 ratio0 = 0
                 ratio1 = 0

                 self.nCalTotal += 1

                 if event.run.runType == 'CIS':
                     if self.adc_problems:
                        if 'problems' in event.data:
                            assert(isinstance(event.data['problems'], set))
                            adcproblems = event.data['problems']
                            #print adcproblems
                        else:
                            adcproblems = ['']
                     else:                         
                         print('something is wrong, the flagtype has been given an "ADC" prefix \
                                but there is no self.adc_problems list. This will not work -- skipping this worker')
                         self.debugtxt.write('something is wrong, the flagtype has been given an "ADC" prefix \
                                but there is no self.adc_problems list. This will not work -- skipping this worker')
                         continue
                     ## Print problems[self.flag]
              
                     progress = 1
                     self.totals[channel_index] += 1

                     if self.exclude_other_flags == True:
                         failprior = False
                         for r in self.previousflags:
                             if problems[r]:
                                 failprior = True

                         ## This selects runs that passed prior flags.
                         if not failprior:
                             progress = 2

                         if progress == 2:
                             adcfails = False
                             for piter in range(len(self.adc_problems)):
                                 if self.adc_problems[piter] in adcproblems:
                                    adcfails = True
                             
                             if not adcfails:
                                 progress = 3
                                 self.nCalFlag += 1
                             
                             if adcfails:
                                 self.nCalFailFlag += 1
                                 self.entries[channel_index] += 1

                     elif not self.exclude_other_flags:
                        progress = 2
                        adcfails = False
                        for piter in range(len(self.adc_problems)):
                            #print piter
                            if self.adc_problems[piter] in adcproblems:
                                adcfails = True
                        if not adcfails:
                            progress = 3
                            self.nCalFlag += 1
                             
                        if adcfails:
                            self.nCalFailFlag += 1
                            self.entries[channel_index] += 1

         
                     if self.totals[channel_index] != 0:
                         self.ratios[channel_index] = float(self.entries[channel_index])/float(self.totals[channel_index])
                         # Fills the 2D histograms with the most recent fractions.
                         if w == 0:
                             self.graphs0[x].SetBinContent(y, z+1, self.ratios[channel_index])
                         if w == 1:
                             self.graphs1[x].SetBinContent(y, z+1, self.ratios[channel_index])

                 event.data['goodEvent'] = goodEvent
                 event.data['flag_progress'] = progress   
                 if progress >max_progress:
                     max_progress = progress
                 newevents.add(event)
           
             if max_progress >= 1:
                 self.nChanTotal += 1 
             if max_progress >= 2:
                 self.nChanOtherFlags += 1
             if max_progress == 3:
                 self.nChanFlag += 1
                 
      
