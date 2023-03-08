############################################################
#
# do_diode_plot.py
#
############################################################
#
# Author: Henric
#
# A very hot Friday in Aug 2015
#
# Goal:
# Compute an history plot for the diode variation
#
#
#############################################################

from src.GenericWorker import *
from src.oscalls import *
import src.MakeCanvas
import time

class do_diode_plot(GenericWorker):
    "Compute history plot for Laser2 monitoring diodes"

    c1 = None

    def __init__(self, runType='Las', limit=1, part=-1, doEps = False, nDays = -1):
        self.runType  = runType
        self.doEps    = doEps
        self.part     = part
        self.limit    = limit
        self.events    = set()
        self.run_list  = []
        self.part_list = set()
        self.PMTool    = LaserTools()
        self.nDaysBef  = nDays

        self.time_max  = 0
        self.time_min  = 10000000000000000

        self.max_var = 0

        self.outputTag = outputTag # global variable to tag output histogram file name
        self.dir    = getPlotDirectory(subdir=self.outputTag)

        if self.c1==None:
            self.c1 = src.MakeCanvas.MakeCanvas()
            self.c1.SetTitle("Diode plots")

    #
    # Here we collect all the relevant information
    #
    def ProcessStart(self):
        global run_list
        for run in run_list.getRunsOfType('Las'):
            if 'diodes' in run.data:

                time = run.time_in_seconds
                if self.time_min > time:
                    self.time_min = time

                if self.time_max < time:
                    self.time_max = time

                self.run_list.append(run)
    #
    # Make sure people at least implement this
    #
    def ProcessRegion(self, region):
        return region

    #
    # At the end we produce the plots
    #
    def ProcessStop(self):
        self.run_list = sorted(self.run_list, key=lambda run: run.runNumber)

        # # Cosmetics (Part 1): the lines which shows the maximum acceptable variation

        # self.line_down = ROOT.TLine(0,-self.limit,self.time_max-self.time_min+1,-self.limit)
        # self.line_down.SetLineColor(4)
        # self.line_down.SetLineWidth(2)

        # self.line_up = ROOT.TLine(0,self.limit,self.time_max-self.time_min+1,self.limit)
        # self.line_up.SetLineColor(4)
        # self.line_up.SetLineWidth(2)
        # firstbeam2012 = '2012-04-05 0:37:00'
        # c = time.strptime(firstbeam2012, '%Y-%m-%d %H:%M:%S')
        # t0 = time.mktime(c)
        # self.line_vert = ROOT.TLine(t0-self.time_min,-20.,
        #                             t0-self.time_min, 20. )
        # self.line_vert.SetLineColor(7)
        # self.line_vert.SetLineWidth(1)


        self.nDaysBef = self.time_max - self.nDaysBef*86400

        # Then we do the graphs for all the partitions
        graph_lim = max(1.1*self.max_var,10.)

        title = "diode evolution [%]"
        self.plot_name = "diode_history"

        title_ratiod2 = "ratio (D2) diode evolution [%]"
        self.plot_name_ratiod2 = "ratio_diode_history_d2"

        title_ratiod4 = "ratio (D4) diode evolution [%]"
        self.plot_name_ratiod4 = "ratio_diode_history_d4"

        title_ratiod6 = "ratio (D6) diode evolution [%]"
        self.plot_name_ratiod6 = "ratio_diode_history_d6"


        self.tgraph_hg = []
        self.tgraph_lg = []
        self.tgraph_hg_ratiod2 = []
        self.tgraph_lg_ratiod2 = []
        self.tgraph_hg_ratiod4 = []
        self.tgraph_lg_ratiod4 = []
        self.tgraph_hg_ratiod6 = []
        self.tgraph_lg_ratiod6 = []


        for diode in range(10):
            self.tgraph_hg.append(ROOT.TGraphErrors())
            self.tgraph_lg.append(ROOT.TGraphErrors())

        for diode2 in range(10):
            if (diode2==2):
                continue
            self.tgraph_hg_ratiod2.append(ROOT.TGraphErrors())
            self.tgraph_lg_ratiod2.append(ROOT.TGraphErrors())

        for diode4 in range(3,10):
            if (diode4==4):
                continue
            self.tgraph_hg_ratiod4.append(ROOT.TGraphErrors())
            self.tgraph_lg_ratiod4.append(ROOT.TGraphErrors())

        for diode6 in range(7, 10):
            self.tgraph_hg_ratiod6.append(ROOT.TGraphErrors())
            self.tgraph_lg_ratiod6.append(ROOT.TGraphErrors())


        self.c1.cd()
        self.c1.SetFrameFillColor(0)

        self.c1.SetFillColor(0)
        self.c1.SetBorderMode(0)
        self.c1.SetGridx(1)
        self.c1.SetGridy(1)

        ROOT.gStyle.SetOptTitle(1)
        ROOT.gStyle.SetTimeOffset(0)


