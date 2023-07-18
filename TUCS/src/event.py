# Author: Christopher Tunnell <tunnell@hep.uchicago.edu>
#
# March 04, 2009
#

from src.run import *

class Event:
    "This is an event"

    def __init__(self, run, data):
        self.run  = run
        self.region = None
        self.data = data

    def __str__(self):
        return "%s\n%s\n%s" % (self.run, self.region.GetHash(), self.data)

    def SetRegion(self, region):
        self.region = region

