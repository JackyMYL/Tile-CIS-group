############################################################
#
# do_pmts_plot_2gains.py
#
############################################################
#
# Author: Henric, using Sebs stuff
#
# August 20, 2011
#
# Goal:
# Compute an history plot for the pmts of a drawer variations
#
# Input parameters are:
#
# -> part: the partition number (1=LBA, 2=LBC, 3=EBA, 4=EBC) you want to plot.
#          DEFAULT VAL = 0 : produces all the plots
#
# -> drawer: the drawer number (from 1 to 64) you want to plot.
#            DEFAULT VAL = 0 : produces all the plots
#
# -> limit: the maximum tolerable variation (in %). If this variation
#           is excedeed the plots will have a RED background
#
# -> doWiki: used by laser experts to update the status webpage
#
# -> doEps: provide eps plots in addition to default png graphics
#
# For more info on the LASER system : http://atlas-tile-laser.web.cern.ch
#
#############################################################

from src.GenericWorker import *
from src.oscalls import *
import ROOT
import math
import time

class do_pmts_plot_2gains(GenericWorker):
    "Compute history plot for the pmts of a drawer"


    def __init__(self, part=0, module=0, limit=2, doEps = True, ymin=-10., ymax=+5., drawflaser=False):

        self.doEps     = doEps
        self.part      = part
        self.module    = module
        self.limit     = limit
        self.module_list = []
        self.flaser    = drawflaser

        self.outputTag = outputTag # global variable to tag output histogram file name
        self.dir    = getPlotDirectory(subdir=self.outputTag)

        self.ymin = ymin
        self.ymax = ymax

        for i in range(256):
            self.module_list.append([])

        self.PMTool   = LaserTools()
        self.origin   = ROOT.TDatime()
        self.time_max = 0
        self.time_min = 10000000000000000

        self.n_pmt = 0
        self.problemtxt = set()
        self.part_name = ["LBA", "LBC", "EBA", "EBC"]

        self.partset = set()

        self.badproblems = set(['Channel masked (unspecified)', 'No PMT connected',
                                'No HV', 'Wrong HV', 'ADC masked (unspecified)',
                                'ADC dead', 'Severe stuck bit', 'Severe data corruption',
                                'Very Large HF noise'])


    def ProcessStart(self):

        global run_list
        for run in run_list.getRunsOfType('Las'):

            time = run.time_in_seconds
            if self.time_min > time:
                self.time_min = time
                self.origin = ROOT.TDatime(run.time)

            if self.time_max < time:
                self.time_max = time


####
#
## Makes lists of events per drawer
#
####
    def ProcessRegion(self, region):

        for event in region.GetEvents():

            if event.run.runType=='Las':

                if 'status' not in event.data:
                    continue

#                if (event.data['is_OK']==False):
#                    continue

                [part, module, channel, gain] = region.GetNumber()
                if self.part != 0 and part != self.part: # if you just want one part
                    continue

                if self.module != 0 and module != self.module:
                    continue

                self.partset.add(part-1)

                index = 64*(part-1) + (module-1)
                self.module_list[index].append(event)
