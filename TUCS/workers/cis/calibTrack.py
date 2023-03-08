# Author: Dave Hollander <daveh@uchicago.edu>
#
# November 10, 2009
#

from src.GenericWorker import *
from src.oscalls import *
import src.MakeCanvas
from src.ReadGenericCalibration import *
from src.region import *
from math import *

class calibTrack(GenericWorker):
    "Track the calibration changes per channel"

    def __init__(self, calibType = 'calibration'):
        self.dir = getPlotDirectory() + '/cis'
        self.calibType = calibType
        createDir(self.dir)
        self.c1 = src.MakeCanvas.MakeCanvas()

    def ProcessStart(self):
        self.graphs1 = [ROOT.TH2D('graphs1','',64,0,63,48,-0.5,47) for i in range(4)]
        self.graphs2 = [ROOT.TH2D('graphs2','',64,0,63,48,-0.5,47) for i in range(4)]

    def ProcessStop(self):
        self.c1.cd()
        ROOT.gStyle.SetPalette(1)
        self.c1.SetLeftMargin(0.14)
        self.c1.SetRightMargin(0.14)

        self.c1.Print("%s/CalibTrack_high.eps[" % (self.dir))
        self.c1.Print("%s/CalibTrack_low.eps[" % (self.dir))

        for i in range(4):
            # todo fixme, this should be in src/region.py
            if   i == 0: name = 'LBA'
            elif i == 1: name = 'LBC'
            elif i == 2: name = 'EBA'
            elif i == 3: name = 'EBC'

            graph = self.graphs1[i]
            graph.SetMaximum(1.2)
            graph.Draw("COLZ")
            graph.GetXaxis().SetTitle("Module")
            graph.GetYaxis().SetTitle("Channel number")
            graph.Draw("COLZ")

            leg = ROOT.TLegend(0.6190,0.96,1.0,1.0)
            leg.SetBorderSize(0)
            leg.SetFillColor(0)
        
            leg.AddEntry(graph, "low gain : channel mean / detector mean","P")
            
            leg.Draw()
        
            pt = ROOT.TPaveText(0.1017812,0.96,0.3053435,1.0, "brNDC")
            pt.AddText("%s Status" % name)
            pt.SetBorderSize(0)
            pt.SetFillColor(0)
            pt.Draw()

            self.c1.Print("%s/CalibTrack_low.eps" % (self.dir)) 
                        
            graph2 = self.graphs2[i]
            graph2.SetMaximum(1.2)
            graph2.Draw("COLZ")
            graph2.SetFillColor(0)
            graph2.GetXaxis().SetTitle("Module")
            graph2.GetYaxis().SetTitle("Channel number")
            graph2.Draw("COLZ")
                        
            graph.Draw("COLZ")
            graph2.Draw("COLZ")
            
            leg = ROOT.TLegend(0.6190,0.96,1.0,1.0)
            leg.SetBorderSize(0)
            leg.SetFillColor(0)
        
            leg.AddEntry(graph2, "high gain : channel mean / detector mean","P")

            leg.Draw()
        
            pt = ROOT.TPaveText(0.1017812,0.96,0.3053435,1.0, "brNDC")
            pt.AddText("%s Status" % name)
            pt.SetBorderSize(0)
            pt.SetFillColor(0)
            pt.Draw()

            self.c1.Print("%s/CalibTrack_high.eps" % (self.dir))
                        
        self.c1.Print("%s/CalibTrack_low.eps]" % (self.dir))
        self.c1.Print("%s/CalibTrack_high.eps]" % (self.dir))
        self.c1.Clear()
                    
    def ProcessRegion(self, region):
        if 'gain' not in region.GetHash():
            return

        x, y, z, w = region.GetNumber()
        x = x - 1
        
        meanlo = 0
        nlo = 0
                
        meanhi = 0
        nhi = 0                        
        
        for event in region.GetEvents():
            if event.run.runType == 'CIS':
                variable1 = 'calibratableRegion'
                variable2 = 'calibratableEvent'
                if self.calibType in event.data and variable1 in event.data and\
                       event.data[variable1] and variable2 in event.data and\
                       event.data[variable2]:
                                             
                    if 'lowgain' in region.GetHash():
                        meanlo += event.data[self.calibType]
                        nlo += 1
                    else:
                        meanhi += event.data[self.calibType]
                        nhi += 1
                        
        if nlo != 0:
            ratiolo = (meanlo/nlo)/1.294
            self.graphs1[x].Fill(y, z, ratiolo)
                                    
        if nhi != 0:
            ratiohi = (meanhi/nhi)/81.367
            self.graphs2[x].Fill(y, z, ratiohi)
                        
