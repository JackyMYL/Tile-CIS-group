# Author: Christopher Tunnell <tunnell@hep.uchicago.edu>
#
# Modified by: Andrew Hard <ahard@uchicago.edu>  September 3, 2010     
#              John Dougherty <jdougherty@uchicago.edu>
#
#

# 
# This worker generates the following plots in plots/latest/cis/EventData:
#   FitAmpDistribution_<region>.eps
#     The distribution of fitted amplitudes for all events in <region> 
#     with dac and phase values specified in the macro
#     
#   Event_<region>.eps
#    The event samples from <region> with dac and phase values specified in
#    the macro, with the extracted data overlayed
#  

from src.ReadGenericCalibration import *
from src.oscalls import *
from src.region import *
from array import array
from src.MakeCanvas import *
from ROOT import TFile
from time import strptime, strftime

import workers.cis.common as common

class GetSamples(ReadGenericCalibration):
    """Get event samples and distributions of fitted energies"""

    def __init__(self,
                  processingDir=('root://castoratlas//castor/cern.ch/atlas/'
                                 'atlascerngroupdisk/det-tile/{Tyear}/'), # if run into problems, try change Tyear into the year, eg: 2023
                  all=False, region='', print_amplitude=False, 
                  print_event=False, single_event=0, timing_option=False, flagtype=None, timing_discretion=True):
        self.processingDir = processingDir
        self.all = all
        self.region = region
        self.print_amplitude = print_amplitude
        self.print_event = print_event
        self.single_event = single_event
        self.timing_option = timing_option
        self.flagtype=flagtype
        self.timing_discretion = timing_discretion
        self.ftDict = {}
        self.badRuns = set()
        self.dir = os.path.join(getPlotDirectory(), "cis", "Investigate", "EventData")
        createDir(self.dir)
        self.c1 = MakeCanvas()
        self.c1.SetHighLightColor(2)
        self.c2 = MakeCanvas()
        self.c3 = MakeCanvas()
        ROOT.gStyle.SetOptStat(0)
        ROOT.gErrorIgnoreLevel = 1001
        
    def Get_Index(self, ros, mod, chan):
        """convert the 3D channel array to a 1D array"""
        return (ros     * 64 * 48
                + mod   * 48
                + chan)
    
    
    def Get_SampIndex(self, ros, mod, chan, samp):
        """convert the 4D sample array to a 1D array"""
        return (ros  * 64 * 48 * 7
                + mod     * 48 * 7
                + chan         * 7 
                + samp)
        
    def ProcessStart(self):
        # Initial values for the fitted amplitude histograms.
        if not self.timing_option:
            [self.dachi,self.daclo,self.phase] = [dachi,daclo,phase]
            [self.examine,self.event_data] = [[],[]]
        else:
            self.examine = examine
            print('self examine from Map Flag Failure:')
            print(self.examine)
            self.event_data = event_data
            [self.nbin,self.maxs] = [{},{}]
            [self.nf_i,self.f_ni,self.ffail] = [0,0,0]
    def ProcessStop(self):
        # print output summaries
        if self.timing_option:
            event_data = self.event_data
            print('Number of events with timing issues: ' + str(self.ffail))
        
        if self.print_event:
            print(" ")
            print("Summary Data for Event Plots: ")
            print("  detector region      = ", self.region)
            print("  high-gain DAC value  = ", self.dachi)
            print("  low-gain DAC value   = ", self.daclo)
            print("  phase value          = ", self.phase)
        
        if self.print_event and self.single_event:
            print("  printing event plot for event ", self.single_event)

        if self.print_amplitude:
            print(" ")
            print("Summary Data for Fitted Amplitude Histograms: ")
            print("  detector region      = ", self.region)
            print("  high-gain DAC value  = ", self.dachi)
            print("  low-gain DAC value   = ", self.daclo)

        global NTimingCIS
        NTimingCIS = self.event_data
        
    def ProcessRegion(self, region):
        """This processes the region"""
        if 'gain' not in region.GetHash():
            return
        if self.print_event:
            self.c2.cd()
        
        # a shortcut to minimize computation time for timing_option.
        if (self.timing_option 
            and str(region.GetHash()) not in self.examine):
            return
        
        dirstr = '%s%02d' % (region.GetHash().split('_')[1], 
                             int(region.GetHash().split('_')[2][1:]))
        factor = 2.0*4.096*100.0/1023.0 # DAC to charge conversion   
        foundEventToProcess = False
        
        for event in region.GetEvents():
            if event.run.runType == 'CIS':
                self.run = event.run.runNumber
                # only proceed if we asked for all events or there is moreInfo
                if (not self.all
                    and not ('moreInfo' in event.data 
                             and event.data['moreInfo'])):
                    continue
                    
                foundEventToProcess = True
                # load the ROOT file and h2000 tree into ftDict
                if event.run.runNumber and event.run.runNumber not in self.ftDict:
                    if event.run.runNumber > 189319:
                        self.processingDir = 'root://eosatlas///eos/atlas/atlascerngroupdisk/det-tile/{Tyear}/'
                    timeform = time.strptime(event.run.time, "%Y-%m-%d %H:%M:%S")
                    eventyear = time.strftime('%Y',timeform)
                    f = TFile.Open('{Tdir}tile_{Tnum}_CIS.0.aan.root'.format(Tdir=self.processingDir.format(
                        Tyear=str(eventyear)), Tnum=str(event.run.runNumber)),"read")
                    if f == None:
                        t = None
                        print('Failed to open a file.')
                        if event.run.runNumber not in self.badRuns:
                            print(('Error: GetSamples could not load run'
                                '%d for %s' % (event.run.runNumber, dirstr)))
                            self.badRuns.add(event.run.runNumber)
                        continue
                    else:
                        t = f.Get('h2000')
                        self.ftDict[event.run.runNumber] = [f, t]
                        if (not t):
                            print('could not find h2000 tree')
        if not foundEventToProcess:
            return
        
        if 'lowgain' in region.GetHash():
            gain = 'lo'
        else:
            gain = 'hi'
           
        for event in region.GetEvents():
            if event.run.runType == 'CIS':

                MaxFit = 0
                MinFit = 1025
                AmploList = []
                histo = ROOT.TH1F('ADC_Samples', '', 1125, -50, 1075)

                if self.print_event:
                    SAMPLES_lo = ROOT.TProfile("Samples_lo","",7,0,7)
                    SAMPLES_hi = ROOT.TProfile("Samples_hi","",7,0,7)

                # only proceed with this loop if event.run.runNumber in ftDict and
                #  1) we've explicitly asked for all events, or
                #  2) event.data['moreInfo'] has data
                if ((not self.all 
                    and 'moreInfo' in event.data
                    and not event.data['moreInfo'])
                    or
                    (event.run.runNumber not in self.ftDict)):
                    continue
                
                f, t = self.ftDict[event.run.runNumber]
                x, y, z, w = region.GetNumber()
                index = self.Get_Index(x-1, y-1, z)

                # for retrieving data from ntuple
                t.SetBranchStatus("*", 0)
                t.SetBranchStatus("tFit_%s" % (gain), 1)
                t.SetBranchStatus("cispar", 1)
                t.SetBranchStatus("DMUBCID_%s" % (gain), 1)
                t.SetBranchStatus("sample_%s" % (gain), 1)
                t.SetBranchStatus("eFit_%s" % (gain), 1)
                t.SetBranchStatus("pedFit_%s" % (gain), 1)
                t.SetBranchStatus("OFLunits", 1)

                event.tfits = []
                event.pfits = []
                event.efits = []
                nevt = t.GetEntries()
                timelist = []
                ylist = []

                # for loop over CIS events (individual injections)
                for i in range(300, nevt):
                    if t.GetEntry(i) <= 0:
                        return
                    if t.cispar[7] != 100:
                        continue

                    # define the CIS parameters (see Twiki)
                    phase = t.cispar[5]
                    dac = t.cispar[6]
                    cap = t.cispar[7]
                    charge = factor * dac
                    #print cap, dac, charge, phase

                    if 'lo' in region.GetHash() and 300.0 <= charge <= 700.0:
                        FitRange = True
                    elif 'hi' in region.GetHash() and 3.0 <= charge <= 10.0:
                       FitRange = True
                    else:
                       FitRange = False

                    t_of_fit = getattr(t, 'tFit_%s' % (gain))
                    e_of_fit = getattr(t, 'eFit_%s' % (gain))
                    p_of_fit = getattr(t, 'pedFit_%s' % (gain))
                    samples = getattr(t, 'sample_%s' % (gain))
                    OFLunits = getattr(t, 'OFLunits')
                    max_samp = -1000
                    max = 0
                    for p in range(0,7):
                        indexSamp = self.Get_SampIndex(x-1, y-1, z, p)
                        #print dac, phase, p, samples[indexSamp]
                        if samples[indexSamp] > max:
                            max = samples[indexSamp]
                            max_samp = p
			

                        if dac*cap*2.0*(4.096/1023) < ( (1023-60) / event.data['calibration']): 
                            histo.Fill(float(samples[indexSamp]))
                    if (max_samp == 0 or max_samp == 6) and FitRange:
                        print("EDGE SAMPLE ", region.GetHash(), "dac: ", dac, "phase: ", phase, " sample #: ", max_samp,  "value: ", max, '\n') 
                    if (max_samp == 1 or max_samp == 5) and FitRange:
                        print("NEXT TO EDGE SAMPLE ", region.GetHash(), "dac: ", dac, "phase: ", phase, " sample #: ", max_samp,  "value: ", max, '\n') 
                    # Check to see if pedestal value is the result of overflow in the samples
                    # and correct the value if this is the case
                    if p_of_fit[index] > 1000:
                        p_of_fit[index] = p_of_fit[index] - int(p_of_fit[index]/10000)*10000

                    # This section fills timing option data
                    if self.timing_option and phase in range(0,225,16):

                        event_index = ('%d_%s_%d_%d_%d_%d' % 
                                        (event.run.runNumber, region.GetHash(),
                                         i, cap, dac, phase))

                        event_ntuple = (event.run.runNumber, region.GetHash(), 
                                        i, dac, phase)

                        for p in range(0,7):
                            indexSamp = self.Get_SampIndex(x-1, y-1, z, p)
                            
                            if ((charge >= 300 and charge <= 700 
                                 and gain == 'lo')
                                or
                                 (charge >=3 and charge <= 10
                                  and gain == 'hi')):

                                try: self.maxs[event_index]
                                except:
                                    self.maxs[event_index] = samples[indexSamp]
                                    self.nbin[event_index] = p

                                if samples[indexSamp] >=  self.maxs[event_index]:
                                    self.nbin[event_index] = p             
                                    self.maxs[event_index] = samples[indexSamp]

                        # Readout data and ntuple construction for
                        # TimingFlag.py macro
                        
                        # prints run#, region, event#, cap, dac, phase
                        if self.nbin.get(event_index) in (0,6):
                            print('     Failed Edge Flag: ')
                            print('         location = ', event_index)
                            print('         maximum bin = ', self.nbin[event_index])
                            self.ffail += 1
                            self.event_data.append(event_ntuple)
                        elif self.nbin.get(event_index) in (1,5):
                            print('     Failed Next to Edge Flag: ')
                            print('         location = ', event_index)
                            print('         maximum bin = ', self.nbin[event_index])
                            self.ffail += 1
                            self.event_data.append(event_ntuple)
                        
                        elif not self.timing_discretion:
                            # print '     Failed {0}: '.format(self.flagtype)
                            self.ffail += 1
                            self.event_data.append(event_ntuple)

                    # This section fills the CIS event plots
                    #print phase
                    if self.print_event and phase == self.phase:
                        for p in range(0,7):
                            indexSamp = self.Get_SampIndex(x-1,y-1,z,p)

                            if dac == self.daclo and gain == 'lo':
                                if self.single_event:
                                    if ((i % 4) + 1 )== int(self.single_event):
                                        SAMPLES_lo.Fill(p, samples[indexSamp])
                                        SAMPLES_lo.Fill(p, samples[indexSamp]+1)
                                        #SAMPLES_lo.Draw()
                                        event.tfits.append(t_of_fit[index])
                                        event.pfits.append(p_of_fit[index])
                                        event.efits.append(e_of_fit[index])
                                else:
                                    SAMPLES_lo.Fill(p, samples[indexSamp])
                                    event.tfits.append(t_of_fit[index])
                                    event.pfits.append(p_of_fit[index])
                                    event.efits.append(e_of_fit[index])

                            if dac == self.dachi and gain == 'hi':
                                if self.single_event: 
                                    if ((i % 4) + 1) == int(self.single_event):
                                        SAMPLES_hi.Fill(p, samples[indexSamp])
                                        SAMPLES_hi.Fill(p, samples[indexSamp]+1)
                                        SAMPLES_hi.Fill(p, samples[indexSamp]-1)
                                       # SAMPLES_hi.Draw()
                                        event.tfits.append(t_of_fit[index])
                                        event.pfits.append(p_of_fit[index])
                                        event.efits.append(e_of_fit[index])
                                else:
                                    SAMPLES_hi.Fill(p, samples[indexSamp])
                                    event.tfits.append(t_of_fit[index])
                                    event.pfits.append(p_of_fit[index])
                                    event.efits.append(e_of_fit[index])

                    # This section fills the fitted amplitude histograms
                    if self.print_amplitude and phase in range(0,225,16):
                        if (dac == self.dachi and gain == 'hi') or (dac == self.daclo and gain == 'lo'):
                            AmploList.append(e_of_fit[index])
                            print(e_of_fit[index], MinFit, MaxFit)
                            if e_of_fit[index] > MaxFit:
                                MaxFit = e_of_fit[index]
                            elif e_of_fit[index] < MinFit:
                                MinFit = e_of_fit[index]
                            
                # fit, format, and print the event plots
                if self.print_event and event.tfits:

                    self.c3.cd()
                    self.c3.Clear()
                    CISpulse = ROOT.TGraph()
                    CISpulse.SetMarkerStyle(7)
                    CISpulse.SetMarkerColor(4)
                    CISpulse.SetLineColor(4)

                    if gain == 'hi':
                        pulse = common.PULSE_SHAPE['highgain']
                        leak = common.LEAK_SHAPE['highgain']
                        sample_plot = SAMPLES_hi

                    else:
                        pulse = common.PULSE_SHAPE['lowgain']
                        leak = common.LEAK_SHAPE['lowgain']
                        sample_plot = SAMPLES_lo

                    mtfit = sum(event.tfits)/len(event.tfits)
                    mpfit = sum(event.pfits)/len(event.pfits)
                    mefit = sum(event.efits)/len(event.efits)

                    for p, (ppoint, lpoint) in enumerate(zip(pulse, leak)):
                        sec = float(ppoint[0])
                        amp = float(ppoint[1])
                        lamp = float(lpoint[1])
                        CISpulse.SetPoint(p, 
                                        ((0.035 * (sec + mtfit)) + 3.5),
                                        (amp * mefit) + lamp + mpfit)

                    CISpulse.GetXaxis().SetTitle("Sample Number")
                    CISpulse.GetYaxis().SetTitle("ADC Counts")
                    CISpulse.GetXaxis().SetLimits(0,7)
                    CISpulse.GetXaxis().SetNdivisions(-7)
                    self.c3.SetTicks(1,1)
                    CISpulse.Draw("ALP")
                    sample_plot.Draw("SAME")

                    # set legend
                    tl = ROOT.TLatex()
                    tl.SetTextAlign(12)
                    tl.SetTextSize(0.03)
                    tl.SetNDC()
                    tl.DrawLatex(0.20, 0.90, "%s" % region.GetHash())
                    tl.DrawLatex(0.20, 0.87, "Run %d" % event.run.runNumber)
                    if sample_plot == SAMPLES_hi:
                        tl.DrawLatex(0.20, 0.84, "DAC %d" % self.dachi)
                    else:
                        tl.DrawLatex(0.20, 0.84, "DAC %d" % self.daclo)

                    tl.DrawLatex(0.20, 0.81, "Phase %d" % self.phase)
                    self.c3.Print("%s/Event_%s_%i.png" % (self.dir,region.GetHash(), self.run))

                    self.c3.cd()                    
                    self.c2.Clear()
                    histo.GetXaxis().SetTitle("Sample Value (ADC Counts)")
                    histo.GetYaxis().SetTitle("Number of Samples")
                    self.c2.SetLogy()
                    histo.Draw()
                    tl.SetTextAlign(12)
                    tl.SetTextSize(0.04)
                    tl.SetNDC()
                    tl.DrawLatex(0.16, 0.97, "%s Run %i" % (region.GetHash(), self.run))

                    # #print stuck bit info on histogram
                    # tl.SetTextColor(2)
                    # tl_y = 0.8                     
                    # for list in event.data['StuckBits']:

                    #    if list == 'AtZero':
                    #        value = 0
                    #    else:
                    #        value = 1
                    #    for bit in event.data['StuckBits'][list]:
                    #         tl.DrawLatex(0.7, tl_y, "Bit %s stuck at %i" % (bit, value))
                    #         tl_y -= 0.05 #don't let text overlap!
                           
                    self.c2.Print("%s/SampHist_%s_%i.png" % (self.dir,region.GetHash(), self.run))

                    if self.print_amplitude:
                        xmin = int(0.995*MinFit)
                        xmax = int(1.005*MaxFit)
                        nbin = xmax - xmin
                        amphist = self.afithi = ROOT.TH1F('amphist', '', nbin, xmin, xmax)
                        for ampfit in AmploList:
                            amphist.Fill(ampfit)

                        self.c2.Clear()
                        amphist.GetXaxis().SetTitle("Fitted Amplitude (ADC Counts)")
                        amphist.GetYaxis().SetTitle("# of Events")
                        #Draw/Format Stat Box
                        amphist.SetStats(True)
                        ROOT.gStyle.SetOptStat("ourme")
                        ROOT.gStyle.SetStatY(0.925)
                        ROOT.gStyle.SetStatX(0.865)
                        self.c2.SetLeftMargin(0.14)
                        self.c1.SetRightMargin(0.14)
                        self.c1.SetTicks(1,1)
                        amphist.Draw()

                        #Draw Legend
                        tl = ROOT.TLatex()
                        tl.SetTextAlign(12)
                        tl.SetTextSize(0.03)
                        tl.SetNDC()
                        tl.DrawLatex(0.20, 0.905, "%s" % region.GetHash())
                        tl.DrawLatex(0.20, 0.875, "Run %i" % self.run)
                        if "high" in region.GetHash():
                            tl.DrawLatex(0.20, 0.845, "DAC %i" % self.dachi)
                        else:
                            tl.DrawLatex(0.20, 0.845, "DAC %i" % self.daclo)

                        self.c2.Print("%s/FittedAmplitudeDist_%s_%r.png" % (self.dir, region.GetHash(), event.run.runNumber))
