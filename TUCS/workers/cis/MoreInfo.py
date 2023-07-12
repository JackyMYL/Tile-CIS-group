# Author: Joshua Montgomery <Joshua.Montgomery@cern.ch>
#
# November 3, 2011
#October 9, 2012 Outlier information added

from src.GenericWorker import *

class MoreInfo(GenericWorker):
    'Adding Edge, Next to Edge, No Response, and Outlier information to event.data[moreInfo]'

    def ProcessStart(self):
        self.n    = 0
        self.n_es = 0
        self.n_nr = 0
        self.n_o  = 0

    def ProcessStop(self):
        print('Edge Samples', self.n)
        print('Next To Edge Samples', self.n_es)  
        print('No Response', self.n_nr)
        print('Outliers', self.n_o)

    def ProcessRegion(self, region):
        newevents = set()
        for event in region.GetEvents():
            if event.run.runType == 'CIS' and\
               'CIS_problems' in event.data and\
               'Edge Sample' in event.data['CIS_problems'] and\
               event.data['CIS_problems']['Edge Sample']:
                event.data['moreInfo']=True
                self.n+=1
                
            else:
                event.data['moreInfo']=False
                
            if event.run.runType == 'CIS' and\
               'CIS_problems' in event.data and\
               'Next To Edge Sample' in event.data['CIS_problems'] and\
               event.data['CIS_problems']['Next To Edge Sample']:
                event.data['moreInfo']=True
                self.n_es+=1
                
            else:
                event.data['moreInfo']=False
                
            if event.run.runType == 'CIS' and\
               'CIS_problems' in event.data and\
               'No Response' in event.data['CIS_problems'] and\
               event.data['CIS_problems']['No Response']:
                event.data['moreInfo']=True
                self.n_nr+=1
                
            else:
                event.data['moreInfo']=False
                
            if event.run.runType == 'CIS' and\
               'CIS_problems' in event.data and\
               'Outlier' in event.data['CIS_problems'] and\
               event.data['CIS_problems']['Outlier']:
                event.data['moreInfo']=True
                self.n_o+=1

            else:
                event.data['moreInfo']=False
                
            newevents.add(event)
        region.SetEvents(newevents)
        
        
        
        
        return

