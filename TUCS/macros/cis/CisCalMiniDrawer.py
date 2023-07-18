###################################################################################################
# Author: Jeff Shahinian <jeffrey.david.shahinian@cern.ch>
# Date:   June 20, 2014
#
# This (very preliminary) script provides (very preliminary) CIS constants for the new minidrawer
# electronics by fitting the pulses to a Gaussian + pedestal, extracting the amplitudes for
# different DAC settings, and performing the CIS scan. It should be run from the Tucs directory.
# The file samples.root should also be located in the Tucs directory.
#
# Things to do:
#   Figure out and implement the DAC setting to injected charge conversion
#   Refine Chi^2 cut for flagging bad pulses, add other (better) ways to do this.
#   Better way of printing the pulses
#   Make it conform to the TUCS framework (move the class to a worker and call the worker, have
#   plots saved in sensible directories)
#   Improve pulse fitting procedure (doesn't do so well with very small pusles)
#   Define fit range for the CIS scans
#   Perform CIS scan for multiple channels at once
#   Make compatible with phase settings once they are added to the ntuple
#   Should CIS scan fit include a constant?
###################################################################################################

import os, sys
os.chdir(os.getenv('TUCS','.'))
sys.path.insert(0, 'src')
from oscalls import *
import Get_Consolidation_Date
import MakeCanvas
import ROOT
import argparse
import numpy as np

class CisCalMiniDrawer:
    def __init__(self):
        self.amp_guess      = 0
        self.sigma_guess    = 1
        #self.ped_guess      = 250
        self.fitrange_min   = 0
        self.fitrange_max   = 64
        self.mean_lowlimit  = 0
        self.mean_highlimit = 64
        self.samples        = []
        self.CISscan        = ROOT.TGraph()
        ROOT.gStyle.SetOptFit(0011)
        ROOT.gStyle.SetStatY(0.9)
        ROOT.gStyle.SetStatX(0.37)
        ROOT.gStyle.SetStatW(0.1)
        ROOT.gStyle.SetStatH(0.04)
    
    def FitPulse(self, event):
        for i in range(64):
            self.samples.append(event["samples"].Eval(i))
        self.mean_guess = self.samples.index(max(self.samples)) #Use index of max bin as guess for the mean
        
        self.ped_guess = event["samples"].Eval(2)
    
        for i in range(10):
            self.gauss_ped = ROOT.TF1("gauss_ped", "gaus(0) + [3]",self.fitrange_min,self.fitrange_max)
            if args.dac: self.gauss_ped.SetNpx(10000)
            if event["dac"] == 0:
                self.sigma_guess = 100
            self.gauss_ped.SetParameter(0,self.amp_guess)
            self.gauss_ped.SetParameter(1,self.mean_guess)
            self.gauss_ped.SetParameter(2,self.sigma_guess)
            self.gauss_ped.SetParameter(3,self.ped_guess)
            if event["dac"] == 0:
                self.gauss_ped.SetParLimits(0,0,100)
            else:
                self.gauss_ped.SetParLimits(0,0,10000)
            self.gauss_ped.SetParLimits(1,self.mean_lowlimit,self.mean_highlimit)
            self.gauss_ped.SetParLimits(2,0,100)
            #self.gauss_ped.SetParLimits(3,210,270)
            self.gauss_ped.SetParLimits(3,0,4095)
            self.gauss_ped.SetParName(0, "Amplitude")
            self.gauss_ped.SetParName(1, "Mean")
            self.gauss_ped.SetParName(2, "Sigma")
            self.gauss_ped.SetParName(3, "Pedestal")
            self.gauss_ped.SetLineColor(ROOT.kBlue)
            event["samples"].Fit("gauss_ped","RM")
            self.amp_guess      = self.gauss_ped.GetParameter(0)
            self.mean_guess     = self.gauss_ped.GetParameter(1)
            self.sigma_guess    = self.gauss_ped.GetParameter(2)
            self.ped_guess      = self.gauss_ped.GetParameter(3)
            self.mean_lowlimit  = self.mean_guess - self.gauss_ped.GetParameter(2)
            self.mean_highlimit = self.mean_guess + self.gauss_ped.GetParameter(2)
            if i == 9:
                if self.gauss_ped.GetChisquare() > 500000:
                    chisquare.append({'event' : event, 'chisquare' : self.gauss_ped.GetChisquare()})
        event["amp"] = self.gauss_ped.GetParameter(0)
    
        
    def PlotPulse(self, pulses, dac, channel, gain):
        c2.cd()
        #ROOT.gStyle.SetOptFit(1111)
        #pulses[2600]["samples"].Draw("AP")
        for dac_val in dac:
            for chan in channel:
                for pulse in pulses:
                    if pulse["dac"] == dac_val:
                        pulse["samples"].Draw("AP")
                        pulse["samples"].SetTitle("c%02d_%s_%s" % (int(chan),gain,dac_val))
                        pulse["samples"].GetXaxis().SetTitle("Sample Number")
                        pulse["samples"].GetYaxis().SetTitle("Amplitude (ADC Counts)")
                        c2.Print("pulse_c%02d_%s_%s.eps" % (int(chan),gain,dac_val))
    
    def CISScan(self, pulses, dac_vals, amps, scan, channel, gain):
        for event in pulses:
            CisCalMiniDrawer().FitPulse(event)
            for i in range(len(dac_vals)):
                if event["dac"] == dac_vals[i]:
                    amps[i]["amp"].append(event["amp"])
                    amps[i]["dac"] = event["dac"]
                           
        for idx,entry in enumerate(amps):
            scan[idx]["dac"] = entry["dac"]
            scan[idx]["amp"] = np.mean(entry["amp"])
        
        for idx,entry in enumerate(scan):
            self.CISscan.SetPoint(idx,entry["dac"],entry["amp"])
        #self.lin_fit = ROOT.TF1("lin_fit", "[0]*x",512,max(dac_vals))
        #self.lin_fit = ROOT.TF1("lin_fit", "[0]*x",50,max(dac_vals))
        self.lin_fit = ROOT.TF1("lin_fit", "[0]*x",10,130)
        self.lin_fit.SetLineColor(ROOT.kRed)
        self.lin_fit.SetParName(0, "Slope")
        self.CISscan.Fit("lin_fit", "RM")
    
        c1.cd()
        self.CISscan.SetTitle("c%02d_%s" % (int(channel[0]),gain))
        self.CISscan.GetXaxis().SetTitle("Injection Size")
        self.CISscan.GetYaxis().SetTitle("Amplitude (ADC Counts)")
        self.CISscan.Draw("AP")
        c1.Print("scan_c%02d_%s.eps" % (int(channel[0]),gain))
        c1.Clear()
        return self.lin_fit.GetParameter(0)