####
#
## Goes over the lists of events per module to make plots
#
####
    def ProcessStop(self):

        self.PrepareRoot()
        #
        #  First we are going to make some plots per partition
        #
        self.n_pmt = 0
        for i_part in self.partset:
            n_warn = 0
            n_bad  = 0
            n_unkn = 0

            for i_drawer in range(64): # 0 to 63
                if self.module != 0 and i_drawer != self.module-1:
                    continue

                module_events = self.module_list[64*i_part+i_drawer]

                if len(module_events)==0:
                    continue

                n_orange    = 0
                n_red       = 0
                n_black     = 0
                pmt_list    = []

                for i in range(48):
                    pmt_list.append([])

                for event in module_events:
                    [part_num, module, pmt, gain] = event.region.GetNumber(1)
                    pmt_list[pmt-1].append(event)
                    
                for i_pmt in range(48):

                    # Don't go further if the channel is not instrumented
                    if self.PMTool.is_instrumented(i_part,i_drawer,i_pmt+1) == False:
                        continue

                    pmt_events   = pmt_list[i_pmt]
                    max_var      = 0

                    for event in pmt_events:
                        if 'deviation' in event.data:
                            if max_var<math.fabs(event.data['deviation']):
                                max_var = math.fabs(event.data['deviation'])

                    graph_lim = 10.

                    hist_name = "%s%02d_pmt%02d"%(self.part_name[i_part],i_drawer+1,i_pmt+1)
                    hist_title = "%s%02d pmt%02d"%(self.part_name[i_part],i_drawer+1,i_pmt+1)
                    xmin =-15.0
                    xmax = 15.0
                    self.hist.append(ROOT.TH1F(hist_name, hist_title ,100, xmin, xmax))

                    good=True
                    for event in pmt_events: # fill the histogram
                        if 'deviation' in event.data:

                            deltagain = 1.
                            if 'hv_db' in event.data:
                                if (event.data['hv_db'])!=0 and event.data['HV']!=0.:
                                    try:
                                        deltagain = pow(event.data['HV']/event.data['hv_db'],6.9)
                                    except:
                                        pass

                            self.hist[self.n_pmt].Fill(event.data['deviation']/deltagain)

                        if event.data['status']!=0:
                            good=False
                    #
                    ### If pmt has only good event, we use it for the partition plots
                    #
                    if good:
                        self.mean[i_part].Fill(self.hist[self.n_pmt].GetMean())            # MEAN
                        self.rms[i_part].Fill(self.hist[self.n_pmt].GetRMS())              # RMS

                    self.n_pmt += 1

        self.DoPerPartitionPlots()
        #
        # Here we go for the actual pmt plots
        #
        self.PreparePerDrawerCanvas()

        for i_part in range(4):
            self.limit2.append(3*self.mean[i_part].GetRMS())

        self.n_pmt = 0

        hv=list(range(48))

        for i_part in self.partset:

            for i_drawer in range(64):

                if self.module != 0 and i_drawer != self.module-1:
                    continue

                # if (self.PMTool.getNewLVPS(i_part+1, i_drawer+1)):
                #     self.c1.SetFillColor(88)
                # else:
                #     self.c1.SetFillColor(0)

                module_events = self.module_list[64*i_part+i_drawer]

                if len(module_events)==0:
                    continue

