############################################################
#
# getFiberTotals.py
#
############################################################
#
# Author: Henric <Henric.Wilkens@cern.ch>, 
#
# June, 2021
#
# Goal: Get absolute signal level for clear fibres
#
#############################################################


from src.GenericWorker import *
from src.region import *
from src.stats import *
from array import *
import math

from src.laser.toolbox import *

class getFiberTotals(GenericWorker):

    "This worker computes the PP fiber Total signal"
    
    def __init__(self, verbose=False):

        self.PMTool   = LaserTools()
        self.run_dict = {}


    def ProcessStart(self): 

        global run_list
        for run in run_list.getRunsOfType('Las'):
            self.run_dict[run.runNumber] = [stats() for x in range(384)] 
            run.data['fibretotals'] = [0 for x in range(384)]
        return


    def ProcessRegion(self, region):

        if len(region.GetNumber())==4:
            layer = region.GetLayerName()
            cell = region.GetCellName()
            
            [part, module, pmt, gain] = region.GetNumber(1)

            ros = part-1
            drawer = module-1
            fibre = self.PMTool.get_fiber_index(ros, drawer, pmt)
    
            for event in region.GetEvents():            
                # We are going to correct all channels provided they have a deviation 
                if event.run.runType=='Las' and event.data['signal']>0.:
                    if (event.run.data['wheelpos'] == 6) and gain==1:
                        continue

                    if (event.run.data['wheelpos'] == 8) and gain==0:
                        continue
                        
                    self.run_dict[event.run.runNumber][fibre].fill(event.data['signal'])
        return


    def ProcessStop(self):

        global run_list
        for run in run_list.getRunsOfType('Las'):
            for fibre in range(384):
                if self.run_dict[run.runNumber][fibre].n()!=0: 
                    run.data['fibretotals'][fibre] = self.run_dict[run.runNumber][fibre].mean() 
                
        return
