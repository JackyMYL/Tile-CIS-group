# Author: Brendan Haas <brendanalberthaas@gmail.com>
#
# August 15th 2011
#
#Yes, I know this code is inefficient, but it's easy enough to understand and allows for individual customization of the 8 outputted plots

from src.GenericWorker import *
import src.MakeCanvas
from src.oscalls import *

class HistPlotRegions(GenericWorker):

    c1 = None

    def __init__(self, runType, savePlot=False):
        self.runType = runType
        self.savePlot = savePlot

        self.dir = getPlotDirectory()

        self.firstTime = True
        self.vals = {}

        self.HistChanList = []
        
        if self.c1==None:
            self.c1 = src.MakeCanvas.MakeCanvas()
            #self.c1.SetTitle("Put here a nice title")

    def ProcessStart(self):
        if self.firstTime:
            return
        
        self.histregions0 = ROOT.TH2D('histregions0', 'High-Gain LBA', 64, 0, 65, 48, 0, 49)
        self.histregions1 = ROOT.TH2D('histregions1', 'High-Gain LBC', 64, 0, 65, 48, 0, 49)
        self.histregions2 = ROOT.TH2D('histregions2', 'High-Gain EBA', 64, 0, 65, 48, 0, 49)
        self.histregions3 = ROOT.TH2D('histregions3', 'High-Gain EBC', 64, 0, 65, 48, 0, 49)
        self.histregions4 = ROOT.TH2D('histregions4', 'Low-Gain LBA', 64, 0, 65, 48, 0, 49)
        self.histregions5 = ROOT.TH2D('histregions5', 'Low-Gain LBC', 64, 0, 65, 48, 0, 49)
        self.histregions6 = ROOT.TH2D('histregions6', 'Low-Gain EBA', 64, 0, 65, 48, 0, 49)
        self.histregions7 = ROOT.TH2D('histregions7', 'Low-Gain EBC', 64, 0, 65, 48, 0, 49)
        
    def ProcessStop(self):
        if self.firstTime:
            self.firstTime = False
            return
            
        self.c1.cd()
        ROOT.gStyle.SetPalette(1)
        ROOT.gStyle.SetOptStat(0)
        self.c1.SetLeftMargin(0.14)
        self.c1.SetRightMargin(0.14)

#LBA High Gain

        self.histregions0.SetMaximum(.1)
        self.histregions0.SetMinimum(-.5)
        self.histregions0.GetXaxis().SetTitle("Module Number")
        self.histregions0.GetXaxis().CenterTitle(True)
        self.histregions0.GetYaxis().SetTitle("Channel Number")
        self.histregions0.GetYaxis().CenterTitle(True)
        self.histregions0.Draw("COLZ")

        leg0 = ROOT.TLegend(0.6190, 0.96, 1.0, 1.0)
        leg0.SetBorderSize(0)
        leg0.SetFillColor(0)
        leg0.AddEntry(histregions0, "Percent Change in CIS Constant", "P")
        leg0.Draw()

        title0 = ROOT.TLatex()
        title0.SetNDC()
        title0.SetTextFont(62)
        title0.SetTextSize(.045)
        title0.DrawLatex(.25, .955, "LBA High-Gain Region History")

        self.c1.Modified()  
        
        self.c1.Print("%s/HistRegionsLBAHigh.png" % self.dir)
        self.c1.Print("%s/HistRegionsLBAHigh.eps" % self.dir)
        self.c1.Print("%s/HistRegionsLBAHigh.root" % self.dir)

#LBC High Gain

        self.histregions1.SetMaximum(.1)
        self.histregions1.SetMinimum(-.5)
        self.histregions1.GetXaxis().SetTitle("Module Number")
        self.histregions1.GetXaxis().CenterTitle(True)
        self.histregions1.GetYaxis().SetTitle("Channel Number")
        self.histregions1.GetYaxis().CenterTitle(True)
        self.histregions1.Draw("COLZ")

        leg1 = ROOT.TLegend(0.6190, 0.96, 1.0, 1.0)
        leg1.SetBorderSize(0)
        leg1.SetFillColor(0)
        leg1.AddEntry(histregions1, "Percent Change in CIS Constant", "P")
        leg1.Draw()

        title1 = ROOT.TLatex()
        title1.SetNDC()
        title1.SetTextFont(62)
        title1.SetTextSize(.045)
        title1.DrawLatex(.25, .955, "LBC High-Gain Region History")

        self.c1.Modified()  
        
        self.c1.Print("%s/HistRegionsLBCHigh.png" % self.dir)
        self.c1.Print("%s/HistRegionsLBCHigh.eps" % self.dir)
        self.c1.Print("%s/HistRegionsLBCHigh.root" % self.dir)

