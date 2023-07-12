# Author: Brendan Haas <brendanalberthaas@gmail.com>
#
# August 17th 2011
#
# Yes, I know this code is inefficient, but it's easy enough to understand and allows for indivudal customization of the 8 outputted plots
#
# Modified: Peter Camporeale and Mengyang Li
# Date: May 2023
# Content: Added special graph for LBA 14, the demonstrator

import os.path

import ROOT

import src.MakeCanvas
import src.oscalls
import src.ReadGenericCalibration
from src.region import *


class CISConstantRegions(src.ReadGenericCalibration.ReadGenericCalibration):
    "Plot the distribution of calibration constants for both gains"

    def __init__(self):
        super(CISConstantRegions, self).__init__()

        # set up the plots and text directories:
        self.dir = os.path.join(src.oscalls.getPlotDirectory(),'cis', 'Public_Plots',
                                'CISConstantsMaps')
        src.oscalls.createDir(self.dir)
        
        outputdir = os.path.join(src.oscalls.getResultDirectory(), 'results')
        #outputdir = getResultDirectory('cis/CISconregions')
        src.oscalls.createDir(outputdir)
        self.vals = {}

        self.c1 = src.MakeCanvas.MakeCanvas()

        self.hval0 = ROOT.TH2D('hval0', '', 64, 1, 65, 48, 0, 48)
        self.hval1 = ROOT.TH2D('hval1', '', 64, 1, 65, 48, 0, 48)
        self.hval2 = ROOT.TH2D('hval2', '', 64, 1, 65, 48, 0, 48)
        self.hval3 = ROOT.TH2D('hval3', '', 64, 1, 65, 48, 0, 48)
        self.hval4 = ROOT.TH2D('hval4', '', 64, 1, 65, 48, 0, 48)
        self.hval5 = ROOT.TH2D('hval5', '', 64, 1, 65, 48, 0, 48)
        self.hval6 = ROOT.TH2D('hval6', '', 64, 1, 65, 48, 0, 48)
        self.hval7 = ROOT.TH2D('hval7', '', 64, 1, 65, 48, 0, 48)
        #demonstrator
        self.hval8 = ROOT.TH2D('hval7', '', 64, 1, 65, 48, 0, 48)

        self.ChanList = []

    def ProcessStop(self):
        self.c1.cd()
        ROOT.gStyle.SetPalette(1)
        ROOT.gStyle.SetOptStat(0)
        self.c1.SetLeftMargin(0.14)
        self.c1.SetRightMargin(0.14)

#LBA High Gain
        self.Draw_Hist(self.hval0, 'LBA', 'high')
        self.c1.Modified()
        self.c1.Print("%s/CISConstantsLBAHigh.png" % self.dir)

#LBC High Gain
        self.Draw_Hist(self.hval1, 'LBC', 'high')
        self.c1.Modified()
        self.c1.Print("%s/CISConstantsLBCHigh.png" % self.dir)

#EBA High Gain
        self.Draw_Hist(self.hval2, 'EBA', 'high')
        self.c1.Modified()
        self.c1.Print("%s/CISConstantsEBAHigh.png" % self.dir)

#EBC High Gain
        self.Draw_Hist(self.hval3, 'EBC', 'high')
        self.c1.Modified()
        self.c1.Print("%s/CISConstantsEBCHigh.png" % self.dir)

#LBA Low Gain
        self.Draw_Hist(self.hval4, 'LBA', 'low')
        self.c1.Modified()
        self.c1.Print("%s/CISConstantsLBALow.png" % self.dir)

#LBC Low Gain
        self.Draw_Hist(self.hval5, 'LBC', 'low')
        self.c1.Modified()
        self.c1.Print("%s/CISConstantsLBCLow.png" % self.dir)

#EBA Low Gain
        self.Draw_Hist(self.hval6, 'EBA', 'low')
        self.c1.Modified()
        self.c1.Print("%s/CISConstantsEBALow.png" % self.dir)

#EBC Low Gain

        self.Draw_Hist(self.hval7, 'EBC', 'low')
        self.c1.Modified()
        self.c1.Print("%s/CISConstantsEBCLow.png" % self.dir)


#LBA14 (demonstrator) High Gain
        self.Draw_Hist(self.hval8, 'LBA', 'high', mod=14)
        self.c1.Modified()
        self.c1.Print("%s/CISConstantsLBADemonstrator.png" % self.dir)


