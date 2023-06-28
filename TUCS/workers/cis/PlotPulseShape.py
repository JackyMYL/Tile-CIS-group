# Author:  Andrew Hard        <ahard@uchicago.edu>
# Contrib: John Dougherty     <jdougherty@uchicago.edu>
#
# December 8, 2010
# Modified April 6, 2011
# Modified November 22, 2013

from src.ReadGenericCalibration import *
from src.oscalls import *
from src.region import *
from array import array
from src.MakeCanvas import *
from ROOT import TFile
from time import strptime, strftime
import datetime

import workers.cis.common as common

class PlotPulseShape(ReadGenericCalibration):
    "Use the injections at various phases to map out the injected pulse shape for a given DAC setting in a particluar channel during one run."

    def __init__(self, processingDir='root://castoratlas//castor/cern.ch/atlas/atlascerngroupdisk/det-tile/{Tyear}/', # if run into problems, make {Tyear} directly 2023
                all=False, region='', discretion=False):
        self.discretion = discretion
        self.processingDir = processingDir
        self.all=all
        self.region = region
        
        self.ftDict = {}
        self.badRuns = set()
        self.dir = getPlotDirectory() + "/cis"
        createDir(self.dir)
        self.dir = "%s/TimingFlag" % self.dir
        createDir(self.dir)
        self.dir = "%s/PulseShapes" % self.dir
        createDir(self.dir)
        
        self.c1 = MakeCanvas()
        self.c1.SetHighLightColor(2)

        self.dachi=dachi
        self.daclo=daclo
        
        ROOT.gErrorIgnoreLevel = 1001

    def Get_Index(self, ros, mod, chan):
        return (ros    * 64 * 48
                + mod       * 48
                + chan)
    
    def Get_SampIndex(self, ros, mod, chan, samp):
        return (ros    * 64 * 48 * 7
                + mod       * 48 * 7
                + chan           * 7
                + samp)
        
    def ProcessStart(self):
        # Official ATLAS formatting for CIS note plots.
        #ROOT.gROOT.ProcessLine(".x Style.C")
       
        self.integer1 = 1
        self.integer2 = 1

        self.lo_max = 0
        self.hi_max = 0

        self.lo_min = 1000
        self.hi_min = 1000
        
    def ProcessStop(self):
        
        print(" ")
        print("Summary Data for Event Plots: ")
        print("  detector region      = ", self.region)
        print("  high-gain DAC value  = ", self.dachi)
        print("  low-gain DAC value   = ", self.daclo)


    def ProcessRegion(self, region):
        global NTimingCIS
        if 'gain' not in region.GetHash():
            return
        self.c1.cd()

        dirstr = '%s%02d' % (region.GetHash().split('_')[1], int(region.GetHash().split('_')[2][1:]))
        factor = 2.0*4.096*100.0/1023.0
        foundEventToProcess = False
        
        for event in region.GetEvents():
            if event.run.runType == 'CIS':
                if self.discretion:
                    if NTimingCIS:
                        proceed = False
                        for (ernumb, data_region, NTi, NTdac, NTphase) in NTimingCIS:
                            if (ernumb, data_region) == (event.run.runNumber, region.GetHash()):
                                proceed = True
                        if not proceed:
                            continue
                    else:
                        print('no specific bad timing channels found in list from MapFlagFailure...using all given regions instead')
            
                if 'moreInfo' not in event.data and not self.all:
                    continue
                if not self.all and not event.data['moreInfo']:
                    continue
                foundEventToProcess = True
                if event.run.runNumber and event.run.runNumber not in self.ftDict:
                    timeform = time.strptime(event.run.time, "%Y-%m-%d %H:%M:%S")
                    eventyear = time.strftime('%Y',timeform)
                    if event.run.runNumber > 189319:
                        self.processingDir = 'root://eosatlas///eos/atlas/atlascerngroupdisk/det-tile/{Tyear}/'
                    f = TFile.Open('{Tdir}tile_{Tnum}_CIS.0.aan.root'.format(Tdir=self.processingDir.format(
                        Tyear=str(eventyear)), Tnum=str(event.run.runNumber)),"read")

                    if f == None:
                        print('Failed to open a file.')
                        t = None
                        if event.run.runNumber not in self.badRuns:
                            print('Error: GetSamples could not load run', event.run.runNumber, ' for %s...' % dirstr)
                            self.badRuns.add(event.run.runNumber)
                        continue
                    else:
                        t = f.Get('h2000')
                    self.ftDict[event.run.runNumber] = [f, t]
                   
        if not foundEventToProcess:
            return

        if 'lowgain' in region.GetHash():
            gain = 'lo'
        else:
            gain = 'hi'
        
        for event in region.GetEvents():
            if event.run.runType == 'CIS':

                SAMPLES_lo = ROOT.TGraphErrors()
                SAMPLES_hi = ROOT.TGraphErrors()
                
                if not self.all and \
                       ('moreInfo' in event.data and not event.data['moreInfo']):
                    continue
                if event.run.runNumber not in self.ftDict:
                    continue
                
                [f, t] = self.ftDict[event.run.runNumber]
                [x, y, z, w] = region.GetNumber()
                index = self.Get_Index(x-1, y-1, z)

                t.SetBranchStatus("*", 0)
                t.SetBranchStatus("tFit_%s" % (gain), 1)
                t.SetBranchStatus("cispar", 1)
                t.SetBranchStatus("DMUBCID_%s" % (gain), 1)
                t.SetBranchStatus("sample_%s" % (gain), 1)
                t.SetBranchStatus("eFit_%s" % (gain), 1)
                t.SetBranchStatus("pedFit_%s" % (gain), 1)

                pfits = []
                efits = []

                nevt = t.GetEntries()
                # for loop over CIS events
                for i in range(300, nevt):
                    if t.GetEntry(i) <= 0:
                        return
                    if t.cispar[7] != 100:
                        continue

                    # define the CIS parameters (Twiki h2000)
                    phase = t.cispar[5]
                    dac = t.cispar[6]
                    cap = t.cispar[7]
                    charge = factor * dac
                    
                    t_of_fit = getattr(t, 'tFit_%s' % (gain))
                    e_of_fit = getattr(t, 'eFit_%s' % (gain))
                    p_of_fit = getattr(t, 'pedFit_%s' % (gain))
                    samples = getattr(t, 'sample_%s' % (gain))

                    # Check to see if pedestal value is the result of overflow in the samples
                    # and correct the value if this is the case.
                    if p_of_fit[index] > 1000:  
                        p_of_fit[index] = p_of_fit[index] - int(p_of_fit[index]/10000)*10000
                                    
                    Toff = float(t_of_fit[index])
                                
                    # This section retrieves info for the pulse shape.
                    if dac==self.daclo:
                        if 'lo' in region.GetHash():
                            for p in range(0,7):
                                indexSamp = self.Get_SampIndex(x-1,y-1,z,p)
                                t_time = p*25 - Toff - 3*25
                                SAMPLES_lo.SetPoint(self.integer1, t_time, samples[indexSamp])
                                self.integer1 += 1
                                pfits.append(p_of_fit[index])
                                efits.append(e_of_fit[index])

                    elif dac==self.dachi:
                        if 'hi' in region.GetHash():
                            for p in range(0,7):
                                indexSamp = self.Get_SampIndex(x-1,y-1,z,p)
                                t_time = p*25 - Toff - 3*25
                                SAMPLES_hi.SetPoint(self.integer2, t_time, samples[indexSamp])
                                self.integer2 += 1
                                pfits.append(p_of_fit[index])
                                efits.append(e_of_fit[index])

                # fit formatting
                self.c1.cd()
                CISpulse = ROOT.TGraphErrors()
                CISpulse.SetMarkerStyle(7)
                CISpulse.SetMarkerColor(4)
                CISpulse.SetLineColor(4)

                if gain == 'hi':
                    sample_plot = SAMPLES_hi
                    pulse = common.PULSE_SHAPE['highgain']
                    leak = common.LEAK_SHAPE['highgain']

                else:
                    sample_plot = SAMPLES_lo
                    pulse = common.PULSE_SHAPE['lowgain']
                    leak = common.LEAK_SHAPE['lowgain']
                
                mtfit = 0
                mpfit = sum(pfits)/len(pfits)
                mefits = sum(efits)/len(efits)

                for p, (ppoint, lpoint) in enumerate(zip(pulse, leak)):
                    sec = float(ppoint[0])
                    amp = float(ppoint[1])
                    lamp = float(lpoint[1])
                    CISpulse.SetPoint(p, 
                                      (sec + mtfit), 
                                      ((amp * mefits) + lamp + mpfit))

                CISpulse.GetXaxis().SetTitle("Time (ns)")
                CISpulse.GetYaxis().SetTitle("ADC Counts")
                CISpulse.GetXaxis().SetLimits(-100,100)
                CISpulse.Draw("ALP")
                sample_plot.SetMarkerSize(0.5)
                sample_plot.Draw("P")
                    
                # set legend
                tl = ROOT.TLatex()
                tl.SetTextAlign(12)
                tl.SetTextSize(0.03)
                tl.SetNDC()
                tl.DrawLatex(0.20,0.90,"%s" % region.GetHash())
                tl.DrawLatex(0.20,0.87,"Run %d" % event.run.runNumber)
                if sample_plot == SAMPLES_hi:
                    tl.DrawLatex(0.20,0.84,"DAC %d" % self.dachi)
                else:
                    tl.DrawLatex(0.20,0.84,"DAC %d" % self.daclo)
                    
                self.c1.Print("%s/Event_%s.png" % (self.dir, region.GetHash()))
