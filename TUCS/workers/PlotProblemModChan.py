# Author: David Hollander <daveh@uchicago.edu>
#
# December 1, 2009
#

from src.GenericWorker import *
from src.oscalls import *
import src.MakeCanvas

class PlotProblemModChan(GenericWorker):
    "Make a plot of problems for module number versus channel number for all partitions"

    c1 = None

    def __init__(self, runType = 'CIS', parameter='isCalibrated', parameter2='isCalibrated'):
        self.runType = runType
        self.parameter = parameter
        self.parameter2 = parameter2

        self.dir = os.path.join(getPlotDirectory(), "cis", "Investigate", 'Problems')
        createDir(self.dir) 

        if self.c1==None:
            self.c1 = src.MakeCanvas.MakeCanvas()
            #self.c1.SetTitle("Put here a nice title")


    def ProcessStart(self):
        self.graphs1 = [ROOT.TGraph() for i in range(4)]
        self.graphs1i = [0 for i in range(4)]
        
        self.graphs2 = [ROOT.TGraph() for i in range(4)]
        self.graphs2i = [0 for i in range(4)]


    def ProcessStop(self):
        self.c1.cd()

        self.c1.Print("%s/%s.ps" % (self.dir, self.parameter))

        for i in range(4):
            # todo fixme, this should be in src/region.py
            if   i == 0: name = 'LBA'
            elif i == 1: name = 'LBC'
            elif i == 2: name = 'EBA'
            elif i == 3: name = 'EBC'

            graph = self.graphs1[i]
            if graph.GetN():
                graph.Draw("AP")
                graph.SetFillColor(0)
                graph.GetXaxis().SetTitle("Module Number")
                graph.GetYaxis().SetTitle("Channel Number within Module")
                graph.GetXaxis().SetLimits(0.2,65.8)
                graph.GetYaxis().SetRangeUser(-0.5,48.8)
                
                graph.SetMarkerStyle(20)
                graph.SetMarkerSize(2.0)
                graph.SetMarkerColor(ROOT.kRed)
                graph.Draw("AP")

            graph2 = self.graphs2[i]
            if graph2.GetN():
                graph2.Draw("AP")
                graph2.SetFillColor(0)
                graph2.GetXaxis().SetTitle("Module Number")
                graph2.GetYaxis().SetTitle("Channel Number within Module")
                graph2.GetXaxis().SetLimits(0.2,65.8)
                graph2.GetYaxis().SetRangeUser(-0.5,48.8)
                                                
                graph2.SetMarkerStyle(20)
                graph2.SetMarkerSize(1.3)
                graph2.SetMarkerColor(ROOT.kBlue)
                               
            if graph.GetN():  graph.Draw("AP")
            if graph2.GetN() and not graph.GetN():  graph2.Draw("AP")
            elif graph2.GetN(): graph2.Draw("P")

            #print graph.GetN(), graph2.GetN()
                        
            leg = ROOT.TLegend(0.6190,0.91,1.0,1.0)
            leg.SetBorderSize(0)
            leg.SetFillColor(0)

            if graph.GetN():  leg.AddEntry(graph, "low gain", "p")
            if graph2.GetN(): leg.AddEntry(graph2, "high gain", "p")

            leg.Draw()
            
            pt = ROOT.TPaveText(0.1017812,0.9129412,0.5053435,0.9952941, "brNDC")
            if self.parameter == self.parameter2:
                pt.AddText("%s Status: %s" % (name, self.parameter))
            else:
                pt.AddText("%s Status: %s & %s" % (name, self.parameter, self.parameter2))
 
            pt.SetBorderSize(0)
            pt.SetFillColor(0)
            pt.Draw()
            
            self.c1.Print("%s/%s_%s.png" % (self.dir, self.parameter, name))
                    


    def ProcessRegion(self, region):
        if 'gain' not in region.GetHash():
            return
        x, y, z, w = region.GetNumber()
        x = x - 1
        plot = False
        for event in region.GetEvents():
            #print event.data
            if event.run.runType == self.runType and 'low' in region.GetHash():
                if self.parameter in event.data and self.parameter2 in event.data:
                    if event.data[self.parameter] or event.data[self.parameter2]:
                        plot = True
                if self.parameter == 'CIS_problems' and self.parameter2 == 'CIS_problems' and self.parameter in event.data:
                    plot = False
                    for key in event.data['CIS_problems']:
                        if event.data['CIS_problems'][key]:
                       	    plot = True
                if plot:
                    self.graphs1[x].SetPoint(self.graphs1i[x], y, z)
                    self.graphs1i[x] += 1
                    break
                    
        for event in region.GetEvents():
            if event.run.runType == self.runType and 'high' in region.GetHash():
                if self.parameter in event.data and self.parameter2 in event.data:
                    if event.data[self.parameter] or event.data[self.parameter2]:
                        plot = True 
                if self.parameter == 'CIS_problems' and self.parameter2 == 'CIS_problems' and self.parameter in event.data:
                    plot = False
                    for key in event.data['CIS_problems']:
                       if event.data['CIS_problems'][key]:
                           plot = True
                if plot:
                    self.graphs2[x].SetPoint(self.graphs2i[x], y, z)
                    plot = True
                    self.graphs2i[x] += 1
                    break

