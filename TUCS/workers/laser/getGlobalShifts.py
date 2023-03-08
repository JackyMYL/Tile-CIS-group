############################################################
#
# getGlobalShifts.py
#
############################################################
#
# Author: Seb Viret <viret@in2p3.fr>
#
# July 06, 2009
#
# Goal: 
# Get the overall relative gain variation per partition
#
# Input parameters are:
#
# -> n_iter: the number of iterations necessary to get the offset value 
#  
# -> siglim: the number of st.dev. considered for outlier rejection (for iterations) 
#         
#
# For more info on the LASER system : http://atlas-tile-laser.web.cern.ch
#
#############################################################


from src.GenericWorker import *
from src.region import *
from array import *
import math

from src.laser.toolbox import *

class getGlobalShifts(GenericWorker):
    "This worker computes the partition variation"
    
    # make this runs eventually
    def __init__(self, siglim=2.0, n_iter=5, verbose=False):
        self.siglim     = siglim
        self.n_iter    = n_iter
        self.verbose   = verbose
        
        self.PMTool   = LaserTools()
        self.run_dict       = {}
        self.run_list = []


    def ProcessStart(self):
        
        global run_list
        for run in run_list.getRunsOfType('Las'):
            self.run_list.append(run)
            self.run_dict[run.runNumber] = []
        
    
    # Collect the events for each region
         
    def ProcessRegion(self, region):
        
        for event in region.GetEvents():
            if 'deviation' in event.data:
                self.run_dict[event.run.runNumber].append(event)
                                        

    # We perform the analysis once the events have been collected
         
    def ProcessStop(self):
                 
        for run in sorted(self.run_list, key=lambda run: run.runNumber): # We have to deal with the multi-run case

            # Initialize the partition shifts arrays 
            e_FIL_n   = [0 for x in range(4)]        
            sig_FIL_n = [100000 for x in range(4)]
                    
            # Then compute the corrections iteratively
            for iter in range(self.n_iter): 
            
                n_FIL   = [0 for x in range(4)]
                e_FIL   = [0 for x in range(4)]
                sig_FIL = [0 for x in range(4)]

                for event in self.run_dict[run.runNumber]:


                    if event.data['isBad'] or event.data['status']&0x10:
                        continue
                        
                    [part_num, i, j, w] = self.PMTool.GetNumber(event.data['region'])
                    part_num -= 1
                    var = event.data['deviation']-e_FIL_n[part_num]  
                    if math.fabs(var) < self.siglim*sig_FIL_n[part_num]:
                        n_FIL[part_num] += 1
                        e_FIL[part_num] += var
                
                for i in range(4):
                    if n_FIL[i] != 0:
                        e_FIL[i] /= n_FIL[i]
                        n_FIL[i] = 0
                
                for event in self.run_dict[run.runNumber]:
                    [part_num, i, j, w] = self.PMTool.GetNumber(event.data['region'])
                    part_num -= 1
                    var = event.data['deviation']-e_FIL[part_num]-e_FIL_n[part_num]
                    if math.fabs(var) < self.siglim*sig_FIL_n[part_num]:
                        n_FIL[part_num]   += 1
                        sig_FIL[part_num] += var*var
                    
                for i in range(4):
                    if n_FIL[i] > 1:
                        sig_FIL_n[i] = math.sqrt(sig_FIL[i]/(n_FIL[i]-1))
                        e_FIL_n[i]  += e_FIL[i]
                        

            run.data['part_var'] = e_FIL_n

            if self.verbose: # some printouts
                for i in range(4):

                    print('Run',run.runNumber,': Filter wheel is introducing a global '\
                          , e_FIL_n[i], '+/-', sig_FIL_n[i], '% shift in partition ', self.PMTool.get_partition_name(i))


        
