############################################################
#
# do_global_plot.py
#
############################################################
#
# Author: Henric, based on work by Seb Viret
#
# November 10, 2011
#
# Goal:
# Compute an history plot for the global variation
#
# Input parameters are:
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
import time

class do_global_plot(GenericWorker):
    "Compute history plot of global correction"

    c1 = None

    def __init__(self, runType='Las', limit=3, doEps = False):
        self.runType  = runType
        self.doEps    = doEps
        self.limit    = limit
        self.events    = set()
        self.run_list  = []
        self.part_list = set()
        self.PMTool    = LaserTools()


        self.time_max  = 0
        self.time_min  = 10000000000000000

        self.outputTag = outputTag # global variable to tag output histogram file name
        self.dir    = getPlotDirectory(subdir=self.outputTag)

        try:
            self.HistFile.cd()
        except:
            self.initHistFile("Tucs.HIST{}.root".format(self.outputTag))
        self.HistFile.cd()

        if ROOT.gDirectory.FindObject("Laser")==None:
            ROOT.gDirectory.mkdir("Laser")

        ROOT.gDirectory.cd("Laser")
        
        self.max_var = 0

        if self.c1==None:
            self.c1 = src.MakeCanvas.MakeCanvas()
            self.c1.SetTitle("Global plots")

    #
    # Here we collect all the relevant information
    #
    def ProcessStart(self):
        global run_list
        for run in run_list.getRunsOfType('Las'):
            if 'part_var' in run.data:

                time = run.time_in_seconds
                if self.time_min > time:
                    self.time_min = time

                if self.time_max < time:
                    self.time_max = time

                if self.max_var<math.fabs(100*(run.data['part_var']-1)):
                    self.max_var = math.fabs(100*(run.data['part_var']-1))

                if 'wheelpos' in run.data:
                    self.run_list.append(run)
    #
    # Make sure people at least implement this
    #
    def ProcessRegion(self, region):
        return region


    #
    # Plot function to be used later
    #
    def plot(self, part=''):

        ROOT.gStyle.SetOptTitle(0)
        ROOT.gStyle.SetTimeOffset(0)

        ROOT.gStyle.SetOptStat(0)
        ROOT.gStyle.SetStatX(0.78)
        ROOT.gStyle.SetStatY(0.83)
        ROOT.gStyle.SetEndErrorSize(0.)

        self.c1.SetFrameFillColor(0)
        self.c1.SetFillColor(0);
        self.c1.SetBorderMode(0);
        self.c1.SetGridx(1);
        self.c1.SetGridy(1);
        # hack
#        self.c1.SetLeftMargin(0.14)
#        self.c1.SetRightMargin(0.14)

        


        part_suffix = '' if part=='' else '_'+part

        # Then we do the graphs for all the partitions
        graph_lim = max(1.1*self.max_var,self.limit)

        self.plot_name = "global_history"


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

        pad = self.c1.cd()
#        self.frame = ROOT.TH2F('Cadre', '   ',\
#                               100, self.time_min-43200, self.time_max+43200,
#                               100, -graph_lim, graph_lim)

        self.frame = pad.DrawFrame(cadre_xmin, -graph_lim, cadre_xmax,
                                   graph_lim, 'Cadre')
        
        self.frame.GetXaxis().SetTimeDisplay(1)
        self.frame.GetYaxis().SetTitleOffset(1.)
        self.frame.GetXaxis().SetLabelOffset(0.03)
        self.frame.GetYaxis().SetLabelOffset(0.01)
        self.frame.GetXaxis().SetLabelSize(0.015)
        self.frame.GetYaxis().SetLabelSize(0.04)
        self.frame.GetXaxis().SetTimeFormat("#splitline{%Y}{%d/%m}")
        self.frame.GetXaxis().SetNdivisions(ndiv)
        self.frame.SetMarkerStyle(20)


        title = "global evolution [%]" 
        if "side" in part:
            title = "global evolution " + part.split('part')[1] + " side [%]"
        elif part!="":
            title = "global evolution " + part + " [%]"
        self.frame.GetYaxis().SetTitle(title)


