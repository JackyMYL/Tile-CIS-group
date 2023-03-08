############################################################
#
# do_global_time_plot.py
#
############################################################
#
# Author: Henric
#
# February, 2012 
#
# Goal: 
# Compute an history plot for the global time variation
#
#############################################################

from src.GenericWorker import *
import src.MakeCanvas
import src.oscalls
import os.path

from src.laser.toolbox import *
import ROOT
import os

class do_global_time_plot(GenericWorker):
    "Compute history plot"

    c1 = None

    def __init__(self, runType='Las', limit=1, part=-1, doEps = False):
        self.runType  = runType
        self.doEps    = doEps
        self.part     = part
        self.limit    = limit                
        self.events    = set()
        self.run_list  = []
        self.part_list = set()
        self.PMTool    = LaserTools()        

        self.outputTag = outputTag # global variable to tag output histogram file name
        self.dir    = getPlotDirectory(subdir=os.path.join(self.outputTag,'Time'))

        self.origin    = ROOT.TDatime()
        self.time_max  = 0
        self.time_min  = 10000000000000000

        self.max_var = 0
        self.partnms   = ['LBA','LBC','EBA','EBC']

        if self.c1==None:
            self.c1 = src.MakeCanvas.MakeCanvas()
            self.c1.SetTitle("Per partition time offsets")
    #
    # Here we collect all the relevant information
    #
    def ProcessStart(self):
        global run_list
        for run in run_list.getRunsOfType('Las'):
            if 'MeanTime' in run.data:
                
                time = run.time_in_seconds
                if self.time_min > time:
                    self.time_min = time
                    self.origin = ROOT.TDatime(run.time)
                            
                if self.time_max < time:
                    self.time_max = time

                self.run_list.append(run)

# Make sure people at least implement this
    def ProcessRegion(self, region):
        return region


#
# At the end we produce the plots
#    
    def ProcessStop(self):

        ROOT.gStyle.SetPaperSize(20,26)
        c_w = int(2600)
        c_h = int(2000)
        self.c1 = ROOT.TCanvas("c1","acanvas",c_w,c_h)
        self.c1.cd()

        self.c1.SetWindowSize(2*c_w - self.c1.GetWw(), 2*c_h - self.c1.GetWh())

        ROOT.gStyle.SetTimeOffset(self.origin.Convert())
        ROOT.gStyle.SetOptTitle(1)
        ROOT.gStyle.SetTitleX(0.1)
        ROOT.gStyle.SetTitleW(0.2)
        ROOT.gStyle.SetTitleBorderSize(0)                                          
        ROOT.gStyle.SetTitleFontSize(0.05)
        ROOT.gStyle.SetTitleOffset(0.1)
        ROOT.gStyle.SetTitleFillColor(0)
        
        tgraph = [[],[],[],[]]
        for ros in range(4):
            tgraph[ros].append(ROOT.TGraph())
            tgraph[ros].append(ROOT.TGraph())
            tgraph[ros][0].SetTitle(self.partnms[ros])
            tgraph[ros][0].SetMarkerStyle(7)
            tgraph[ros][0].SetMarkerSize(20)
            tgraph[ros][0].SetMarkerColor(4)
            tgraph[ros][1].SetTitle(self.partnms[ros])
            tgraph[ros][1].SetMarkerStyle(7)
            tgraph[ros][1].SetMarkerSize(20)
            tgraph[ros][1].SetMarkerColor(8)
            
        self.run_list = sorted(self.run_list, key=lambda run: run.runNumber)
        for run in self.run_list:
            a = run.data['MeanTime']
            if run.data['wheelpos']==6:
                gain=0
            else:
                gain=1
            for ros in range(4):
                n = tgraph[ros][gain].GetN()
                tgraph[ros][gain].SetPoint(n,run.time_in_seconds-self.time_min, a[ros])

        # Then draw it...
        # Prepare the canvas for new module
        self.c1.Clear()
        self.c1.Range(0,0,1,1)
        self.c1.SetFillColor(0)
        self.c1.SetBorderMode(0)
        self.c1.cd()
        self.c1.Divide(2,2)

        for ros in range(4):
            pad = self.c1.cd(ros+1)
            frame = pad.DrawFrame(-43200,-16.,self.time_max-self.time_min+43200,31.)
            frame.GetXaxis().SetTimeDisplay(1)
            frame.GetXaxis().SetTimeFormat("#splitline{%Y}{%d/%m}")
            frame.GetXaxis().SetNdivisions(-503)
            frame.GetYaxis().SetTitle("Partition time [ns]")    
            frame.GetXaxis().SetLabelSize(0.03)
            frame.GetXaxis().SetLabelOffset(0.03)
            frame.SetTitle(self.partnms[ros])
            for gain in range(2):
                tgraph[ros][gain].Draw('P,same')

            self.c1.cd(ros+1).Modified()

        self.c1.Update()
        plot_name = "global_time"
        self.c1.Print("%s/%s.ps" % (self.dir,plot_name))

        for ros in range(4):
            for graph in tgraph[ros]:
                graph.Delete()
                
        self.c1.Close()