#                n_orange    = 0
#                n_red       = 0
#                n_black     = 0
                pmt_list    = []

                # Clear pmt list for this module
                pmt_list = []
                pmt_cell_name = []
                for i in range(48):
                    pmt_list.append([])
                    pmt_cell_name.append('')

                for event in module_events:
                    [part_num, module, pmt, gain] = event.region.GetNumber(1)

                    pmt_list[pmt-1].append(event)
                    if pmt_cell_name[pmt-1]=='':
                        pmt_cell_name[pmt-1] = "PMT %d %s" % (pmt, event.region.GetCellName())

                for i_pmt in range(48):
                    # Clean the TGraphs
                    for tgraph in [ self.tgraphhv[i_pmt], self.tgraphhigh[i_pmt], self.tgraphlow[i_pmt],
                                    self.tgraphaffected[i_pmt], self.tgraphsaturated[i_pmt],
                                    self.tgraphbad[i_pmt], self.tgraphPisa[i_pmt], self.tgraphflaser[i_pmt] ]:
                        tgraph.Set(0)

                    # Don't go further if the channel is not instrumented
                    if self.PMTool.is_instrumented(i_part,i_drawer,i_pmt+1) == False:
                        continue

                    pmt_events = sorted(pmt_list[i_pmt], key=lambda event: event.run.time)

                    self.problemtxt.clear()
                    hvdone = False

                    for event in pmt_events:                       # fill the TGraphs
                        x = event.run.time_in_seconds-self.time_min
                        deltagain = 0.
                        if 'hv_db' in event.data:
                            if (event.data['hv_db'])!=0:
                                try:
                                    deltagain = 100.*(pow(event.data['HV']/event.data['hv_db'],6.9)-1)
                                    npoints = self.tgraphhv[i_pmt].GetN()
                                    self.tgraphhv[i_pmt].SetPoint(npoints, x, deltagain)
                                except:
                                    # print "exception in pow():",event.data['HV'],event.data['hv_db']
                                    pass

                        if 'status' not in event.data:
                            continue

                        if (event.data['status']&0x4) or (event.data['status']&0x10) or math.fabs(deltagain)>10.:
                            tgraph = self.tgraphbad[i_pmt]
                        elif event.data['status']&0x100:
                            tgraph = self.tgraphsaturated[i_pmt]
                        elif event.data['status']!=0:
                            tgraph = self.tgraphaffected[i_pmt]
                        else:
                            gain = event.region.GetNumber(0)[3]
                            if gain:
                                tgraph = self.tgraphhigh[i_pmt]
                            else:
                                tgraph = self.tgraphlow[i_pmt]

                        if 'deviation' in event.data:
                            y = event.data['deviation']
                            ey = event.data['deverr']
                            n = tgraph.GetN()
                            if self.ymin==None and self.ymax==None:
                                tgraph.SetPoint(n, x+gain*12000, y)
                            else:
                                tgraph.SetPoint(n, x+gain*12000, min(max(y,.95*self.ymin),.95*self.ymax))
                            tgraph.SetPointError(n, 0., ey)

                        if 'Pisa_deviation' in event.data:
                            tgraph = self.tgraphPisa[i_pmt]
                            y = event.data['Pisa_deviation']
                            ey = event.data['Pisa_deverr']
                            n = tgraph.GetN()
                            if self.ymin==None and self.ymax==None:
                                tgraph.SetPoint(n, x+gain*12000, y)
                            else:
                                tgraph.SetPoint(n, x+gain*12000, min(max(y,.95*self.ymin),.95*self.ymax))
                            tgraph.SetPointError(n, 0., ey)

                        if 'f_laser_db' in event.data and gain:
                            tgraph = self.tgraphflaser[i_pmt]
                            self.flaser=True
                            ## f_laser witen in deviation basis
                            #y = 100.*(1/event.data['f_laser_db']-1.)
                            ## BEWARE, in the db we have f_laser_db=1/f_laser
                            y = 100*(event.data['f_laser_db']-1.)
                            n = tgraph.GetN()
                            if self.ymin==None and self.ymax==None:
                                tgraph.SetPoint(n, x+gain*12000, y)
                            else:
                                tgraph.SetPoint(n, x+gain*12000, min(max(y,.95*self.ymin),.95*self.ymax))

                        if 'problems' in event.data:
                            for problem in event.data['problems']:
                                self.problemtxt.add(problem)

                    self.problembox[i_pmt].Clear()
                    for problem in self.problemtxt:
                        self.problembox[i_pmt].AddText(problem)

                self.DoPerDrawerPlots(i_part,i_drawer,pmt_cell_name)

        #for textbox in self.problembox:
            #textbox.Delete() This crashes now ?!!
        self.problembox = []

        for hist in self.mean:
            hist.Delete()

        for hist in self.rms:
            hist.Delete()

        for hist in self.hist:
            hist.Delete()


    def PrepareRoot(self):
        self.l1 = ROOT.TLatex()
        self.l1.SetNDC()

        ROOT.gStyle.SetTimeOffset(self.origin.Convert())
        ROOT.gStyle.SetOptTitle(1)
        ROOT.gStyle.SetTitleX(0.2)
        ROOT.gStyle.SetTitleW(0.2)
        ROOT.gStyle.SetTitleBorderSize(0)
        ROOT.gStyle.SetTitleFontSize(0.1)
        ROOT.gStyle.SetTitleOffset(0.1)
        ROOT.gStyle.SetTitleFillColor(0)
        ROOT.gStyle.SetPaperSize(26,20)
        #
        ROOT.gStyle.SetOptStat(0)
        ROOT.gStyle.SetStatX(.86)
        ROOT.gStyle.SetStatY(.95)
        ROOT.gStyle.SetStatW(.2)
        ROOT.gStyle.SetEndErrorSize(0.)

        self.mean       = []
        self.rms        = []
        self.comment    = []
        self.limit2     = []
        self.pt         = []
        self.hist  = []

        for i_part in range(4):
            part_name = self.part_name[i_part]
            self.mean.append(ROOT.TH1F(part_name+"_MEAN",part_name+" MEAN", 50, -5., 5.))
            self.rms.append(ROOT.TH1F(part_name+"_RMS",part_name+" RMS" , 50, 0, 2.5))
            self.mean[i_part].GetYaxis().SetTitle("Number of entries")
            self.mean[i_part].GetXaxis().SetTitle("PMT variation mean %s" % ('(in %)'))
            self.mean[i_part].GetXaxis().SetTitleOffset(1)
            self.mean[i_part].GetXaxis().SetLabelOffset(0.005)
            self.mean[i_part].GetXaxis().SetLabelFont(42)
            self.mean[i_part].GetXaxis().SetLabelSize(0.04)
            self.mean[i_part].GetXaxis().SetNdivisions(-205)

            self.rms[i_part].GetYaxis().SetTitle("Number of entries")
            self.rms[i_part].GetXaxis().SetTitle("PMT variation RMS %s" % ('(in %)'))
            self.rms[i_part].GetXaxis().SetTitleOffset(1)
            self.rms[i_part].GetXaxis().SetLabelOffset(0.005)
            self.rms[i_part].GetXaxis().SetLabelFont(42)
            self.rms[i_part].GetXaxis().SetLabelSize(0.04)
            self.rms[i_part].GetXaxis().SetNdivisions(-205)

        self.tgraphhigh = []
        self.tgraphlow = []
        self.tgraphbad = []
        self.tgraphaffected = []
        self.tgraphsaturated = []
        self.tgraphhv = []
        self.tgraphPisa = []
        self.tgraphflaser = []
        self.fit = []
        self.problembox = []
        self.slopebox   = []

        for i_pmt in range(48):
            markersize = .05
            self.problembox.append(ROOT.TPaveText(0.40,0.9,0.95,1.,"brNDC"))
            self.problembox[i_pmt].SetFillColor(623)
            self.problembox[i_pmt].SetTextSize(0.07)
            self.problembox[i_pmt].SetTextFont(42)
            self.problembox[i_pmt].SetBorderSize(0)

            self.slopebox.append(ROOT.TPaveText(0.20,0.3,0.9,0.5,"brNDC"))
            self.slopebox[i_pmt].SetBorderSize(0)

            self.tgraphhigh.append(ROOT.TGraphErrors())
            self.tgraphhigh[i_pmt].SetMarkerColor(4)
            self.tgraphhigh[i_pmt].SetLineColor(4)
            self.tgraphhigh[i_pmt].SetMarkerStyle(7)
            self.tgraphhigh[i_pmt].SetMarkerSize(markersize);

            self.tgraphlow.append(ROOT.TGraphErrors())
            self.tgraphlow[i_pmt].SetMarkerColor(8)
            self.tgraphlow[i_pmt].SetLineColor(8)
            self.tgraphlow[i_pmt].SetMarkerStyle(7)
            self.tgraphlow[i_pmt].SetMarkerSize(markersize);

            self.tgraphbad.append(ROOT.TGraphErrors())
            self.tgraphbad[i_pmt].SetMarkerColor(2)
            self.tgraphbad[i_pmt].SetLineColor(2)
            self.tgraphbad[i_pmt].SetMarkerStyle(7)
            self.tgraphbad[i_pmt].SetMarkerSize(markersize);

            self.tgraphaffected.append(ROOT.TGraphErrors())
            self.tgraphaffected[i_pmt].SetMarkerColor(800)
            self.tgraphaffected[i_pmt].SetLineColor(800)
            self.tgraphaffected[i_pmt].SetMarkerStyle(7)
            self.tgraphaffected[i_pmt].SetMarkerSize(markersize);

            self.tgraphsaturated.append(ROOT.TGraphErrors())
            self.tgraphsaturated[i_pmt].SetMarkerColor(804)
            self.tgraphsaturated[i_pmt].SetLineColor(804)
            self.tgraphsaturated[i_pmt].SetMarkerStyle(7)
            self.tgraphsaturated[i_pmt].SetMarkerSize(markersize);

            self.tgraphhv.append(ROOT.TGraph())
            self.tgraphhv[i_pmt].SetLineColor(1)

            self.tgraphflaser.append(ROOT.TGraph())
            self.tgraphflaser[i_pmt].SetLineColor(7)

            self.tgraphPisa.append(ROOT.TGraphErrors())
            self.tgraphPisa[i_pmt].SetMarkerColor(6)
            self.tgraphPisa[i_pmt].SetLineColor(6)
            self.tgraphPisa[i_pmt].SetMarkerStyle(7)
            self.tgraphPisa[i_pmt].SetMarkerSize(markersize);

        return


    def DoPerPartitionPlots(self):
        c_w = int(2600)
        c_h = int(2000)

        self.c2 = ROOT.TCanvas("MEAN", "MEAN CANVAS", c_w, c_h)
        self.c2.SetWindowSize(2*c_w - self.c2.GetWw(), 2*c_h - self.c2.GetWh())

        self.c2.Range(0,0,1,1)
        self.c2.SetFillColor(0)
        self.c2.SetBorderMode(0)

        self.c2.cd()
        self.c2.Divide(2,2)
        for i_part in range(4):
            self.c2.cd(i_part+1).SetLogy(1)
            self.c2.cd(i_part+1).SetLeftMargin(0.14)
            self.c2.cd(i_part+1).SetRightMargin(0.14)