#        self.hhist
#        self.hhist
#        self.hhist
#        self.hhist
#        self.hhist
#        self.hhist
#        self.hhist
#        self.hhist
#        self.hhist
#        self.hhist

        Diode_Ref = [0.,0.,0.,0.,0.,0.,0.,0.,0.,0.,0.,0.,0.,0.,0.,0.,0.,0.,0.,0.,0.]
        delta_Diode_Ref =  [0.,0.,0.,0.,0.,0.,0.,0.,0.,0.,0.,0.,0.,0.,0.,0.,0.,0.,0.,0.,0.]
        FirstRun=0

        for run in self.run_list:
            for diode in range(10):
                if (run.data['wheelpos']==8):
                    tgraph = self.tgraph_hg[diode]
                    gain=1
                else:
                    tgraph = self.tgraph_lg[diode]
                    gain=0
                n = tgraph.GetN()
                tgraph.SetPoint(n, run.time_in_seconds, run.data['diodes'][2*diode+gain])
                tgraph.SetPointError(n, 0., run.data['diodes_s'][2*diode+gain] )

            for diode2 in range(9):
                if (run.data['wheelpos']==8):
                    tgraph_ratiod2 = self.tgraph_hg_ratiod2[diode2]
                    offset=1
                else:
                    tgraph_ratiod2 = self.tgraph_lg_ratiod2[diode2]
                    offset=0
                n = tgraph_ratiod2.GetN()
                if (diode2<2):
                    d = diode2
                else:
                    d = diode2 + 1
                if (run.data['diodes'][2*d+offset]!=0):
                    if (run.data['diodes'][4+offset]!=0):
                        b = run.data['diodes'][2*d+offset]/run.data['diodes'][4+offset]
                        delta_b = b*math.sqrt((run.data['diodes_s'][2*d+offset]/run.data['diodes'][2*d+offset])**2 +
                                              (run.data['diodes_s'][4+offset]/run.data['diodes'][4+offset])**2)
                        tgraph_ratiod2.SetPoint(n, run.time_in_seconds, b)
                        tgraph_ratiod2.SetPointError(n, 0., delta_b)
                    else:
                        a = 4+offset
                        print("RATIO D2 run.data['diodes'][",a,"]=", run.data['diodes'][a])
                else:
                    c = 2*d+offset
                    print("RATIO D2 run.data['diodes'][",c,"]=", run.data['diodes'][c])


            for diode4 in range(6):
                if (run.data['wheelpos']==8):
                    tgraph_ratiod4 = self.tgraph_hg_ratiod4[diode4]
                    offset=1
                else:
                    tgraph_ratiod4 = self.tgraph_lg_ratiod4[diode4]
                    offset=0
                n = tgraph_ratiod4.GetN()
                if (diode4<1):
                    d = diode4 + 3
                else:
                    d = diode4 + 4
                if (run.data['diodes'][2*d+offset]!=0):
                    if (run.data['diodes'][8+offset]!=0):
                        b = run.data['diodes'][2*d+offset]/run.data['diodes'][8+offset]
                        delta_b = b*math.sqrt((run.data['diodes_s'][2*d+offset]/run.data['diodes'][2*d+offset])**2 +
                                              (run.data['diodes_s'][8+offset]/run.data['diodes'][8+offset])**2)
                        tgraph_ratiod4.SetPoint(n, run.time_in_seconds, b)
                        tgraph_ratiod4.SetPointError(n, 0., delta_b )
                    else:
                        a = 8+offset
                        print("RATIO D4 run.data['diodes'][",a,"]=", run.data['diodes'][a])
                else:
                     c = 2*d+offset
                     print("RATIO D4 run.data['diodes'][",c,"]=", run.data['diodes'][c])
            for diode6 in range(3):
                if (run.data['wheelpos']==8):
                    tgraph_ratiod6 = self.tgraph_hg_ratiod6[diode6]
                    offset=1
                else:
                    tgraph_ratiod6 = self.tgraph_lg_ratiod6[diode6]
                    offset=0
                n = tgraph_ratiod6.GetN()
                d = diode6 + 7
                if (run.data['diodes'][2*d+offset]!=0):
                    if (run.data['diodes'][12+offset]!=0):
                        b = run.data['diodes'][2*d+offset]/run.data['diodes'][12+offset]
                        delta_b = b*math.sqrt((run.data['diodes_s'][2*d+offset]/run.data['diodes'][2*d+offset])**2+(run.data['diodes_s'][12+offset]/run.data['diodes'][12+offset])**2)
                        tgraph_ratiod6.SetPoint(n, run.time_in_seconds, b)
                        tgraph_ratiod6.SetPointError(n, 0., delta_b )
                    else:
                        a = 12+offset
                        print("RATIO D6 run.data['diodes'][",a,"]=", run.data['diodes'][a])
                else:
                    c = 2*d+offset
                    print("RATIO D6 run.data['diodes'][",c,"]=", run.data['diodes'][c])


        for diode in range(9):
            self.Normalized(self.tgraph_lg_ratiod2[diode])
            self.Normalized(self.tgraph_hg_ratiod2[diode])

        for diode in range(6):
            self.Normalized(self.tgraph_lg_ratiod4[diode])
            self.Normalized(self.tgraph_hg_ratiod4[diode])

        for diode in range(3):
            self.Normalized(self.tgraph_lg_ratiod6[diode])
            self.Normalized(self.tgraph_hg_ratiod6[diode])


        self.c1.cd()
        ROOT.gStyle.SetOptStat(0)
        ROOT.gStyle.SetStatX(0.78)
        ROOT.gStyle.SetStatY(0.83)
        ROOT.gStyle.SetEndErrorSize(0.)

        for diode in range(10):
            self.tgraph_lg[diode].SetMarkerStyle(29)
            self.tgraph_lg[diode].SetMarkerColor(8)
            self.tgraph_hg[diode].SetMarkerStyle(30)
            self.tgraph_hg[diode].SetMarkerColor(4)

            format = "Diode %d Low gain"
            for tgraph in [self.tgraph_lg[diode], self.tgraph_hg[diode]]:
                title = format % diode
                tgraph.GetXaxis().SetTimeDisplay(1)
                tgraph.GetYaxis().SetRangeUser(0.,8192.)
                tgraph.GetYaxis().SetTitleOffset(1.5)
                tgraph.GetXaxis().SetLabelOffset(0.03)
                tgraph.GetYaxis().SetLabelOffset(0.01)
                tgraph.GetXaxis().SetLabelSize(0.04)
                tgraph.GetYaxis().SetLabelSize(0.04)
                tgraph.GetXaxis().SetTimeFormat("#splitline{%Y}{%d/%m}")
                tgraph.GetXaxis().SetNdivisions(-503)
                tgraph.GetYaxis().SetTitle(title)
                format = "Diode %d high gain"


        legend1 = ROOT.TLegend(0.6,0.75,0.8,0.90)
        legend1.AddEntry(self.tgraph_lg[0],"Low gain (filter 6)","p")
        legend1.AddEntry(self.tgraph_hg[0],"high gain (filter 8)","p")

        legend1.Draw()

        self.c1.Divide(5,4)

        option = "AP"
