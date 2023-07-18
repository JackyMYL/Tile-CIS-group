############################################################
#
# do_spreadcell_plot.py
#
############################################################
#
# Author: Emmanuelle Dubreuil <Emmanuelle.Dubreuil@cern.ch>
#
# 18th March 2013
#
# Goal: Do a plot for one given cell, channel by channel
#
# Input parameters are:
#
# -> cell : the cell number (A=100, B=200, C=300, D=400)+(cell number)
#    for ex. A10 = 110, D5 = 405
#
# -> limit: the maximum tolerable variation (in %). Represented by two lines
#           
# -> doEps: provide eps plots in addition to default png graphics
#
# For more info on the LASER system : http://atlas-tile-laser.web.cern.ch
#
#############################################################

from src.GenericWorker import *
from src.oscalls import *
import src.MakeCanvas
import time

class do_spreadcell_plot(GenericWorker):
    "Compute history plot for a given cell, channel by channel"

    c1 = None

    def __init__(self, runType='Las', limit=1, cell=0, doEps = False):
        self.runType  = runType
        self.doEps    = doEps
        self.cell     = cell
        self.limit    = limit        
        self.PMTool   = LaserTools()
        self.origin   = ROOT.TDatime()

        self.LG_evts  = set()
        self.HG_evts  = set()

        self.time_max = 0
        self.time_min = 10000000000000000

        self.hhist_lg = []

        self.outputTag = outputTag # global variable to tag output histogram file name
        self.dir    = getPlotDirectory(subdir=self.outputTag)

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
        # First retrieve all the relevant partition infos

        for event in region.GetEvents():

            if 'calibration' not in event.data:
                continue
                        
#            [part_num, i, j, w] = self.PMTool.GetNumber(event.data['region'])
            [part_num, i, j, w] = event.region.GetNumber()
            part_num -= 1
            i        -= 1
            ind       = self.PMTool.get_index(part_num,i,j,w)

            pmt = self.PMTool.get_PMT_index(part_num,i,j)
            i += 1
            indcell   = self.PMTool.get_cell_index(part_num,i,pmt) #Get cell index needs a PMT number starting from 1
            


            
            if indcell == self.cell:


                if indcell == self.cell:
                    self.LG_evts.add(event)

                if indcell == self.cell:
                    self.HG_evts.add(event)
                                    


    def ProcessStop(self):

        # Then we do the graphs

        
        max_var = 0
                    
        for event in self.LG_evts:

            if 'deviation' not in event.data:
                continue

            if max_var<math.fabs(event.data['deviation']):
                max_var = math.fabs(event.data['deviation'])

        # Cosmetics (Part 2): the partition graph itself
        if math.fabs(max_var) < 100:
            graph_lim = 1.1*(math.fabs(max_var))
        else:
            graph_lim = 1.1*(math.fabs(max_var))
        
                      
        tmp = "Gain variation [%]" 
                    
        self.plot_name_lg = "cells_%d_spread_lg"%(self.cell)

        self.c1.SetFrameFillColor(0)
        self.c1.SetFillColor(0);
        self.c1.SetBorderMode(0); 
        self.c1.SetGridx(1);
        self.c1.SetGridy(1);



        # Cosmetics (Part 1): the lines which shows the maximum acceptable variation
            
        self.line_down = ROOT.TLine(0,-self.limit,self.time_max-self.time_min+1,-self.limit)
        self.line_down.SetLineColor(4)
        self.line_down.SetLineWidth(2)
        
        self.line_up = ROOT.TLine(0,self.limit,self.time_max-self.time_min+1,self.limit);
        self.line_up.SetLineColor(4)
        self.line_up.SetLineWidth(2)
        
        
        self.cadre = ROOT.TH2F('Cadre', '',\
                               1000, 0, self.time_max-self.time_min+1, 10000, -graph_lim, graph_lim)
        

        for m in range(64):
            name_h = "cell_deviation_ch %d" % (m)
            self.hhist_lg.append(ROOT.TGraph())            
            
        ROOT.gStyle.SetTimeOffset(self.origin.Convert());
        
        
        self.cadre.GetXaxis().SetTimeDisplay(1)
        self.cadre.GetYaxis().SetTitleOffset(1.1)
        self.cadre.GetXaxis().SetLabelOffset(0.001)
        self.cadre.GetYaxis().SetLabelOffset(0.01)
        self.cadre.GetXaxis().SetLabelSize(0.04)
        self.cadre.GetYaxis().SetLabelSize(0.04)           
        self.cadre.GetXaxis().SetTimeFormat("%Y/%d/%m")
        self.cadre.GetXaxis().SetNdivisions(-503)
        self.cadre.GetYaxis().SetTitle(tmp)
        self.cadre.GetXaxis().SetTitle('date')
                               
        for event in self.LG_evts : # fill the histogram
            if 'deviation' not in event.data:
                continue
#            if ((event.data['region'].find('LBA_m54')!=-1) or (event.data['region'].find('LBC_m28')!=-1) or (event.data['region'].find('EBC_m01')!=-1) or (event.data['region'].find('LBA_m13')!=-1)):
            if ((event.region.GetHash().find('LBA_m54')!=-1) or (event.region.GetHash().find('LBC_m28')!=-1) or (event.region.GetHash().find('EBC_m01')!=-1) or (event.region.GetHash().find('LBA_m13')!=-1)):
                continue
            if event.run.time_in_seconds-self.time_min==0:
                event.data['deviation'] = event.data['deviation'] + 0.000001

            [part_num, mod, ch, w] = event.region.GetNumber()

            for n in range(64):
                if n==mod:
                    npoints = self.hhist_lg[n].GetN()
                    self.hhist_lg[n].SetPoint(npoints,event.run.time_in_seconds-self.time_min,event.data['deviation'])
                    #print 'test do_spread',event.data['deviation'],event.data['region'],mod
                    print('test do_spread',event.data['deviation'],event.region.GetHash(),mod)
 
        # Then draw it...
                
        self.c1.cd()
        ROOT.gStyle.SetOptStat(0)
        ROOT.gStyle.SetStatX(0.78)
        ROOT.gStyle.SetStatY(0.83)
        self.cadre.Draw()

        for h in range(64):
            self.hhist_lg[h].SetMarkerStyle(20)
            self.hhist_lg[h].SetMarkerColor(h)
            self.hhist_lg[h].Draw("P,same")
    
        self.line_up.Draw("same")
        self.line_down.Draw("same")
        
        # hack
        self.c1.SetLeftMargin(0.14)
        self.c1.SetRightMargin(0.14)
        self.c1.Modified()
        
        l = ROOT.TLatex()
        l.SetNDC();
        l.SetTextFont(72);
        
        l2 = ROOT.TLatex()
        l2.SetNDC();

        
        self.c1.Modified()  
        
        self.c1.Print("%s/%s.png" % (self.dir,self.plot_name_lg))
        self.c1.Print("%s/%s.C" % (self.dir,self.plot_name_lg))
        if self.doEps:
            self.c1.Print("%s/%s.eps" % (self.dir,self.plot_name_lg))
