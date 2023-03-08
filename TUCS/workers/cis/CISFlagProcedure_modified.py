# Author: Christopher Tunnell <tunnell@hep.uchicago.edu>
# March 04, 2009
#
# Modified: Dave Hollander <daveh@uchicago.edu>
# February 4, 2010

from src.GenericWorker import *
from src.oscalls import *
import src.MakeCanvas
import datetime

class CISFlagProcedure_modified(GenericWorker):
    "Run the CIS flagging procedure to mark problems"

    c1 = None

    def __init__(self, dbCheck=True, add_data_point=False):
#        self.dir = getPlotDirectory()
        self.dbCheck = dbCheck
        self.add_data_point = add_data_point

        if self.c1==None:
            self.c1 = src.MakeCanvas.MakeCanvas()
            #self.c1.SetTitle("Put here a nice title")


    def ProcessStart(self):
        self.fout = open(os.path.join(getResultDirectory(),"noCIS.txt"), "w")
        
        # This number is the required number of calibrations before we consider a channel good.
        self.requiredCalibs = 1
                       
        self.nCalTotal = 0
        self.nCalDigitalErrors = 0
        self.nCalLargeRMS = 0
        self.nCalChi2Low = 0
        self.nCalMaxPoint = 0
        self.nCalLikelyCalib = 0
        self.nCalStuckBit = 0
        self.nCalDeviation = 0

        self.nChanTotal = 0
        self.nChanDigitalErrors = 0
        self.nChanLargeRMS = 0
        self.nChanChi2Low = 0
        self.nChanMaxPoint = 0
        self.nChanLikelyCalib = 0
        self.nChanStuckBit = 0
        self.nChanDeviation = 0
        self.nChanStatistics = 0
        
        self.nGood = 0
        self.nBad = 0

        # the lines below relate to the StudyFlag.py worker.
        try:
            flag
            self.flag = flag
        except:
            self.flag = 'none'
        if self.flag == 'all':
            self.fail_chan_list = fail_chan_list

        
    def ProcessStop(self):
        self.fout.close()

        if self.flag == 'all':
            fail_chan_list = self.fail_chan_list
            #print fail_chan_list
        
        print('Calibrations')
        print('\tTotal:                              ', self.nCalTotal)
        print('\tPassing digital error cut:          ', self.nCalDigitalErrors, self.nCalTotal-self.nCalDigitalErrors)
        print('\tPassing large RMS cut:              ', self.nCalLargeRMS, self.nCalDigitalErrors - self.nCalLargeRMS)
        print('\tPassing low Chi2 cut:               ', self.nCalChi2Low, self.nCalLargeRMS - self.nCalChi2Low)
        print('\tPassing max. value in fit range cut:', self.nCalMaxPoint, self.nCalChi2Low - self.nCalMaxPoint)
        print('\tPassing likely calib cut:           ', self.nCalLikelyCalib, self.nCalMaxPoint - self.nCalLikelyCalib)
        print('\tPassing stuck bit cut:              ', self.nCalStuckBit, self.nCalLikelyCalib-self.nCalStuckBit)
        print('\tPassing <1% deviation cut:          ', self.nCalDeviation, self.nCalStuckBit - self.nCalDeviation)
        
        print('ADC Channels')
        print('\tTotal:                              ', self.nChanTotal)
        print('\tPassing digital error cut:          ', self.nChanDigitalErrors, self.nChanTotal-self.nChanDigitalErrors)
        print('\tPassing large RMS cut:              ', self.nChanLargeRMS, self.nChanDigitalErrors - self.nChanLargeRMS)
        print('\tPassing low Chi2 cut:               ', self.nChanChi2Low, self.nChanLargeRMS - self.nChanChi2Low)
        print('\tPassing max. value in fit range cut:', self.nChanMaxPoint, self.nChanChi2Low - self.nChanMaxPoint)
        print('\tPassing likely calib cut:           ', self.nChanLikelyCalib, self.nChanMaxPoint - self.nChanLikelyCalib)
        print('\tPassing stuck bit cut:              ', self.nChanStuckBit, self.nChanLikelyCalib - self.nChanStuckBit)
        print('\tPassing <1% deviation cut:          ', self.nChanDeviation, self.nChanLikelyCalib - self.nChanDeviation)
        
        print()
        print('Good Regions (>', self.requiredCalibs, 'successful calibrations):', self.nGood)
        print('Bad Regions: ', self.nBad)

        print('For wiki:')
        print('| %s | %d | %d (-%d) | %d (-%d) | %d (-%d) | %d (-%d) | %d (-%d) | %d (-%d) | %d (-%d) | %d |' %\
              (datetime.date.today().strftime("%d/%m/%y"), self.nBad, \
               self.nChanDeviation, self.nChanStuckBit - self.nChanDeviation,\
               self.nChanStuckBit, self.nChanLikelyCalib-self.nChanStuckBit,\
               self.nChanLikelyCalib, self.nChanMaxPoint - self.nChanLikelyCalib,\
               self.nChanMaxPoint, self.nChanChi2Low - self.nChanMaxPoint,\
               self.nChanChi2Low, self.nChanLargeRMS - self.nChanChi2Low,\
               self.nChanLargeRMS, self.nChanDigitalErrors - self.nChanLargeRMS,\
               self.nChanDigitalErrors, self.nChanTotal-self.nChanDigitalErrors,\
               self.nChanTotal
               ))

        
        if self.add_data_point:
            if not os.path.isfile('{0}/Wiki_Status_Log.txt'.format(self.add_data_point)):
                print('WARNING: CANNOT FIND THE WIKI STATUS OUTPUT IN THE EXPORT FOLDER FOR THE PERFORMANCE PLOT DATA')
            wiki_log = open(os.path.join(getResultDirectory(),'{0}/Wiki_Status_Log.txt'.format(self.add_data_point)), 'a')

            wiki_log.write('| %s | %d | %d (-%d) | %d (-%d) | %d (-%d) | %d (-%d) | %d (-%d) | %d (-%d) | %d (-%d) | %d | N/A | \n' %\
              (datetime.date.today().strftime("%d/%m/%y"), self.nBad, \
               self.nChanDeviation, self.nChanStuckBit - self.nChanDeviation,\
               self.nChanStuckBit, self.nChanLikelyCalib-self.nChanStuckBit,\
               self.nChanLikelyCalib, self.nChanMaxPoint - self.nChanLikelyCalib,\
               self.nChanMaxPoint, self.nChanChi2Low - self.nChanMaxPoint,\
               self.nChanChi2Low, self.nChanLargeRMS - self.nChanChi2Low,\
               self.nChanLargeRMS, self.nChanDigitalErrors - self.nChanLargeRMS,\
               self.nChanDigitalErrors, self.nChanTotal-self.nChanDigitalErrors,\
               self.nChanTotal
               ))
           
            wiki_log.close()
        
    def ProcessRegion(self, region):

        # Only look at each gain within some channel
        if 'gain' not in region.GetHash():
            return

        newevents = set()

        # Decrement this number.  This number is the required number of calibrations before we consider a channel good.
        numberCalibs = self.requiredCalibs
        max_progress = 0
        
        for event in region.GetEvents():
            goodEvent = False
            progress = 0
            
            #print event.run.runType
            
            if 'CIS' in event.run.runType:

                if 'CIS_problems' not in event.data:
                     print('below region does not have key problems')
                     print(region.GetHash())
                     print(event.run.runNumber)
                     continue
                assert('CIS_problems' in event.data)
                assert(isinstance(event.data['CIS_problems'], dict))

                problems = event.data['CIS_problems']

                progress = 1
                badqFlag = True
                badDev = False
                self.nCalTotal += 1
                if not problems['Digital Errors']:
                    progress = 2
                    badqFlag = True
                    badDev = False
                    self.nCalDigitalErrors += 1

                    if not problems['Large Injection RMS']:
                        progress = 3
                        badqFlag = True
                        badDev = False
                        self.nCalLargeRMS += 1

                        if not problems['Low Chi2']:
                            progress = 4
                            badqFlag = True
                            badDev = False
                            self.nCalChi2Low += 1

                            if not problems['Fail Max. Point']:
                                progress = 5
                                badqFlag = True
                                badDev = False
                                self.nCalMaxPoint += 1

                                if not problems['Fail Likely Calib.']:
                                    progress = 6
                                    badqFlag = True
                                    badDev = False
                                    self.nCalLikelyCalib += 1


                                    if not problems['Stuck Bit']:
                                        progress = 7
                                        badqFlag = True
                                        badDev = False
                                        self.nCalStuckBit += 1

                                        if 'DB Deviation' not in problems and self.dbCheck:
                                            print('this region missing DB variable')
                                            print(region.GetHash())
                                        if ('DB Deviation' in problems and
                                               not problems['DB Deviation']) or not self.dbCheck:
                                            progress = 8
                                            self.nCalDeviation += 1
                                            badqFlag = False
                                            badDev = False
                                            numberCalibs -= 1
                                            goodEvent = True
                                    else:
                                        pass #stuck bit
                                else:
                                    pass # fail likely calib
                            else:
                                pass # fail max point
                        else:
                            #event.data['dumpScan'] = True
                            pass # fail chi2 low
                    else:
                        #event.data['dumpScan'] = True
                        #print region.GetHash()
                        pass # fail rms
                else:
                    #event.data['dumpScan'] = True
                    #print region.GetHash(), event.data['nDigitalErrors'], problems['Large Injection RMS'], event.data['scan']
                    #c1 = ROOT.TCanvas()
                    #event.data['scan'].Draw("ALP")
                    #c1.Print("blah%s.eps" % region.GetHash())
                                            
                    pass # fail digital errors

            event.data['goodEvent'] = goodEvent
            event.data['badqFlag'] = badqFlag
            event.data['badDev'] = badDev
            event.data['flag_progress'] = progress
            if progress >max_progress:
                max_progress = progress

            newevents.add(event)

        Chi2 = False
        RMS = False
        FailMax = False

        x, y, z, w = region.GetNumber()

        if max_progress >= 1:
            self.nChanTotal += 1
        if max_progress >= 2:
            self.nChanDigitalErrors += 1
        if max_progress >= 3:
            self.nChanLargeRMS += 1
        if max_progress >= 4:
            self.nChanChi2Low += 1
        if max_progress >= 5:
            self.nChanMaxPoint += 1
        if max_progress >= 6:
            self.nChanLikelyCalib += 1
        if max_progress >= 7:
            self.nChanStuckBit += 1
        if max_progress >= 8:
            self.nChanDeviation += 1

        if max_progress == 3:
            Chi2 = True
        if max_progress == 2:
            RMS= True
        if max_progress == 4:
            FailMax = True

        # This is where the channels for noCIS.txt are written.
        if max_progress == 0:
            self.fout.write('%d %d %d %d\n' % (x, y , z, w))

        newevents2 = set()

        for event in newevents:
            if Chi2:
                event.data['Chi2'] = True
            else:
                event.data['Chi2'] = False
            if RMS:
                event.data['RMS'] = True
            else:
                event.data['RMS'] = False
            if FailMax:
                event.data['FailMax'] = True
            else:
                event.data['FailMax'] = False
            
            if numberCalibs <= 0:
                event.data['goodRegion'] = True
            else:
                event.data['goodRegion'] = False

            if max_progress < 7:
                event.data['moreInfo'] = True
            else:
                if 'moreInfo' not in event.data:
                    event.data['moreInfo'] = False
                else:
                    event.data['moreInfo'] = event.data['moreInfo'] | False
                    
            newevents2.add(event)

        if numberCalibs <= 0:
            self.nGood += 1
        else:
            self.nBad += 1
            #print self.nBad, max_progress, region.GetHash()
            if self.flag == 'all':
                self.fail_chan_list.append(region.GetHash())

        region.SetEvents(newevents2)
