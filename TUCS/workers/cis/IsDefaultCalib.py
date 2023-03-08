# Author: Christopher Tunnell <tunnell@hep.uchicago.edu>
#
# March 04, 2009
#

from src.GenericWorker import *
import src.MakeCanvas
from math import *

class IsDefaultCalib(GenericWorker):
    "Determine if a CIS default calibration constant is being used"

    c1 = None

    def __init__(self):
        if self.c1==None:
            self.c1 = src.MakeCanvas.MakeCanvas()
            #self.c1.SetTitle("Put here a nice title")

    
    def ProcessStart(self):
        self.ndefaultcalib = 0

    def ProcessStop(self):
        print('Gains with default calibration: ', self.ndefaultcalib)

    def ProcessRegion(self, region):
        if 'gain' not in region.GetHash():
            return

        defaultcalib = False

        for event in region.events:
            if event.run.runType == 'CIS':
                if 'calibration' in event.data:
                    if 'high' in region.GetHash():
                        const = 81.8399963379
                    else:
                        const = 1.27874994278
                    if abs((event.data['f_cis_db'] - const)) < 0.00000001:
                        defaultcalib = True

        if defaultcalib:
#            print 'default calibration found for ', region.GetHash()
            self.ndefaultcalib += 1

        newevents = set()
        for event in region.events:
            if event.run.runType == 'CIS':
                if 'calibration' in event.data:
                    event.data['isDefaultCalib'] = defaultcalib

            newevents.add(event)
        region.events = newevents
