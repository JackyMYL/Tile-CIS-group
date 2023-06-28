# Author: Christopher Tunnell <tunnell@hep.uchicago.edu>
#
# March 24, 2009
# Edited: Vikram Upadhyay <vikram.upadhyay@cern.ch> , Nov 5, 2014
# Edited: Andrew Smith, Kathyrn Chapman, Oct 23 2018
# Edited: Peter Camporeale, May 2023

from src.ReadGenericCalibration import *
from src.oscalls import *
from src.region import *

class CalibDist(ReadGenericCalibration):
    "Plot the distriubiton of calibration constants for both gains"
    
    def __init__(self,dateLabel):
        self.dateLabel = dateLabel
        self.dir = getPlotDirectory()
        self.dir = '%s/cis' % self.dir
        createDir(self.dir)
        self.dir = '%s/Public_Plots' % self.dir
        createDir(self.dir)
        self.dir = '%s/CISConstantsDistributions' % self.dir
        createDir(self.dir)
        self.c1 = src.MakeCanvas.MakeCanvas()

    def ProcessStart(self):
        self.hvalhi = ROOT.TH1D('hvalhi', '', 50, 74.004, 88.716)
        self.hvallo = ROOT.TH1D('hvallo', '', 50, 1.17796, 1.41004)
        self.hvaldem = ROOT.TH1D('hvaldem', '', 15, 39.5, 42.5) #Adjust parameters
        self.hvaldemlo = ROOT.TH1D('hvaldemlo', '', 15, 1.17796, 1.41004)
        self.hvalhi.GetYaxis().SetRangeUser(0,1400)
        self.hvallo.GetYaxis().SetRangeUser(0,1400) 
        self.hvaldem.GetYaxis().SetRangeUser(0,30) #Adjust parameters
        self.hvaldemlo.GetYaxis().SetRangeUser(0,30) #Adjust parameters
        #ROOT.TStyle.SetHistLineColor(ROOT.ROOT.kBlue)
        self.hvalhi.SetLineColor(ROOT.kBlue+2)
        self.hvallo.SetLineColor(ROOT.kBlue+2)
        self.hvaldem.SetLineColor(ROOT.kBlue+2)
        self.hvaldemlo.SetLineColor(ROOT.kBlue+2)
        self.hvalhi.SetLineWidth(2)
        self.hvallo.SetLineWidth(2)
        self.hvaldem.SetLineWidth(2)
        self.hvaldemlo.SetLineWidth(2)

    def ProcessStop(self):
        self.c1.cd()
        self.c1.SetLogy(0)
        #ROOT.gStyle.SetOptStat(111110)
        ROOT.gStyle.SetOptStat(0)
        #ROOT.gStyle.SetStatX(0.83)
        #ROOT.gStyle.SetStatY(0.83)
        ROOT.gPad.SetTickx()
        ROOT.gPad.SetTicky()

        self.c1.Modified()
        self.c1.Update()
        self.c1.Modified()

        # Add underflow and overflow
        nbins = self.hvallo.GetSize
        #print nbins
        #self.hvallo.SetBinContent(1, h.GetBinContent(1) + h.GetBinContent(0))
        #self.hvallo.SetBinContent(h.GetSize(), h.GetBinContent(h.GetSize()) + h.GetBinContent(h.GetSize() + 1))
        #self.hvalhi.SetBinContent(1, h.GetBinContent(1) + h.GetBinContent(0))
        #self.hvalhi.SetBinContent(h.GetSize()-2, h.GetBinContent(h.GetSize()) + h.GetBinContent(h.GetSize() + 1))
       
        module_type_string = ["Low-Gain ", "High-Gain ", "Dem. High-Gain", "Dem. Low-Gain"]
        # self.hvallo.GetXaxis().SetTitle("Low-gain Calibration [ADC counts / pC]")
        # self.hvalhi.GetXaxis().SetTitle("High-gain Calibration [ADC counts / pC]")
        # self.hvaldem.GetXaxis().SetTitle("Half-gain Calibration [ADC counts / pC]")
        title_index = -1
        for hval in [self.hvallo, self.hvalhi, self.hvaldem, self.hvaldemlo]:
            title_index += 1
            module_title = module_type_string[title_index]
            hval.GetXaxis().SetTitle("Mean "+module_title+"CIS Constant [ADC counts / pC]")
            hval.GetYaxis().SetTitle("Number of ADC Channels")
            hval.SetTitleOffset(1.4, 'Y')
            hval.GetXaxis().CenterTitle(True)
            #hval.SetMaximum(4200)
            hval.Draw()
            hval.SetBinContent(1, hval.GetBinContent(1) + hval.GetBinContent(0))
            hval.SetBinContent(hval.GetSize(), hval.GetBinContent(hval.GetSize()) + hval.GetBinContent(hval.GetSize() + 1))
            print(hval.GetEntries())

            # hack
            self.c1.SetLeftMargin(0.14)
            self.c1.SetRightMargin(0.14)
            self.c1.Modified()

            # l = ROOT.TLatex()
            # l.SetNDC()
            # l.SetTextFont(72)
            # l.DrawLatex(0.18,0.865,"ATLAS") 

            # l0 = ROOT.TLatex()
            # l0.SetNDC()
            # #l2.SetTextFont(72)
            # l0.DrawLatex(0.27,0.865,"Preliminary")

            l2 = ROOT.TLatex()
            l2.SetNDC()
            l2.DrawLatex(0.18,0.785, module_title)
 
            l3 = ROOT.TLatex()
            l3.SetNDC()
            l3.DrawLatex(0.18, 0.825, "Tile Calorimeter")
                

            l4 = ROOT.TLatex()
            l4.SetNDC()
            #l4.DrawLatex(0.18, 0.743, "Oct 2, 2016")
            #l4.DrawLatex(0.18, 0.743, "Aug 21-Oct 21, 2015")
            l4.DrawLatex(0.18, 0.745, self.dateLabel)
            #yearstr = "2017"
            #NO TITLES KIDS
            #l3 = ROOT.TLatex()
            #l3.SetNDC()
            #l3.SetTextSize(0.04)
            #l3.DrawLatex(0.24,0.91,"#bf{CIS Calibration Constant Distribution}");
            #l3.DrawLatex(0.24,0.96,"#bf{CIS Constant Distribution: Oct-Dec 2014}");
             
            
            l5 = ROOT.TLatex()
            l5.SetNDC()
            #l5.SetTextAlign(12)
            # l5.SetTextSize(.038)
            l5.DrawLatex(0.59, 0.865, "Mean  %.3g" %(float(hval.GetMean(1))))

            l6 = ROOT.TLatex()
            l6.SetNDC()
            #l5.SetTextAlign(12)
            # l6.SetTextSize(.038)
            l6.DrawLatex(0.59, 0.825, "RMS/Mean  %.3g%%" %(100*float(hval.GetRMS(1)/hval.GetMean(1))))


            
            ####Vikramadded###########
            ####AndrewSmithaddedadded#####
            """
            ##DONT  Add "Stats" Boxes
            ptstats = TPaveText(0.65,0.70,0.85,0.90,"brNDC")
            ptstats.SetName("stats")
            ptstats.SetBorderSize(0)
            ptstats.SetFillColor(0)
            ptstats.SetTextAlign(12)
            text = ptstats.AddText(0.03, 0.90, "Entries")
            text.SetTextSize(.035)
            text = ptstats.AddText(0.97,0.90, str(int(hval.GetEntries())))
            text.SetTextAlign(32)
            text.SetTextSize(.035)
            text = ptstats.AddText(0.03, 0.70, "Mean")
            text.SetTextSize(.035)
            text = ptstats.AddText(0.97, 0.70, "%.03g" % (hval.GetMean(1)))
            text.SetTextAlign(32)
            text.SetTextSize(.035)
            text = ptstats.AddText(0.03, 0.50, "RMS")
            text.SetTextSize(.035)
            text = ptstats.AddText(0.97, 0.50, "%.03g" % (hval.GetRMS(1)))
            text.SetTextAlign(32)
            text.SetTextSize(.035)
            text = ptstats.AddText(0.03, 0.30, "Underflow")
            text.SetTextSize(.035)
            text = ptstats.AddText(0.97, 0.30, str(int(hval.GetBinContent(0))))
            text.SetTextAlign(32)
            text.SetTextSize(.035)
            text = ptstats.AddText(0.03, 0.10, "Overflow")
            text.SetTextSize(.035)
            text = ptstats.AddText(0.97, 0.10, str(int(hval.GetBinContent(hval.GetNbinsX()+1))))
            text.SetTextAlign(32)
            text.SetTextSize(.035)
            ptstats.Draw()
            """
            self.c1.Modified()
            ############################"""
            self.c1.Print("%s/calib_dist_%s.eps" % (self.dir, hval.GetName()))
            self.c1.Print("%s/calib_dist_%s.C" % (self.dir, hval.GetName()))
            self.c1.Print("%s/calib_dist_%s.png" % (self.dir, hval.GetName()))
            self.c1.Print("%s/calib_dist_%s.root" % (self.dir, hval.GetName()))
        
    def ProcessRegion(self, region):
        meanlo = 0
        nlo = 0

        meanhi = 0
        nhi = 0

        meandem = 0
        ndem = 0

        meandemlo = 0
        ndemlo = 0
        
        
        for event in region.GetEvents():
            if event.run.runType == 'CIS':

                if 'calibration' in event.data: #\
            #        and event.data.has_key('calibratableEvent') and event.data['calibratableEvent']:
##                and event.data.has_key('calibratableRegion') and event.data['calibratableRegion']:

                    if 'lowgain' in region.GetHash() and 'LBA_m14' not in region.GetHash():
                        meanlo += event.data['calibration']
                        nlo += 1
                    elif 'lowgain' in region.GetHash() and 'LBA_m14' in region.GetHash():
                        meandemlo += event.data['calibration']
                        ndemlo += 1
                    elif 'LBA_m14' in region.GetHash() and 'highgain' in region.GetHash():
                        meandem += event.data['calibration']
                        ndem += 1
                    else:
                        meanhi += event.data['calibration']
                        nhi += 1
        
        # print(ndem, nhi, nlo)

        if nlo != 0:
            self.hvallo.Fill(meanlo/nlo)
            if meanlo/nlo <1.18:
                print(region.GetHash())

        if nhi != 0:
            self.hvalhi.Fill(meanhi/nhi)
            if  meanhi/nhi < 75:
                print(region.GetHash())
        
        if ndem != 0:
            self.hvaldem.Fill(meandem/ndem)
        
        if ndemlo != 0:
            self.hvaldemlo.Fill(meandemlo/ndemlo)
                        
                             