#EBA High Gain

        self.histregions2.SetMaximum(.1)
        self.histregions2.SetMinimum(-.5)
        self.histregions2.GetXaxis().SetTitle("Module Number")
        self.histregions2.GetXaxis().CenterTitle(True)
        self.histregions2.GetYaxis().SetTitle("Channel Number")
        self.histregions2.GetYaxis().CenterTitle(True)
        self.histregions2.Draw("COLZ")

        leg2 = ROOT.TLegend(0.6190, 0.96, 1.0, 1.0)
        leg2.SetBorderSize(0)
        leg2.SetFillColor(0)
        leg2.AddEntry(histregions2, "Percent Change in CIS Constant", "P")
        leg2.Draw()

        title2 = ROOT.TLatex()
        title2.SetNDC()
        title2.SetTextFont(62)
        title2.SetTextSize(.045)
        title2.DrawLatex(.25, .955, "EBA High-Gain Region History")

        self.c1.Modified()  
        
        self.c1.Print("%s/HistRegionsEBAHigh.png" % self.dir)
        self.c1.Print("%s/HistRegionsEBAHigh.eps" % self.dir)
        self.c1.Print("%s/HistRegionsEBAHigh.root" % self.dir)

#EBC High Gain

        self.histregions3.SetMaximum(.1)
        self.histregions3.SetMinimum(-.5)
        self.histregions3.GetXaxis().SetTitle("Module Number")
        self.histregions3.GetXaxis().CenterTitle(True)
        self.histregions3.GetYaxis().SetTitle("Channel Number")
        self.histregions3.GetYaxis().CenterTitle(True)
        self.histregions3.Draw("COLZ")

        leg3 = ROOT.TLegend(0.6190, 0.96, 1.0, 1.0)
        leg3.SetBorderSize(0)
        leg3.SetFillColor(0)
        leg3.AddEntry(histregions3, "Percent Change in CIS Constant", "P")
        leg3.Draw()

        title3 = ROOT.TLatex()
        title3.SetNDC()
        title3.SetTextFont(62)
        title3.SetTextSize(.045)
        title3.DrawLatex(.25, .955, "EBC High-Gain Region History")

        self.c1.Modified()  
        
        self.c1.Print("%s/HistRegionsEBCHigh.png" % self.dir)
        self.c1.Print("%s/HistRegionsEBCHigh.eps" % self.dir)
        self.c1.Print("%s/HistRegionsEBCHigh.root" % self.dir)

#LBA Low Gain

        self.histregions4.SetMaximum(.1)
        self.histregions4.SetMinimum(-.5)
        self.histregions4.GetXaxis().SetTitle("Module Number")
        self.histregions4.GetXaxis().CenterTitle(True)
        self.histregions4.GetYaxis().SetTitle("Channel Number")
        self.histregions4.GetYaxis().CenterTitle(True)
        self.histregions4.Draw("COLZ")

        leg4 = ROOT.TLegend(0.6190, 0.96, 1.0, 1.0)
        leg4.SetBorderSize(0)
        leg4.SetFillColor(0)
        leg4.AddEntry(histregions4, "Percent Change in CIS Constant", "P")
        leg4.Draw()

        title4 = ROOT.TLatex()
        title4.SetNDC()
        title4.SetTextFont(62)
        title4.SetTextSize(.045)
        title4.DrawLatex(.25, .955, "LBA Low-Gain Region History")

        self.c1.Modified()  
        
        self.c1.Print("%s/HistRegionsLBALow.png" % self.dir)
        self.c1.Print("%s/HistRegionsLBALow.eps" % self.dir)
        self.c1.Print("%s/HistRegionsLBALow.root" % self.dir)

#LBC Low Gain

        self.histregions5.SetMaximum(.1)
        self.histregions5.SetMinimum(-.5)
        self.histregions5.GetXaxis().SetTitle("Module Number")
        self.histregions5.GetXaxis().CenterTitle(True)
        self.histregions5.GetYaxis().SetTitle("Channel Number")
        self.histregions5.GetYaxis().CenterTitle(True)
        self.histregions5.Draw("COLZ")

        leg5 = ROOT.TLegend(0.6190, 0.96, 1.0, 1.0)
        leg5.SetBorderSize(0)
        leg5.SetFillColor(0)
        leg5.AddEntry(histregions5, "Percent Change in CIS Constant", "P")
        leg5.Draw()

        title5 = ROOT.TLatex()
        title5.SetNDC()
        title5.SetTextFont(62)
        title5.SetTextSize(.045)
        title5.DrawLatex(.25, .955, "LBC Low-Gain Region History")

        self.c1.Modified()  
        
        self.c1.Print("%s/HistRegionsLBCLow.png" % self.dir)
        self.c1.Print("%s/HistRegionsLBCLow.eps" % self.dir)
        self.c1.Print("%s/HistRegionsLBCLow.root" % self.dir)

