# Author: Michael Miller <miller@uchicago.edu>
#
# A class for dumping a text file of bad channels in calibration
# runs
#
# February 27, 2009
#

from src.GenericWorker import *
from src.oscalls import *

class DumpIsBadToFile(GenericWorker):
    "A class for dumping a text file of bad channels in calibration runs"

    def __init__(self, runType):
        self.runType = runType
        
    def ProcessStart(self):
        self.fileName = os.path.join(getResultDirectory(),self.runType + "_isBad.txt")
        self.fout = open( self.fileName, "w")

    def ProcessStop(self):
        self.fout.close()


    def ProcessRegion(self, region):
        if len(region.GetEvents()) == 0:
            return

        for event in region.GetEvents():
            if event.run.runType != self.runType:
                continue

            if ('isBad' in event.data and event.data['isBad']) or\
                   ('goodRegion' in event.data and not event.data['goodRegion']):
                x, y, z, w = region.GetNumber(1)
                self.fout.write('%d %02d %02d\n' % (x-1, y, z))
                return

                
        
