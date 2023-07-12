# Author: Christopher Tunnell <tunnell@hep.uchicago.edu>
#
# March 04, 2009
#

from src.GenericWorker import *

class PrintDB(GenericWorker):
    "A class for printing calibration DB values"

    def ProcessRegion(self, region):
        if len(region.GetEvents()) == 0:
            return

        print((region.GetHash(), region.GetHash(1)))
        for event in region.GetEvents():
            if 'f_cis_db' in event.data:
                print(('\t%s: %f' % (event.run.runType, event.data['f_cis_db'])))
                

        
