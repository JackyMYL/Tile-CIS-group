# Author: Joshua Montgomery <Joshua.J.Montgomery@gmail.com>
#
# March 07, 2012
#
from src.GenericWorker import *

class CleanCIS(GenericWorker):
    "Clear out all events where is no valid data"

    def __init__(self):
        
        if 'failed_to_read_list' in globals():
            print('these runs on fail list', failed_to_read_list)
            self.failedrunlist = failed_to_read_list
        else:
            self.failedrunlist = []


    def ProcessRegion(self, region):
        myEvents = set()
        for event in region.GetEvents():
            if event.run.runType=='CIS':
                if not event.run.runNumber in self.failedrunlist:
                #print event.data, event.data['region']
                    if 'gain' in event.region.GetHash():
                        if 'CIS_Clean' in event.data:
                            if event.data['CIS_Clean']:
                                myEvents.add(event)
                        else:
                            print('this is being processed wrong', event.data, event.run.runNumber, event.run.runType)
            else: # Preserve other event types
                myEvents.add(event)
                
        region.SetEvents(myEvents)
        
