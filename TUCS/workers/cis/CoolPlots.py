#################################################################################
#!/usr/bin/env python    
# Author : Grey Wilburn <grey.williams.wilburn@cern.ch>
# Date   : An unseasonably warm late winter afternoon in 2015
#
#Based on database_flag_hist.py by Vikram Upadhyay
#################################################################################
#"This script takes an input of a date range from the user, and plots 
#the number of BADCIS channels, NOCIS channels, and masked channeks
#for each run in that period.
#Something nice to put on Tile-in-ONE...
#################################################################################

from src.GenericWorker import *
from src.oscalls import *
import ROOT
from subprocess import call

class CoolPlots(GenericWorker):
    
    def __init__(self, calflags='All', savePlot=False):
        print("Init: database_flag_hist() worker has been constructed and is waiting to go!")
        self.calflags = 'CIS'
        self.savePlot = savePlot

        self.dir = getPlotDirectory()
        self.dir = '%s/cis/Public_Plots/CoolPlots' % self.dir
        createDir(self.dir)
        self.result = getResultDirectory()
        
    def ProcessStart(self):
        print("Start: database_flag_hist() worker is about to be sent data")
        print(Use_run_list)
        print("self.dir=%s"%self.dir)
        self.time_dict = {}
        self.ymax = 0
    
    def ProcessRegion(self, region):
        for event in region.GetEvents():
           runnum = event.run.runNumber
           if not runnum in self.time_dict:
              self.time_dict[runnum] = event.run.time_in_seconds
    
    def ProcessStop(self):
        print("Stop: database_flag_hist() worker has finished being sent data, and is going to do it's analysis")
        self.cool_dict = {}

        for i in self.time_dict:
           self.cool_dict[i] = {}
           self.cool_dict[i]['Masked'] = 0
           self.cool_dict[i]['NoCIS'] = 0
           self.cool_dict[i]['BadCIS'] = 0
           self.cool_dict[i]['MaskedCIS'] = 0
           
           call(['ReadBchFromCool.py --tag=UPD4 --run=%d'%i], stdout = open( '%s/Conditions_Database.txt'%self.result, 'w'), shell=True)
           file = open('%s/Conditions_Database.txt'%self.result, 'r')
           for line in file:
                if 'BAD' in line:
                    self.cool_dict[i]['Masked'] += 1
                    if '1103' in line or '1104' in line:
                       self.cool_dict[i]['MaskedCIS'] += 1
                if '1103' in line:
                    self.cool_dict[i]['NoCIS'] += 1
                if '1104' in line:
                    self.cool_dict[i]['BadCIS'] += 1
        print(self.cool_dict)
        
        c1 = src.MakeCanvas.MakeCanvas()
       
        BC_graph = self.Fill_Graph('BadCIS', ROOT.kBlue, 23)
        NC_graph = self.Fill_Graph('NoCIS', ROOT.kBlack, 22)
        MC_graph = self.Fill_Graph('MaskedCIS', ROOT.kOrange, 20)
        MK_graph = self.Fill_Graph('Masked', ROOT.kRed, 21) 
       
        #Set up legend
        leg = ROOT.TLegend(0.55, 0.66, 0.83, 0.9, "", "brNDC")
        leg.SetBorderSize(0)
        leg.SetTextFont(1)
        leg.SetFillColor(0)
        leg.SetTextSize(0.03)
        
        leg.AddEntry(BC_graph, 'ADC\'s w/ BadCIS flag', "P")
        leg.AddEntry(NC_graph, 'ADC\'s w/ NoCIS flag', "P")
        leg.AddEntry(MC_graph, 'ADC\'s Masked due to CIS', "P")
        leg.AddEntry(MK_graph, 'ADC\'s Masked for any reason', "P")

        BC_graph.Draw('AP')
        x_axis = BC_graph.GetXaxis()
        y_axis = BC_graph.GetYaxis()
        
        NC_graph.Draw('psame')
        MC_graph.Draw('psame')
        MK_graph.Draw('psame')
        leg.Draw()

        tl = ROOT.TLatex()
        tl.SetNDC()
        tl.SetTextSize(0.04)
        tl.DrawLatex(0.26,0.95,"#bf{CIS COOL Database Statuses by Run}")

        self.Format_Plot(x_axis, y_axis, c1)
        
        y_axis.SetRangeUser(0,int(self.ymax * 1.75))
       
        filename = "%s/COOL_Flag_History.png" % self.dir
        c1.Print(filename)

    def Fill_Graph(self, flagname, color, marker):        
        tg = ROOT.TGraph()
        i = 0 #Start counting at 1 => bad stuff happens...
        
        for run in self.cool_dict:
            prob_num = self.cool_dict[run][flagname]
            run_time = self.time_dict[run]
            tg.SetPoint(i, run_time, prob_num)
            i += 1

            #Is this point greater than the max
            if prob_num > self.ymax:
                self.ymax = prob_num # if yes, it's the new max
        
        tg.SetMarkerStyle(marker)
        tg.SetMarkerSize(1)
        tg.SetMarkerColor(color)
        return tg

    def Format_Plot(self, x_axis, y_axis, c):
        #I stole much of this formatting from PerformancePlots.py
        timerange = x_axis.GetXmax() - x_axis.GetXmin()
        if timerange <= (10512000/2): # two months
            nweeks = int(timerange/657000)
            x_axis.SetNdivisions(nweeks, 5, 10, ROOT.kTRUE)
            x_axis.SetTimeDisplay(1)
            x_axis.SetTimeFormat('#splitline{%b %d}{%Y} %F1970-01-01 00:00:00')
            x_axis.SetLabelOffset(0.025)
        elif timerange <= (13140000): # five months
            nbiweeks = int(timerange/(1314000))
            x_axis.SetNdivisions(nbiweeks, 5, 10, ROOT.kTRUE)
            x_axis.SetTimeDisplay(1)
            x_axis.SetTimeFormat('#splitline{%b %d}{%Y} %F1970-01-01 00:00:00')
            x_axis.SetLabelOffset(0.025)
        elif timerange <= (21024000): # 8 months
            nmonths = int(timerange/(2628000))
            x_axis.SetNdivisions(nmonths, 5, 10, ROOT.kTRUE)
            x_axis.SetTimeFormat('#splitline{%b}{%Y} %F1970-01-01 00:00:00')
            x_axis.SetLabelOffset(0.025)
            x_axis.SetTimeDisplay(1)
        else:
            ntwomonths = int((timerange/5256000))
            x_axis.SetNdivisions(ntwomonths, 5, 10, ROOT.kTRUE)
            x_axis.SetTimeDisplay(1)
            x_axis.SetTimeFormat('#splitline{%b}{%Y} %F1970-01-01 00:00:00')
            x_axis.SetLabelOffset(0.025)
        x_axis.SetLabelSize(0.025)
        x_axis.SetTickLength(0.04)
       
        y_axis.SetTitle('Number of TileCal ADC\'s')   
        y_axis.CenterTitle(True)
        y_axis.SetTitleOffset(1.2)
        y_axis.SetTitleSize()
        y_axis.SetLabelSize(0.03)
        y_axis.SetLabelOffset(0.005)
        y_axis.SetNdivisions(10, 5, 0, ROOT.kTRUE)
 
        c.SetLeftMargin(0.10)
        c.SetTopMargin(0.07)
        c.SetBottomMargin(0.09)
        c.SetRightMargin(0.09)
