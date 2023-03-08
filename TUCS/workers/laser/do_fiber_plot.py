############################################################
#
# do_fiber_plot.py
#
############################################################
#
# Author: Henric, based on work by Seb Viret
#
# March 20, 2012
#
# Goal:
# Compute an history plot for the patch panel fiber variation
#
# Input parameters are:
#
# -> fib: the PP fiber number (from 0 to 383) you want to plot.
#         DEFAULT VAL = -1 : produces all the plots
#
# -> limit: y-axis limit
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


class do_fiber_plot(GenericWorker):

    "Compute history plot for the patch-panel LASER fibres"

    c1 = None

    def __init__(self, runType='Las', fib=-1, limit=10, doEps = False):
        self.runType   = runType
        self.doEps     = doEps
        self.fib       = fib
        self.limit     = limit

        self.outputTag = outputTag # global variable to tag output histogram file name
        self.dir    = getPlotDirectory(subdir=self.outputTag)

        self.fiber_list      = []
        self.fiber_ind_list  = [[] for x in range(384)]

        for i in range(384):
            self.fiber_list.append([])

        self.PMTool = LaserTools()
        self.time_max = 0
        self.time_min = 10000000000000000

        try:
            self.HistFile.cd()
        except:
            self.initHistFile("Tucs.HIST{}.root".format(self.outputTag))
        self.HistFile.cd()

        if ROOT.gDirectory.FindObject("Laser")==None:
            ROOT.gDirectory.mkdir("Laser")
        ROOT.gDirectory.cd("Laser")

        if self.c1 == None:
            cw = 1400
            ch = 1000
            self.c1 = src.MakeCanvas.MakeCanvas(cw,ch)
            self.c1.SetWindowSize(2*cw - self.c1.GetWw(), 
                                  2*ch - self.c1.GetWh())
            self.c1.Range(0,0,1,1)
            self.c1.SetTitle("Clear fibre corrections")


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

        self.PrepareCanvas()

        #  we do the graphs for all the fibers

        for i_fib in range(384):

            if self.fib != -1 and i_fib != self.fib:      # if you just want one fiber
                continue

            max_var = 0
            name    = self.PMTool.get_fiber_name(i_fib)

            for run in run_list.getRunsOfType('Las'):
                x = math.fabs(100.*(run.data['fiber_var'][i_fib]-1.))
                if max_var<x:
                    max_var = x

            if max_var == 0:
                continue

            # Cosmetics (Part 2): the fiber graph itself

            self.frame1.GetYaxis().SetTitle("%s evolution %s" % (name,'(in %)'))

            graph_lim = max(1.1*max_var,self.limit)
            self.frame1.SetMaximum(graph_lim)
            if graph_lim<100.:
                self.frame1.SetMinimum(-graph_lim)
            else:
                self.frame1.SetMinimum(-100.)

            self.tgraph_lg.Set(0)
            self.tgraph_hg.Set(0)
            self.tgraph_lg_bad.Set(0)
            self.tgraph_hg_bad.Set(0)
            self.tgraph_total_lg.Set(0)
            self.tgraph_total_hg.Set(0)
            self.tgraph_total_lg_bad.Set(0)
            self.tgraph_total_hg_bad.Set(0)

            for run in run_list.getRunsOfType('Las'): # fill the histogram

                y = 100.*(run.data['fiber_var'][i_fib]-1.0)

                if run.data['wheelpos'] == 6:
                    if y<-20.:
                        tgraph = self.tgraph_lg_bad
                    else:
                        tgraph = self.tgraph_lg

                if run.data['wheelpos'] == 8:
                    if y<-20:
                        tgraph = self.tgraph_hg_bad
                    else:
                        tgraph = self.tgraph_hg

                i = tgraph.GetN()

                if y!=0.:
                    ey=100.*run.data['fiber_var_err'][i_fib]
                    tgraph.SetPoint(i, run.time_in_seconds,y)
                    tgraph.SetPointError(i, 0., ey)

                gain = 0
                if run.data['wheelpos'] == 6:
                    gain = 0
                if run.data['wheelpos'] == 8:
                    gain = 1

                if 'fibretotals' in run.data:
                    y = self.corr[gain]*run.data['fibretotals'][i_fib]

                    if run.data['wheelpos'] == 6:
                        if y<50.:
                            tgraph = self.tgraph_total_lg_bad
                        else:
                            tgraph = self.tgraph_total_lg

                    if run.data['wheelpos'] == 8:
                        if y<50.:
                            tgraph = self.tgraph_total_hg_bad
                        else:
                            tgraph = self.tgraph_total_hg

                    i = tgraph.GetN()
                    tgraph.SetPoint(i, run.time_in_seconds, y)           

            # Put things on disk
            self.c1.Modified()
            self.c1.Update()
