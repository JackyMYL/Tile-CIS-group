# Author: Andrew Hard <ahard@uchicago.edu>
#
# This worker plots the % change in the CIS calibration
# for every channel between two run intervals. The plot
# is a 2D module-channel graph.
#
# June 6, 2011
#

from src.GenericWorker import *
from src.oscalls import *
import src.MakeCanvas

class MapCalibChange(GenericWorker):
    "Compute history plot"

    c1 = None

    def __init__(self, runType, savePlot=False):
        self.runType = runType
        self.savePlot = savePlot

        self.dir = getPlotDirectory() + '/cis'
        createDir("%s/CalibChange" % self.dir)
        self.dir = "%s/CalibChange" % self.dir
        createDir(self.dir)

        if self.c1==None:
            self.c1 = src.MakeCanvas.MakeCanvas()
            #self.c1.SetTitle("Put here a nice title")

        # important definitions
        self.firstTime = True
        self.old_calibs = {}
        self.new_calibs = {}

    def ProcessStart(self):
        
        print(self.firstTime)
        
    def ProcessStop(self):

        # format and print histograms.
        self.c1.cd()
        ROOT.gStyle.SetPalette(1)
        ROOT.gStyle.SetOptStat(0)
        self.c1.SetLeftMargin(0.14)
        self.c1.SetRightMargin(0.14)
                
        # program runs twice: once for each run interval.
        if self.firstTime:
            self.firstTime = False
            return
        else:
            for gain in range(2):   
                if gain == 0:   gain_name = "lowgain"
                elif gain == 1: gain_name = "highgain"
                
                for partition in range(4):
                    if   partition == 0: name = 'LBA'
                    elif partition == 1: name = 'LBC'
                    elif partition == 2: name = 'EBA'
                    elif partition == 3: name = 'EBC'
                    
                    difference_plot = ROOT.TProfile2D('graphs0','',64,0.5,64.5,48,-0.5,47.5)

                    for module in range(1,65):
                        for channel in range(0,48):
                            key = '%s_%s_%s_%s' % (partition,module,channel,gain)

                            try:
                                self.new_calibs[key]
                            except:
                                self.new_calibs[key] = 0
                                self.old_calibs[key] = 0
                            
                            bin_new = self.new_calibs[key]
                            bin_old = self.old_calibs[key]
                                                            
                            if bin_old != 0 and bin_new != 0:
                                change = float(100*(bin_new-bin_old)/(bin_old))
                            else:
                                change = 0
                            
                            difference_plot.Fill(module,channel,change)

                    difference_plot.GetXaxis().SetTitle("Module")
                    difference_plot.GetYaxis().SetTitle("Channel number")
                    difference_plot.Draw("COLZ")
                                    
                    leg = ROOT.TLegend(0.6190,0.96,1.0,1.0)
                    leg.SetBorderSize(0)
                    leg.SetFillColor(0)
                    leg.AddEntry(difference_plot, "% Change in CIS Calibration","P")
                    leg.Draw()
                    
                    pt = ROOT.TPaveText(0.1017812,0.96,0.3053435,1.0, "brNDC")
                    pt.AddText("%s %s" % (name, gain_name))
                    pt.SetBorderSize(0)
                    pt.SetFillColor(0)
                    pt.Draw()
                    
                    self.c1.Print("%s/CalibChange_%s_%s.root" % (self.dir, name, gain_name))
                    self.c1.Print("%s/CalibChange_%s_%s.eps" % (self.dir, name, gain_name))
                                        
        
    def ProcessRegion(self, region):
        if 'gain' not in region.GetHash() or region.GetEvents() == set():
            return

        # x: partition, y: module, z: channel, w: gain.
        [x, y, z, w] = region.GetNumber()
        x = x - 1

        # default value is zero.
        if self.firstTime:
            self.new_calibs['%s_%s_%s_%s' % (x,y,z,w)] = 0
            self.old_calibs['%s_%s_%s_%s' % (x,y,z,w)] = 0

        calib_sum = 0
        calib_index = 0

        for event in region.GetEvents():
            if event.run.runType == self.runType:
                if 'calibration' in event.data and 'goodRegion' in event.data and 'goodEvent' in event.data:
                    if event.data['goodRegion'] and event.data['goodEvent']:

                        calib_sum += (event.data['calibration'])
                        calib_index += 1
                        
        if calib_index !=0:
            mean = calib_sum/calib_index
            
            if self.firstTime:
                self.new_calibs['%s_%s_%s_%s' % (x,y,z,w)] = mean
            else:
                self.old_calibs['%s_%s_%s_%s' % (x,y,z,w)] = mean

                
                

