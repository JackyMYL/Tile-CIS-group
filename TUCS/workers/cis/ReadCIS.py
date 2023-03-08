# Author: Christopher Tunnell <tunnell@hep.uchicago.edu>
#
# March 04, 2009
#
# September 19. 2011 Fixed retrieval/staging bug, Joshua Montgomery <Joshua.Montgomery@cern.ch>
#
# March 07, 2012 --> ReadCIS now arranged by run number, has companion CleanCIS.py
# This is modeled on ReadLaser.py
# Joshua Montgomery <Joshua.Montgomery@cern.ch>
#
# June 2018 -- This macro can now read old CIS files (pre-2018)
#              in the old processing directory, as well as current ones
#              this  may need to be changed again if the 2018 files are moved
#              Andrew Smith <ancsmith@cern.ch>
# NOTE THAT CLEANCIS.PY MUST FOLLOW READCIS.PY IN ANY MACRO!

import os
from src.ReadGenericCalibration import *
from src.region import *
from math import *
from src.run import *
import random
import time
from workers.cis.common import GetNumber, is_instrumented, get_PMT_index

class ReadCIS(ReadGenericCalibration):
    "Read in CIS calibration factors and quality flags from CIS calibration ntuples"

    def __init__(self, processingDir='/afs/cern.ch/user/t/tilecali/w0/ntuples/cis', turnOffStatCuts=False):
#    def __init__(self, processingDir='/afs/cern.ch/user/t/tilecali/work/public/ntuples/cis', turnOffStatCuts=False):
        self.processingDir = processingDir
        #self.processingDirOld = '/afs/cern.ch/user/t/tilecali/work/public/ntuples/cis'
        self.turnOffStatCuts = turnOffStatCuts
        self.run_dict       = {}
        self.run_list       = []
        self.failedruns     = []
        
    def get_index(self, ros, mod, chan, gain):
        return ros  *64*48*2\
            + mod      *48*2\
            + chan        *2\
            + gain

    def get_bit_index(self, ros, mod, chan, gain, status):
        return ros *64*48*2*4\
            + mod     *48*2*4\
            + chan       *2*4\
            + gain         *4\
            + status

    def ProcessStart(self):
        global run_list
        for run in run_list.getRunsOfType('CIS'):
            
            if run.runNumber < 375187: #January 31st, 2018 (earliest run in new location, checked on 10-23-2018)
                self.processingDir = "/afs/cern.ch/user/t/tilecali/work/public/ntuples/cis"

            elif run.runNumber >= 375187:
                self.processingDir='/afs/cern.ch/user/t/tilecali/w0/ntuples/cis'
                #self.processingDir = "/afs/cern.ch/user/t/tilecali/work/public/ntuples/cis"
            else: 
               pass
            #self.processingDir=processingDir
            
        #filename = "tileCalibCIS_256196_0.root"
            filename = "%s/tileCalibCIS_%s_CIS.0.root" % (self.processingDir,run.runNumber)
            if not os.path.exists(filename):
                #filename = "tileCalibCIS_%s_0.root" % run.runNumber
                filename = "%s/tileCalibCIS_%s_0.root" % (self.processingDir,run.runNumber)
                if not os.path.exists(filename):
                    #filename = "tileCalibTool_%s_CIS.0.root" % run.runNumber
                    filename = "%s/tileCalibTool_%s_CIS.0.root" % (self.processingDir,run.runNumber)
                    if not os.path.exists(filename):
                        print("Error: ReadCISFile couldn't load run", run.runNumber, "...")
                        self.failedruns.append(run.runNumber)
                        continue
            run.data['filename'] = os.path.basename(filename)
            self.run_list.append(run)
            self.run_dict[run.runNumber] = []
            continue

    def ProcessStop(self):
        print('- ProcessStop -')
        # In the finalization loop we store the CIS relevant info
        # For each run we just open the tree once, otherwise it's awfully slow...
        for run in sorted(self.run_list, key=lambda run: run.runNumber):
            print((run.data['filename'])) 

            if run.runNumber < 375187: #January 31st, 2018 (earliest run in new location, checked on 10-23-2018)
                self.processingDir = "/afs/cern.ch/user/t/tilecali/work/public/ntuples/cis"

            elif run.runNumber >= 375187:
                self.processingDir='/afs/cern.ch/user/t/tilecali/w0/ntuples/cis'

            else:
                pass 
            f, t = self.getFileTree(run.data['filename'], 'h3000')
             

            if [f, t] == [None, None]:
                print('Failed for run ',run.runNumber)
                continue
            try:
                t.GetEntry(0)
            except AttributeError:
                print(run.runNumber, f, t)
                print('This failure is only normal if parent marco is Public_Plots')
                continue

            t.SetBranchStatus('*', 0)

            t.SetBranchStatus('calib', 1)
            t.SetBranchStatus('qflag', 1)
            t.SetBranchStatus('chi2', 1)
            t.SetBranchStatus('nDigitalErrors', 1)
            t.SetBranchStatus('BitStatus', 1)

            calib = getattr(t, 'calib')
            qflag = getattr(t, 'qflag')
            chi2 = getattr(t, 'chi2')
            nDigitalErrors = getattr(t, 'nDigitalErrors')
            #BitStatus = getattr(t, 'BitStatus')

    
            for event in self.run_dict[run.runNumber]:     
                event.data['CIS_Clean'] = True
                if event.run != run:
                    print('CIS Event run is not in the right dict', event.run.runNumber, event.region.GetHash(), run.runNumber)
                    event.data['CIS_Clean'] = False
                    continue
                # Get the index of this region within the file
                #[x, y, z, w] = GetNumber(event.data['region'])
                [x, y, z, w] = event.region.GetNumber()

                if get_PMT_index(x-1,y-1,z) < 0:
                    event.data['CIS_Clean'] = False                    
                    continue

                if not hasattr(t, 'nDigitalErrors'):
                    print('this tree has no nDigitalErrors!', event.run.runNumber, region.GetHash())
                    event.data['CIS_Clean'] = False                    
                    continue

                index = self.get_index(x, y - 1, z, w)
                zero_index = self.get_bit_index(x, y-1, z, w, 0)
                one_index = self.get_bit_index(x, y-1, z, w, 1)
                bit_status_dict = {zero_index: [], one_index: []}

