############################################################
#
# syst_errors_evolution.py
#
############################################################
#
# Author: Seb Viret <viret@in2p3.fr>
#
# March 10, 2010
#
# Goal: 
# Evolution of the systematic error due to light distribution instability
#
# Input parameters are:
#
# -> gain: the gain you want to test 
#         
# -> limit: the maximum tolerable error (in %). 
#          
#
# For more info on the LASER system : http://atlas-tile-laser.web.cern.ch
#
#############################################################

from src.GenericWorker import *
from src.laser.toolbox import *
from src.region import *
from src.oscalls import *

import src.MakeCanvas
import time
import math

class syst_errors_evolution(GenericWorker):
    "Compute systematic error evolution along time"

    c1 = None
   
    def __init__(self, limit=0.3, gain=0):

        self.limit = limit
        graph_lim  = 3*self.limit
        self.gain  = gain
     
        self.outputTag = outputTag # global variable to tag output histogram file name
        self.dir    = getPlotDirectory(subdir=self.outputTag)


        # Create the different canvas
        self.channel = src.MakeCanvas.MakeCanvas()
                    
        # Then create the different histograms
        self.ch  = ROOT.TH1F('channel variation', '', 100, -graph_lim, graph_lim)

        self.events   = set()
        self.run_list = []
        self.PMTool   = LaserTools()
        self.origin    = ROOT.TDatime()
        self.time_max  = 0
        self.time_min  = 10000000000000000

        if self.c1==None:
            self.c1 = src.MakeCanvas.MakeCanvas()
            #self.c1.SetTitle("Put here a nice title")


    def ProcessStart(self):
        
        global run_list
        for run in run_list.getRunsOfType('Las'):
            time = run.time_in_seconds
            if self.time_min > time:
                self.time_min = time
                self.origin = ROOT.TDatime(run.time)
                
            if self.time_max < time:
                self.time_max = time


        



    def ProcessRegion(self, region):
                          
        for event in region.GetEvents():
            if 'deviation' in event.data and not event.data['status']:
                self.events.add(event)
                                         
                if event.run.runNumber not in self.run_list:
                    self.run_list.append(event.run.runNumber)

        return
 


    def ProcessStop(self):

        self.run_list.sort()

        self.first    = True 
        self.sig_ch_0 = 0.

        
        self.hhist = ROOT.TH2F('Fiber_systematics', '',\
                               100, 0, self.time_max-self.time_min+1, 100, 0, 3*self.limit)

        self.c1.SetFrameFillColor(0)
        self.c1.SetFillColor(0);
        self.c1.SetBorderMode(0); 
        self.c1.SetGridx(1);
        self.c1.SetGridy(1);
        
        ROOT.gStyle.SetTimeOffset(self.origin.Convert());
        
        self.hhist.GetXaxis().SetTimeDisplay(1)
        self.hhist.GetYaxis().SetTitleOffset(1.)
        self.hhist.GetXaxis().SetLabelOffset(0.03)
        self.hhist.GetYaxis().SetLabelOffset(0.01)
        self.hhist.GetXaxis().SetLabelSize(0.04)
        self.hhist.GetYaxis().SetLabelSize(0.04)           
        self.hhist.GetXaxis().SetTimeFormat("#splitline{%Y}{%d/%m}")
        self.hhist.GetXaxis().SetNdivisions(-503)
        self.hhist.GetYaxis().SetTitle('Systematic error due to fiber effect (in %)')
        self.hhist.SetMarkerStyle(20)

        for run in self.run_list:

            self.ch.Reset() 
            self.time = 0.
            
            for event in self.events:                 
                
                if run != event.run.runNumber:
                    continue

                #[p, i, j, w] = self.PMTool.GetNumber(event.data['region'])
                [p, i, j, w] = event.region.GetNumber()

                if w!=self.gain:
                    continue

                if not event.data['status']:   # Don't put event on summary plot if already on BC list
                    if (event.data['calibration']>0.0025 and event.run.data['wheelpos']==8) or\
                           (event.data['calibration']>0.1 and event.run.data['wheelpos']==6):

                        self.ch.Fill(event.data['deviation'])
                        self.time = event.run.time_in_seconds

            # Here we deal with all the necessary cosmetics
            
            self.ch.Fit("gaus","Q0")
            self.ch_fit = ROOT.TVirtualFitter.Fitter(self.ch)
            self.sig_ch = self.ch_fit.GetParameter(2)
        

            if self.first:               
                self.sig_ch_0  = self.sig_ch
                self.first=False
            else:
                self.syst_fib = math.sqrt(math.fabs(self.sig_ch*self.sig_ch-self.sig_ch_0*self.sig_ch_0))
                self.hhist.Fill(self.time-self.time_min,self.syst_fib)
            

        # Then draw it...
                
        self.c1.cd()
        ROOT.gStyle.SetOptStat(0)
        ROOT.gStyle.SetStatX(0.78)
        ROOT.gStyle.SetStatY(0.83)
        self.hhist.Draw()
        
        # hack
        self.c1.SetLeftMargin(0.14)
        self.c1.SetRightMargin(0.14)
        self.c1.Modified()
            
        l = ROOT.TLatex()
        l.SetNDC();
        l.SetTextFont(72);
        l.DrawLatex(0.1922,0.867,"ATLAS");
        
        l2 = ROOT.TLatex()
        l2.SetNDC();
        l2.DrawLatex(0.1922,0.811,"Preliminary");
        
        self.c1.Modified()  
        
        self.c1.Print("%s/%s_%d.png" % (self.dir,'systematics',self.gain))
        self.c1.Print("%s/%s_%d.eps" % (self.dir,'systematics',self.gain))
        self.c1.Print("%s/%s_%d.C" % (self.dir,'systematics',self.gain))