#
# Draw mean
#
        ROOT.gStyle.SetOptFit(11)
        ROOT.gStyle.SetOptStat(2210)

        for i_part in range(4):
            self.c2.cd(i_part+1)
            self.mean[i_part].SetStats(1)
            self.mean[i_part].Fit("gaus")
            #self.mean[i_part].Draw()
            self.c2.cd(i_part+1).Modified()

        self.c2.Modified()
        self.c2.Update()
        if self.doEps:
            self.c2.Print("%s/Mean_PMTs.ps" % (self.dir))
        else:
            self.c2.Print("%s/Mean_PMTs.png" % (self.dir))
        self.c2.Print("%s/Mean_PMTs.C" % (self.dir))
#
# Draw rms
#
        self.c2.cd()
        self.c2.cd().Clear()
        self.c2.Divide(2,2)
        for i_part in range(4):
            self.c2.cd(i_part+1).SetLogy(1)
            self.c2.cd(i_part+1).SetLeftMargin(0.14)
            self.c2.cd(i_part+1).SetRightMargin(0.14)
        ROOT.gStyle.SetOptFit(0)
        ROOT.gStyle.SetOptStat(102210)
        ROOT.gStyle.SetStatW(.4)

        for i_part in range(4):
            self.c2.cd(i_part+1).Clear()
            self.rms[i_part].SetStats(1)
            self.rms[i_part].Draw()
            self.c2.cd(i_part+1).Modified()

        self.c2.Modified()
        self.c2.Update()
        if self.doEps:
            self.c2.Print("%s/Rms_PMTs.ps" % (self.dir))
        else:
            self.c2.Print("%s/Rms_PMTs.png" % (self.dir))
        self.c2.Print("%s/Rms_PMTs.C" % (self.dir))

        ROOT.gStyle.SetOptStat(0)
        return


    def PreparePerDrawerCanvas(self):
        c_w = int(2600)
        c_h = int(2000)

        self.c1 = ROOT.TCanvas("PerDrawerCanvas","a canvas",c_w,c_h)
        self.c1.SetWindowSize(2*c_w - self.c1.GetWw(), 2*c_h - self.c1.GetWh())

        self.c1.Range(0,0,1,1)
        self.c1.SetFillColor(0)
        self.c1.SetBorderMode(0)
        self.c1.cd()
        self.c1.Divide(6,8,0.001,0.002)

        self.c1.Modified()
        self.c1.Update()

        ROOT.gEnv.SetValue("Canvas.PrintDirectory",self.dir)
    
        return


    def DoPerDrawerPlots(self, i_part, i_drawer, pmt_cell_name):
        # Draw module/filter text

        self.c1.cd()
        
        x = 0.20
        y = 0.34
        LatexFontSize=0.05

        l1 = self.l1.DrawLatex(x,y,'%s%02d' % (self.part_name[i_part],(i_drawer+1)))
        y -= 0.01
        if i_part>1: # Extended barrels
            x -= 0.166
        legend = ROOT.TLegend(x,y-1.2*LatexFontSize,x+.25,y)
        legend.SetFillColor(0)
        legend.SetBorderSize(0)
        legend.AddEntry(self.tgraphhv[0],"High voltage","L")
        if self.flaser:
            legend.AddEntry(self.tgraphflaser[0],"f_laser","L")
        legend.AddEntry(self.tgraphhigh[0],"High Gain","P")
        legend.AddEntry(self.tgraphlow[0], "Low Gain", "P")
        legend.AddEntry(self.tgraphbad[0],"Bad status","P")
        legend.AddEntry(self.tgraphaffected[0], "Affected|Noisy status", "P")
        legend.AddEntry(self.tgraphsaturated[0], "Saturated", "P")
        if self.tgraphPisa[0].GetN():
            legend.AddEntry(self.tgraphPisa[0],"Pisa method","P")

        legend.SetNColumns(2)
        legend.Draw()

        for i_pmt in range(48):
            pad = self.c1.cd(i_pmt+1)
            pad.Clear()

            # Don't go further if the channel is not instrumented
            if self.PMTool.is_instrumented(i_part,i_drawer,i_pmt+1) == False:
                continue

            pad.SetFrameFillColor(0)
            pad.SetLeftMargin(0.17);
            pad.SetRightMargin(0.07);
            pad.SetTopMargin(0.02);
            pad.SetBottomMargin(0.20);
            pad.Draw()

            histtitle = pmt_cell_name[i_pmt]
            #print "Drawing hist ",histtitle

            if self.ymin==None and self.ymax==None:
                hist = pad.DrawFrame(-86400,-10, self.time_max-self.time_min+86400, +5, histtitle)
                hist.GetYaxis().SetRangeUser(-10,+5)
            else:
                hist = pad.DrawFrame(-86400,self.ymin, self.time_max-self.time_min+86400, self.ymax, histtitle)
                hist.GetYaxis().SetRangeUser(self.ymin,self.ymax)

            hist.GetXaxis().SetTimeDisplay(1)
            hist.GetXaxis().SetLabelOffset(0.05)
            hist.GetXaxis().SetLabelFont(42)
            hist.GetXaxis().SetLabelSize(0.1)
            hist.GetXaxis().SetTimeFormat("%d/%m")
            hist.GetXaxis().SetNdivisions(-503)

            hist.GetYaxis().SetLabelFont(42)
            hist.GetYaxis().SetLabelSize(0.1)
            if ( i_pmt%6 == 0 ):
                hist.GetYaxis().SetTitleFont(42)
                hist.GetYaxis().SetTitleSize(0.1)
                hist.GetYaxis().SetTitleOffset(0.7)
                hist.GetYaxis().SetTitle("PMT variation [%]")

            option = 'P,same'
            for tgraph in [ self.tgraphPisa[i_pmt], self.tgraphaffected[i_pmt],
                           self.tgraphsaturated[i_pmt], self.tgraphbad[i_pmt],
                           self.tgraphhigh[i_pmt], self.tgraphlow[i_pmt] ]:
                if tgraph.GetN()>1:
                    tgraph.Sort()

                    if self.ymax==None and ROOT.TMath.MaxElement(tgraph.GetN(),tgraph.GetY()) > hist.GetMaximum():
                        hist.GetYaxis().SetRangeUser(hist.GetMinimum(),ROOT.TMath.MaxElement(tgraph.GetN(),tgraph.GetY())*1.10)
                    if self.ymin==None and ROOT.TMath.MinElement(tgraph.GetN(),tgraph.GetY()) < hist.GetMinimum():
                        hist.GetYaxis().SetRangeUser(ROOT.TMath.MinElement(tgraph.GetN(),tgraph.GetY())*1.10,hist.GetMaximum())
                    tgraph.Draw(option)
                option = 'P,same'

            if self.tgraphhv[i_pmt].GetN()>1:
                self.tgraphhv[i_pmt].Sort()
                self.tgraphhv[i_pmt].Draw("L, same")

            if self.tgraphflaser[i_pmt].GetN()>1:
                self.tgraphflaser[i_pmt].Sort()
                self.tgraphflaser[i_pmt].Draw("L,same")

            if self.problembox[i_pmt].GetSize():
                self.problembox[i_pmt].Draw()

            pad.Modified()
            pad.Update()

        self.c1.Modified()
        self.c1.Update()

        if i_drawer==0: # Open PDF file
            self.c1.Print("%s/new%s.pdf[" % (self.dir, self.part_name[i_part]))

        self.c1.Print( "%s/new%s.pdf" % (self.dir,self.part_name[i_part]), 
                       "Title:%s%02d" % (self.part_name[i_part],(i_drawer+1)) )

        if i_drawer==63: # Close PDF file
            self.c1.Print("%s/new%s.pdf]" % (self.dir,self.part_name[i_part]))

#       Clean
        l1.Delete()

        for i_pmt in range(48):
            pad = self.c1.cd(i_pmt+1)
            pad.Clear()

        return
# The End