#                for bit_index in [zero_index, one_index]:
#                    bitstat = BitStatus[bit_index]
#                    if bitstat != 0:
#                        bitstat_binary = '{0:010b}'.format(BitStatus[bit_index])
#                        bitstat_list = list(bitstat_binary)
#                        for i in range(0,10):
#                            if bitstat_list[i] == '1':
#                                bit_status_dict[bit_index].append(9-int(i))
                event.data['StuckBits'] = {}
                event.data['StuckBits']['AtZero'] = 0 #bit_status_dict[zero_index]
                event.data['StuckBits']['AtOne'] = 0 #bit_status_dict[one_index]
               
                # See if there were even injections
                if int(qflag[index]) & 3  != 3:
                    #print 'CIS Event is missing injections in run', event.run.runNumber, event.data['region']
                    event.data['CIS_Clean']  = False                    
                    continue
                    
                # Start filling the data for this event
                event.data['calibration']    = calib[index]
                event.data['quality_flag']   = int(qflag[index])  #tk remove me temoporary backward compatibility!
                event.data['nDigitalErrors'] = int(nDigitalErrors[index])
                
                # Define problems for the channel
                problems = {}
                
                event.data['chi2'] =   chi2[index]

                # Check for digital errors
                if int(qflag[index]) & 64 != 64:
                    assert(event.data['nDigitalErrors'] != 0)
                    problems['Digital Errors'] = True
                else:
                    problems['Digital Errors'] = False
                    
                # Maximum point in fit range
                if int(qflag[index]) & 16 != 16:
                    problems['Fail Max. Point'] = True
                else:
                    problems['Fail Max. Point'] = False
                    
                # Maximum point in fit range
                if int(qflag[index]) & 8 != 8:
                    problems['Fail Likely Calib.'] = True
                else:
                    problems['Fail Likely Calib.'] = False
                    
                if not self.turnOffStatCuts:
                    # Large RMS cut
                    if int(qflag[index]) & 32 != 32:
                        problems['Large Injection RMS'] = True
                    else:
                        problems['Large Injection RMS'] = False
                        
                    # Chi2
                    if int(qflag[index]) & 128 != 128:
                        problems['Low Chi2'] = True
                    else:
                        problems['Low Chi2'] = False
                    
                if int(qflag[index]) & 256 != 256:
                    problems['Edge Sample'] = True
                else:
                    problems['Edge Sample'] = False
                    
                if  int(qflag[index]) & 512 != 512:
                    problems['Next To Edge Sample'] = True
                else:
                    problems['Next To Edge Sample'] = False
                
                if int(qflag[index]) & 1024 != 1024 and int(event.run.runNumber) > 226470:
                    problems['Stuck Bit'] = True
                else:
                    problems['Stuck Bit'] = False

#               high gain is 1, low gain is 0              
                if (w==0 and calib[index] < 0.14) or\
                   (w==1 and calib[index] < 10):
                    problems['No Response'] = True
                else:
                    problems['No Response'] = False
                
#                if ('low' in event.data['region'] and abs(t.calib[index]-1.29)/1.29 >= .06 and abs(t.calib[index]-1.29)/1.29 <= .15) or\
#                   ('high' in event.data['region'] and abs(t.calib[index]-81.8)/81.8 >= .06 and abs(t.calib[index]-81.8)/81.8 <= .15):
#               high gain is 1, low gain is 0
                if ( w==0 and abs(calib[index]-1.29)/1.29 >= .06 and abs(calib[index]-1.29)/1.29 <= .15) or\
                   ( w==1 and abs(calib[index]-81.8)/81.8 >= .06 and abs(calib[index]-81.8)/81.8 <= .15):

                    problems['Outlier'] = True
                    #print event.data['region']
                else:
                    problems['Outlier'] = False

                event.data['CIS_problems'] = problems
                event.data['time']         = event.run.time_in_seconds

#                 if not ((abs(t.calib[index] - 1.29) > 0.000001 and abs(
#                                                 t.calib[index] - 81.8) > 0.000001)):			
#                     print "\
# Warning: SOMETHING VERY CLOSE TO THE DETECTOR AVERAGE \n \
# IS BEING USED FOR THE CIS CALIBRATIONS IN", event.run.runNumber, event.data['region']
            #f.Close()   ##Close the file for this event to save space
            global failed_to_read_list
            failed_to_read_list = self.failedruns

    def ProcessRegion(self, region):    
        # See if it's a gain      
        newevents = set()
        if 'gain' not in region.GetHash(): 
             for event in region.GetEvents(): 
                 if event.run.runType != 'CIS': 
                     newevents.add(event) 
             region.SetEvents(newevents) 
             return 
        for event in region.GetEvents():
            event.data['CIS_Clean'] = True
            if event.run.runType == 'CIS' and 'filename' in event.run.data:
                self.run_dict[event.run.runNumber].append(event)
        return
