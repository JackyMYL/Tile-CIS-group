# Author: Henric Wilkens <Henric.Wilkens@cern.ch>
#
# January 04, 2009
#
#import gc

from src.GenericWorker import *

class CleanLaser(GenericWorker):
    "Clear out all events without valid data"

    def ProcessRegion(self, region):
        myEvents = set()
        for event in region.GetEvents():
            if event.run.runType=='Las':            # Apply selection to laser events
                if 'is_OK' in event.data:     # This is set in ReadLaser
                    myEvents.add(event)
                else:
                    del event
            else:                                   # Preserve other event types
                myEvents.add(event)
        region.SetEvents(myEvents)

#    def ProcessStop(self):
#        gc.collect()
#    There will anyway be a garbage collection in go.py 
