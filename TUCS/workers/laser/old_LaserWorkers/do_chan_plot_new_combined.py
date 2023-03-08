############################################################
#
# do_chan_plot_new.py
#
############################################################
#
# Author: Henric
#
# June 2nd 2017
#
# Goal: Do a plot for one given channel. This plot could be 
#       an history DQ plot, but also a linearity plot.
#       By default, .png and .C files are produced
#
# Input parameters are:
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

class do_chan_plot_new_combined(GenericWorker):
    
    "Produce nice laser history plot for a channel"

    c1 = None

    def __init__(self, runType='Las', limit=1, doEps = False):
        self.runType  = runType
        self.doEps    = doEps
        self.limit    = limit        

        self.outputTag = outputTag # global variable to tag output histogram file name
        self.dir    = getPlotDirectory(subdir=self.outputTag)

        self.origin   = ROOT.TDatime()
        self.PMTool   = LaserTools()

        self.LG_evts  = set() # Events with low gain info
        self.HG_evts  = set() # Events with high gain info

        self.time_max = 0
        self.time_min = 10000000000000000

        if self.c1==None:
            self.c1 = src.MakeCanvas.MakeCanvas()


    def ProcessStart(self):
        
        global run_list
        for run in run_list.getRunsOfType('Las'):
            time = run.time_in_seconds
            if self.time_min > time:
                self.time_min = time
                self.origin = ROOT.TDatime(run.time)
                
            if self.time_max < time:
                self.time_max = time

        self.c1.Clear()
        self.c1.cd()
        self.c1.Divide(1,2)
    
        self.c1.SetFrameFillColor(0)
        self.c1.SetFillColor(0);
        self.c1.SetBorderMode(0);
        self.c1.SetGridx(1);
        self.c1.SetGridy(1);
        
        ROOT.gStyle.SetOptStat(0)
        ROOT.gStyle.SetStatX(0.78)
        ROOT.gStyle.SetStatY(0.83)
        
        ROOT.gStyle.SetOptTitle(1)
        ROOT.gStyle.SetTitleX(0.15)
        ROOT.gStyle.SetTitleW(0.2)
        ROOT.gStyle.SetTitleBorderSize(0)                                         
        ROOT.gStyle.SetTitleFontSize(0.1)
        ROOT.gStyle.SetEndErrorSize(0.)

        try:
            self.HistFile.cd()
        except:
            self.initHistFile("output/Tucs.Time.root")
        self.HistFile.cd()
        ROOT.gDirectory.mkdir("Laser")
        ROOT.gDirectory.cd("Laser")
        

    def ProcessRegion(self, region):
                          
        # First retrieve all the relevant partition infos

        if 'doChanPlot' not in region.data:
            return

        self.LG_evts = []
        self.HG_evts = []
        
        [part, module, pmt] = region.GetNumber(1)
        self.fibre = self.PMTool.get_fiber_index(part-1,module-1,pmt)

        self.beta = 6.9                 
        if 'beta' in region.data:
            if region.data['beta']>5:
                self.beta = region.data['beta']
                
        
        for chan_region in region.GetChildren('readout'):
            [part_num, mod, chan, gain] = chan_region.GetNumber()
                
            for event in chan_region.GetEvents():
                if event.run.runType!='Las':
                    continue
                    
                if gain==0:
                    self.LG_evts.append(event)

                if gain==1:
                    self.HG_evts.append(event)

        if len(self.LG_evts + self.HG_evts)!=0:

            part_names = ['LBA','LBC','EBA','EBC']
            
            self.histtitle =  "%s%02d_pmt%02d" % (part_names[part-1],module,pmt)
            self.plot_name = "channel_%s_history"%(self.histtitle)
            self.plot_name = self.plot_name.replace(' ','_')
            
            self.histtitle = "%s %s" % ( self.histtitle, event.region.GetCellName())
            
            self.PlotRegion()

            
    def ProcessStop(self):
