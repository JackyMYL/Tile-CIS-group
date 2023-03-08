############################################################
#
# do_cell_deviation_plot.py
#
############################################################
#
# Author: Giulia, based on work by Henric 
#
# July, 2017
#
# Goal: 
# Compute the time evolution plot of the average PMT signal drift and average gain drift
#
# Input parameters are:
#
# -> fib: the PP fiber number (from 0 to 383) you want to plot.
#         DEFAULT VAL = -1 : produces all the plots 
#
# -> limit: the maximum tolerable variation (in %). If this variation
#           is excedeed the plots will have a RED background
#
# -> doEps: provide eps plots in addition to default png graphics
#
# For more info on the LASER system : http://atlas-tile-laser.web.cern.ch
#
#############################################################


from src.GenericWorker import *
from src.oscalls import *
import src.MakeCanvas
import math
import sys 
import ROOT


class do_cell_deviation_plot(GenericWorker):
    "Compute the time evolution plot of the average PMT signal drift and average gain drift"

    c1 = None

    def __init__(self, runType='Las', fib=-1, limit=1, doEps = False):
        self.runType   = runType
        self.doEps     = doEps
        self.fib       = fib
        self.limit     = limit
        self.finalRun  = runnumber
        self.ymin      = -10.
        self.ymax      = 10.

        self.outputTag = outputTag # global variable to tag output histogram file name
        self.dir    = getPlotDirectory(subdir=self.outputTag)

        self.cell_name = ['A1', 'A2', 'A3', 'A4', 'A5', 'A6', 'A7', 'A8', 'A9', 'A10', 'BC1', 'BC2', 'BC3', 'BC4', 'BC5', 'BC6', 'BC7', 'BC8', 'B9', 'D0', 'D1', 'D2', 'D3', 'A12', 'A13', 'A14', 'A15', 'A16', 'B11', 'B12', 'B13', 'B14', 'B15', 'C10', 'D4', 'D5', 'D6', 'E1', 'E2', 'E3', 'E4']

        self.PMTool = LaserTools()
        self.time_max = 0
        self.time_min = 10000000000000000

        try:
            self.HistFile.cd()
        except:
            self.initHistFile("rootfile/Cell_evolution.root")
        self.HistFile.cd()
        ROOT.gDirectory.mkdir("Laser")
        ROOT.gDirectory.cd("Laser")

        if self.c1 == None:
            self.c1 = src.MakeCanvas.MakeCanvas()
            self.c1.SetTitle("Time evolution")

        
    def ProcessStart(self):
        global run_list
        for run in run_list.getRunsOfType('Las'):
            time = run.time_in_seconds
            if self.time_min > time:
                self.time_min = time
                            
            if self.time_max < time:
                self.time_max = time

        
    def ProcessRegion(self, region):
        return 
                    

    def ProcessStop(self):
        # Cosmetics (Part 1): the lines which shows the maximum acceptable variation
        ROOT.gROOT.SetBatch(ROOT.kFALSE)
        
        self.PrepareCanvas()
        
        for i_cell in range(41):

            max_var = 0
            name = self.cell_name[i_cell]
                
            for run in run_list.getRunsOfType('Las'):
                if 'cell_deviation' in run.data:
                    x = math.fabs(run.data['cell_deviation'][i_cell])
                   
            # Cosmetics (Part 2): the fiber graph itself
            self.hhist.GetYaxis().SetTitle("%s evolution %s" % (name,'(in %)'))
            graph_lim = 10.
            self.hhist.SetMaximum(graph_lim) 
            self.hhist.SetMinimum(-graph_lim)            

            self.tgraph_gain.Set(0)
            self.tgraph_hg.Set(0)
            for run in run_list.getRunsOfType('Las'): # fill the histogram
                #if run.data['wheelpos'] == 6:
                #    tgraph = self.tgraph_lg
                if 'cell_deviation' in run.data:
                    tgraph = self.tgraph_hg
                    i = tgraph.GetN()
                    y = run.data['cell_deviation'][i_cell]

                    if y!=0.:
                        ey = run.data['cell_deviation_err'][i_cell]
                        tgraph.SetPoint(i, run.time_in_seconds,min(max(y,.95*self.ymin),.95*self.ymax))
                        tgraph.SetPointError(i, 0., ey)

                    else:
                        ey=0.

                if 'gain_deviation' in run.data:
                    tgraph = self.tgraph_gain
                    i = tgraph.GetN()
                    y = run.data['gain_deviation'][i_cell]
                    if y!=0:
                        ey= run.data['gain_deviation_err'][i_cell]
                        tgraph.SetPoint(i, run.time_in_seconds, min(max(y,.95*self.ymin),.95*self.ymax))
                        tgraph.SetPointError(i, 0., ey)
                    else:
                        ey=0.
                            
            # Put things on disk
            self.c1.Modified()  
            if self.doEps:
                ROOT.gStyle.SetPaperSize(26,20)
                self.c1.Print("%s/%s.eps" % (self.dir,"/Evolution_%s_cell" % (name)))
                self.c1.Print("%s/%s.root" % (self.dir,"/Evolution_%s_cell" % (name)))
            else:
                self.c1.Print("%s/%s.png" % (self.dir,"/Evolution_%s_cell" % (name)))

            self.HistFile.cd()
            self.tgraph_gain.SetName('Gain_%s'%name)
            self.tgraph_gain.Write()
            self.tgraph_hg.SetName('Signal_%s'%name)
            self.tgraph_hg.Write()
            
        #   end for i_fib in range(384):
        

        self.CleanRoot()


    def PrepareCanvas(self):
        pad = self.c1.cd()

        self.c1.SetLeftMargin(0.14)
        self.c1.SetRightMargin(0.14)
        self.c1.SetFrameFillColor(0)
        self.c1.SetFillColor(0);
        self.c1.SetBorderMode(0); 
        self.c1.SetGridx(1);
        self.c1.SetGridy(1);
            
        ROOT.gStyle.SetOptStat(0)
        ROOT.gStyle.SetStatX(0.78)
        ROOT.gStyle.SetStatY(0.83)
        ROOT.gStyle.SetEndErrorSize(0.)
        ROOT.gStyle.SetTimeOffset(0)
        ROOT.gStyle.SetOptTitle(0)

        self.hhist = pad.DrawFrame(self.time_min-43200., -5.*self.limit, self.time_max+43200.,
                                   5.*self.limit, 'Signal_gain_evolution')
        self.hhist.SetFillColor(50);
        self.hhist.GetXaxis().SetTimeDisplay(1)
        self.hhist.GetYaxis().SetTitleOffset(1.)
        self.hhist.GetXaxis().SetLabelOffset(0.03)
        self.hhist.GetYaxis().SetLabelOffset(0.01)
        self.hhist.GetXaxis().SetLabelSize(0.04)
        self.hhist.GetYaxis().SetLabelSize(0.04)           
        self.hhist.GetXaxis().SetTimeFormat("#splitline{%Y}{%d/%m}")
        self.hhist.GetXaxis().SetNdivisions(-503)

        self.tgraph_hg = ROOT.TGraphErrors()
        self.tgraph_gain = ROOT.TGraphErrors()
        
        self.tgraph_gain.SetMarkerStyle(5)
        self.tgraph_gain.SetMarkerColor(6)
        self.tgraph_hg.SetMarkerStyle(5)
        self.tgraph_hg.SetMarkerColor(4)
        self.tgraph_gain.Draw("P,same")
        self.tgraph_hg.Draw("P,same")
        
        self.legend1 = ROOT.TLegend(0.65,0.75,0.75,0.9)
        self.legend1.AddEntry(self.tgraph_hg,"#bar{#delta}_{c}","p")
        
        self.legend1.AddEntry(self.tgraph_gain,"#bar{#delta}_{G}","p")
        #self.legend1.AddEntry (self.tgraph_gain, "Pisa method", "p")
        self.legend1.SetFillColor(0)
        self.legend1.Draw()        
        
        l1 = ROOT.TLatex()
        l1.SetNDC();
        l1.SetTextFont(72);
        l1.DrawLatex(0.1922,0.867,"ATLAS");
        
        l2 = ROOT.TLatex()
        l2.SetNDC();
        l2.DrawLatex(0.1922,0.811,"Internal");
        

    def CleanRoot(self):
        #         self.line_vert1.Delete()
        #         self.line_vert2.Delete()
        #         self.line_vert3.Delete()
        self.hhist.Delete()
        self.tgraph_gain.Delete()
        self.tgraph_hg.Delete()

