# Author: Christopher Tunnell <tunnell@hep.uchicago.edu>
#
# March 04, 2009
#
from src.oscalls import *
from src.region import *
from src.event import *
from ROOT import gROOT,TFile
#import unittest

class GenericWorker(object):
    "Generic Worker Class"

    # one day we'll have test-suites
    #   testsuite = unittest.TestSuite() 

    # Constructor
    def __init__(self, verbose=False):
        if verbose:
            print("Print class set to verbose")
        self.verbose = verbose

    def initHistFile(self,filename='output/Tucs.HIST.root'):
        fullfilename=os.path.join(getResultDirectory(),filename)
        self.HistFile = gROOT.GetFile(fullfilename)
        try:
            self.HistFile.cd()
        except:
            self.HistFile = TFile(fullfilename,'RECREATE')

    # The set of events are passed to processEvents, then processEvent
    # on each of the single events.  This allows classes to pick if they
    # want just events, or the whole set.  handleEvents mainly does checks
    # though.
    def HandleDetector(self, detector):
        if not isinstance(detector, Region):
            print('The following worker was not passed a region', self)
            return

        assert(isinstance(detector, Region))

        type = 'readout'
        if hasattr(self, 'type'):
            type = self.type
                            
        self.ProcessStart()\
        
        for region in detector.RegionGenerator(type):
            self.ProcessRegion(region)

        self.ProcessStop()
            
        return detector

# Make sure people at least implement this
#    def ProcessRegion(self, region):
#        return region

    def ProcessStart(self):
        return

    def ProcessStop(self):
        return