#             if self.doEps:
#                 
# #                self.c1.Print("%s/%s.ps" % (self.dir,"%s_fiber_history" % (name)),"Landscape")
#                 
#             else:
#                 self.c1.Print("%s/%s.png" % (self.dir,"%s_fiber_history" % (name)))

            ROOT.gStyle.SetPaperSize(26,20)
            if i_fib==0:
                pdf_name = "%s/LB_fibre_history.pdf" % (self.dir)
                self.c1.Print(pdf_name+"[")
            elif i_fib==128:
                self.c1.Print(pdf_name+"]")
                pdf_name = "%s/EBA_fibre_history.pdf" % (self.dir)
                self.c1.Print(pdf_name+"[")
            elif i_fib==256:
                self.c1.Print(pdf_name+"]")
                pdf_name = "%s/EBC_fibre_history.pdf" % (self.dir)
                self.c1.Print(pdf_name+"[")
            
            self.c1.Print(pdf_name,"Title:%s"% (name))

            if i_fib==383:
                self.c1.Print(pdf_name+"]","Title:%s"% (name))

            self.HistFile.cd("Laser")
            self.tgraph_lg.SetName('%03d_lowgain'%i_fib)
            self.tgraph_lg.SetTitle("%s evolution %s" % (name,'(in %)'))
            self.tgraph_lg.Write()
            self.tgraph_hg.SetName('%03d_highgain'%i_fib)
            self.tgraph_hg.SetTitle("%s evolution %s" % (name,'(in %)'))
            self.tgraph_hg.Write()
        #   end for i_fib in range(384):

        self.CleanRoot()


    def PrepareCanvas(self):
        cadre_hl_ratio = 81.84/1.24
        self.corr = [1.,  cadre_hl_ratio]

        weeks = int((self.time_max - self.time_min)/(86400*7))
        
        padding = (7*86400*(weeks+1) - (self.time_max-self.time_min))/2.
        cadre_xmin = self.time_min - padding
        cadre_xmax = self.time_max + padding
        
        if weeks>40:
            ndiv = -(800+(weeks+1)//8)   # tick every 8 week 
        elif weeks>20:
            ndiv = -(400+(weeks+1)//4)   # tick every 4 week  
        elif weeks>10:
            ndiv = -(1400+(weeks+1)//2)  # tick every 8 week 
        else:
            ndiv = -(700+weeks+1)

        ROOT.gStyle.SetOptStat(0)
        ROOT.gStyle.SetStatX(0.78)
        ROOT.gStyle.SetStatY(0.83)
        ROOT.gStyle.SetEndErrorSize(0.)
        ROOT.gStyle.SetTimeOffset(0)
        ROOT.gStyle.SetOptTitle(0)

        self.c1.Divide(1, 2)
        pad = self.c1.cd(1)

        pad.SetLeftMargin(0.14)
        pad.SetRightMargin(0.14)
        pad.SetFrameFillColor(0)

        pad.SetFillColor(0);
        pad.SetBorderMode(0);
        pad.SetGridx(1);
        pad.SetGridy(1);

        #        self.frame1 = ROOT.TH1F('Fibre canvas', 'Fibre_canvas',\
        #                               100, -43200., self.time_max-self.time_min+43200.)
        self.frame1 = pad.DrawFrame(cadre_xmin, self.limit, cadre_xmax,
                                   self.limit, 'Fibre correction')
        self.frame1.SetFillColor(50);
        self.frame1.GetXaxis().SetTimeDisplay(1)
        self.frame1.GetYaxis().SetTitleOffset(.6)
        self.frame1.GetXaxis().SetLabelOffset(0.03)
        self.frame1.GetYaxis().SetLabelOffset(0.01)
        self.frame1.GetXaxis().SetLabelSize(0.03)
        self.frame1.GetYaxis().SetLabelSize(0.04)
        self.frame1.GetXaxis().SetTimeFormat("#splitline{%d/%m}{%Y}")
        self.frame1.GetXaxis().SetNdivisions(ndiv)


        self.tgraph_hg = ROOT.TGraphErrors()
        self.tgraph_hg_bad = ROOT.TGraphErrors()
        self.tgraph_hg.SetMarkerStyle(30)
        self.tgraph_hg.SetMarkerColor(4)
        self.tgraph_hg_bad.SetMarkerStyle(30)
        self.tgraph_hg_bad.SetMarkerColor(2)
        self.tgraph_lg = ROOT.TGraphErrors()
        self.tgraph_lg_bad = ROOT.TGraphErrors()
        self.tgraph_lg.SetMarkerStyle(29)
        self.tgraph_lg.SetMarkerColor(8)
        self.tgraph_lg_bad.SetMarkerStyle(29)
        self.tgraph_lg_bad.SetMarkerColor(2)
        self.tgraph_lg.Draw("P,same")
        self.tgraph_lg_bad.Draw("P,same")
        self.tgraph_hg.Draw("P,same")
        self.tgraph_hg_bad.Draw("P,same")

        
        l1 = ROOT.TLatex()
        l1.SetNDC();
        l1.SetTextFont(72);
        l1.DrawLatex(0.1922,0.867,"ATLAS");

        l2 = ROOT.TLatex()
        l2.SetNDC();
        l2.DrawLatex(0.1922,0.811,"Internal");

        self.c1.cd()

        self.legend1 = ROOT.TLegend(0.15,0.47,0.36,0.55)
        self.legend1.SetFillStyle(0)
        self.legend1.AddEntry(self.tgraph_lg,"Low gain (filter 6)","p")
        self.legend1.AddEntry(self.tgraph_hg,"High gain (filter 8)","p")
        self.legend1.Draw()

        pad = self.c1.cd(2)

        pad.SetLeftMargin(0.14)
        pad.SetRightMargin(0.14)
        pad.SetFrameFillColor(0)
        pad.SetFillColor(0);
        pad.SetBorderMode(0);
        pad.SetGridx(1);
        pad.SetGridy(1);

        cadre_ymin = 0. 
        cadre_ymax = 600.
        self.frame2 = pad.DrawFrame(cadre_xmin, cadre_ymin, cadre_xmax, cadre_ymax, 'Fibre Total')
#        self.frame2 = ROOT.TH2F('CadreSignal', 'Total',\
#                                100, cadre_xmin, cadre_xmax, 100, cadre_ymin, cadre_ymax)
#        self.frame2.Draw()
        self.frame2.SetFillColor(50);
        self.frame2.GetXaxis().SetTimeDisplay(1)
        self.frame2.GetYaxis().SetTitleOffset(.6)
        self.frame2.GetXaxis().SetLabelOffset(0.03)
        self.frame2.GetYaxis().SetLabelOffset(0.01)
        self.frame2.GetXaxis().SetLabelSize(0.03)
        self.frame2.GetYaxis().SetLabelSize(0.04)
        self.frame2.GetXaxis().SetTimeFormat("#splitline{%d/%m}{%Y}")
        self.frame2.GetXaxis().SetNdivisions(ndiv)
        self.frame2.GetYaxis().SetTitle("mean channel low gain signal [pC]")

        ROOT.gStyle.SetHatchesLineWidth(1)

#        self.box = ROOT.TBox(cadre_xmin, 0, cadre_xmax, 100.)
#        self.box.SetLineWidth(0)
#        self.box.SetFillStyle(3004)
#        self.box.SetFillColor(2)
#        self.box.Draw()

        self.text = ROOT.TPaveText(cadre_xmin, cadre_ymin, cadre_xmax , 50., "br")
        self.text.SetFillColor(2)
        self.text.SetFillStyle(3004)
        self.text.SetTextSize(0.07)
        self.text.SetTextFont(42)
        self.text.SetTextColor(2)
        self.text.SetBorderSize(0)
        self.text.AddText("too low")
        self.text.Draw()

        self.tgraph_total_lg = ROOT.TGraph()
        self.tgraph_total_lg.SetMarkerStyle(29)
        self.tgraph_total_lg.SetMarkerColor(8)
        self.tgraph_total_lg_bad = ROOT.TGraph()
        self.tgraph_total_lg_bad.SetMarkerStyle(29)
        self.tgraph_total_lg_bad.SetMarkerColor(2)

        self.tgraph_total_hg = ROOT.TGraph()
        self.tgraph_total_hg.SetMarkerStyle(30)
        self.tgraph_total_hg.SetMarkerColor(4)
        self.tgraph_total_hg_bad = ROOT.TGraph()
        self.tgraph_total_hg_bad.SetMarkerStyle(30)
        self.tgraph_total_hg_bad.SetMarkerColor(2)

        self.tgraph_total_lg.Draw("P,same")
        self.tgraph_total_lg_bad.Draw("P,same")
        self.tgraph_total_hg.Draw("P,same")
        self.tgraph_total_hg_bad.Draw("P,same")

        self.axis = ROOT.TGaxis(cadre_xmax, cadre_ymin, cadre_xmax, cadre_ymax, cadre_ymin, cadre_ymax/cadre_hl_ratio, 506, "+L" )
        self.axis.SetTitleFont(self.frame2.GetTitleFont())
        self.axis.SetTitleSize(self.frame2.GetTitleSize())
        self.axis.SetLabelSize(0.04)
        self.axis.SetTitleOffset(.6)
        self.axis.SetLabelFont(self.frame2.GetLabelFont())

        self.axis.SetTitle("mean channel high gain signal [pC]")
        self.axis.Draw()

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
        self.frame1.Delete()
        self.frame2.Delete()
        self.tgraph_lg.Delete()
        self.tgraph_hg.Delete()
        self.tgraph_total_lg.Delete()
        self.tgraph_total_hg.Delete()
        self.tgraph_lg_bad.Delete()
        self.tgraph_hg_bad.Delete()
        self.tgraph_total_lg_bad.Delete()
        self.tgraph_total_hg_bad.Delete()
        self.c1.Close()