#        self.c1.cd()
#        self.frame.Draw()

        self.tgraph_lg.SetMarkerStyle(29)
        self.tgraph_lg.SetMarkerColor(8)
        self.tgraph_hg.SetMarkerStyle(30)
        self.tgraph_hg.SetMarkerColor(4)
        self.tgraph_pisa.SetLineColor(6)

        legend1 = ROOT.TLegend(0.17,0.20,0.50,0.35)
        legend1.SetFillColorAlpha(0,0.)
        if self.tgraph_lg.GetN() != 0:
            legend1.AddEntry(self.tgraph_lg,"Low gain (filter 6)","p")
        if self.tgraph_hg.GetN() != 0:
            legend1.AddEntry(self.tgraph_hg,"High gain (filter 8)","p")
        if self.tgraph_pisa.GetN()!=0:
            legend1.AddEntry(self.tgraph_pisa,"statistical correction","l")
        legend1.Draw()


        self.tgraph_lg.Draw("P,same")
        self.tgraph_hg.Draw("P,same")
        if self.tgraph_pisa.GetN():
            self.tgraph_pisa.Draw("L,same")

        l = ROOT.TLatex()
        l.SetNDC();
        l.SetTextFont(72);
        l.DrawLatex(0.1922,0.867,"ATLAS");

        l2 = ROOT.TLatex()
        l2.SetNDC();
        l2.DrawLatex(0.1922,0.811,"Internal");

        self.c1.Modified()
        self.c1.Update()

        if self.doEps:
            ROOT.gStyle.SetPaperSize(20,26)
            self.c1.Print("%s/%s.pdf" % (self.dir,self.plot_name+part_suffix))
        else:
            self.c1.Print("%s/%s.png" % (self.dir,self.plot_name+part_suffix))
        self.c1.Print("%s/%s.root" % (self.dir,self.plot_name+part_suffix))

        self.HistFile.cd("Laser")
        
        self.tgraph_lg.SetName("Global_correction_low_gain"+part_suffix)
        self.tgraph_lg.Write()
        self.tgraph_hg.SetName("Global_correction_high_gain"+part_suffix)
        self.tgraph_hg.Write()
        if self.tgraph_pisa.GetN()!=0:
            self.tgraph_pisa.SetName("Gain_evolution_stable_cells")
            self.tgraph_pisa.Write()        



    #
    # At the end we produce the plots
    #
    def ProcessStop(self):
        self.run_list = sorted(self.run_list, key=lambda run: run.runNumber)
        
        if not self.run_list:
            return


        self.tgraph_hg = ROOT.TGraphErrors()
        self.tgraph_lg = ROOT.TGraphErrors()
        self.tgraph_pisa = ROOT.TGraph()

#        # Inclusive and split per side
#        part_list = ['','partA','partC']

        # Inclusive, split per side and per EB/LB
        part_list = ['','partA','partC','EB','LB']

        for _part in part_list:

            partvar = 'part_var'
            partvarerr = 'part_var_err'
           
            if _part !='':
                partvar = 'part_var_'+_part
                partvarerr = 'part_var_err_'+_part

            self.tgraph_lg.Set(0)
            self.tgraph_hg.Set(0)
            self.tgraph_pisa.Set(0)
 
            for run in self.run_list:

                if not partvar in run.data: continue

                if run.data['wheelpos'] == 6:
                    tgraph = self.tgraph_lg
                if run.data['wheelpos'] == 8:
                    tgraph = self.tgraph_hg
                n = tgraph.GetN()
                tgraph.SetPoint( n, run.time_in_seconds, 100*(run.data[partvar]-1) )                
                tgraph.SetPointError(n,0.,100*run.data[partvarerr])

                if 'part_var_pisa' in run.data:
                    tgraph = self.tgraph_pisa
                    n = tgraph.GetN()
                    tgraph.SetPoint( n, run.time_in_seconds, 100*(run.data['part_var_pisa']-1) )

            if tgraph.GetN() > 0:
                self.plot(part=_part)

        self.c1.Close()
