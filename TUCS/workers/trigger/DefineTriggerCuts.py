# Author: Bernardo Sotto-Maior Peralva <bernardo@cern.ch>
#
# March 04, 2010
#

from src.GenericWorker import *
from src.oscalls import *
import src.MakeCanvas
import ROOT

class DefineTriggerCuts(GenericWorker):
    "Define Trigger Cuts based on PMT scans histograms with the 'print' data variable set"

    def __init__(self, zeroGainCutValue = 0.1, lowGainCutValue = 0.5):
        #create histograms
        self.histMeanTile = ROOT.TH1D("All Channels Tile (Mean value)", "All Channels Tile (Mean value)",100, -50, 200)
        self.histMeanL1Calo = ROOT.TH1D("All Channels L1Calo (Mean value)", "All Channels L1Calo (Mean value)",100, -50, 2000)
        self.histRmsTile = ROOT.TH1D("All Channels Tile (RMS value)", "All Channels Tile (RMS value)",100, -50, 200)
        self.histRmsL1Calo = ROOT.TH1D("All Channels L1Calo (RMS value)", "All Channels L1Calo (RMS value)",100, -50, 200)
        self.histMeanRmsTile = ROOT.TH2F("MeanRmsTile", "Mean x RMS Tile", 25, -50, 200, 25, -50, 200);
        self.histMeanRmsL1Calo = ROOT.TH2F("MeanRmsL1Calo", "Mean x RMS L1Calo", 25, -50, 200, 25, -50, 200);

        self.zeroGainCutValue = zeroGainCutValue
        self.lowGainCutValue = lowGainCutValue
        self.zeroGainCut =-1
        self.lowGainCut =-1
        
        self.c1 = src.MakeCanvas.MakeCanvas()
        self.dir = getPlotDirectory()
        createDir('%s/print' % self.dir)
        self.dir = '%s/print' % self.dir

        self.subdirs = []

    def ProcessStart(self):
        global run_list
        for run in run_list.getRunsOfType('L1Calo'):
            self.subdirs += [ self.dir + '/RunNumber%s' %run.runNumber ]
        for subdir in self.subdirs:
            print("Sub-directory to be created: %s" %subdir)
            createDir(subdir)
        if len(self.subdirs)==0:
            print("No subdirs, just setting subdir to dir")
            self.subdirs += [ self.dir ]

    def ProcessRegion(self, region):
        
        newevents = set()

        if 'gain' not in region.GetHash():
            for event in region.GetEvents():
                if event.run.runType != 'staging':
                    newevents.add(event)
            region.SetEvents(newevents)
            return
        
         # Either lowgain or highgain should work
        if 'lowgain' in region.GetHash():
            for event in region.GetEvents():
                [part, mod, chan, gain] = region.GetNumber()
                self.zeroGainCut = self.zeroGainCutValue*event.data['DACvalue']
                self.lowGainCut  = self.lowGainCutValue*event.data['DACvalue']
                if (event.data['nEvtL1Calo'] != 0):
                    self.histMeanTile.Fill(event.data['meanTile'])
                    self.histMeanL1Calo.Fill(event.data['meanL1Calo'])
                    self.histRmsTile.Fill(event.data['rmsTile'])
                    self.histRmsL1Calo.Fill(event.data['rmsL1Calo'])
                    self.histMeanRmsTile.Fill(event.data['meanTile'],event.data['rmsTile'])
                    self.histMeanRmsL1Calo.Fill(event.data['meanL1Calo'],event.data['rmsL1Calo'])

    def ProcessStop(self):
        
        #Plot and save histogram for L1Calo
        #self.c2 = ROOT.TCanvas("canvas2", "All Channels L1Calo (Mean value)", 600, 600)
        self.c1.cd()
        #ROOT.gStyle.SetOptStat(1111)
        self.histMeanL1Calo.Draw()
        self.histMeanL1Calo.SetTitle("Histogram for L1Calo Mean Values and Cuts")
        self.histMeanL1Calo.SetXTitle("Mean value")
        self.histMeanL1Calo.SetStats(0)
        self.c1.SetLogy()
        peak = self.histMeanL1Calo.GetBinCenter(self.histMeanL1Calo.GetMaximumBin());

        #Plot vertical cut lines for L1Calo histogram
        lowGainCutLineL1Calo = ROOT.TLine()
        lowGainCutLineL1Calo.SetLineColor(58)
        lowGainCutLineL1Calo.DrawLine(self.lowGainCut,0,self.lowGainCut,self.histMeanL1Calo.GetMaximum())

        deadCutLineL1Calo = ROOT.TLine()
        deadCutLineL1Calo.SetLineColor(58)
        deadCutLineL1Calo.DrawLine(self.zeroGainCut,0,self.zeroGainCut,self.histMeanL1Calo.GetMaximum())

        self.c1.Print("%s/histMeanL1Calo.pdf" % (self.subdirs[0]),"pdf")

        #Plot and save histogram for Tile
        #self.c1 = ROOT.TCanvas("canvas1", "All Channels Tile (Mean value)", 600, 600)
        self.c1.cd()
        self.histMeanTile.Draw()
        self.histMeanTile.SetTitle("Histogram for Tile Mean Values and Cuts")
        self.histMeanTile.SetXTitle("Mean value")
        self.histMeanTile.SetStats(0)
        self.c1.SetLogy()

        #Plot vertical cut lines for Tile histogram
        lowGainCutLineTile = ROOT.TLine()
        lowGainCutLineTile.SetLineColor(58)
        lowGainCutLineTile.DrawLine(self.lowGainCut,0,self.lowGainCut,self.histMeanTile.GetMaximum())

        deadCutLineTile = ROOT.TLine()
        deadCutLineTile.SetLineColor(58)
        deadCutLineTile.DrawLine(self.zeroGainCut,0,self.zeroGainCut,self.histMeanTile.GetMaximum())

        self.c1.Print("%s/histMeanTile.pdf" % (self.subdirs[0]), "pdf")

        print("Zero Gain Cut: ", self.zeroGainCut)
        print("Low Gain Cut: ", self.lowGainCut)

        #Plot RMS values for Tile
        #self.c3 = ROOT.TCanvas("canvas3", "All Channels Tile (RMS value)", 600, 600)
        self.c1.cd()
        self.histRmsTile.Draw()
        self.histRmsTile.SetTitle("Histogram for All Channels Tile (RMS value)")
        self.histRmsTile.SetXTitle("RMS value")
        self.histRmsTile.SetStats(0)
        self.c1.SetLogy()

        self.c1.Print("%s/histRmsTile.pdf" % (self.subdirs[0]), "pdf")

        #Plot RMS values for L1Calo
        #self.c4 = ROOT.TCanvas("canvas4", "All Channels L1Calo (RMS value)", 600, 600)
        self.c1.cd()
        self.histRmsL1Calo.Draw()
        self.histRmsL1Calo.SetTitle("Histogram for All Channels L1Calo (RMS value)")
        self.histRmsL1Calo.SetXTitle("RMS value")
        self.histRmsL1Calo.SetStats(0)
        self.c1.SetLogy()

        self.c1.Print("%s/histRmsL1Calo.pdf" % (self.subdirs[0]), "pdf")

        #2D plot Mean x RMS Tile
        #self.c5 = ROOT.TCanvas("canvas5", "Mean x RMS Tile", 600, 600)
        self.c1.cd()
        self.histMeanRmsTile.Draw()
        self.histMeanRmsTile.SetTitle("Mean x RMS Tile")
        self.histMeanRmsTile.SetXTitle("Mean value")
        self.histMeanRmsTile.SetYTitle("RMS value")
        self.histMeanRmsTile.SetStats(0)
        self.c1.SetLogy()

        self.c1.Print("%s/histMeanRmsTile.pdf" % (self.subdirs[0]), "pdf")

        #2D plot Mean x RMS L1Calo
        #self.c6 = ROOT.TCanvas("canvas6", "Mean x RMS L1Calo", 600, 600)
        self.c1.cd()
        self.histMeanRmsL1Calo.Draw()
        self.histMeanRmsL1Calo.SetTitle("Mean x RMS L1Calo")
        self.histMeanRmsL1Calo.SetXTitle("Mean value")
        self.histMeanRmsL1Calo.SetYTitle("RMS value")
        self.histMeanRmsL1Calo.SetStats(0)
        self.c1.SetLogy()

        self.c1.Print("%s/histMeanRmsL1Calo.pdf" % (self.subdirs[0]), "pdf")