#EBA Low Gain

        self.histregions6.SetMaximum(.1)
        self.histregions6.SetMinimum(-.5)
        self.histregions6.GetXaxis().SetTitle("Module Number")
        self.histregions6.GetXaxis().CenterTitle(True)
        self.histregions6.GetYaxis().SetTitle("Channel Number")
        self.histregions6.GetYaxis().CenterTitle(True)
        self.histregions6.Draw("COLZ")

        leg6 = ROOT.TLegend(0.6190, 0.96, 1.0, 1.0)
        leg6.SetBorderSize(0)
        leg6.SetFillColor(0)
        leg6.AddEntry(histregions6, "Percent Change in CIS Constant", "P")
        leg6.Draw()

        title6 = ROOT.TLatex()
        title6.SetNDC()
        title6.SetTextFont(62)
        title6.SetTextSize(.045)
        title6.DrawLatex(.25, .955, "EBA Low-Gain Region History")

        self.c1.Modified()  
        
        self.c1.Print("%s/HistRegionsEBALow.png" % self.dir)
        self.c1.Print("%s/HistRegionsEBALow.eps" % self.dir)
        self.c1.Print("%s/HistRegionsEBALow.root" % self.dir)

#EBC Low Gain

        self.histregions7.SetMaximum(.1)
        self.histregions7.SetMinimum(-.5)
        self.histregions7.GetXaxis().SetTitle("Module Number")
        self.histregions7.GetXaxis().CenterTitle(True)
        self.histregions7.GetYaxis().SetTitle("Channel Number")
        self.histregions7.GetYaxis().CenterTitle(True)
        self.histregions7.Draw("COLZ")

        leg7 = ROOT.TLegend(0.6190, 0.96, 1.0, 1.0)
        leg7.SetBorderSize(0)
        leg7.SetFillColor(0)
        leg7.AddEntry(histregions7, "Percent Change in CIS Constant", "P")
        leg7.Draw()

        title7 = ROOT.TLatex()
        title7.SetNDC()
        title7.SetTextFont(62)
        title7.SetTextSize(.045)
        title7.DrawLatex(.25, .955, "EBC Low-Gain Region History")

        self.c1.Modified()  
        
        self.c1.Print("%s/HistRegionsEBCLow.png" % self.dir)
        self.c1.Print("%s/HistRegionsEBCLow.eps" % self.dir)
        self.c1.Print("%s/HistRegionsEBCLow.root" % self.dir)

        def sortbyhistnumber(tup):
            return tup[1]

        def sortbyhistregion(tup):
            return tup[0]

        #Lines for sorting based on region
        with open(os.path.join(getResultDirectory(),'HistChanRegionList.log'), 'w') as listhistchannels1:
            for entry in sorted(self.HistChanList, key = sortbyhistregion):
                listhistchannels1.write("%s\t%s \n" % entry)

        #Lines for sorting based on % change in CIS Constant
        with open(os.path.join(getResultDirectory(),'HistChanNumberList.log'), 'w') as listhistchannels2:
            for entry in sorted(self.HistChanList, key = sortbyhistnumber):
                listhistchannels2.write("%s\t%s \n" % entry)

        print("HistChanRegionList.log and HistChanNumberList.log updated in Tucs directory")

    def ProcessRegion(self, region):
        if 'gain' not in region.GetHash() or region.GetEvents() == set():
            return

        mean = 0
        n = 0
        for event in region.GetEvents():
            if event.runType == self.runType:
                if 'calibration' in event.data and\
                       'goodRegion' in event.data and\
                       'goodEvent' in event.data:
#                       event.data.has_key('calibratableRegion'):
                    if event.data['goodRegion'] and event.data['goodEvent']:
                        mean += event.data['calibration']
                        n += 1
        if n == 0:
            return
        mean = mean / n
        
        if self.firstTime:
            self.vals[region.GetHash()] = mean
        else:
            if region.GetHash() in self.vals:
                variation = 100*(mean-self.vals[region.GetHash()])/mean
                det, part, mod, chan, gain = region.GetHash().split('_')
                mod = int(mod[1:])
                chan = int(chan[1:])
                if part == 'LBA' and gain == 'highgain':
                    self.histregions0.SetBinContent(mod, chan, variation)
                if part == 'LBC' and gain == 'highgain':
                    self.histregions1.SetBinContent(mod, chan, variation)
                if part == 'EBA' and gain == 'highgain':
                    self.histregions2.SetBinContent(mod, chan, variation)
                if part == 'EBC' and gain == 'highgain':
                    self.histregions3.SetBinContent(mod, chan, variation)
                if part == 'LBA' and gain == 'lowgain':
                    self.histregions4.SetBinContent(mod, chan, variation)
                if part == 'LBC' and gain == 'lowgain':
                    self.histregions5.SetBinContent(mod, chan, variation)
                if part == 'EBA' and gain == 'lowgain':
                    self.histregions6.SetBinContent(mod, chan, variation)
                if part == 'EBC' and gain == 'lowgain':
                    self.histregions7.SetBinContent(mod, chan, variation)
                #Line to determine what channels to view on log file
                if variation >= -100 and variation <= 100:
                    histstrregion = str(region)
                    self.HistChanList.append((histstrregion, variation))
            else:
                print(("Couldn't find corresponding for %s" % region.GetHash()))
