############################################################
#
# ReadLaserLin.py
#
############################################################
#
# Author: Seb Viret <viret@in2p3.fr>
#
# November 26, 2009, modified on March 22, 2010
#
# Goal: 
# Get the Laser event information coming from a linearity run. Read the ROOTuple
# produced with TileLaserLinearityTool:
#
# http://alxr.usatlas.bnl.gov/lxr/source/atlas/TileCalorimeter/TileCalib/TileCalibAlgs/src/TileLaserLinearityCalibTool.cxx?v=head
#
# Input parameters are:
#
# -> processingDir: where to find the ROOTuple processed with TileLaserDefaultTool
#          DEFAULT VAL = '/afs/cern.ch/user/t/tilecali/w0/ntuples/las'
#
# -> signalMin: the minimum VALUE to accept a PMT signal, in pC 
#          DEFAULT VAL = 1pC
#
# -> nEvtCut: the minimum number of events, for a given channel to be recorded
#          DEFAULT VAL = 500
#
#
# For more info on the LASER system : http://atlas-tile-laser.web.cern.ch
#
#############################################################

from src.ReadGenericCalibration import *
import random
import time

# For using the LASER tools
from src.laser.toolbox import *

class ReadLaserLin(ReadGenericCalibration):
    "The Laser Linearity Data Reader"

    processingDir  = None
    numberEventCut = None
    ftDict         = None

    def __init__(self, processingDir='/afs/cern.ch/user/t/tilecali/w0/ntuples/las', signalMin=1, nEvtCut=500):
        self.processingDir  = processingDir # Where are the files located?
        self.numberEventCut = nEvtCut       # Minimum number of entries per channel
        self.signalCut      = signalMin     # Minimum signal (in picoCoulombs)
        self.ftDict         = {}            # ROOT files store
        self.PMTool         = LaserTools()  # LASER toolbox (see /src/laser/)
        self.events         = set()         # Event container
        self.run_list       = set()         # List of runs

        # Below you can choose a reference PMT in the TileCal and look at the linearity w.r.t. it.

        self.r_part         = 1             # Partition of the reference PMT
        self.r_mod          = 18            # Module of the reference PMT
        self.r_chan         = 6             # Number of the reference PMT


    # This macro is just intended to fill the event container, list of runs, and
    # open the rootfiles, if necessary
        
    def ProcessRegion(self, region):

        for event in region.GetEvents():

            if event.runNumber and event.runType == 'Las' and\
                   event.runNumber not in self.ftDict: # Not registered

                f, t = self.getFileTree('tileCalibLAS_LIN_%s_Las.0.root' % event.runNumber, 'h3000')
                
                if [f, t] != [None, None]:
                    self.run_list.add(event.runNumber)
                        
                if [f, t] == [None, None]:
                    f, t = self.getFileTree('tileCalibLAS_LIN_%s.root' % event.runNumber, 'h3000')

                    if [f, t] != [None, None]:
                        self.run_list.add(event.runNumber)
                            
                    if [f, t] == [None, None]:
                        continue # File not found...

                    self.ftDict[event.runNumber] = [f, t]
                    
            if 'lowgain' not in event.data['region']: # We will put HG info with LG info 
                continue

            self.events.add(event)


    #
    # Here we store the info
    #
    # REMINDER : WE have stored only LOW gain events here

    def ProcessStop(self):

        for run in self.run_list: # You could work on many runs
                
            f,t = self.ftDict[run] # Open the ROOTtree
            t.GetEntry(0)       

            # The reference PMT (this is for crosscheck)
            ref = self.PMTool.get_index(self.r_part-1, self.r_mod-1, self.r_chan,0) 
            
            for event in self.events: # Then loop on events
            
                if event.runType != 'Las' or event.runNumber != run:
                    continue
                
                [part, mod, chan, gain] = self.PMTool.GetNumber(event.data['region'])
                 
                if self.PMTool.get_PMT_index(part-1,mod-1,chan) < 0: # Not a channel
                    continue
                
                index = self.PMTool.get_index(part-1, mod-1, chan, gain)

                event.data['is_OK']            = True         # This channel could be calibrated

                event.data['calibration']      = 0.
                event.data['requamp']          = t.requamp    # Requested amplitude
                event.data['time']             = time.mktime(time.strptime(event.time, "%Y-%m-%d %H:%M:%S")) 

                # Here we are creating list, because we will store
                # one value per filter wheel position

                event.data['number_entries']   = []       # Number of entries
                event.data['gain']             = []       # ADC gain
                event.data['residual']         = []       # Residual w.r.t. the linearity (in %)
                event.data['PMT_signal']       = []       # PMT signal
                event.data['PMT_signal_std']   = []       # PMT stddev
                event.data['r_PMT_signal']     = []       # PMT signal of reference PMT
                event.data['r_PMT_signal_std'] = []       # PMT stddev of reference PMT
                event.data['PMTvD_signal']     = []       # PMT/D1 ratio 
                event.data['PMTvD_signal_std'] = []       # PMT/D1 stddev
                event.data['PMTvP_signal']     = []       # PMT/PM1 ratio 
                event.data['PMTvP_signal_std'] = []       # PMT/PM1 stddev 


                event.data['BoxDiode']         = []       # Diode 1 signal
                event.data['BoxDiode_std']     = []       # Diode 1 stddev
                event.data['BoxPMT']           = []       # PMT 1&2 mean signal
                event.data['BoxPMT_std']       = []       # PMT 1&2 mean stddev    
                    
                # Then we store the information collected for each filter position
                # There are eight possible wheel positions (different attenuations)
 
                for filter in range(8): 
            
                    pos  = filter*24576+index # Position in the ntuple of low gain for the event
                    pref = filter*24576+ref   # Position in the ntuple of low gain for the reference
                    
                    # We proceed to some selection cuts 

                    # Selection proceeds as follows:
                    #
                    # First cuts are on the number of events and signal value (they are in pC)
                    #
                    # Then, the gain value with the largest number of events is chosen
                    # This is of particular importance for the gain transition region
                    #

                    #
                    # First pass of cuts: signal and number of entries
                    #
                    
                    if (t.n_LASER_entries[pos] > self.numberEventCut and\
                        t.signal[pos] >= self.signalCut) or \
                        (t.n_LASER_entries[pos+1] > self.numberEventCut and\
                         t.signal[pos+1] >= self.signalCut):

                        # Second pass: choice of the gain

                        if t.n_LASER_entries[pos] > t.n_LASER_entries[pos+1]: # LG signal wins
                            self.LG = 1
                        else:
                            self.LG = 0
                        
                        if t.n_LASER_entries[pref] > t.n_LASER_entries[pref+1]: # LG signal for ref wins
                            self.rLG = 1
                        else:
                            self.rLG = 0

                        # Then we fill the event, taking the correct gain info
                        
                        event.data['number_entries'].append(self.LG*t.n_LASER_entries[pos]+(1-self.LG)*t.n_LASER_entries[pos+1])
                        event.data['gain'].append(1-self.LG)
                        event.data['residual'].append(0.)
                        event.data['PMT_signal'].append(self.LG*t.signal[pos]+(1-self.LG)*t.signal[pos+1])
                        event.data['PMT_signal_std'].append(self.LG*t.signal_s[pos]+(1-self.LG)*t.signal_s[pos+1])
                        event.data['PMTvD_signal'].append(self.LG*t.signal_cor[pos]+(1-self.LG)*t.signal_cor[pos+1])
                        event.data['PMTvD_signal_std'].append(self.LG*t.signal_cor_s[pos]+(1-self.LG)*t.signal_cor_s[pos+1])
                        event.data['PMTvP_signal'].append(self.LG*t.signal_cor2[pos]+(1-self.LG)*t.signal_cor2[pos+1])
                        event.data['PMTvP_signal_std'].append(self.LG*t.signal_cor2_s[pos]+(1-self.LG)*t.signal_cor2_s[pos+1])
                        event.data['r_PMT_signal'].append(self.rLG*t.signal[pref]+(1-self.rLG)*t.signal[pref+1])              
                        event.data['r_PMT_signal_std'].append(self.rLG*t.signal_s[pref]+(1-self.rLG)*t.signal_s[pref+1])  
                        event.data['BoxDiode'].append(t.diode[4*filter])
                        event.data['BoxDiode_std'].append(t.diode_s[4*filter])


                        # For box PMT signal we take the overall mean (PMT signal is constant over time)

                        PMT    = 0.
                        PMTsig = 0.
                        n_pts  = 0

                        for i in range(8):

                            if (t.PMT[2*i] !=0):                                
                                PMT += t.PMT[2*i]
                                PMTsig += t.PMT_s[2*i]*t.PMT_s[2*i]
                                n_pts += 1

                            if (t.PMT[2*i+1] !=0):                                
                                PMT += t.PMT[2*i+1]
                                PMTsig += t.PMT_s[2*i+1]*t.PMT_s[2*i+1]
                                n_pts += 1

                        event.data['BoxPMT'].append(PMT/n_pts)                        
                        event.data['BoxPMT_std'].append(sqrt(PMTsig/n_pts))
                        
                    else: # If the cut is not passed, one still has to fill the list
                        event.data['number_entries'].append(0)
                        event.data['gain'].append(-1)
                        event.data['PMT_signal'].append(0)
                        event.data['PMT_signal_std'].append(0)
                        event.data['PMTvD_signal'].append(0)
                        event.data['PMTvD_signal_std'].append(0)
                        event.data['PMTvP_signal'].append(0)
                        event.data['PMTvP_signal_std'].append(0)
                        event.data['r_PMT_signal'].append(0)
                        event.data['r_PMT_signal_std'].append(0)
                        event.data['BoxDiode'].append(0)
                        event.data['BoxDiode_std'].append(0)
                        event.data['BoxPMT'].append(0)
                        event.data['BoxPMT_std'].append(0)
                        event.data['residual'].append(0.)
            
        self.ftDict = {}
                    
