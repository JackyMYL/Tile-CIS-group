# Author: Dave Hollander <daveh@uchicago.edu>
#
# April 19, 2010
# Only to be used for pre may 31 2010 ntuples

from src.ReadGenericCalibration import *
from src.oscalls import *
from src.region import *
from array import array
from src.MakeCanvas import *
from ROOT import TFile

class timingCIS(ReadGenericCalibration):
    "Get the fitted time for channels in a module as a function of injected charge"
    
    def __init__(self, processingDir='root://castoratlas//castor/cern.ch/atlas/atlascerngroupdisk/det-tile/2010/',\
                 getSamples=True, getInjDist=True, all=False):
        self.processingDir = processingDir
        self.all=all
        self.ftDict = {} # Used for linear constant.  Each element is a [TTree, TFile]
        self.badRuns = set()
        self.dir = getPlotDirectory() + "/cis"
        createDir('%s/timing' % self.dir)
        self.dir = '%s/timing' % self.dir
        createDir(self.dir) 
        self.c1 = MakeCanvas()
        self.c1.SetHighLightColor(2)
        
        
    def ProcessStart(self):
        self.timeEny2D_hi = ROOT.TProfile2D('timeEny2D', '', 48, 0, 48, 12, -1, 13)
        self.timeEny2D_lo = ROOT.TProfile2D('timeEny2D', '', 48, 0, 48, 40, 50, 800)

        
    def ProcessStop(self):
        if self.timeEny2D_hi and self.timeEny2D_lo:
            self.c1.cd()
            self.c1.SetLeftMargin(0.14)
            self.c1.SetRightMargin(0.14)
            ROOT.gStyle.SetPalette(1)
            self.c1.Print("%s/timing_stack_%s.ps[" % (self.dir, self.module))
            self.timeEny2D_hi.GetXaxis().SetTitle("PMT - 1 (high gain)")
            self.timeEny2D_lo.GetXaxis().SetTitle("PMT - 1 (low gain)")
                
            for timeEny in [self.timeEny2D_hi, self.timeEny2D_lo]:
                timeEny.GetYaxis().SetTitle("Injected charge (pC)")
                timeEny.GetZaxis().SetTitle("Fitted time (ns)")
                timeEny.Draw('COLZ')
                self.c1.Print("%s/timing_stack_%s.ps" % (self.dir, self.module))

            self.c1.Print("%s/timing_stack_%s.ps]" % (self.dir, self.module))
        else:
            pass
           
    
    def ProcessRegion(self, region):
        # See if it's a gain
        if 'gain' not in region.GetHash():
            return

        self.c1.cd()
                       
        dirstr = '%s%02d' % (region.GetHash().split('_')[1], int(region.GetHash().split('_')[2][1:]))
        factor = 2.0*4.096*100.0/1023.0 # From TileCisDefaultCalibTool.cxx
                        
        # Prepare events
        foundEventToProcess = False
        [x, y, z, w] = region.GetNumber()
      
        for event in region.GetEvents():                       
            if event.runType == 'CIS':
                               
                if 'moreInfo' not in event.data and not self.all:
                    continue                
                if not self.all and not event.data['moreInfo']:
                    continue
                              
                foundEventToProcess = True

                if event.runNumber and\
                       event.runNumber not in self.ftDict:
                    
                    print('%s%s/tiletb_%s_CIS.%s.0.aan.root' % (self.processingDir, dirstr, event.runNumber, dirstr))
                    f = TFile.Open('%s%s/tiletb_%s_CIS.%s.0.aan.root' % (self.processingDir, dirstr, event.runNumber, dirstr), "read")

                    if f == None:
                        t = None
                    else:
                        t = f.Get('h1000')
                    
                    if [f, t] == [None, None]:
                        if event.runNumber not in self.badRuns:
                            print("Error: GetSamples couldn't load run", event.runNumber, ' for %s...' % dirstr)
                            self.badRuns.add(event.runNumber)
                        continue
                    self.ftDict[event.runNumber] = [f, t]

        
        if not foundEventToProcess:
            return

        map = {'LBA': 'A', 'LBC': 'C', 'EBA': 'D', 'EBC': 'E'}
        if 'lowgain' in region.GetHash():
            gain = 'lo'
        else:
            gain = 'hi'

        module = int(region.GetHash().split('_')[2][1:])
        chan = int(region.GetHash(1).split('_')[3][1:]) - 1
        partition = region.GetHash().split('_')[1]

        self.module = dirstr

        if not event.runNumber in self.badRuns:                
            newevents = set()
            self.c1.Print("%s/timing_%s.ps[" % (self.dir, region.GetHash()))
            for event in region.GetEvents():
                if event.runType == 'CIS':
                    timeEny_lo = ROOT.TProfile("fitted time", "", 48, 0, 800)
                    timeEny_hi = ROOT.TProfile("fitted time", "", 12, 0, 12)
                    ROOT.gStyle.SetOptStat(0)

                    if not self.all and \
                           ('moreInfo' in event.data and not event.data['moreInfo']):
                        continue

                    # Load up the tree, file and scans for this run
                    if event.runNumber not in self.ftDict:
                        continue

                    [f, t] = self.ftDict[event.runNumber]

                    injections = {}

                    nevt = t.GetEntries()

                    j = 0
                    #t.Print()
                    for i in range(300, nevt):
                        if t.GetEntry(i) <= 0:
                            print('huh?')
                            return

                        # Make sure that it is the 100 pF capacitor
                        if t.m_cispar[7] != 100:
                            continue

                        phase = t.m_cispar[5]
                        dac = t.m_cispar[6]

                        t_of_fit = getattr(t, 'tfit%s%02d%s' % (map[partition], module, gain))
                        t_bcid = getattr(t, 'bcid%s%02d%s' % (map[partition], module, gain))
                       
                        if phase==0:
                            if 'lo' in region.GetHash():
                                self.timeEny2D_lo.Fill(chan, dac*factor, t_of_fit[chan])
                                timeEny_lo.Fill(dac*factor, t_of_fit[chan])
                            else:
                                self.timeEny2D_hi.Fill(chan, dac*factor, t_of_fit[chan])
                                timeEny_hi.Fill(dac*factor, t_of_fit[chan])

                    tl = ROOT.TLatex()
                    tl.SetTextAlign(12)
                    tl.SetTextSize(0.03)
                    tl.SetNDC()

                    self.module = dirstr

                    if 'lo' in region.GetHash():
                        timeEny_lo.Draw()
                        timeEny_lo.GetXaxis().SetTitle("Injected charge (pC)")
                        timeEny_lo.GetYaxis().SetTitle("Fitted time (ns)")
                        timeEny_lo.Draw()
                        tl.DrawLatex(0.20,0.90,"Lowgain")
                        tl.DrawLatex(0.20,0.87,"Run %d" % event.runNumber)
                        self.c1.Print("%s/timing_%s.ps" % (self.dir, region.GetHash()))

                    else:
                        self.c1.cd()
                        timeEny_hi.Draw()
                        timeEny_hi.GetXaxis().SetTitle("Injected charge (pC)")
                        timeEny_hi.GetYaxis().SetTitle("Fitted time (ns)")
                        timeEny_hi.Draw()
                        tl.DrawLatex(0.20,0.90,"Highgain")
                        tl.DrawLatex(0.20,0.87,"Run %d" % event.runNumber)
                        self.c1.Print("%s/timing_%s.ps" % (self.dir, region.GetHash()))
            self.c1.Print("%s/timing_%s.ps]" % (self.dir, region.GetHash()))
  
