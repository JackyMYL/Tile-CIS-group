# Author: Christopher Tunnell <tunnell@hep.uchicago.edu>
#
# March 04, 2009
#

from src.GenericWorker import *

class EdgeCompare(GenericWorker):
    'Edge compare'

    def ProcessStart(self):
        self.n = 0

    def ProcessStop(self):
        print('edge samples', self.n)

    def ProcessRegion(self, region):
        newevents = set()
        for event in region.GetEvents():
            if event.runType == 'CIS' and\
               'CIS_problems' in event.data and\
               'Edge Sample' in event.data['CIS_problems'] and\
               event.data['CIS_problems']['Edge Sample']:
                event.data['moreInfo']=True
                self.n+=1
                
            else:
                event.data['moreInfo']=False
            newevents.add(event)
        region.SetEvents(newevents)
        return
