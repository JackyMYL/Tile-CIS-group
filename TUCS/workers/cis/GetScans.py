# Author: Christopher Tunnell <tunnell@hep.uchicago.edu>
#
# March 04, 2009
#

from src.ReadGenericCalibration import *
from src.region import *
import os
import pickle as pkl
import pandas as pd
class GetScans(ReadGenericCalibration):
    "Grab the graph(s) of CIS scan(s) from the CIS calibration ntuple"

    def __init__(self, processingDir='/afs/cern.ch/user/t/tilecali/w0/ntuples/cis', getScans=True, getScansRMS=False, all=False):
        self.all = all
        self.processingDir = processingDir
        self.getScans = getScans
        self.getScansRMS = getScansRMS
        self.ftDict = {} # Used for linear constant.  Each element is a [TTree, TFile]
        self.badRuns = set()

    def get_index(self, ros, mod, chan, gain):
        return ros  *64*48*2\
            + mod      *48*2\
            + chan        *2\
            + gain

    def ProcessStart(self):
        self.n = 0
        self.data=[]
        self.raw_fit_data=[]

    def ProcessStop(self):
        print('Grabbed %d scans...' % self.n)
    
    def ProcessRegion(self, region):
        # See if it's a gain
        if 'gain' not in region.GetHash():
            return

        # Prepare events
        foundEventToProcess = False
        processRequest = False
        for event in region.GetEvents(): 
            if 'CIS' in event.run.runType:
            
                foundEventToProcess = True

                if ('moreInfo' in event.data and event.data['moreInfo']) or self.all:
                    processRequest = True
                else:
                    continue
            
                if event.run.runNumber and\
                       event.run.runNumber not in self.ftDict:
                    f, t = self.getFileTree('tileCalibCIS_%s_CIS.0.root' % event.run.runNumber, 'h3000')
                    print(os.path.abspath('tileCalibCis_%s_CIS.0.root' % event.run.runNumber))
                    if [f, t] == [None, None]:
                        f, t = self.getFileTree('tileCalibCIS_%s_0.root' % event.run.runNumber, 'h3000')
                        if [f, t] == [None, None]:
                            f, t = self.getFileTree('tileCalibTool_%s_CIS.0.root' % event.run.runNumber, 'h3000')
                            if [f, t] == [None, None]:
                                if event.run.runNumber not in self.badRuns:
                                    print("Error: ReadCISFile couldn't load run", event.run.runNumber, "...")
                                    self.badRuns.add(event.run.runNumber)
                                continue
                    print(f.GetName())
                    templist=f.GetListOfKeys()
                    templist.Print('all')
                    scans = f.Get('cisScans')
                    if (scans):
                        print('scans not null')
                    self.getScans
                    if (scans):
                        print('scans not null again')
                    else:
                        print('scans are null')
                    scans_rms = f.Get('cisScansRMS')
                    if (self.getScans and not scans) or\
                       (self.getScansRMS and not scans_rms) or\
                       (self.getScans and scans.GetName() != 'TMap') or\
                       (self.getScansRMS and scans_rms.GetName() != 'TMap'):
                        if event.run.runNumber not in self.badRuns:
                            print('GetScans: Could not find scans. Maybe use ReadOldCISFile?')
                            self.badRuns.add(event.run.runNumber)
                        continue
                    
                    self.ftDict[event.run.runNumber] = [f, t, scans, scans_rms]

        if not foundEventToProcess:
            return

        # I used the Upward Lowenheim-Skolem Theorem to determine the validity
        # of this statement.  Actually, not really. :)
        if not processRequest and not self.all:
            return

        # counter
        self.n += 1

        newevents = set()

        
        for event in region.GetEvents():
            if event.run.runType == 'CIS':

                # Load up the tree, file and scans for this run
                if event.run.runNumber not in self.ftDict:
                    continue

                [f, t, scans, scans_rms] = self.ftDict[event.run.runNumber]
                t.GetEntry(0) 
                x,y,z,w = region.GetNumber()
                key = 'scan%d_%d_%d_%d' % (x, y-1, z, w)
                if self.getScans and scans:
                    obj = scans.GetValue(key)
                    obj.Print()
                    self.raw_fit_data.append({'region':region.GetHash(), 'x':[obj.GetPointX(i) for i in range(28)], 'y':[obj.GetPointY(i) for i in range(28)]\
                        ,'ex':[obj.GetErrorX(i) for i in range(28)], 'ey':[obj.GetErrorY(i) for i in range(28)]})
                    print("Get X Object",obj.GetPointX(0))
                    print("X lIst",[obj.GetPointX(i) for i in range(28)])

                    gscan = obj.Clone()
                    gscan.Draw("ALP")
                    #gscan.SetFillColor(0)
                    #gscan.SetLineWidth(6)
                    gscan.GetXaxis().SetTitle("Injected Charge (pC)")
                    gscan.GetXaxis().CenterTitle(True)
                    gscan.GetYaxis().SetTitle("Fit CIS Amplitude (ADC counts)")
                    gscan.SetMarkerSize(1.6)
                    gscan.SetMarkerStyle(20)
                    if gscan.GetFunction("fslope"):
                        gscan.GetFunction("fslope").SetLineWidth(5)
                        gscan.GetFunction("fslope").SetLineColor(2)
                    fslope = gscan.GetFunction("fslope")
                    print(fslope)
                    # N = gscan.GetN()
                    
                    # print(f"Region = {region.GetHash()}")
                    # print(f"$\\chi^2$ = {gscan.Chisquare(fslope)}")
                    # print(f"N={N}")
                    # print(f"$\\chi^2/N$ = {gscan.Chisquare(fslope)/N}")
                    chisq_data = {'region':region.GetHash(), 'runNumber':event.run.runNumber, 'CISconstant':event.data['calibration'], 'chi2':gscan.Chisquare(fslope), 'N':gscan.GetN()}
                    self.data.append(chisq_data)
                    print(region.GetHash())

                if self.getScansRMS and scans_rms:
                    event.data['scan_rms'] = (scans_rms.GetValue(key)).Clone()
        
            newevents.add(event)

        outfile = open('/afs/cern.ch/user/p/pcampore/Tucs/CISPulse/chi2_data','wb')
        pkl.dump(self.data,outfile)
        outfile.close()

        outfile = open('/afs/cern.ch/user/p/pcampore/Tucs/CISPulse/fit_datapoints','wb')
        pkl.dump(self.raw_fit_data,outfile)
        outfile.close()
        region.SetEvents(newevents)