############################## ARGUMENT PARSING ##############################
##############################################################################
parser = argparse.ArgumentParser(description=
'Info here.', 
formatter_class=argparse.RawTextHelpFormatter)

parser.add_argument('--ch', action='store', nargs='*', type=str, default='',
                    required=True, help=
'Select the channel(s) you want to plot/calibrate. Must between 0 and 11.\n\
If using the --cal option, you can only specifiy one channel.\n\
EX: python macros/cis/CisCalMiniDrawer.py --ch 0 --gain lo --dac 512 --cal \n\
EX: python macros/cis/CisCalMiniDrawer_test.py --ch 0 3 6 --gain lo --dac 0 512')

parser.add_argument('--gain', action='store', nargs=1, type=str, default='',
                    required=True, help=
'Select the gain you want to plot/calibrate. Should be \'hi\' or \'lo\'.')

parser.add_argument('--dac', action='store', nargs='+', type=int, default=False,
                    required=False, help=
'Select the dac settings you want to plot. Must be valid settings separated by whitespace.\n\
Without this argument, no plots will be produced.')

parser.add_argument('--cal', action='store_true', default=False,
                    help=
'Use this switch to perform the calibration. Default is False. Can only calibrate one channel at a time.')

args=parser.parse_args()

channel = args.ch
if channel == '':
    print 'WARNING: NO CHANNEL SPECIFIED. SETTING CHANNEL TO 0.'
    channel = [0]
if args.gain[0] != 'hi' and args.gain[0] != 'lo':
    print 'WARNING: NOT A VALID GAIN SELECTION. USING HIGH GAIN'
    gain = 'hg'
else:
    gain = args.gain[0]
dac = args.dac
###############################################################################
###############################################################################

f = ROOT.TFile("samples.root")
t = f.Get("h2001")
c1 = MakeCanvas.MakeCanvas()
c1.SetTicks(1,1)
c2 = MakeCanvas.MakeCanvas()
c2.SetTicks(1,1)

pulses    = []
dac_vals  = []
amps      = []
scan      = []
chisquare = []

for event in t:
    pulses.append({"samples" : ROOT.TGraph()})
    if gain == 'hi':
        nsamples = len(event.sample_hg)/12
    elif gain == 'lo':
        nsamples = len(event.sample_lg)/12
    dac_vals.append(event.dac)
dac_vals = list(set(dac_vals)) #Create list of DAC values used in CIS scan 

if dac: #Check to see specified DAC setting is a valid one
    for dac_val in dac:
        if dac_val not in dac_vals:
            print 'SPECIFIED DAC SETTING NOT VALID. NOT PRINTING PULSES. VALID SETTINGS ARE:'
            print [int(dac_val) for dac_val in dac_vals]
            dac = 0

for dac_val in dac_vals:
    amps.append({"amp" : [], "dac" : []})
    scan.append({"amp" : [], "dac" : []})

for idx,event in enumerate(t):
    p = 0
    if gain == 'hi':
        for i in range(int(channel[0])*64, (int(channel[0])+1)*64):
            pulses[idx]["samples"].SetPoint(p,p,event.sample_hg[i])
            pulses[idx]["dac"] = event.dac
            p += 1
    elif gain == 'lo':
        for i in range(int(channel[0])*64, (int(channel[0])+1)*64):
            pulses[idx]["samples"].SetPoint(p,p,event.sample_lg[i])
            pulses[idx]["dac"] = event.dac
            p += 1

if args.cal:
    if gain == 'lo':
        file = open(os.path.join(getResultDirectory(),'cis_const_lo'), 'a')
    elif gain == 'hi':
        file = open(os.path.join(getResultDirectory(),'cis_const_hi'), 'a')
    cis_const = CisCalMiniDrawer().CISScan(pulses,dac_vals,amps,scan,channel,gain)
    print 'INJECTIONS FAILING CHI^2 FLAG:'
    for entry in chisquare:
        print entry
    print 'CIS CONSTANT: ', cis_const
    cis_const = str(cis_const)
    file.write(cis_const + '\n')
    file.close()

if dac: CisCalMiniDrawer().PlotPulse(pulses,dac,channel,gain)


