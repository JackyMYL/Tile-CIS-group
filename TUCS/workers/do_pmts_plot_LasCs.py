############################################################
#
# do_pmts_plot_LasCs.py
#
############################################################
#
# Author: Henric, using Sebs stuff
#
# January, 2013
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
##
# For more info on the LASER system : http://atlas-tile-laser.web.cern.ch
#
#############################################################

from src.GenericWorker import *
import src.oscalls
import os.path
import ROOT
import math
import time

class do_pmts_plot_LasCs(GenericWorker):
    "Compute history plot for the pmts of a drawer NEW"


    def __init__(self, part=0, module=0, limit=2, doEps = False, ymin=-20., ymax=+15.):

        self.doEps     = doEps
        self.part      = part
        self.module    = module
        self.limit     = limit

        self.module_list = []

        self.ymin = ymin
        self.ymax = ymax

        for i in range(256):
            self.module_list.append([])            

        self.PMTool   = LaserTools()
        self.origin   = ROOT.TDatime()
        self.time_max = 0
        self.time_min = 10000000000000000

        self.dir      =  os.path.join(src.oscalls.getPlotDirectory(),'LaserCesium')
        src.oscalls.createDir(self.dir)

        self.problemtxt = set()
        self.part_name = ["LBA", "LBC", "EBA", "EBC"]

        self.rosset = set()

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
        return
####
#
## Makes lists of events per drawer
#
####
    def ProcessRegion(self, region):
        numbers = region.GetNumber(1)
        if len(numbers)==4:
            [part, module, pmt, gain] = numbers
        elif len(numbers)==3:
            [part, module, pmt] = numbers
            name = self.PMTool.getCellName(part-1,module,pmt)
            if name in ['E3','E4', 'MBTS']:
                return
        else:
            return 

        for event in region.GetEvents():
            if event.run.runType=='Las':
                if 'status' not in event.data:
                    continue
            elif event.run.runType=='cesium':
                pass
            else:
                continue

            if self.part != 0 and part != self.part: # if you just want one part
                continue

            if self.module != 0 and module != self.module: 
                continue

            

            self.rosset.add(part-1)
                
            index = 64*(part-1) + (module-1)
            self.module_list[index].append(event)
        return
