############################################################
#
# do_LasCs_plots.py
#
############################################################
#
# Author: Henric
#
# Input parameters are:
# Even though its not FORTRAN, its good to be able to print....
#        1         2         3         4         5         6         7         8 
#2345678901234567890123456789012345678901234567890123456789012345678901234567890
#
###########################################################

from src.GenericWorker import *
import src.MakeCanvas
from src.laser.toolbox import *
import src.oscalls
import os.path
import ROOT
import time

class do_LasCs_plots(GenericWorker):
    "Compute history plot Las&Cs"
    c1 = None
    
    def __init__(self, part=1, mod=1, chan=0, doEps = False, verbose=False):
        self.verbose = verbose

        self.doEps    = doEps
        self.PMTool   = LaserTools()
        self.index    = self.PMTool.get_index(part-1,mod-1,chan,0)
        self.origin   = ROOT.TDatime()

        self.tgraph_las_lg_bad = ROOT.TGraphErrors()
        self.tgraph_las_hg_bad = ROOT.TGraphErrors()
        self.tgraph_las_lg = ROOT.TGraphErrors()
        self.tgraph_las_hg = ROOT.TGraphErrors()
        self.tgraph_cs     = ROOT.TGraph()
        self.tgraph_flasdb = ROOT.TGraph()
        self.tgraph_fcsdb = ROOT.TGraph()
        self.tgraph_hv = ROOT.TGraph()
        
        self.time_max = 0
        self.time_min = 10000000000000000

        self.dir      =  os.path.join(src.oscalls.getPlotDirectory(),'LaserCesium')
        src.oscalls.createDir(self.dir)

        self.problems = set()

        self.cadre_ymin = 0.8
        self.cadre_ymax = 1.1

        if self.c1==None:
            self.c1 = src.MakeCanvas.MakeCanvas()
            self.c1.SetTitle("Laser & Cesium history plots")

        
    def ProcessStart(self):
        global run_list
        for run in run_list.getRunsOfType('Las')+run_list.getRunsOfType('cesium'):
            
            if run.time == None: continue
            
            if run.time_in_seconds < self.time_min:
                self.time_min = run.time_in_seconds
                self.origin = ROOT.TDatime(str(run.time))
                
            if run.time_in_seconds > self.time_max:
                self.time_max = run.time_in_seconds

            
    def ProcessRegion(self, region):
        numbers = region.GetNumber()

        if len(numbers)==4:
            [part, module, channel, gain] = numbers
        elif len(numbers)==3:
            [part, module, channel] = numbers
        else:
            return 



        index = self.PMTool.get_index(part-1, module-1, channel,0)
        if index!=self.index:
            return
        
        for event in region.GetEvents():
            time = event.run.time_in_seconds-self.time_min
            value = 0.
            value_err = -1.
            if event.run.runType=='Las':
                if 'problems' in event.data:
                    self.problems = self.problems.union(event.data['problems'])
                    
                if 'deviation' not in event.data:
                    continue

                if event.data['status']!=0:
                    if gain:
                        tgraph = self.tgraph_las_hg_bad
                    else:
                        tgraph = self.tgraph_las_lg_bad
                else:
                    if gain:
                        tgraph = self.tgraph_las_hg
                    else:
                        tgraph = self.tgraph_las_lg
                    
                value = 1.+event.data['deviation']/100.
                value_err = event.data['deverr']/100.

                beta = 6.9
                if 'beta' in event.region.GetParent().data:
                    beta = event.region.GetParent().data['beta']
                                    
                
                if 'HV' in event.data and 'hv_db' in event.data:
                    if event.data['hv_db']>0 and event.data['HV']>0:
                        npoints = self.tgraph_hv.GetN()
                        self.tgraph_hv.SetPoint(npoints,
                                                time,
                                                pow(event.data['HV']/event.data['hv_db'],beta))

                if 'f_laser_db' in event.data:
                    npoints = self.tgraph_flasdb.GetN()
                    self.tgraph_flasdb.SetPoint( npoints,
                                                 time,
                                                 event.data['f_laser_db'] )

                if 'f_laser_db' in event.data:
                    npoints = self.tgraph_flasdb.GetN()
                    self.tgraph_flasdb.SetPoint( npoints,
                                                 time,
                                                 event.data['f_laser_db'] )

                if 'f_cesium_db' in event.data:
                    npoints = self.tgraph_fcsdb.GetN()
                    self.tgraph_fcsdb.SetPoint( npoints,
                                                 time,
                                                 event.data['f_cesium_db'] )
                    # print event.data['f_cesium_db']

            elif event.run.runType=='cesium' and 'calibration' in event.data:
                tgraph = self.tgraph_cs
                if isinstance(event.data['calibration'], float):
                    value = event.data['calibration']/event.data['f_integrator_db']
                else:
                    value = 0.
                # print "%4.1f" % (100*(value-1.))
                    
            else:
                continue

            value = max(value, self.cadre_ymin)
            value = min(value, self.cadre_ymax)
            
            npoints = tgraph.GetN()
            tgraph.SetPoint(npoints,time,value)
            if value_err!=-1.:
                tgraph.SetPointError(npoints,0,value_err)


    def ProcessStop(self):
        n = 0
        for tgraph in [ self.tgraph_las_hg, self.tgraph_las_hg_bad,
                        self.tgraph_las_lg, self.tgraph_las_lg_bad, self.tgraph_cs ]:
            n += tgraph.GetN()
        if n==0:
            # Then there is nothing to do
            return

        self.c1.cd()
        self.c1.Clear()    

        ROOT.gStyle.SetOptStat(0)
        ROOT.gStyle.SetStatX(0.78)
        ROOT.gStyle.SetStatY(0.83)

        ROOT.gStyle.SetOptTitle(1)
        ROOT.gStyle.SetTitleX(0.15)
        ROOT.gStyle.SetTitleW(0.2)
        ROOT.gStyle.SetTitleBorderSize(0)                                          
        ROOT.gStyle.SetTitleFontSize(0.1)
        ROOT.gStyle.SetEndErrorSize(0.)

        tpad1 = ROOT.TPad("1","plot pad",0.0,0.1,1.0,1.0)
        x =  tpad1.GetBottomMargin()
        tpad1.SetBottomMargin(x/1.8)
        tpad2 = ROOT.TPad("2","info pad",0.0,0.0,1.0,0.1)

        tpad1.Draw()
        tpad2.Draw()
        
        ROOT.gStyle.SetTimeOffset(self.origin.Convert());

        self.tgraph_las_hg_bad.SetMarkerStyle(30)
        self.tgraph_las_lg_bad.SetMarkerStyle(29)
        self.tgraph_las_hg_bad.SetMarkerColor(2)
        self.tgraph_las_lg_bad.SetMarkerColor(2)
        self.tgraph_las_hg.SetMarkerStyle(30)
        self.tgraph_las_lg.SetMarkerStyle(29)
        self.tgraph_cs.SetMarkerStyle(31)
        self.tgraph_flasdb.SetMarkerStyle(32)
        self.tgraph_fcsdb.SetMarkerStyle(33)

        histtitle = self.PMTool.get_pmt_name_index(self.index)
        
        
        
        cadre_xmin = -43200.
        cadre_xmax = self.time_max-self.time_min+43200.

