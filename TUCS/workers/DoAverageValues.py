# Author: Henric Wilkens <Henric.Wilkens@cern.ch>, Giullia Di Gregorio <giulia-digregorio@libero.it>
#
#
#import gc

from src.GenericWorker import *
from src.stats import *


class DoAverageValues(GenericWorker):
    "Evaluation of the average"

    def __init__(self, key='gain_Pisa', selection=(lambda event: True), removeOutliers=True, verbose=True):
	
        self.key           = key
        self.selection     = selection
        self.verbose       = verbose
        self.removeOutliers = removeOutliers

    def ProcessRegion(self, region):

        #Here we verify that we are in the correct place (adc level)
        numbers = region.GetNumber()
        if len(numbers)!= 4:
            return 

        stat = stats()
       
        for event in region.GetEvents():

            if self.key not in event.data:
                continue

            if not self.selection(event):
                continue

            stat.fill(event.data[self.key])

        if self.removeOutliers:
            if stat.n()>1:
                mean = stat.mean()
                rms = stat.rms()
            
                stat.reset()
                for event in region.GetEvents():
                
                    if self.key not in event.data:   
                        continue

                    if not self.selection(event):
                        continue

                    if self.key in event.data:   
                        if abs(event.data[self.key]-mean)<2.*rms:
                            stat.fill(event.data[self.key])

            if stat.n()>1:
                mean = stat.mean()
                rms = stat.rms()
            
                stat.reset()
                for event in region.GetEvents():
                
                    if self.key not in event.data:   
                        continue

                    if not self.selection(event):
                        continue
                
                    if self.key in event.data:   
                        if abs(event.data[self.key]-mean)<1.*rms:
                            stat.fill(event.data[self.key])
      
        if stat.n()>1:
            if (self.verbose): print(("%s DoAverageValues: average %8.5f RMS %7.5f from #runs %d" %(region.GetHash(), stat.mean(), stat.rms(), stat.n())))
            region.data[self.key] = stat.mean()
        else:
            if (self.verbose): print(("%s DoAverageValues: lost all events" %(region.GetHash())))

            