#Make a two-page PDF with all 8 histograms. This makes it easier to distribute results by email.
        self.c1.Clear()
        self.c1.Divide(2,2)
        self.c1.cd(1)
        self.Draw_Hist(self.hval0, 'LBA', 'high')

        self.c1.cd(2)
        self.Draw_Hist(self.hval4, 'LBA', 'low')

        self.c1.cd(3)
        self.Draw_Hist(self.hval1, 'LBC', 'high')

        self.c1.cd(4)
        self.Draw_Hist(self.hval5, 'LBC', 'low')
        self.c1.Modified()
        self.c1.Print("%s/CISConstantsALL.pdf(" % self.dir)

        self.c1.cd(1)
        self.Draw_Hist(self.hval2, 'EBA', 'high')

        self.c1.cd(2)
        self.Draw_Hist(self.hval6, 'EBA', 'low')

        self.c1.cd(3)
        self.Draw_Hist(self.hval3, 'EBC', 'high')

        self.c1.cd(4)
        self.Draw_Hist(self.hval7, 'EBC', 'low')
        self.c1.Modified()
        self.c1.Print("%s/CISConstantsALL.pdf)" % self.dir)

        def sortbynumber(tup):
            return tup[1]

        def sortbyregion(tup):
            return tup[0]

        # Chnaged output/cis/CISconregions to results

        #Lines for sorting based on region
        with open(os.path.join(src.oscalls.getResultDirectory(),'results/CalibChanRegionList.log'), 'w') as listchannels1:
            for entry in sorted(self.ChanList, key = sortbyregion):
                listchannels1.write("%s\t%s \n" % entry)

        #Lines for sorting based on CIS Constant
        with open(os.path.join(src.oscalls.getResultDirectory(),'results/CalibChanNumberList.log'), 'w') as listchannels2:
            for entry in sorted(self.ChanList, key = sortbynumber, reverse=True):
                listchannels2.write("%s\t%s \n" % entry)
                                         
        print("CalibChanRegionList.log and CalibChanNumberList.log updated in Tucs directory")

    def ProcessRegion(self, region):
        "Fill the calibration distribution using the values from a region."

        meanlo = 0
        nlo = 0

        # High gain excluding demonstrator 
        meanhi = 0
        nhi = 0

        # Demonstrator (maybe generalize it to include channels that will generally default to half gain)
        meandem = 0
        ndem = 0

        for event in region.GetEvents():
            if event.run.runType == 'CIS':
                variable1 = 'calibratableRegion'
                variable2 = 'calibratableEvent'
                if ('calibration' in event.data):
                   # and variable1 in event.data and event.data[variable1]
                   # and variable2 in event.data and event.data[variable2]):
                    if 'lowgain' in region.GetHash():
                        meanlo += event.data['calibration']
                        nlo += 1
                    else:
                        if 'LBA' in region.GetHash() and 'm14' in region.GetHash():
                            meandem += event.data['calibration']
                            ndem += 1
                        else: # All other normal highgain channels 
                            meanhi += event.data['calibration']
                            nhi += 1

        if nlo:
            distributionlo = meanlo / nlo
            det, part, mod, chan, gain = region.GetHash().split('_')
            mod = int(mod[1:])
            chan = int(chan[1:])
            if part == 'LBA' and gain == 'lowgain':
                self.hval4.SetBinContent(mod, chan+1, distributionlo)
            if part == 'LBC' and gain == 'lowgain':
                self.hval5.SetBinContent(mod, chan+1, distributionlo)
            if part == 'EBA' and gain == 'lowgain':
                self.hval6.SetBinContent(mod, chan+1, distributionlo)
            if part == 'EBC' and gain == 'lowgain':
                self.hval7.SetBinContent(mod, chan+1, distributionlo)
            #Below Line lets one customize range of list of outlier channels for lowgain
            if distributionlo >= 0 or distributionlo <= 1000:
                strregion = str(region)
                self.ChanList.append((strregion, distributionlo))

        if nhi:
            distributionhi = meanhi / nhi
            det, part, mod, chan, gain = region.GetHash().split('_')
            mod = int(mod[1:])
            chan = int(chan[1:])
            # Separate out demonstrator
            if not part == 'LBA' or not mod == 14 or not gain == 'highgain':
                if part == 'LBA' and gain == 'highgain':
                    self.hval0.SetBinContent(mod, chan+1, distributionhi)
                if part == 'LBC' and gain == 'highgain':
                    self.hval1.SetBinContent(mod, chan+1, distributionhi)
                if part == 'EBA' and gain == 'highgain':
                    self.hval2.SetBinContent(mod, chan+1, distributionhi)
                if part == 'EBC' and gain == 'highgain':
                    self.hval3.SetBinContent(mod, chan+1, distributionhi)
            #Below Line lets one customize range of list of outlier channels for higain
            if distributionhi >= 0 or distributionhi <= 1000:
                strregion = str(region)
                self.ChanList.append((strregion, distributionhi))
        
        if ndem:
            distributiondem = meandem / ndem
            det, part, mod, chan, gain = region.GetHash().split('_')
            mod = int(mod[1:])
            chan = int(chan[1:])
            # Separate out demonstrator
            if part == 'LBA' and mod == 14 and gain == 'highgain':
                if part == 'LBA' and gain == 'highgain':
                    self.hval8.SetBinContent(mod, chan+1, distributiondem)
            #Below Line lets one customize range of list of outlier channels for higain
            if distributiondem >= 0 or distributiondem <= 1000:
                strregion = str(region)
                self.ChanList.append((strregion, distributiondem))

    def Draw_Hist(self, hist, part, gain, mod=False):
        if gain == 'low':
            gainname = 'Low-Gain'
            min = 1.22
            max = 1.36
        else:
            if part =='LBA' and mod: #If we just give it any module number (nonzero), it will be true 
                gainname = 'Half-Gain'
                min = 39.5
                max = 42.5
            else:
                gainname = 'High-Gain'
                min = 76.0
                max = 86.0
        hist.GetXaxis().SetTitle("Module Number")
        hist.GetXaxis().CenterTitle(True)
        hist.GetYaxis().SetTitle("Channel Number")
        hist.GetYaxis().CenterTitle(True)
        hist.SetMinimum(min)
        hist.SetMaximum(max)
        hist.Draw("COLZ")

        leg = ROOT.TLatex()
        leg.SetNDC()
        leg.SetTextSize(0.03)
        leg.DrawLatex(0.78, 0.980, "Avg. CIS Constant")

        title = ROOT.TLatex()
        title.SetNDC()
        title.SetTextFont(62)
        title.SetTextSize(.045)
        title.DrawLatex(0.14, .96, "%s %s Avg. CIS Constants" % (part, gainname))


