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

    def __init__(self, runType, savePlot=False, setmax=1, setmin=1):
        self.runType = runType
        self.savePlot = savePlot

        self.dir = getPlotDirectory()
        self.dir = '%s/cis' % self.dir
        createDir(self.dir)
        self.dir = '%s/Public_Plots' % self.dir
        createDir(self.dir)
        self.dir = '%s/HistoryPlots' % self.dir
        createDir(self.dir)
        self.c1 = src.MakeCanvas.MakeCanvas()
        self.firstTime = True
        self.vals = {}
        self.setmax = setmax
        self.setmin = setmin

        self.HistChanList = []

        if self.c1==None:
            self.c1 = src.MakeCanvas.MakeCanvas()
            #self.c1.SetTitle("Put here a nice title")


    def ProcessStart(self):
        if self.firstTime:
            return
        
        self.histregions0 = ROOT.TH2D('histregions0', '', 64, 1, 65, 48, 0, 48)
        self.histregions1 = ROOT.TH2D('histregions1', '', 64, 1, 65, 48, 0, 48)
        self.histregions2 = ROOT.TH2D('histregions2', '', 64, 1, 65, 48, 0, 48)
        self.histregions3 = ROOT.TH2D('histregions3', '', 64, 1, 65, 48, 0, 48)
        self.histregions4 = ROOT.TH2D('histregions4', '', 64, 1, 65, 48, 0, 48)
        self.histregions5 = ROOT.TH2D('histregions5', '', 64, 1, 65, 48, 0, 48)
        self.histregions6 = ROOT.TH2D('histregions6', '', 64, 1, 65, 48, 0, 48)
        self.histregions7 = ROOT.TH2D('histregions7', '', 64, 1, 65, 48, 0, 48)
        
        self.bin_dict = {}
        for part in ['LBA', 'LBC', 'EBA', 'EBC']:
            self.bin_dict[part] = {}
            for gain in ['lowgain', 'highgain']:
                self.bin_dict[part][gain] = {}
                for mod in range(1,65):
                    self.bin_dict[part][gain][mod] = {}
                    for chan in range(1,49):
                        self.bin_dict[part][gain][mod][chan] = 0
       
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
        self.FormatHisto(self.histregions0, 'LBA', 'highgain')
        self.c1.Modified()  
        self.c1.Print("%s/HistRegionsLBAHigh.png" % self.dir)

#LBC High Gain
        self.FormatHisto(self.histregions1, 'LBC', 'highgain')
        self.c1.Modified()  
        self.c1.Print("%s/HistRegionsLBCHigh.png" % self.dir)

#EBA High Gain
        self.FormatHisto(self.histregions2, 'EBA', 'highgain')
        self.c1.Modified()  
        self.c1.Print("%s/HistRegionsEBAHigh.png" % self.dir)

#EBC High Gain
        self.FormatHisto(self.histregions3, 'EBC', 'highgain')
        self.c1.Modified()  
        self.c1.Print("%s/HistRegionsEBCHigh.png" % self.dir)

#LBA Low Gain
        self.FormatHisto(self.histregions4, 'LBA', 'lowgain')
        self.c1.Modified()  
        self.c1.Print("%s/HistRegionsLBALow.png" % self.dir)

#LBC Low Gain
        self.FormatHisto(self.histregions5, 'LBC', 'lowgain')
        self.c1.Modified()  
        self.c1.Print("%s/HistRegionsLBCLow.png" % self.dir)

#EBA Low Gain
        self.FormatHisto(self.histregions6, 'EBA', 'lowgain')
        self.c1.Modified()  
        self.c1.Print("%s/HistRegionsEBALow.png" % self.dir)

#EBC Low Gain
        self.FormatHisto(self.histregions7, 'EBC', 'lowgain')
        self.c1.Modified()  
        self.c1.Print("%s/HistRegionsEBCLow.png" % self.dir)

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
            if event.run.runType == self.runType:
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
        det, part, mod, chan, gain = region.GetHash().split('_')
        mod = int(mod[1:])
        chan = int(chan[1:])
        
        if self.firstTime:
            self.vals[region.GetHash()] = mean
        else:
            if region.GetHash() in self.vals:
                variation = 100*(mean-self.vals[region.GetHash()])/mean
                self.bin_dict[part][gain][mod][chan+1] = 1
                if part == 'LBA' and gain == 'highgain':
                    self.histregions0.SetBinContent(mod, chan+1, variation)
                if part == 'LBC' and gain == 'highgain':
                    self.histregions1.SetBinContent(mod, chan+1, variation)
                if part == 'EBA' and gain == 'highgain':
                    self.histregions2.SetBinContent(mod, chan+1, variation)
                if part == 'EBC' and gain == 'highgain':
                    self.histregions3.SetBinContent(mod, chan+1, variation)
                if part == 'LBA' and gain == 'lowgain':
                    self.histregions4.SetBinContent(mod, chan+1, variation)
                if part == 'LBC' and gain == 'lowgain':
                    self.histregions5.SetBinContent(mod, chan+1, variation)
                if part == 'EBA' and gain == 'lowgain':
                    self.histregions6.SetBinContent(mod, chan+1, variation)
                if part == 'EBC' and gain == 'lowgain':
                    self.histregions7.SetBinContent(mod, chan+1, variation)
                #Line to determine what channels to view on log file
                if variation >= -100 and variation <= 100:
                    histstrregion = str(region)
                    self.HistChanList.append((histstrregion, variation))
            else:
                print("Couldn't find corresponding for %s" % region.GetHash())
                self.bin_dict[part][gain][mod][chan] = 1

    def FormatHisto(self, histo, part, gain):

        for i in range(1,65):
            for j in range(1,49):
                if self.bin_dict[part][gain][i][j] == 0:
                    histo.SetBinContent(i, j, -1000.0)
        histo.SetAxisRange(self.setmin, self.setmax, "Z")
        histo.GetXaxis().SetTitle("Module Number")
        histo.GetXaxis().CenterTitle(True)
        histo.GetYaxis().SetTitle("Channel Number")
        histo.GetYaxis().CenterTitle(True)
        histo.Draw("COLZ")
   
        leg = ROOT.TLatex()
        leg.SetNDC()
        leg.SetTextSize(0.03)
        leg.DrawLatex(0.68, 0.980, "Percent Change in CIS Constant") 

        if gain == 'highgain':
            gain = 'High-Gain'
        else:
            gain = 'Low-Gain'

        title = ROOT.TLatex()
        title.SetNDC()
        title.SetTextFont(62)
        title.SetTextSize(.045)
        title.DrawLatex(.14, .955, "%s %s Region History" % (part, gain))

       
