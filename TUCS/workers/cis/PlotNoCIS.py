# Author: David Hollander  January 29, 2010  <daveh@uchicago.edu>
# Updated: Andrew Hard     November 18, 2010 <ahard@uchicago.edu>
#
# This worker shows the channels in TileCal that are not sending CIS data.  If the histogram for a 
# particular module does not print, this simply means that there are no problems present. 
# This corrects an earlier bug where modules with no problems would show failing channels
# from one of the other modules.

from src.GenericWorker import *
from src.oscalls import *
import src.MakeCanvas

class PlotNoCIS(GenericWorker):
    "Make a plot of problems for module number versus channel number for all partitions"

    c1 = None

    def __init__(self):
    
        self.dir = os.path.join(getPlotDirectory(), "cis", "Investigate", 'WholeDetector')
        createDir(self.dir)

        if self.c1==None:
            self.c1 = src.MakeCanvas.MakeCanvas()
            #self.c1.SetTitle("Put here a nice title")


    def ProcessStart(self):
        print(getResultDirectory())
        self.fout = open(os.path.join(getResultDirectory(),"noCIS.txt"), "r")
        
        self.graphs1 = [ROOT.TGraph() for i in range(4)]
        self.graphs1i = [0 for i in range(4)]
        
        self.graphs2 = [ROOT.TGraph() for i in range(4)]
        self.graphs2i = [0 for i in range(4)]


    def ProcessStop(self):
        self.fout.close()
        os.remove(os.path.join(getResultDirectory(),'noCIS.txt'))
        
        self.c1.cd()

        self.c1.Print("%s/noCIS.ps[" % (self.dir))

        for i in range(4):
            
            if   i == 0: name = 'LBA'
            elif i == 1: name = 'LBC'
            elif i == 2: name = 'EBA'
            elif i == 3: name = 'EBC'

            graph = self.graphs1[i]

            graph.Draw("AP")
            graph.SetFillColor(0)
            graph.GetXaxis().SetTitle("Module Number")
            graph.GetYaxis().SetTitle("Channel Number within Module")
            graph.GetXaxis().SetLimits(-1,65.8)
            graph.GetYaxis().SetRangeUser(-1,48.8)
            
            graph.SetMarkerStyle(20)
            graph.SetMarkerSize(2.0)
            graph.SetMarkerColor(ROOT.kRed)
            graph.Draw("AP")
            #print graph.GetN()

            graph2 = self.graphs2[i]

            graph2.Draw("AP")
            graph2.SetFillColor(0)
            graph2.GetXaxis().SetTitle("Module Number")
            graph2.GetYaxis().SetTitle("Channel Number within Module")
            graph2.GetXaxis().SetLimits(-1,65.8)
            graph2.GetYaxis().SetRangeUser(-1,48.8)
            
            graph2.SetMarkerStyle(20)
            graph2.SetMarkerSize(1.3)
            graph2.SetMarkerColor(ROOT.kBlue)
                
            if graph.GetN():
                graph.Draw("AP")
            if graph2.GetN() and not graph.GetN():
                graph2.Draw("AP")
            elif graph2.GetN():
                graph2.Draw("P")                       
                        
            leg = ROOT.TLegend(0.6190,0.91,1.0,1.0)
            leg.SetBorderSize(0)
            leg.SetFillColor(0)

            if graph.GetN():
                leg.AddEntry(graph, "low gain", "p")
            if graph2.GetN():
                leg.AddEntry(graph2, "high gain", "p")

            leg.Draw()
            
            pt = ROOT.TPaveText(0.1017812,0.9229412,0.3053435,0.9952941, "brNDC")
            pt.AddText("%s Status: No CIS" % name)
            pt.SetBorderSize(0)
            pt.SetFillColor(0)
            pt.Draw()

            self.c1.Print("%s/noCIS_%s.png" % (self.dir, name))
                    
        self.c1.Print("%s/noCIS.ps]" % (self.dir))


    def ProcessRegion(self, region):
        for line in self.fout:
            x = int(line.split(' ')[0])
            y = int(line.split(' ')[1])
            z = int(line.split(' ')[2])
            w = int(line.split(' ')[3])

            x = x - 1
            if w == 0:
                self.graphs1[x].SetPoint(self.graphs1i[x], y, z)
                self.graphs1i[x] += 1
                break
                               
            if w == 1:
                self.graphs2[x].SetPoint(self.graphs2i[x], y, z)
                self.graphs2i[x] += 1
                break

            return