#        self.c1.Close()
#        ROOT.gSystem.ProcessEvents()
        pass
    
                    
    def PlotRegion(self):
        # Then we do the graphs
        max_var = 0 # The maximum variation, in % (gain or normalized residuals)


        
        for event in self.LG_evts:
            if 'deviation' in event.data and event.data['number_entries']>100:
                if max_var<math.fabs(event.data['deviation']) and event.data['deviation']>-99.:
                    max_var = math.fabs(event.data['deviation'])
                
        for event in self.HG_evts:
            if 'deviation' in event.data and event.data['number_entries']>100:
                if max_var<math.fabs(event.data['deviation']) and event.data['deviation']>-99.:
                    max_var = math.fabs(event.data['deviation'])
                  
        graph_lim = max(1.2*max_var,5*self.limit)
        
        # Cosmetics (Part 1): the lines which show the maximum acceptable variation
            
        self.line_down = ROOT.TLine(0,-self.limit,self.time_max-self.time_min+1,-self.limit)
        self.line_down.SetLineColor(4)
        self.line_down.SetLineWidth(2)
            
        self.line_up = ROOT.TLine(0,self.limit,self.time_max-self.time_min+1,self.limit);
        self.line_up.SetLineColor(4)
        self.line_up.SetLineWidth(2)

        cadre_xmin = 0
        cadre_xmax = self.time_max-self.time_min+1
        cadre_ymin = 0
        cadre_ymax = 1000
        cadre_hl_ratio = 81.84/1.24
            
        self.cadreSignal = ROOT.TH2F('CadreSignal', self.histtitle,\
                                     100, cadre_xmin, cadre_xmax , 100, cadre_ymin, cadre_ymax)
            
        self.cadreDeviation = ROOT.TH2F('CadreDeviation', self.histtitle,\
                                        100, cadre_xmin, cadre_xmax , 100, max(-graph_lim,-100.), graph_lim)
            
#        self.hhist_lg = ROOT.TProfile('Channel_hist_lg', '',\
#                                      100, 0, self.time_max-self.time_min+1,-10000, 10000)

