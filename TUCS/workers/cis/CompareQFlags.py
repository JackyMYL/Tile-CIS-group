# Author: Christopher Tunnell <tunnell@hep.uchicago.edu>
#
# March 04, 2009
#

from src.GenericWorker import *
import src.MakeCanvas

class CompareQFlags(GenericWorker):
    "Set the CalibBat bit for some runType"

    c1 = None

    def __init__(self, runType = 'CIS'):
        self.runType = runType
        self.nNewNotOld = 0
        self.nNewOld = 0
        self.nNotNewOld = 0
        self.nNotNewNotOld = 0

        self.nNoiseNotLikely = 0
        self.nNoiseLikely = 0
        self.nNotNoiseNotLikely = 0
        self.nNotNoiseLikely = 0

        if self.c1==None:
            self.c1 = src.MakeCanvas.MakeCanvas()
            #self.c1.SetTitle("Put here a nice title")


    def ProcessStop(self):
        print('   New NotOld', self.nNewNotOld)
        print('   New    Old', self.nNewOld)
        print('NotNew    Old', self.nNotNewOld)
        print('NotNew NotOld', self.nNotNewNotOld)
        print()
        print('   Noise NotLikely', self.nNoiseNotLikely)
        print('   Noise    Likely', self.nNoiseLikely)
        print('NotNoise NotLikely', self.nNotNoiseNotLikely) 
        print('NotNoise    Likely', self.nNotNoiseLikely) 
                                        
    
    def ProcessRegion(self, region):
        if 'gain' not in region.GetHash():
            return

        foundGoodUnlikelyCalib = False
        foundGoodNoise = False
        found = False

        FoundNew = False
        FoundOld = False

        mostRecentRun = 0

        for event in region.events:
            if 'quality_flag' in event.data:
                found = True
                mostRecentRun = event.run.runNumber

                if event.data['quality_flag'] & 16 == 16:
                    foundGoodUnlikelyCalib = True
                if event.data['quality_flag'] & 8 == 8:
                    foundGoodNoise = True
                    
                if event.data['quality_flag'] & 24 == 24:
                    FoundNew = True
                if event.data['quality_flag'] & 4 == 4:
                    FoundOld = True

#        for event in region.events:
#            if event.runNumber == mostRecentRun:
#                event.data['isCalibrated'] = FoundNew



        if found:
            if foundGoodNoise and foundGoodUnlikelyCalib:
                self.nNoiseLikely += 1
            if foundGoodNoise and not foundGoodUnlikelyCalib:
                self.nNoiseNotLikely += 1
            if not foundGoodNoise and foundGoodUnlikelyCalib:
                self.nNotNoiseLikely += 1
            if not foundGoodNoise and not foundGoodUnlikelyCalib:
                self.nNotNoiseNotLikely += 1
                                                                            
            if FoundNew and FoundOld:
                self.nNewOld += 1
            if FoundNew and not FoundOld:
                self.nNewNotOld += 1
            if not FoundNew and FoundOld:
                self.nNotNewOld += 1
            if not FoundNew and not FoundOld:
                self.nNotNewNotOld += 1

