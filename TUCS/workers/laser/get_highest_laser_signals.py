############################################################
#
# get_lowest_laser_signals.py
#
############################################################
#
# Author: Marco van Woerden (13/07/2012)
#
# Output:
# Histograms pointing out which channels have the lowest signal output (in pC).
#
# Input parameters are:
# -> part: the partition number (1=LBA, 2=LBC, 3=EBA, 4=EBC) you want to plot.
# -> number: number of channels in the output
#
#############################################################

from src.GenericWorker import *
from src.oscalls import *
import src.MakeCanvas

class get_highest_laser_signals(GenericWorker):
    "Find signals with highest average output (in pC)."

    c1 = None
    c2 = None

    def __init__(self,  part=1, number=100, cells=[]):
        self.part     = part
        self.number   = max(20,number,len(cells)*60)
        self.l_size   = 0.04
        if self.number > 100:
            self.l_size = 0.04 / float(self.number) * 100.
        self.mod      = -1
        self.chan     = -1
        self.PMTool   = LaserTools()
        self.LG_evts  = list() # Events with low gain info
        self.HG_evts  = list() # Events with high gain info

        self.outputTag = outputTag # global variable to tag output histogram file name
        self.dir    = getPlotDirectory(subdir=self.outputTag)

        self.cells = cells
        if cells == []:
            self.cells = list(range(1,49))

        self.sum_signals = []
        self.sm2_signals = []
        self.num_signals = []
        self.var_signals = []
        self.bad_signals = []
        for idx in range(0,2*48*64*4):
            self.sum_signals += [0.]
            self.sm2_signals += [0.]
            self.num_signals += [0.]
            self.var_signals += [0.]
            self.bad_signals += [False]

        self.minsig_lg_idx = []
        self.minsig_hg_idx = []

        if self.c1==None:
            self.c1 = src.MakeCanvas.MakeCanvas()
            #self.c1.SetTitle("Put here a nice title")

        if self.c2==None:
            self.c2 = src.MakeCanvas.MakeCanvas()
            #self.c2.SetTitle("Put here a nice title")


    def ProcessStart(self):
        global run_list

    def ProcessRegion(self, region):
        # First retrieve all the relevant partition infos

        numbers = region.GetNumber()

        if len(numbers)!=4:
            return

        [part, module, chan, gain] = numbers        

        ind       = self.PMTool.get_index(part-1, module-1, chan, 0)

        match_found = False
        for mod in range(1,65):
            for ch in self.cells:
                if ind == self.PMTool.get_index(self.part-1,mod-1,ch,0):
                    match_found = True
                    self.mod  = mod
                    self.chan = ch
                    break
        if not match_found:
            return

        for event in region.GetEvents():
            if event.run.runType!='Las':
                continue

            if gain==0:
                self.LG_evts.append([event,self.mod,self.chan])

            if gain==1:
                self.HG_evts.append([event,self.mod,self.chan])


    def ProcessStop(self):

        self.c1.Clear()
        self.c1.cd()

        self.p1 = ROOT.TPad("LG signals","LG signals",0.,0.55,1.,0.95,0,0)
        self.p2 = ROOT.TPad("HG signals","HG signals",0.,0.05,1.,0.45,0,0)

        for pad in [self.p1,self.p2]:
            pad.SetBottomMargin(0.35)
            pad.SetLeftMargin(0.15)
            pad.SetRightMargin(0.03)
            pad.SetTopMargin(0.01)
            pad.Draw()

        #self.c1.Divide(1,2)

        self.tgraph_lg = ROOT.TGraphErrors()
        self.tgraph_hg = ROOT.TGraphErrors()
        self.tgraph_lg_bad = ROOT.TGraphErrors()
        self.tgraph_hg_bad = ROOT.TGraphErrors()

        self.ratio_hl = 50.

        ROOT.gStyle.SetOptStat(0)
        ROOT.gStyle.SetStatX(0.78)
        ROOT.gStyle.SetStatY(0.83)
        ROOT.gStyle.SetPalette(1)
        ROOT.gStyle.SetOptTitle(1)
        ROOT.gStyle.SetTitleX(0.15)
        ROOT.gStyle.SetTitleW(0.2)
        ROOT.gStyle.SetTitleBorderSize(0)
        ROOT.gStyle.SetTitleFontSize(0.1)
        ROOT.gStyle.SetEndErrorSize(0.)

        ROOT.gStyle.SetTitleX(0.5)
        ROOT.gStyle.SetTitleAlign(23);

        # FIRST WE STORE ALL NECESSARY DATA
        for mod in range(1,65):
            for ch in self.cells:
                for a in self.LG_evts:
                    event = a[0]
                    if a[1] != mod or a[2] != ch or 'status' not in event.data:
                        continue
                    elif event.data['status']!=0 or 'problems' in event.data:
                        self.bad_signals[self.PMTool.get_index(self.part-1,mod-1,ch-1,0)] = True
                    event = a[0]
                    if 'signal' in event.data:
                        self.sum_signals[self.PMTool.get_index(self.part-1,mod-1,ch-1,0)] += math.fabs(event.data['signal'])
                        self.sm2_signals[self.PMTool.get_index(self.part-1,mod-1,ch-1,0)] += math.fabs(event.data['signal']) * math.fabs(event.data['signal'])
                        self.num_signals[self.PMTool.get_index(self.part-1,mod-1,ch-1,0)] += 1.
                for a in self.HG_evts:
                    event = a[0]
                    if a[1] != mod or a[2] != ch or 'status' not in event.data:
                        continue
                    elif event.data['status']!=0 or 'problems' in event.data:
                        self.bad_signals[self.PMTool.get_index(self.part-1,mod-1,ch-1,1)] = True
                    event = a[0]
                    if 'signal' in event.data:
                        self.sum_signals[self.PMTool.get_index(self.part-1,mod-1,ch-1,1)] += math.fabs(event.data['signal'])
                        self.sm2_signals[self.PMTool.get_index(self.part-1,mod-1,ch-1,1)] += math.fabs(event.data['signal']) * math.fabs(event.data['signal'])
                        self.num_signals[self.PMTool.get_index(self.part-1,mod-1,ch-1,1)] += 1.

        # NOW WE CALCULATE THE MEAN AND VARIANCE
        for idx in range(self.PMTool.get_index(3,63,47,1)):
            [part, module, chan, gain] = self.PMTool.get_rev_index(idx)
            if not (chan+1) in self.cells:
                continue 
            n = self.num_signals[idx]
            if n > 0.:
                self.sum_signals[idx] /= n
            if n > 1.:
                self.var_signals[idx] = math.sqrt(self.sm2_signals[idx] / (n-1.) - self.sum_signals[idx]*self.sum_signals[idx] * n / (n-1.))
                if gain == 0:
                    self.minsig_lg_idx.sort(key=lambda x: x[1])
                    if len(self.minsig_lg_idx) < self.number:
                        self.minsig_lg_idx.append(["%s_LG"%self.PMTool.get_channel_name(part,module,chan),self.sum_signals[idx],self.var_signals[idx],self.bad_signals[idx]])
                    for s in self.minsig_lg_idx[::]:
                        if s[1] < self.sum_signals[idx] and len(self.minsig_lg_idx) == self.number:
                            self.minsig_lg_idx.remove(self.minsig_lg_idx[::][0])
                            self.minsig_lg_idx.append(["%s_LG"%self.PMTool.get_channel_name(part,module,chan),self.sum_signals[idx],self.var_signals[idx],self.bad_signals[idx]])
                            break
                if gain == 1:
                    self.minsig_hg_idx.sort(key=lambda x: x[1])
                    if len(self.minsig_hg_idx) < self.number:
                        self.minsig_hg_idx.append(["%s_HG"%self.PMTool.get_channel_name(part,module,chan),self.sum_signals[idx],self.var_signals[idx],self.bad_signals[idx]])
                    for s in self.minsig_hg_idx[::]:
                        if s[1] < self.sum_signals[idx] and len(self.minsig_hg_idx) == self.number:
                            self.minsig_hg_idx.remove(self.minsig_hg_idx[::][0])
                            self.minsig_hg_idx.append(["%s_HG"%self.PMTool.get_channel_name(part,module,chan),self.sum_signals[idx],self.var_signals[idx],self.bad_signals[idx]])
                            break

        # NOW WE PLOT THE CHANNELS WITH MINIMAL SIGNAL
        self.minsig_lg_idx.sort(key=lambda x: x[1])
        self.minsig_hg_idx.sort(key=lambda x: x[1])
        self.hist_minimal_signals_LG = ROOT.TH2D("maximal LG signals","maximal LG signals",self.number,0,self.number,1000,self.minsig_lg_idx[::][0][1]/1.5,\
                                                 max(0.001,self.minsig_lg_idx[::-1][0][1]*1.5))
        self.hist_minimal_signals_HG = ROOT.TH2D("maximal HG signals","maximal HG signals",self.number,0,self.number,1000,self.minsig_hg_idx[::][0][1]/1.5,\
                                                 max(0.001,self.minsig_hg_idx[::-1][0][1]*1.5))
        self.hist_minimal_signals_LG.GetYaxis().SetTitle("LG signal [pC]")
        self.hist_minimal_signals_HG.GetYaxis().SetTitle("HG signal [pC]")
        entries = self.number
        if len(self.minsig_lg_idx) < self.number:
            entries = len(self.minsig_lg_idx)
        for i in range(1,entries+1):
            self.hist_minimal_signals_LG.GetXaxis().SetBinLabel(i,self.minsig_lg_idx[i-1][0])
            self.hist_minimal_signals_HG.GetXaxis().SetBinLabel(i,self.minsig_hg_idx[i-1][0])
            if self.minsig_lg_idx[i-1][3]:
                self.tgraph_lg_bad.SetPoint(i,i,float(math.fabs(self.minsig_lg_idx[i-1][1])))
                self.tgraph_lg_bad.SetPointError(i,0.5,float(math.fabs(self.minsig_lg_idx[i-1][2])))
            else:
                self.tgraph_lg.SetPoint(i,i,float(math.fabs(self.minsig_lg_idx[i-1][1])))
                self.tgraph_lg.SetPointError(i,0.5,float(math.fabs(self.minsig_lg_idx[i-1][2])))
            if self.minsig_hg_idx[i-1][3]:
                self.tgraph_hg_bad.SetPoint(i,i,float(math.fabs(self.minsig_hg_idx[i-1][1])))
                self.tgraph_hg_bad.SetPointError(i,0.5,float(math.fabs(self.minsig_hg_idx[i-1][2])))
            else:
                self.tgraph_hg.SetPoint(i,i,float(math.fabs(self.minsig_hg_idx[i-1][1])))
                self.tgraph_hg.SetPointError(i,0.5,float(math.fabs(self.minsig_hg_idx[i-1][2])))
            #self.hist_minimal_signals.SetBinError(i,float(math.fabs(self.minsig_lg_idx[i-1][1])))
        for hist in [self.hist_minimal_signals_LG,self.hist_minimal_signals_HG]:
            hist.GetXaxis().SetTitle("")
            hist.GetYaxis().SetTitleOffset(0.6)
            hist.GetYaxis().SetTitleSize(0.04)
            hist.GetYaxis().SetLabelOffset(0.01)
            hist.GetYaxis().SetLabelSize(0.04)
            hist.GetXaxis().SetLabelOffset(0.01)
            hist.GetXaxis().SetLabelSize(self.l_size)
            hist.GetXaxis().SetTitleOffset(0.8)
            #hist.GetXaxis().LabelsOption("a")
            hist.GetXaxis().LabelsOption("v")

        ROOT.gStyle.SetPaperSize(80,40)
        #self.c1.SetWindowSize(1500,300)
        #self.c1.SetCanvasSize(1500,300)

        for tgraph in [self.tgraph_lg,self.tgraph_hg]:
            tgraph.Sort()
            tgraph.SetMarkerColor(4)
            tgraph.SetMarkerStyle(29)
        for tgraph in [self.tgraph_lg_bad,self.tgraph_hg_bad]:
            tgraph.Sort()
            tgraph.SetMarkerColor(2)
            tgraph.SetMarkerStyle(29)

        self.p1.cd()
        self.hist_minimal_signals_LG.Draw("")
        for tgraph in [self.tgraph_lg,self.tgraph_lg_bad]:
            if tgraph.GetN() > 0:
                tgraph.Draw("Psame")
        line1 = ROOT.TF1("line1","[0]",-1.,self.number+1)
        line1.SetParameter(0,530.)
        line1.SetLineColor(2)
        line1.SetLineWidth(2)
        line1.SetLineStyle(7)
        line1.Draw("SAME")
        line2 = ROOT.TF1("line2","[0]",-1.,self.number+1)
        line2.SetParameter(0,50.)
        line2.SetLineColor(2)
        line2.SetLineWidth(2)
        line2.SetLineStyle(7)
        line2.Draw("SAME")

        self.p2.cd()
        self.hist_minimal_signals_HG.Draw("")
        for tgraph in [self.tgraph_hg,self.tgraph_hg_bad]:
            if tgraph.GetN() > 0:
                tgraph.Draw("Psame")
        line3 = ROOT.TF1("line3","[0]",-1.,self.number+1)
        line3.SetParameter(0,8.)
        line3.SetLineColor(2)
        line3.SetLineWidth(2)
        line3.SetLineStyle(7)
        line3.Draw("SAME")
        line4 = ROOT.TF1("line4","[0]",-1.,self.number+1)
        line4.SetParameter(0,50./800.*12.)
        line4.SetLineColor(2)
        line4.SetLineWidth(2)
        line4.SetLineStyle(7)
        line4.Draw("SAME")

        # hack
        self.c1.SetLeftMargin(0.14)
        self.c1.SetRightMargin(0.14)
        self.c1.Modified()
        self.c1.Update()

        self.plot_name = "highest_%i_laser_signals_%s"%(self.number,self.PMTool.get_partition_name(self.part-1))
        self.c1.Print("%s/%s.eps" % (self.dir, self.plot_name))

        self.hist_minimal_signals_LG.Delete()
        self.hist_minimal_signals_HG.Delete()