#        self.hhist_hg = ROOT.TProfile('Channel_hist_hg', '',\
#                                      100, 0, self.time_max-self.time_min+1,-10000, 10000)

        self.tgraph_deviation          = [ROOT.TGraphErrors(), ROOT.TGraphErrors()]
        self.tgraph_deviation_bad      = [ROOT.TGraphErrors(), ROOT.TGraphErrors()]
        self.tgraph_deviation_affected = [ROOT.TGraphErrors(), ROOT.TGraphErrors()]

        self.tgraph          = [ROOT.TGraphErrors(), ROOT.TGraphErrors()]
        self.tgraph_bad      = [ROOT.TGraphErrors(), ROOT.TGraphErrors()]
        self.tgraph_affected = [ROOT.TGraphErrors(), ROOT.TGraphErrors()]
        self.tgraph_saturated = [ROOT.TGraphErrors(), ROOT.TGraphErrors()]
        
        self.tgraph_hvabs = ROOT.TGraph()
        self.tgraph_hvcor = ROOT.TGraph()    
        
        self.tgraph_flaser = ROOT.TGraph()
                    
        ROOT.gStyle.SetTimeOffset(self.origin.Convert())
        
        self.cadreSignal.GetXaxis().SetTimeDisplay(1)
        self.cadreSignal.GetYaxis().SetTitleOffset(1.1)
        self.cadreSignal.GetXaxis().SetLabelOffset(0.03)
        self.cadreSignal.GetYaxis().SetLabelOffset(0.01)
        self.cadreSignal.GetXaxis().SetLabelSize(0.04)
        self.cadreSignal.GetYaxis().SetLabelSize(0.04)           
        self.cadreSignal.GetXaxis().SetTimeFormat("#splitline{%Y}{%d/%m}")
        self.cadreSignal.GetXaxis().SetNdivisions(-503)
        # self.cadreSignal.GetYaxis().SetTitle("low gain signal [pC], voltage[V]")
        self.cadreSignal.GetYaxis().SetTitle("low gain signal [pC], voltage[V]")
            
        self.cadreDeviation.GetXaxis().SetTimeDisplay(1)
        self.cadreDeviation.GetYaxis().SetTitleOffset(1.1)
        self.cadreDeviation.GetXaxis().SetLabelOffset(0.03)
        self.cadreDeviation.GetYaxis().SetLabelOffset(0.01)
        self.cadreDeviation.GetXaxis().SetLabelSize(0.04)
        self.cadreDeviation.GetYaxis().SetLabelSize(0.04)           
        self.cadreDeviation.GetXaxis().SetTimeFormat("#splitline{%Y}{%d/%m}")
        self.cadreDeviation.GetXaxis().SetNdivisions(-503)
        self.cadreDeviation.GetYaxis().SetTitle("deviation [%]")

        events = [self.LG_evts, self.HG_evts]
        gains  = ['low', 'high']

        corr = [1.,  cadre_hl_ratio]

        for gain in [0, 1]:
            for event in events[gain]: # fill the histogram
                if event.data['number_entries']==0:
                    continue

                if 'deverr' not in event.data:
                    continue
                
                # print event.run.runNumber, event.region.GetHash(), event.data['status'] 
                if (event.data['status']&0x4) or (event.data['status']&0x10):
                    tgraph = self.tgraph_bad[gain]
                elif event.data['status']&0x100:
                    tgraph = self.tgraph_saturated[gain]
                elif event.data['status']!=0:
                    tgraph = self.tgraph_affected[gain]
                else:
                    tgraph = self.tgraph[gain]
                npoints = tgraph.GetN()
                tgraph.SetPoint(npoints,event.run.time_in_seconds-self.time_min,corr[gain]*event.data['signal'])
                tgraph.SetPointError(npoints,0,event.data['signalerr'])
                
                if (event.data['status']&0x4) or (event.data['status']&0x10):
                    tgraph = self.tgraph_deviation_bad[gain]
                elif (event.data['status']&0x1f)!=0:
                    tgraph = self.tgraph_deviation_affected[gain]
                else:
                    tgraph = self.tgraph_deviation[gain]              
                
                npoints = tgraph.GetN()
                if 'part_var' in event.run.data:    
                    correction1 = event.run.data['part_var']
                else:
                    correction1 = 1

                correction2 = event.run.data['fiber_var'][self.fibre]
                hv = event.data['hv_db']
                if hv<10.:
                    hv=850
                a = event.data['calibration']/event.data['lasref_db']
                # try:
                #     c = correction1*correction2*pow(event.data['HV']/hv,self.beta)
                # except:
                #     c = correction1*correction2
                c = correction1*correction2
                try:
                    x = 100.*(a/c-1.)
                    tgraph.SetPoint(npoints, event.run.time_in_seconds-self.time_min, x)
                    tgraph.SetPointError(npoints, 0, event.data['deverr']*c)
                except:
                    pass

                if ('f_laser' in event.data):
                    npoints = self.tgraph_flaser.GetN()
                    self.tgraph_flaser.SetPoint(npoints, event.run.time_in_seconds-self.time_min, 100.*(event.data['f_laser']-1.))

        self.problemset = set()
        for event in self.HG_evts+self.LG_evts: # fill the histogram
            if 'HV' in event.data:
                npoints = self.tgraph_hvabs.GetN()
                self.tgraph_hvabs.SetPoint(npoints,event.run.time_in_seconds-self.time_min,event.data['HV'])
                hv_db = event.data['hv_db']
                if hv_db<=0.:
                    hv_db = 830

                try:
                    deltagain =  100.*(pow(event.data['HV']/hv_db,self.beta)-1)
                    npoints = self.tgraph_hvcor.GetN()
                    self.tgraph_hvcor.SetPoint(npoints,event.run.time_in_seconds-self.time_min, deltagain)
                except: # division by 0, or negative HV
                    pass

            if 'problems' in event.data:
                for problem in event.data['problems']:
                    self.problemset.add(problem)
        
        self.tgraph_hvabs.Sort()
        self.tgraph_hvcor.Sort()
        
        # Then draw it...
        if len(self.problemset):
            self.c1.cd(0)
            problembox = ROOT.TPaveText(0.15,0.49,.90,0.54,"brNDC")     
            problembox.SetFillColor(623)
            problembox.SetTextSize(0.040/len(self.problemset))
            problembox.SetTextFont(42)
            problembox.SetBorderSize(0)
            for problem in self.problemset:
                problembox.AddText(problem)
            problembox.Draw()

        self.c1.cd(1)
        self.c1.cd(1).SetTicks(0,0)
        self.cadreSignal.Draw()

        ROOT.gStyle.SetHatchesLineWidth(1)
        
        box = ROOT.TBox(cadre_xmin, 0, cadre_xmax , 15)
        box.SetLineWidth(0)
        box.SetFillStyle(3004)       
        box.SetFillColor(2)
        box.Draw()
        
        text = ROOT.TPaveText(cadre_xmin, 1024/1.293190, cadre_xmax ,cadre_ymax,"br")
        text.SetFillColor(2)
        text.SetFillStyle(3004)   
        text.SetTextSize(0.10)
        text.SetTextFont(42)
        text.SetTextColor(2)
        text.SetBorderSize(0)
        text.AddText("HIC SVNT LEONES")
        text.Draw()

        self.c1.cd(1)
        self.tgraph[0].SetMarkerStyle(29)
        self.tgraph_bad[0].SetMarkerStyle(29)
        self.tgraph_bad[0].SetMarkerColor(2)
        self.tgraph_affected[0].SetMarkerStyle(29)
        self.tgraph_affected[0].SetMarkerColor(800)
        self.tgraph_saturated[0].SetMarkerStyle(29)
        self.tgraph_saturated[0].SetMarkerColor(804)
        self.tgraph[1].SetMarkerStyle(30)
        self.tgraph_bad[1].SetMarkerStyle(30)
        self.tgraph_bad[1].SetMarkerColor(2)
        self.tgraph_affected[1].SetMarkerStyle(30)
        self.tgraph_affected[1].SetMarkerColor(800)
        self.tgraph_saturated[1].SetMarkerStyle(30)
        self.tgraph_saturated[1].SetMarkerColor(804)
        self.tgraph_hvabs.SetLineColor(4)
        self.tgraph_hvabs.SetLineWidth(2)
        self.tgraph_hvcor.SetLineColor(4)
        self.tgraph_hvcor.SetLineWidth(2)
        self.tgraph_flaser.SetLineColor(9)

        legend1 = ROOT.TLegend(0.2,0.62,0.41,0.79)
        legend1.AddEntry(self.tgraph[0],"Low gain (filter 6)","p")
        legend1.AddEntry(self.tgraph[1],"high gain (filter 8)","p")
        legend1.AddEntry(self.tgraph_bad[1],"bad/masked status","p")
        legend1.AddEntry(self.tgraph_affected[1],"affected|noisy status","p")
        legend1.AddEntry(self.tgraph_saturated[1],"saturation","p")
        legend1.AddEntry(self.tgraph_hvabs,"HV","L")

        legend1.Draw()
        
        for tgraph in self.tgraph+ self.tgraph_bad + self.tgraph_affected + self.tgraph_saturated:
            if tgraph.GetN()>0:
                tgraph.Draw("P,same")
        if self.tgraph_hvabs.GetN()>0:
            self.tgraph_hvabs.Draw("L,same")
        else:
            "No entries in tgraph_hvabs"

        axis = ROOT.TGaxis(cadre_xmax, cadre_ymin, cadre_xmax, cadre_ymax, cadre_ymin , cadre_ymax/cadre_hl_ratio,506,"+L" )
        axis.SetTitleFont(self.cadreSignal.GetTitleFont())
        axis.SetTitleSize(self.cadreSignal.GetTitleSize())
        axis.SetLabelSize(0.04)
        axis.SetLabelFont(self.cadreSignal.GetLabelFont())
        axis.SetTitle("high gain signal [pC]")
        axis.Draw()


        self.c1.cd(2)
        self.cadreDeviation.Draw()
        
        legend2 = ROOT.TLegend(0.2,0.65,0.41,0.82)
        legend2.AddEntry(self.tgraph_hvcor,"Gain variation computed from HV","L")
