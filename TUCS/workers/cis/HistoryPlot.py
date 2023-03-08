# Author: Christopher Tunnell <tunnell@hep.uchicago.edu>
#
# March 04, 2009
#

import datetime
from src.GenericWorker import *
from src.oscalls import *
import src.MakeCanvas

class HistoryPlot(GenericWorker):
    "Compute history plot"

    c1 = None

    def __init__(self, runType, dateLabel,savePlot=False):
        self.runType = runType
        self.savePlot = savePlot
        self.dateLabel = dateLabel
        self.dir = getPlotDirectory()
        self.dir = '%s/cis' % self.dir
        createDir(self.dir)
        self.dir = '%s/Public_Plots' % self.dir
        createDir(self.dir)
        self.dir = '%s/HistoryPlots' % self.dir
        createDir(self.dir)

        self.firstTime = True
        self.vals = {}

        if self.c1==None:
            self.c1 = src.MakeCanvas.MakeCanvas()
            #self.c1.SetTitle("Put here a nice title")


    def ProcessStart(self):
        if self.firstTime:
            return

        self.hhist = ROOT.TH1F('Statistics', '', 100, 100*-0.03, 100*+0.03)
        #ROOT.TStyle.SetHistLineColor(kBlue)
        #self.hhist.SetLineColor(kBlue)
        self.c1.SetLogy(1)
        self.hhist.GetXaxis().SetTitle("Variation of ADC Calibration Constants [%]")
        self.hhist.GetXaxis().CenterTitle(True)
        self.hhist.GetYaxis().SetTitle("Number of ADC Channels")
        self.hhist.GetYaxis().CenterTitle(True)
        self.hhist.GetYaxis().SetTitleOffset(1.45)
        self.hhist.SetLineColor(ROOT.kBlue + 2)

    def ProcessStop(self):
        if self.firstTime:
            self.firstTime = False
            return
            
        self.c1.cd()
        #ROOT.gStyle.SetOptStat(111110)
        ROOT.gStyle.SetOptStat(0)
        #ROOT.gStyle.SetStatX(0.78)
        #ROOT.gStyle.SetStatY(0.83)

        ROOT.gPad.SetTickx()
        ROOT.gPad.SetTicky()

	# Add underflow and overflow
        self.hhist.SetBinContent(1, self.hhist.GetBinContent(1) + self.hhist.GetBinContent(0))
        #self.hhist.SetBinContent(100, 1000)
        nbins = self.hhist.GetSize()
        # print("\n\nnbins: ", nbins, "\n\n")
        self.hhist.SetBinContent(int(nbins) -2, self.hhist.GetBinContent(nbins) + self.hhist.GetBinContent(nbins + 1))
        self.hhist.Draw()
        print(self.hhist.GetEntries())
        # hack
        self.c1.SetLeftMargin(0.14)
        self.c1.SetRightMargin(0.14)
        #self.c1.SetTopMargin(0.14)
        self.c1.Modified()


        # l = ROOT.TLatex()
        # l.SetNDC()
        # l.SetTextFont(72)
        # l.DrawLatex(0.16,0.85,"ATLAS") 

        # l2 = ROOT.TLatex()
        # l2.SetNDC()
        # l2.DrawLatex(0.25,0.85,"Preliminary")
 
        l3 = ROOT.TLatex()
        l3.SetNDC()
        l3.DrawLatex(0.16, 0.795, "Tile Calorimeter")
                

        l4 = ROOT.TLatex()
        l4.SetNDC()
        l4.DrawLatex(0.16, 0.74, self.dateLabel)

        '''
        l3 = ROOT.TLatex()
        l3.SetNDC()
        l3.SetTextSize(0.04)
        #l3.DrawLatex(0.27,0.94,"#bf{CIS Stability: Sep vs. Nov-Dec 2014}") #more detailed title for public plots
        l3.DrawLatex(0.40,0.87,"#bf{CIS Stability}")       
        '''
        '''
        ## Add "Stats" Boxes
        pt = TPaveText(0.5363409,0.703125,0.88370927,0.9027778,"brNDC")
        pt.SetName("stats")
        pt.SetBorderSize(0)
        pt.SetFillColor(0)
        pt.SetTextAlign(12)
      
        pt.SetName("stats");
        pt.SetBorderSize(0);
        pt.SetFillColor(0);
        pt.SetTextAlign(12);
        pt.SetTextFont(42);
        AText = pt.AddText(0.03,0.7,"Mean");
        AText.SetTextSize(0.035);
        AText = pt.AddText(0.97,0.7,"%10.2f%%" % (self.hhist.GetMean(1)));
        AText.SetTextSize(0.035);
        AText.SetTextAlign(32);
        AText = pt.AddText(0.03,0.5,"RMS");
        AText.SetTextSize(0.035);
        AText = pt.AddText(0.97,0.5,"%10.2f%%" % (self.hhist.GetRMS(1)));
        AText.SetTextSize(0.035);
        AText.SetTextAlign(32);
        pt.Draw();
 
     
        
        text = ptstats.AddText(0.03, 0.90, "Entries")
        text.SetTextSize(.035)
        text = ptstats.AddText(0.97,0.90, str(int(self.hhist.GetEntries())))
        text.SetTextAlign(32)
        text.SetTextSize(.035)
        text = ptstats.AddText(0.03, 0.70, "Mean")
        text.SetTextSize(.035)
        text = ptstats.AddText(0.97, 0.70, "%.2g%%" % (self.hhist.GetMean(1)))
        text.SetTextAlign(32)
        text.SetTextSize(.035)
        text = ptstats.AddText(0.03, 0.50, "RMS")
        text.SetTextSize(.035)
        text = ptstats.AddText(0.97, 0.50, %.2g%%" % (self.hhist.GetRMS(1)))
        text.SetTextAlign(32)
        text.SetTextSize(.035)
        text = ptstats.AddText(0.03, 0.30, "Underflow")
        text.SetTextSize(.035)
        text = ptstats.AddText(0.97, 0.30, str(int(self.hhist.GetBinContent(0))))
        text.SetTextAlign(32)
        text.SetTextSize(.035)
        text = ptstats.AddText(0.03, 0.10, "Overflow")
        text.SetTextSize(.035)
        text = ptstats.AddText(0.97, 0.10, str(int(self.hhist.GetBinContent(self.hhist.GetNbinsX()+1))))
        text.SetTextAlign(32)
        text.SetTextSize(.035)
        ptstats.Draw()
        
     veText *pt = new TPaveText(0.5363409,0.703125,0.8370927,0.9027778,"brNDC");
   pt->SetName("stats");
   pt->SetBorderSize(0);
   pt->SetFillColor(0);
   pt->SetTextAlign(12);
   pt->SetTextFont(42);
   AText = pt->AddText(0.03,0.7,"Mean");
   AText->SetTextSize(0.035);
   AText = pt->AddText(0.97,0.7,"-0.04%");
   AText->SetTextSize(0.035);
   AText->SetTextAlign(32);
   AText = pt->AddText(0.03,0.5,"RMS");
   AText->SetTextSize(0.035);
   AText = pt->AddText(0.97,0.5,"0.2%");
   AText->SetTextSize(0.035);
   AText->SetTextAlign(32);
   pt->Draw();
   '''   



        l5 = ROOT.TLatex()
        l5.SetNDC()
        l5.SetTextSize(.035)
        l5.DrawLatex(.66,.84,"Mean %10.3f%%" % (self.hhist.GetMean(1)))


        l6 = ROOT.TLatex()
        l6.SetNDC()
        l6.SetTextSize(.035)
        l6.DrawLatex(.66,.795,"RMS %10.3f%%" % (self.hhist.GetRMS(1)))
        
        self.c1.SetTopMargin(0.09)
        self.c1.Modified()  
        
        self.c1.Print("%s/history.png" % self.dir)
        self.c1.Print("%s/history.pdf" % self.dir)
        self.c1.Print("%s/history.C" % self.dir)
        self.c1.Print("%s/history.eps" % self.dir)
        self.c1.Print("%s/history.root" % self.dir)
        
        

    def ProcessRegion(self, region):
        if 'gain' not in region.GetHash() or region.GetEvents() == set():
            return

        mean = 0.
        i = 0
        n = 0
        dates = []
        for event in region.GetEvents():
            if event.run.runType == self.runType:
                if i == 0:
                    dates.append(event.run.time.split()[0])
                if 'calibration' in event.data and\
                       'goodRegion' in event.data and\
                       'goodEvent' in event.data:
                       #event.data.has_key('calibratableRegion'):
                    if event.data['goodRegion'] and event.data['goodEvent']:
                        mean += event.data['calibration']
                        n += 1
                i = 1             
        
        if n == 0:
            return
        mean = mean / n
        
        if self.firstTime:
            self.vals[region.GetHash()] = mean
        else:
            if region.GetHash() in self.vals:
                fill_value = 100*(mean-self.vals[region.GetHash()])/mean
                self.hhist.Fill(fill_value)
                if fill_value > 3 or fill_value < -3:
                    print(f"High CIS deviation in {region.GetHash()}: {fill_value}")
#                print(100*(mean-self.vals[region.GetHash()])/mean, mean, self.vals[region.GetHash()])
            else:
                print("couldn't find corresponding for %s" % region.GetHash())