#        OD = [2., 1., 1., .4, .5, .5, 2., 2., 2.5, 2.]
        OD = [2., 1., 1., .4, .5, .5, 1.5, 1.1, 1.3, 1.2]
        for diode in range(10):
            pad = self.c1.cd(int(diode%5+10*(diode//5)+1))
            self.tgraph_hg[diode].Draw(option)
            mean = self.tgraph_hg[diode].GetMean(2)
            print(mean)
            if diode<3:
                l = ROOT.TLatex()
                l.SetNDC()
                l.DrawLatex(0.4,0.867,"Laser diode OD=%4.1f (T=%5.2f%%)"%(OD[diode],10**(2-OD[diode])))
#                self.tgraph_hg[diode].SetTitle("Laser diode")
            elif diode<6:
                l = ROOT.TLatex()
                l.SetNDC()
                l.DrawLatex(0.4,0.867,"Filter diode OD=%4.1f (T=%5.2f%%)"%(OD[diode],10**(2-OD[diode])))
#                self.tgraph_hg[diode].SetTitle("Filter diode")
            else:
                l = ROOT.TLatex()
                l.SetNDC()
                l.DrawLatex(0.4,0.867,"Mixer diode OD=%4.1f (T=%5.2f%%)"%(OD[diode],10**(2-OD[diode])))
#                self.tgraph_hg[diode].SetTitle("Mixer diode")

            
            self.c1.cd(int(diode%5+10*(diode//5)+6))
            self.tgraph_lg[diode].Draw(option)
            if diode<8:
                mean = self.tgraph_lg[diode].GetMean(2)
            else:
                mean = self.tgraph_hg[diode].GetMean(2)
            goal = 6000.
            print(mean)
            l = ROOT.TLatex()
            l.SetNDC()
            if (mean/goal>0.):
                l.DrawLatex(0.2,0.867,"OD to get %4.0f: %4.1f"%(goal,OD[diode]+math.log10(mean/goal)))

            

        self.c1.SetLeftMargin(0.14)
        self.c1.SetRightMargin(0.14)
        self.c1.Modified()

        # l = ROOT.TLatex()
        # l.SetNDC()
        # l.SetTextFont(72)
        # l.DrawLatex(0.1922,0.867,"ATLAS")

        # l2 = ROOT.TLatex()
        # l2.SetNDC()
        # l2.DrawLatex(0.1922,0.811,"Internal")

        self.c1.Modified()
        self.c1.Update()


        ROOT.gStyle.SetPaperSize(26,20)
        if self.doEps:
            self.c1.Print("%s/%s.pdf" % (self.dir,self.plot_name))
        else:
            self.c1.Print("%s/%s.png" % (self.dir,self.plot_name))
        self.c1.Print("%s/%s.root" % (self.dir,self.plot_name))

        self.c1.Clear()

        c1= None

        if self.c1==None:
            self.c1 = src.MakeCanvas.MakeCanvas()
            self.c1.SetTitle("Ratio diode plots")

        graph_lim = max(1.1*self.max_var,10.)

        self.c1.cd()
        self.c1.SetFrameFillColor(0)

        self.c1.SetFillColor(0)
        self.c1.SetBorderMode(0)
        self.c1.SetGridx(1)
        self.c1.SetGridy(1)

        ROOT.gStyle.SetOptTitle(0)
        ROOT.gStyle.SetTimeOffset(0)

        self.c1.cd()
        ROOT.gStyle.SetOptStat(0)
        ROOT.gStyle.SetStatX(0.78)
        ROOT.gStyle.SetStatY(0.83)
        ROOT.gStyle.SetEndErrorSize(0.)


        for diode2 in range(9):
            self.tgraph_lg_ratiod2[diode2].SetMarkerStyle(29)
            self.tgraph_lg_ratiod2[diode2].SetMarkerColor(8)
            self.tgraph_hg_ratiod2[diode2].SetMarkerStyle(30)
            self.tgraph_hg_ratiod2[diode2].SetMarkerColor(4)

            format = "Ratio diode D%d/D2 Low gain"
            for tgraph_ratiod2 in [self.tgraph_lg_ratiod2[diode2], self.tgraph_hg_ratiod2[diode2]]:
                if (diode2<2):
                    d = diode2
                else:
                    d = diode2 +1
                title = format % d
                tgraph_ratiod2.GetXaxis().SetTimeDisplay(1)
                tgraph_ratiod2.GetYaxis().SetRangeUser(-20.,20.)
                tgraph_ratiod2.GetYaxis().SetTitleOffset(1.)
                tgraph_ratiod2.GetXaxis().SetLabelOffset(0.03)
                tgraph_ratiod2.GetYaxis().SetLabelOffset(0.01)
                tgraph_ratiod2.GetXaxis().SetLabelSize(0.04)
                tgraph_ratiod2.GetYaxis().SetLabelSize(0.04)
                tgraph_ratiod2.GetXaxis().SetTimeFormat("#splitline{%Y}{%d/%m}")
                tgraph_ratiod2.GetXaxis().SetNdivisions(-503)
                tgraph_ratiod2.GetYaxis().SetTitle(title)
                format = "Ratio diode D%d/D2 high gain"



        legend_ratiod2 = ROOT.TLegend(0.6,0.75,0.8,0.90)
        legend_ratiod2.AddEntry(self.tgraph_lg_ratiod2[0],"Low gain (filter 6)","p")
        legend_ratiod2.AddEntry(self.tgraph_hg_ratiod2[0],"high gain (filter 8)","p")

        legend_ratiod2.Draw()

        self.c1.Divide(5,4)

        option = "AP"
        for diode2 in range(9):
            self.c1.cd(diode2%5+10*(diode2//5)+1)
            self.tgraph_hg_ratiod2[diode2].Draw(option)
            self.c1.cd(diode2%5+10*(diode2//5)+6)
            self.tgraph_lg_ratiod2[diode2].Draw(option)

        self.c1.SetLeftMargin(0.14)
        self.c1.SetRightMargin(0.14)
        self.c1.Modified()

        l = ROOT.TLatex()
        l.SetNDC()
        l.SetTextFont(72)
        l.DrawLatex(0.1922,0.867,"ATLAS")

        l2 = ROOT.TLatex()
        l2.SetNDC()
        l2.DrawLatex(0.1922,0.811,"Internal")

        self.c1.Modified()
        self.c1.Update()


        ROOT.gStyle.SetPaperSize(26,20)
        print(self.dir, self.plot_name_ratiod2)
        if self.doEps:
            self.c1.Print("%s/%s.eps" % (self.dir,self.plot_name_ratiod2))
        else:
            self.c1.Print("%s/%s.png" % (self.dir,self.plot_name_ratiod2))
        self.c1.Print("%s/%s.root" % (self.dir,self.plot_name_ratiod2))

        self.c1.Clear()

        c1= None

        if self.c1==None:
            self.c1 = src.MakeCanvas.MakeCanvas()
            self.c1.SetTitle("Ratio diode plots")

        graph_lim = max(1.1*self.max_var,10.)

        self.c1.cd()
        self.c1.SetFrameFillColor(0)

        self.c1.SetFillColor(0)
        self.c1.SetBorderMode(0)
        self.c1.SetGridx(1)
        self.c1.SetGridy(1)

        ROOT.gStyle.SetOptTitle(0)
        ROOT.gStyle.SetTimeOffset(0)

        self.c1.cd()
        ROOT.gStyle.SetOptStat(0)
        ROOT.gStyle.SetStatX(0.78)
        ROOT.gStyle.SetStatY(0.83)
        ROOT.gStyle.SetEndErrorSize(0.)


        for diode4 in range(6):
            self.tgraph_lg_ratiod4[diode4].SetMarkerStyle(29)
            self.tgraph_lg_ratiod4[diode4].SetMarkerColor(8)
            self.tgraph_hg_ratiod4[diode4].SetMarkerStyle(30)
            self.tgraph_hg_ratiod4[diode4].SetMarkerColor(4)

            format = "Ratio diode D%d/D4 Low gain"
            for tgraph_ratiod4 in [self.tgraph_lg_ratiod4[diode4], self.tgraph_hg_ratiod4[diode4]]:
                if (diode4<1):
                    d = diode4 + 3
                else:
                    d = diode4 + 4
                title = format % d
                tgraph_ratiod4.GetXaxis().SetTimeDisplay(1)
                tgraph_ratiod4.GetYaxis().SetRangeUser(-10.,10.)
                tgraph_ratiod4.GetYaxis().SetTitleOffset(1.)
                tgraph_ratiod4.GetXaxis().SetLabelOffset(0.03)
                tgraph_ratiod4.GetYaxis().SetLabelOffset(0.01)
                tgraph_ratiod4.GetXaxis().SetLabelSize(0.04)
                tgraph_ratiod4.GetYaxis().SetLabelSize(0.04)
                tgraph_ratiod4.GetXaxis().SetTimeFormat("#splitline{%Y}{%d/%m}")
                tgraph_ratiod4.GetXaxis().SetNdivisions(-503)
                tgraph_ratiod4.GetYaxis().SetTitle(title)
                format = "Ratio diode D%d/D4 high gain"

        legend_ratiod4 = ROOT.TLegend(0.6,0.75,0.8,0.90)
        legend_ratiod4.AddEntry(self.tgraph_lg_ratiod4[0],"Low gain (filter 6)","p")
        legend_ratiod4.AddEntry(self.tgraph_hg_ratiod4[0],"high gain (filter 8)","p")

        legend_ratiod4.Draw()

        self.c1.Divide(3,4)

        option = "AP"
        for diode4 in range(6):
            self.c1.cd(diode4%3+6*(diode4//3)+1)
            self.tgraph_hg_ratiod4[diode4].Draw(option)
            self.c1.cd(diode4%3+6*(diode4//3)+4)
            self.tgraph_lg_ratiod4[diode4].Draw(option)

        self.c1.SetLeftMargin(0.14)
        self.c1.SetRightMargin(0.14)
        self.c1.Modified()

        l = ROOT.TLatex()
        l.SetNDC()
        l.SetTextFont(72)
        l.DrawLatex(0.1922,0.867,"ATLAS")

        l2 = ROOT.TLatex()
        l2.SetNDC()
        l2.DrawLatex(0.1922,0.811,"Internal")

        self.c1.Modified()
        self.c1.Update()


        ROOT.gStyle.SetPaperSize(26,20)
        print(self.dir, self.plot_name_ratiod4)
        if self.doEps:
            self.c1.Print("%s/%s.eps" % (self.dir,self.plot_name_ratiod4))
        else:
            self.c1.Print("%s/%s.png" % (self.dir,self.plot_name_ratiod4))
        self.c1.Print("%s/%s.root" % (self.dir,self.plot_name_ratiod4))

        self.c1.Clear()

        c1= None

        if self.c1==None:
            self.c1 = src.MakeCanvas.MakeCanvas()
            self.c1.SetTitle("Ratio diode plots")

        graph_lim = max(1.1*self.max_var,10.)

        self.c1.cd()
        self.c1.SetFrameFillColor(0)

        self.c1.SetFillColor(0)
        self.c1.SetBorderMode(0)
        self.c1.SetGridx(1)
        self.c1.SetGridy(1)

        ROOT.gStyle.SetOptTitle(0)
        ROOT.gStyle.SetTimeOffset(0)

        self.c1.cd()
        ROOT.gStyle.SetOptStat(0)
        ROOT.gStyle.SetStatX(0.78)
        ROOT.gStyle.SetStatY(0.83)
        ROOT.gStyle.SetEndErrorSize(0.)


        for diode6 in range(3):
            self.tgraph_lg_ratiod6[diode6].SetMarkerStyle(29)
            self.tgraph_lg_ratiod6[diode6].SetMarkerColor(8)
            self.tgraph_hg_ratiod6[diode6].SetMarkerStyle(30)
            self.tgraph_hg_ratiod6[diode6].SetMarkerColor(4)

            format = "Ratio diode D%d/D6 Low gain"
            for tgraph_ratiod6 in [self.tgraph_lg_ratiod6[diode6], self.tgraph_hg_ratiod6[diode6]]:
                d = diode6 + 7
                title = format % d
                tgraph_ratiod6.GetXaxis().SetTimeDisplay(1)
                tgraph_ratiod6.GetYaxis().SetRangeUser(-7.,7.)
                tgraph_ratiod6.GetYaxis().SetTitleOffset(1.)
                tgraph_ratiod6.GetXaxis().SetLabelOffset(0.03)
                tgraph_ratiod6.GetYaxis().SetLabelOffset(0.01)
                tgraph_ratiod6.GetXaxis().SetLabelSize(0.04)
                tgraph_ratiod6.GetYaxis().SetLabelSize(0.04)
                tgraph_ratiod6.GetXaxis().SetTimeFormat("#splitline{%Y}{%d/%m}")
                tgraph_ratiod6.GetXaxis().SetNdivisions(-503)
                tgraph_ratiod6.GetYaxis().SetTitle(title)
                format = "Ratio diode D%d/D6 high gain"

        legend_ratiod6 = ROOT.TLegend(0.6,0.75,0.8,0.90)
        legend_ratiod6.AddEntry(self.tgraph_lg_ratiod6[0],"Low gain (filter 6)","p")
        legend_ratiod6.AddEntry(self.tgraph_hg_ratiod6[0],"high gain (filter 8)","p")

        legend_ratiod6.Draw()

        self.c1.Divide(3,2)

        option = "AP"
        for diode6 in range(3):
            self.c1.cd(diode6%3+1)
            self.tgraph_hg_ratiod6[diode6].Draw(option)
            self.c1.cd(diode6%3+4)
            self.tgraph_lg_ratiod6[diode6].Draw(option)

        self.c1.SetLeftMargin(0.14)
        self.c1.SetRightMargin(0.14)
        self.c1.Modified()

        l = ROOT.TLatex()
        l.SetNDC()
        l.SetTextFont(72)
        l.DrawLatex(0.1922,0.867,"ATLAS")

        l2 = ROOT.TLatex()
        l2.SetNDC()
        l2.DrawLatex(0.1922,0.811,"Internal")

        self.c1.Modified()
        self.c1.Update()


        ROOT.gStyle.SetPaperSize(26,20)
        print(self.dir, self.plot_name_ratiod6)
        if self.doEps:
            self.c1.Print("%s/%s.eps" % (self.dir,self.plot_name_ratiod6))
        else:
            self.c1.Print("%s/%s.png" % (self.dir,self.plot_name_ratiod6))
        self.c1.Print("%s/%s.root" % (self.dir,self.plot_name_ratiod6))

    def Normalized(self, t):
        if t.GetN()==0:
            return
        t.Sort()
        y=t.GetY()
        x=t.GetX()
        delta_y=t.GetEY()
        y_0=y[0]
        if (y_0!=0):
            for i in range (t.GetN()):
                t.SetPoint(i,x[i],100.*(y[i]/y_0-1.))
                t.SetPointError(i, 0., 100.*delta_y[i]/y_0)
        else:
            t.Dump()
            t.Print("")


