#        legend2.AddEntry(self.tgraph_flaser, "flaser", "L")
#        legend2.Draw()

        self.tgraph_deviation[0].SetMarkerStyle(29)
        self.tgraph_deviation_bad[0].SetMarkerStyle(29)
        self.tgraph_deviation_bad[0].SetMarkerColor(2)
        self.tgraph_deviation_affected[0].SetMarkerStyle(29)
        self.tgraph_deviation_affected[0].SetMarkerColor(800)

        self.tgraph_deviation[1].SetMarkerStyle(30)
        self.tgraph_deviation_bad[1].SetMarkerStyle(30)
        self.tgraph_deviation_bad[1].SetMarkerColor(2)
        self.tgraph_deviation_affected[1].SetMarkerStyle(30)
        self.tgraph_deviation_affected[1].SetMarkerColor(800)


        for tgraph in self.tgraph_deviation + self.tgraph_deviation_bad + self.tgraph_deviation_affected:
            if tgraph.GetN()>0:
                tgraph.Draw("P,same")
        if self.tgraph_hvcor.GetN()>0:
            self.tgraph_hvcor.Sort()
            self.tgraph_hvcor.Draw("L,same")
        else:
            "No entries in tgraph_hvcor"

#        if self.tgraph_flaser.GetN()>0:
#            self.tgraph_flaser.Sort()
#            self.tgraph_flaser.Draw("L,same")
#        else:
#            "No entries in tgraph_flaser"


        self.c1.cd()

        self.c1.Modified()
        self.c1.Update()

        if self.doEps:
            ROOT.gStyle.SetPaperSize(26,20)
            self.c1.Print("%s/%s.eps" % (self.dir, self.plot_name))
        else:
            self.c1.Print("%s/%s.png" % (self.dir,self.plot_name))
            self.c1.Print("%s/%s.C" % (self.dir,self.plot_name))    


        self.HistFile.cd("Laser")
        ROOT.gDirectory.mkdir("HVcorr_%s"%self.plot_name)
        ROOT.gDirectory.cd("HVcorr_%s"%self.plot_name)
        if self.tgraph_hvcor.GetN():
            self.tgraph_hvcor.Write()

        self.cadreSignal.Delete()
        self.cadreDeviation.Delete()

        for tgraph in self.tgraph + self.tgraph_bad + self.tgraph_affected + \
                self.tgraph_deviation + self.tgraph_deviation_bad + self.tgraph_deviation_affected + \
                self.tgraph_saturated + \
                [ self.tgraph_hvabs, self.tgraph_hvcor ]:
            tgraph.Delete()



    
