# Author: Christopher Tunnell <tunnell@hep.uchicago.edu>
#
# March 04, 2009
#

from src.ReadGenericCalibration import *
from src.region import *
from TileCalibBlobPython import TileCalibTools, TileBchTools
from TileCalibBlobPython.TileCalibTools import MINRUN, MINLBK, MAXRUN, MAXLBK
from TileCalibBlobObjs.Classes import *

#=== get a logger
import logging
from TileCalibBlobPython.TileCalibLogger import TileCalibLogger, getLogger

class ReadOldCISFile(ReadGenericCalibration):
    "The CIS Calibration Reader with the file format pre-2009"

    def __init__(self, processingDir='/afs/cern.ch/user/t/tilecali/w0/ntuples/cis', cut=3, getScans=False):
        self.processingDir = processingDir
        self.cut = cut
        self.getScans = getScans
        self.ftDict = {} # Used for linear constant.  Each element is a [TTree, TFile]
        self.scanDict = {} # All CIS scan as TGraph, conditionally filled.
        self.badRuns = set()

    def get_index(self, ros, mod, chan, gain):
        return ros  *64*48*2\
            + mod      *48*2\
            + chan        *2\
            + gain

    def ProcessStop(self):
        self.scanDict = {}
    
    def ProcessRegion(self, region):
        # See if it's a gain
        newevents = set()
        if 'gain' not in region.GetHash():
            for event in region.GetEvents():
                if event.run.runType != 'staging':
                    newevents.add(event)
            region.SetEvents(newevents)
            return

        # Prepare events
        foundEventToProcess = False
        for event in region.GetEvents():
            if event.run.runType == 'staging':
                foundEventToProcess = True
            
                if event.run.runNumber and\
                       event.run.runNumber not in self.ftDict:
                    f, t = self.getFileTree('tileCalibCIS_%s_CIS.0.root' % event.run.runNumber, 'h3000')

                    if [f, t] == [None, None]:
                        f, t = self.getFileTree('tileCalibCIS_%s_0.root' % event.run.runNumber, 'h3000')

                        if [f, t] == [None, None]:
                            f, t = self.getFileTree('tileCalibTool_%s_CIS.0.root' % event.run.runNumber, 'h3000')
                                                    
                            if [f, t] == [None, None]:
                                if event.run.runNumber not in self.badRuns:
                                    print("Error: ReadCISFile couldn't load run", event.run.runNumber, "...")
                                    self.badRuns.add(event.run.runNumber)
                                continue
                    #                    if not hasattr(t, 'nDigitalerrors'):
                    self.ftDict[event.run.runNumber] = [f, t]
                    #elif event.run.runNumber not in self.badRuns: 
                    #    print '\tRun %s has new format' % event.run.runNumber
                    #    self.badRuns.add(event.run.runNumber) 

        if not foundEventToProcess:
            return

        if self.getScans and self.scanDict == {}:
            for k, v in self.ftDict.items():
                f, t = v
                if not f.Get('cisScans'):
                    print("Failed to grab scans")
                    
                l = f.Get("cisScans")
                l.SetOwner(True)
                
                gscan = None
                obj = l.First()
                
                while obj != None:
                    gscan = obj.Clone()
                    gscan.Draw("ALP")
                    gscan.SetFillColor(0)
                    gscan.GetXaxis().SetTitle("Injected Charge (pC)")
                    gscan.GetYaxis().SetTitle("Fitted CIS Amplitude (ADC counts)")
                    gscan.GetYaxis().SetLabelSize(0.05)
                    gscan.GetYaxis().SetTitleSize(0.05)
                    gscan.GetXaxis().SetLabelOffset(0.02)
                    gscan.GetXaxis().SetLabelOffset(0.01)
                    gscan.GetXaxis().SetLabelSize(0.05)
                    gscan.GetXaxis().SetTitleSize(0.05)
                    gscan.GetXaxis().SetTitleOffset(0.93)
                    gscan.SetLineWidth(3)
                    gscan.SetMarkerSize(1.6)
                    gscan.SetMarkerStyle(20)
                    if gscan.GetFunction("fslope"):
                        gscan.GetFunction("fslope").SetLineWidth(5)
                        gscan.GetFunction("fslope").SetLineColor(2)
                    
                    self.scanDict['%s_%s' % (k, obj.GetName())] = gscan
                    obj = l.After(obj)
                    
                l.Clear()

        for event in region.GetEvents():
            if event.run.runType != 'staging' or\
                   event.run.runType == 'CIS':             # Keep non-staging/cis events
                newevents.add(event)
            else:
                if event.run.runNumber not in self.ftDict:
                    continue 
                [f, t] = self.ftDict[event.run.runNumber]
                t.GetEntry(0) 
        
                [x, y, z, w] = region.GetNumber()
                index = self.get_index(x, y - 1, z, w)
                if int(t.qflag[index]) & int(self.cut) != self.cut:  # See if we pasked our quality flag mask
                    continue

                if event.run.runType == 'CIS':
                    data = event.data
                else:
                    data = {}

                data['quality_flag'] =  int(t.qflag[index])
                data['calibration'] = t.calib[index]
                data['chi2'] =   t.chi2[index]
                
                if event.run.runNumber < 100489 and\
                       int(t.qflag[index]) & 7 == 7:
                    data['isBad'] = False
                elif event.run.runNumber >= 100489 and\
                     int(t.qflag[index]) & 27 == 27:
                    data['isBad'] = False
                else:
                    data['isBad'] = True

                key = '%d_scan%d_%d_%d_%d' % (event.run.runNumber, x, y-1, z, w)
                if key in self.scanDict:
                    data['scan'] = self.scanDict[key]

                newevents.add(Event('CIS', event.run.runNumber, data, event.run.time))

        region.SetEvents(newevents)