####
#
## Goes over the lists of events per module to make plots
#
####
    def ProcessStop(self):

        self.PrepareCanvas()
                
        for ros in self.rosset:
            
            for i_drawer in range(64):
            
                if self.module != 0 and i_drawer != self.module-1:
                    continue
                                
                module_events = self.module_list[64*ros+i_drawer]                
                if len(module_events)==0:
                    continue
                                                  
                # Clear pmt list for this module
                pmt_list = []
                for i in range(48):                    
                    pmt_list.append([])
                    
                for event in module_events:
                    if event.run.runType=='Las':
                        [part, module, pmt, gain] = event.region.GetNumber(1)

                    if event.run.runType=='cesium':
                        [part, module, pmt] = event.region.GetNumber(1)
                                       
                    pmt_list[pmt-1].append(event)

                for i_pmt in range(48):
                    # Empty the TGraphs
                    for tgraph in [ self.tgraphhv[i_pmt],
                                    self.tgraphhigh[i_pmt], self.tgraphlow[i_pmt],
                                    self.tgraphaffected[i_pmt], self.tgraphbad[i_pmt],
                                    self.tgraph_cs[i_pmt] ]:
                        tgraph.Set(0)
                    
                    pmt_events   = pmt_list[i_pmt]
                    max_var      = 0
                    
                    for event in pmt_events:                    
                        if 'deviation' in event.data:
                            if max_var<math.fabs(event.data['deviation']):
                                max_var = math.fabs(event.data['deviation'])

                    # Then we do the different channel classification

                    self.problemtxt.clear()

                    name = self.PMTool.getCellName(ros,i_drawer+1,i_pmt+1)
                    
                    for event in pmt_events: # fill the histogram
                        x = event.run.time_in_seconds-self.time_min

                        deltagain = 0.
                        if 'HV' in event.data and 'hv_db' in event.data:
                            if event.data['HV']>0 and event.data['hv_db']>0:
                                npoints = self.tgraphhv[i_pmt].GetN()

                                beta = 6.9
                                if 'beta' in event.region.GetParent().data:
                                    beta = event.region.GetParent().data['beta']
                                
                                deltagain =  100.*( pow(event.data['HV']/event.data['hv_db'], beta) - 1)                    
                                self.tgraphhv[i_pmt].SetPoint(npoints,x,deltagain)
                                
                        if 'deviation' in event.data:
                            y = event.data['deviation']
                            ey = event.data['deverr']
                            if event.data['status']&0x4 or event.data['status']&0x10 or math.fabs(deltagain)>10.:
                                tgraph = self.tgraphbad[i_pmt]
                            elif event.data['status']!=0:
                                tgraph = self.tgraphaffected[i_pmt]
                            else:
                                if 'igh' in event.region.GetHash():
                                    tgraph = self.tgraphhigh[i_pmt]
                                else:
                                    tgraph = self.tgraphlow[i_pmt]
                                
                            n = tgraph.GetN()
                            tgraph.SetPoint(n, x, min(max(y,.95*self.ymin),.95*self.ymax))
                            tgraph.SetPointError(n, 0., ey)

                        if 'problems' in event.data:
                                for problem in event.data['problems']:
                                    self.problemtxt.add(problem)

                        if event.run.runType=='cesium':
                            n = self.tgraph_cs[i_pmt].GetN()
                            if isinstance(event.data['calibration'], float):
                                value = event.data['calibration']/(event.data['f_integrator_db'])
                            else:
                                value = 0.

                            if name in ['E1','E2','C10']:  # This can be removed when we know how to read in Smita's files.
                                value = event.data['f_cesium_db']

                            self.tgraph_cs[i_pmt].SetPoint(n, x, 100.*(value-1.))

                        self.problembox[i_pmt].Clear()
                        for problem in self.problemtxt:
                            self.problembox[i_pmt].AddText(problem)
                            

                self.PreparePmtPads(ros, i_drawer)

        while len(self.hhist):
            self.hhist.pop().Delete()
 
        for textbox in self.problembox:
            textbox.Delete()
        self.problembox = []


    def PrepareCanvas(self):
        #
        ROOT.gStyle.SetTimeOffset(self.origin.Convert())
        ROOT.gStyle.SetOptTitle(1)
        ROOT.gStyle.SetTitleX(0.16)
        ROOT.gStyle.SetTitleW(0.2)  
        ROOT.gStyle.SetTitleBorderSize(0)                                          
        ROOT.gStyle.SetTitleFontSize(0.1)
        ROOT.gStyle.SetTitleOffset(0.1)          
        ROOT.gStyle.SetPaperSize(30,39)
        #
        ROOT.gStyle.SetOptStat(0)
        ROOT.gStyle.SetStatX(0.78)
        ROOT.gStyle.SetStatY(0.83)
        ROOT.gStyle.SetEndErrorSize(0.)
        #
        self.hhist  = []
        self.tgraphhigh = []
        self.tgraphlow = []
        self.tgraphbad = []
        self.tgraphaffected = []
        self.tgraphhv = []
        self.tgraph_cs = []
        self.problembox = []

        #
        c_w = int(1100*2.5)
        c_h = int(900*2.5)

        self.c1 = ROOT.TCanvas("c1","a canvas",c_w,c_h)
        self.c1.SetWindowSize(2*c_w - self.c1.GetWw(), 2*c_h - self.c1.GetWh())
        
        self.c1.Range(0,0,1,1)
        self.c1.SetFillColor(0)
        self.c1.SetBorderMode(0)
        self.c1.cd()
        self.c1.Divide(6,8,0.001,0.001)
        self.c1.Modified()
        self.c1.Update()

        for i_pmt in range(48):
            # histname = 'pmt_%0d' % (i_pmt+1)
            histtitle = 'We will set it later'
            tpad = self.c1.cd(i_pmt+1)
            
            # hist = ROOT.TProfile(histname, histtitle, 100, -43200, self.time_max-self.time_min+43200, self.ymin, self.ymax)
            
            #self.hhist[i_pmt].SetMinimum(self.ymin)
            #self.hhist[i_pmt].SetMaximum(self.ymax)

            self.problembox.append(ROOT.TPaveText(0.30,0.9,0.95,1.,"brNDC"))
            self.problembox[i_pmt].SetFillColor(623)
            self.problembox[i_pmt].SetTextSize(0.07)
            self.problembox[i_pmt].SetTextFont(42)
            self.problembox[i_pmt].SetBorderSize(0)

            self.tgraphhigh.append(ROOT.TGraphErrors())
            self.tgraphhigh[i_pmt].SetMarkerColor(4)
            self.tgraphhigh[i_pmt].SetLineColor(4)
            self.tgraphhigh[i_pmt].SetMarkerStyle(7)
            self.tgraphhigh[i_pmt].SetMarkerSize(2.);
            
            self.tgraphlow.append(ROOT.TGraphErrors())
            self.tgraphlow[i_pmt].SetMarkerColor(8)
            self.tgraphlow[i_pmt].SetLineColor(8)
            self.tgraphlow[i_pmt].SetMarkerStyle(7)
            self.tgraphlow[i_pmt].SetMarkerSize(2.);
            
            self.tgraphbad.append(ROOT.TGraphErrors())
            self.tgraphbad[i_pmt].SetMarkerColor(46)
            self.tgraphbad[i_pmt].SetLineColor(46)
            self.tgraphbad[i_pmt].SetMarkerStyle(7)
            self.tgraphbad[i_pmt].SetMarkerSize(2.);
                    
            self.tgraphaffected.append(ROOT.TGraphErrors())
            self.tgraphaffected[i_pmt].SetMarkerColor(801)
            self.tgraphaffected[i_pmt].SetLineColor(801)
            self.tgraphaffected[i_pmt].SetMarkerStyle(7)
            self.tgraphaffected[i_pmt].SetMarkerSize(2.);

            self.tgraphhv.append(ROOT.TGraph())
            self.tgraphhv[i_pmt].SetLineColor(4)

            self.tgraph_cs.append(ROOT.TGraph())
            self.tgraph_cs[i_pmt].SetMarkerStyle(31)
            self.tgraph_cs[i_pmt].SetMarkerColor(2)
        #
        self.x = 0.20
        self.y = 0.34
        self.LatexFontSize=0.05
        
        self.l1 = ROOT.TLatex()
        self.l1.SetNDC()

        y = self.y-0.01
        self.legend = ROOT.TLegend(self.x,y-1.2*self.LatexFontSize,self.x+.15,y)
        self.legend.AddEntry(self.tgraphhv[0],"High voltage ","L")
        self.legend.AddEntry(self.tgraphhigh[0],"High Gain","P")
        self.legend.AddEntry(self.tgraphlow[0], "Low Gain", "P")
        self.legend.AddEntry(self.tgraphbad[0],"Bad status","P")
        self.legend.AddEntry(self.tgraphaffected[0], "Affected|Noisy status", "P")
        self.legend.AddEntry(self.tgraph_cs[0], "Cesim", "P")
        return 


    def PreparePmtPads(self, ros, i_drawer):

        self.c1.cd()        
        if (self.PMTool.getNewLVPS(ros+1, i_drawer+1)):
            self.c1.SetFillColor(88)
        else:
            self.c1.SetFillColor(0)

        l1 = self.l1.DrawLatex(self.x,self.y,'%s%02d' % (self.part_name[ros],(i_drawer+1)))
        self.legend.Draw()

        for i_pmt in range(48):
            pad = self.c1.cd(i_pmt+1)
            pad.Clear()                    

            pad.SetFrameFillColor(0)      
            pad.SetLeftMargin(0.17);
            pad.SetRightMargin(0.07);
            pad.SetTopMargin(0.02);
            pad.SetBottomMargin(0.20);
                    
            if self.PMTool.is_instrumented(ros,i_drawer,i_pmt+1):
                hist = pad.DrawFrame(-43200, self.ymin,self.time_max-self.time_min+43200 , self.ymax)
                
                histtitle = "PMT %d %s" % (i_pmt+1, self.PMTool.getCellName(ros,i_drawer+1,i_pmt+1) )

                hist.SetTitle(histtitle)

                hist.GetXaxis().SetTimeDisplay(1)
                hist.GetXaxis().SetTimeFormat("%d/%m")
                hist.GetXaxis().SetNdivisions(-503)

                hist.GetXaxis().SetLabelOffset(0.1)
                hist.GetXaxis().SetLabelFont(42)
                hist.GetXaxis().SetLabelSize(0.1)
                
                hist.GetYaxis().SetLabelFont(42)
                hist.GetYaxis().SetLabelSize(0.1)
                hist.GetYaxis().SetTitleFont(42)
                hist.GetYaxis().SetTitleSize(0.1)
                hist.GetYaxis().SetTitleOffset(0.7)
            
                if ( i_pmt%6 == 0 ): 
                    hist.GetYaxis().SetTitle("PMT evolution [%]")
                    hist.SetMarkerStyle(20)
                    hist.SetMarkerSize(.6);
                
                #self.line_up.Draw("same")
                #self.line_down.Draw("same")


                if self.tgraph_cs[i_pmt].GetN()>1:
                    self.tgraph_cs[i_pmt].Sort()
                    Y = self.tgraph_cs[i_pmt].GetY()
                    Y0 = Y[0]
                    for i in range(self.tgraph_cs[i_pmt].GetN()):
                        Y[i]=Y[i]-Y0

                    
                option = 'L,same'
                for tgraph in [ self.tgraphhv[i_pmt], self.tgraphaffected[i_pmt], self.tgraphbad[i_pmt],
                                self.tgraphhigh[i_pmt], self.tgraphlow[i_pmt], self.tgraph_cs[i_pmt]]:
                    # for tgraph in [self.tgraphhv[i_pmt],self.tgraphhigh[i_pmt],self.tgraphlow[i_pmt],self.tgraph_cs[i_pmt]]:
                    if tgraph.GetN()>1:
                        tgraph.Sort()
                        tgraph.Draw(option)
                    option = 'P,same'
                        
                if self.problembox[i_pmt].GetSize():
                    self.problembox[i_pmt].Draw()

                self.c1.cd(i_pmt+1).Update()

        self.c1.Modified()
        self.c1.Update()

        self.plot_name = "%s_LasCs_history" % (self.PMTool.get_module_name(ros,i_drawer))
        self.c1.Print("%s/%s.eps" % (self.dir,self.plot_name))
        l1.Delete()
        return
# The End