#        cadre = ROOT.TH2F('CadreSignal', histtitle,\
#                          100, cadre_xmin, cadre_xmax,
#                          100, self.cadre_ymin, self.cadre_ymax )

        cadre = tpad1.cd().DrawFrame(cadre_xmin, self.cadre_ymin, cadre_xmax, self.cadre_ymax)
        cadre.SetTitle(histtitle)

        cadre.GetXaxis().SetTimeDisplay(1)
        cadre.GetYaxis().SetTitleOffset(1.1)
        cadre.GetXaxis().SetLabelOffset(0.03)
        cadre.GetYaxis().SetLabelOffset(0.01)
        cadre.GetXaxis().SetLabelSize(0.04)
        cadre.GetYaxis().SetLabelSize(0.04)           
        cadre.GetXaxis().SetTimeFormat("#splitline{%Y}{%d/%m}")
        cadre.GetXaxis().SetNdivisions(-503)
        cadre.GetYaxis().SetTitle("calibration")


        self.tgraph_cs.SetMarkerColor(2)
        self.tgraph_flasdb.SetMarkerColor(3)
        self.tgraph_flasdb.SetLineColor(3)
        self.tgraph_fcsdb.SetMarkerColor(2)
        self.tgraph_fcsdb.SetLineColor(2)
        self.tgraph_hv.SetLineColor(4)
        
        # Draw graphs with lines
        for tgraph in [ self.tgraph_hv, self.tgraph_flasdb,
                        self.tgraph_fcsdb ]:
                        
            if tgraph.GetN()>0:
                tgraph.GetXaxis().SetTimeDisplay(1)
                tgraph.GetXaxis().SetLabelSize(0.04)
                tgraph.GetXaxis().SetTimeFormat("#splitline{%Y}{%d/%m}")
                tgraph.GetXaxis().SetNdivisions(-503)

                tgraph.GetYaxis().SetLabelOffset(0.01)
                tgraph.GetYaxis().SetTitleOffset(1.1)
                tgraph.GetYaxis().SetTitle("calibration")
                tgraph.GetYaxis().SetLabelSize(0.04)  
                tgraph.Sort()
                tgraph.Draw('L,same')
                
        # Draw graphs with markers
        for tgraph in [ self.tgraph_las_hg, self.tgraph_las_hg_bad,
                        self.tgraph_las_lg, self.tgraph_las_lg_bad, self.tgraph_cs ]:
            
            if tgraph.GetN()>0:
                tgraph.GetXaxis().SetTimeDisplay(1)
                tgraph.GetXaxis().SetLabelSize(0.04)
                tgraph.GetXaxis().SetTimeFormat("#splitline{%Y}{%d/%m}")
                tgraph.GetXaxis().SetNdivisions(-503)

                tgraph.GetYaxis().SetLabelOffset(0.01)
                tgraph.GetYaxis().SetTitleOffset(1.1)
                tgraph.GetYaxis().SetTitle("calibration")
                tgraph.GetYaxis().SetLabelSize(0.04)  
                tgraph.Sort()
                tgraph.Draw('P,same')


        tpad2.cd()
        x1 = 0.00
        x2 = 0.50
        y1 = 0.10
        y2 = 1.0

        legend1 = ROOT.TLegend(x2, y1, x2+.5, y2)
        legend1.SetNColumns(2) 
        legend1.AddEntry(self.tgraph_las_lg,"Low gain (filter 6)","p")
        legend1.AddEntry(self.tgraph_las_hg,"high gain (filter 8)","p")
        legend1.AddEntry(self.tgraph_cs,"cesium","p")
        legend1.AddEntry(self.tgraph_flasdb,"laser correction in db","L")
        legend1.AddEntry(self.tgraph_fcsdb,"cesium correction in db","L")
        legend1.AddEntry(self.tgraph_hv,"Gain variation computed from HV","L")
        legend1.Draw()

        
        n = len(self.problems)
        fontsize=0.15
        problembox = ROOT.TPaveText(x1, y1, x2, y2,"brNDC")

        if n!=0:
            tpad2.cd()
#            problembox.SetFillColor(623)
            problembox.SetTextSize(fontsize)
            problembox.SetTextAlign(13)
            problembox.SetTextFont(42)
            problembox.SetBorderSize(0)
            problembox.AddText("Problems known in status folder:")
            for problem in self.problems:
#                problembox.AddText("\t %s"%problem)
                problembox.AddText(" - %s"%problem)

            problembox.SetAllWith(" - ", 'Color', 2)
            problembox.SetTextAlign(13)
            problembox.Draw()
            
        
        self.c1.Modified()
        self.c1.Update()
        plot_name = "channel_%s_LasCs_history" % \
                    (self.PMTool.get_pmt_name_index(self.index).replace(" ","_"))
        self.c1.Print("%s/%s.eps" % (self.dir, plot_name))
        
        problembox.Delete()
        cadre.Delete()
        tpad1.Delete()
        tpad2.Delete()
#        c1.Print("%s/%s.C" % (self.dir, plot_name))
#        c1.Print("%s/%s.png" % (self.dir, plot_name))

