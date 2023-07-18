# Author: Christopher Tunnell <tunnell@hep.uchicago.edu>
#
# March 24, 2009
#

from src.ReadGenericCalibration import *
from src.oscalls import *
from src.region import *
from ROOT import gStyle

class TuneCuts(ReadGenericCalibration):
    "Dump plots for the Chi2 and RMS flags"

    def __init__(self, probbad=True):

        self.dir = getPlotDirectory()
        self.dir = '%s/cis' % self.dir
        createDir(self.dir)
        self.dir = '%s/Public_Plots' % self.dir
        createDir(self.dir)
        self.dir = '%s/TuneCutsProbStack' % self.dir
        createDir(self.dir)
        
        self.c1 = src.MakeCanvas.MakeCanvas()
        self.probbad = probbad

    def ProcessStart(self):
        self.hprobgood = ROOT.TH1D('hprobgood', '', 100, 0, 1)
        self.hprobbad = ROOT.TH1D('hprobbad', '', 100, 0, 1)

        self.hprobgoodlowzoom = ROOT.TH1D('hprobgoodlowzoom', '', 30, 0, 0.00002)
        self.hprobbadlowzoom = ROOT.TH1D('hprobbadlowzoom', '', 30, 0, 0.00002)

        self.hprobgoodhighzoom = ROOT.TH1D('hprobgoodhighzoom', '', 30, 0.9996, 1)
        self.hprobbadhighzoom = ROOT.TH1D('hprobbadhighzoom', '', 30, 0.9996, 1)

        self.hrms = [{'lo': ROOT.TH1D("hrmslo", "", 50, 0, 10), 'hi': ROOT.TH1D("hrmshi", "", 50, 0, 10)},
                     {'lo': ROOT.TH1D("hrmslobig", "", 35, 0, 100), 'hi': ROOT.TH1D("hrmshibig", "", 100, 0, 100)}]
        

    def ProcessStop(self):
        self.c1.SetLogy(1)
        self.c1.Print('%s/hprob_stack.ps[' % self.dir)

        self.hrms[0]['hi'].SetFillStyle(3004)
        self.hrms[0]['hi'].SetLineColor(2)
        self.hrms[0]['lo'].SetFillStyle(3005)
        self.hrms[0]['lo'].SetLineColor(4)
        gStyle.SetOptStat(0)

        self.hrms[0]['hi'].SetMaximum(400000)
        self.hrms[0]['lo'].SetMaximum(400000)

        hist_title = 'RMS Fit Energy at Fixed-DAC (ADC counts)'

        self.hrms[0]['lo'].GetXaxis().SetTitle(hist_title)
        self.hrms[0]['lo'].GetXaxis().CenterTitle(True)

        if self.hrms[0]['lo'].GetEntries():
            self.hrms[0]['lo'].Draw()
            self.hrms[0]['hi'].Draw('SAME')
        elif self.hrms[0]['hi'].GetEntries():
            self.hrms[0]['hi'].Draw()

        line = ROOT.TLine()
        line.SetLineStyle(2)
        line.DrawLine(5, 0, 5, 400000)
            
            
        leg = ROOT.TLegend(0.508794,0.708042,0.8429648,0.9213287,"","brNDC")
        (leg.AddEntry(self.hrms[0]['hi'],"high-gain","L")).SetLineWidth(2)
        (leg.AddEntry(self.hrms[0]['lo'],"low-gain","L")).SetLineWidth(2)
        leg.Draw()

        # hack
        self.c1.SetLeftMargin(0.14)
        self.c1.SetRightMargin(0.14)
        self.c1.Modified()
                        
        self.c1.Print('%s/hprob_stack.ps' % self.dir)
        self.c1.Print('%s/hprob_stack_1.eps' % self.dir)
        self.c1.Print('%s/hprob_stack_1.root' % self.dir)

        self.c1.SetLogy(1)
        gStyle.SetOptStat(0)

        self.hrms[1]['hi'].SetFillStyle(3004)
        self.hrms[1]['hi'].SetLineColor(2)
        self.hrms[1]['lo'].SetFillStyle(3005)
        self.hrms[1]['lo'].SetLineColor(4)
        self.hrms[1]['lo'].GetXaxis().SetTitle(hist_title)
        self.hrms[1]['lo'].GetXaxis().CenterTitle(True)

        self.hrms[0]['hi'].SetMaximum(400000)
        self.hrms[0]['lo'].SetMaximum(400000)
        
        if self.hrms[1]['lo'].GetEntries():
            self.hrms[1]['lo'].Draw()
            self.hrms[1]['hi'].Draw('SAME')
        elif self.hrms[1]['hi'].GetEntries():
            self.hrms[1]['hi'].Draw()

        line = ROOT.TLine()
        line.SetLineStyle(2)
        line.DrawLine(5, 0, 5, 300000)
        
        leg = ROOT.TLegend(0.508794,0.708042,0.8429648,0.9213287,"","brNDC")
        (leg.AddEntry(self.hrms[1]['hi'],"high-gain","L")).SetLineWidth(2)
        (leg.AddEntry(self.hrms[1]['lo'],"low-gain","L")).SetLineWidth(2)
        leg.Draw()

        # hack
        self.c1.SetLeftMargin(0.14)
        self.c1.SetRightMargin(0.14)
        self.c1.Modified()
        
        self.c1.Print('%s/hprob_stack.ps' % self.dir)
        self.c1.Print('%s/hprob_stack_2.eps' % self.dir)
        self.c1.Print('%s/hprob_stack_2.root' % self.dir)
        

        self.c1.SetLogy(1)
        gStyle.SetOptStat(0)

        i = 3
        for hbad in [self.hprobbad,\
                     self.hprobbadlowzoom,\
                     self.hprobbadhighzoom]:
            hbad.GetXaxis().SetTitle('Probability of \chi^{2} and NDF')
            hbad.GetXaxis().CenterTitle(True)

            hbad.SetMaximum(5000)
                        
            hbad.Draw()

            line = ROOT.TLine()
            line.SetLineStyle(2)
            line.SetLineColor(2)
            line.DrawLine(0.000002, 0, 0.000002, 5000)

            # hack
            self.c1.SetLeftMargin(0.14)
            self.c1.SetRightMargin(0.14)
            self.c1.Modified()

            self.c1.Print('%s/hprob_stack.ps' % self.dir)
            self.c1.Print('%s/hprob_stack_%d.eps' % (self.dir, i))
            self.c1.Print('%s/hprob_stack_%d.root' % (self.dir, i))
            
            i += 1

        self.c1.Print('%s/hprob_stack.ps]' % self.dir)
    
    def ProcessRegion(self, region):
        for event in region.GetEvents():
            if event.runType == 'CIS':
                numHiRMS = 0
                        
                if ('scan_rms' in event.data and event.data['scan_rms']) and\
                       ('scan_rms' in event.data and event.data['scan_rms']):                    
                    gscan = event.data['scan']
                    gscan_rms = event.data['scan_rms']

                    for i in range(gscan_rms.GetN()):
                        if 'high' in region.GetHash() and not 3.<gscan_rms.GetX()[i]<10.:
                            pass
                        elif 'low' in region.GetHash() and not 300.<gscan_rms.GetX()[i]<700.:
                            pass
                        else:
                            for dict in self.hrms:
                                if 'high' in region.GetHash():
                                    dict['hi'].Fill(gscan_rms.GetErrorY(i))
                                else:
                                    dict['lo'].Fill(gscan_rms.GetErrorY(i))

                    if gscan.GetFunction('fslope'):
                        fit = gscan.GetFunction('fslope').Clone()                       
                    else:
                        print('this event has no fslope', event.runNumber)
                        continue
                                                
                    if self.probbad:#event.data['goodEvent']:
                        for h in [self.hprobbad, self.hprobbadlowzoom, self.hprobbadhighzoom]:
                            h.Fill(ROOT.TMath.Prob(fit.GetChisquare(), fit.GetNDF()))
                    else:
                        for h in [self.hprobgood, self.hprobgoodhighzoom, self.hprobgoodlowzoom]:
                            h.Fill(ROOT.TMath.Prob(fit.GetChisquare(), fit.GetNDF()))
                                


                    
                        
                        
                             
