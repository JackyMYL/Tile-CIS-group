###############################################################################
# Author: Andry Kamenshchikov <akamensh@cern.ch>
#
# 23.11.2013
#
# Functionality:
#	Produce cesium time evolution plots.
#
# Options:
#       quality_par - parameter to defind problem type ( 'problem' if |min-max|>=quality_par),
#                                                        'warning' if 0.5*quality_par<|min-max|<quality_par,
#                                                        'good' if |min-max|<=0.5*quality_par)
#       restricted_prod - option to draw only problematic plots one by one with |min-max|>restriction_par
#       restriction_par - parameter for choice of problematic plots
#
###############################################################################

import gc
import math
import ROOT
import time
import src.oscalls
import os.path

from src.GenericWorker import *
from src.run import *

class time_evolution_plots(GenericWorker):
    "Produce cesium time evolution plots"

    def __init__(self, quality_par=0.1, restricted_prod=True, restriction_par=0.04):
        self.PMTool    = LaserTools()
        self.quality_par = quality_par
        self.r_prod = restricted_prod
        self.r_par = restriction_par
        self.frame_color_schema={"good":kGreen-9, "warning":kYellow-9, "problem":kRed-9}

    def ProcessStart(self):
        self.HV_time_evo_plots={}
        self.time_evo_plots={}
        self.time_evo_plots_status={}
    
    def ProcessRegion(self, region):
        if (region.GetEvents() and len(region.GetNumber(1))==3):
            [part, module, pmt] = region.GetNumber(1)
            partname=self.PMTool.get_partition_name(part-1)
            graph_name="%s_m%02d_pmt%02d" % (partname,module,pmt)
            time_list=[]
            data_list=[]
            HV_time_list=[]
            HV_data_list=[]
            for event in region.GetEvents():
                if ('calibration' in event.data and 'csRun_time' in event.data):
                    current_time=event.data['csRun_time']
                    current_data=event.data['calibration']
                    if (isinstance(current_data,float)):
                        time_list.append(current_time)
                        data_list.append(current_data)
                if ('HV' in event.data and 'csRun_time' in event.data):
                    current_HV_time=event.data['csRun_time']
                    current_HV_data=event.data['HV']
                    if (isinstance(current_HV_data,float)):
                        HV_time_list.append(current_HV_time)
                        HV_data_list.append(current_HV_data)
            if (time_list and data_list):
                mintime = sorted(time_list)[0]
                maxtime = sorted(time_list)[len(time_list)-1]
                mindata = sorted(data_list)[0]
                maxdata = sorted(data_list)[len(data_list)-1]                
                T0=ROOT.TDatime(mintime.year,mintime.month,mintime.day,mintime.hour,mintime.minute,mintime.second)
                X0=T0.Convert()
                ROOT.gStyle.SetTimeOffset(X0)
                T1=ROOT.TDatime(mintime.year,mintime.month,mintime.day,mintime.hour,mintime.minute,mintime.second)
                X1=T1.Convert()-X0
                T2=ROOT.TDatime(maxtime.year,maxtime.month,maxtime.day,maxtime.hour,maxtime.minute,maxtime.second)
                X2=T2.Convert()-X0
                self.time_evo_plots[graph_name]=[ROOT.TGraph(),"good"]
                for i in range(len(time_list)):
                    cur_time=time_list[i]
                    cur_data=data_list[i]
                    Tcurr=ROOT.TDatime(cur_time.year,cur_time.month,cur_time.day,cur_time.hour,cur_time.minute,cur_time.second)
                    Xcurr=Tcurr.Convert()-X0
                    npoints = self.time_evo_plots[graph_name][0].GetN()
                    self.time_evo_plots[graph_name][0].SetPoint(npoints,Xcurr,cur_data)                
                self.time_evo_plots[graph_name][0].SetMarkerColor(2)
                self.time_evo_plots[graph_name][0].SetMarkerSize (0.2)
                self.time_evo_plots[graph_name][0].Sort()
                deltaY_prev=math.fabs(mindata-maxdata)
                deltaX=math.fabs(0.1*(X1-X2)) if X1!=X2 else math.fabs(0.1*X0)
                deltaY=math.fabs(0.1*(mindata-maxdata)) if mindata!=maxdata else math.fabs(0.1*mindata)
                self.time_evo_plots[graph_name][0].GetXaxis().SetLimits(X1-deltaX,X2+deltaX)
                if (deltaY_prev<self.quality_par):
                    self.time_evo_plots[graph_name][0].SetMaximum((maxdata+mindata)/2.+self.quality_par*0.6)
                    self.time_evo_plots[graph_name][0].SetMinimum((maxdata+mindata)/2.-self.quality_par*0.6)
                    if (deltaY_prev>self.quality_par*0.5):
                        self.time_evo_plots[graph_name][1]="warning"                        
                else:
                    self.time_evo_plots[graph_name][0].SetMaximum(maxdata+deltaY)
                    self.time_evo_plots[graph_name][0].SetMinimum(mindata-deltaY)
                    self.time_evo_plots[graph_name][1]="problem"
                if (self.r_prod) and (deltaY_prev>self.r_par):
                        self.time_evo_plots[graph_name].append(deltaY_prev)

            if (HV_time_list and HV_data_list and data_list and time_list):
                mintimeHV = sorted(HV_time_list)[0]
                maxtimeHV = sorted(HV_time_list)[len(HV_time_list)-1]
                ref_data=0
                reference=0
                for HVtime in sorted(HV_time_list):
                    if HVtime not in time_list:
                        continue                   
                    ref_cand_index=HV_time_list.index(HVtime)
                    if HV_data_list[ref_cand_index]:                        
                        ref_data=HV_data_list[ref_cand_index]
                        reference=data_list[time_list.index(HVtime)]
                        break
                if (not ref_data) or (not reference):
                    return                
                T0=ROOT.TDatime(mintimeHV.year,mintimeHV.month,mintimeHV.day,mintimeHV.hour,mintimeHV.minute,mintimeHV.second)
                X0=T0.Convert()
                ROOT.gStyle.SetTimeOffset(X0)
                T1=ROOT.TDatime(mintimeHV.year,mintimeHV.month,mintimeHV.day,mintimeHV.hour,mintimeHV.minute,mintimeHV.second)
                X1=T1.Convert()-X0
                T2=ROOT.TDatime(maxtimeHV.year,maxtimeHV.month,maxtimeHV.day,maxtimeHV.hour,maxtimeHV.minute,maxtimeHV.second)
                X2=T2.Convert()-X0
                self.HV_time_evo_plots[graph_name]=[ROOT.TGraph()]
                for i in range(len(HV_time_list)):
                    cur_time=HV_time_list[i]
                    cur_data=HV_data_list[i]
                    cur_value=pow(cur_data/ref_data,6.9)*reference
                    Tcurr=ROOT.TDatime(cur_time.year,cur_time.month,cur_time.day,cur_time.hour,cur_time.minute,cur_time.second)
                    Xcurr=Tcurr.Convert()-X0
                    npoints = self.HV_time_evo_plots[graph_name][0].GetN()
                    self.HV_time_evo_plots[graph_name][0].SetPoint(npoints,Xcurr,cur_value)                
                self.HV_time_evo_plots[graph_name][0].SetLineColor(4)
                self.HV_time_evo_plots[graph_name][0].SetMarkerColor(4)
                self.HV_time_evo_plots[graph_name][0].SetMarkerSize (0.2)
                self.HV_time_evo_plots[graph_name][0].Sort()
        
    def ProcessStop(self):
        dirname='CsTimeEvoPlots'
        self.dir      =  os.path.join(src.oscalls.getPlotDirectory(),dirname)
        src.oscalls.createDir(self.dir)
        if self.r_prod:
            keys_to_draw=[]
            for ros in range(4):
                part=self.PMTool.get_partition_name(ros)
                for drawer in range(64):
                    module=drawer+1
                    for chan in range(48):
                        pmt=self.PMTool.get_PMT_index(ros,drawer,chan)
                        expected_graph_name="%s_m%02d_pmt%02d" % (part,module,pmt)
                        if expected_graph_name in self.time_evo_plots:
                            if len(self.time_evo_plots[expected_graph_name])>2:
                                keys_to_draw.append(expected_graph_name)
            if keys_to_draw:
                width=4
                height=3
                np=width*height-1
                nc=int(math.ceil(float(len(keys_to_draw))/float(np)))
                self.plot_name="Problem_book"
                c_w = int(800)
                c_h = int(600)
                self.c_cc = ROOT.TCanvas("canvas","canvas", c_w,c_h)
                self.c_cc.SetWindowSize(2*c_w - self.c_cc.GetWw(), 2*c_h - self.c_cc.GetWh())
                self.c_cc.Print("%s/%s.pdf[" % (self.dir,self.plot_name))
                for c_id in range(nc):
                    self.c_cc.cd()
                    self.c_cc.Clear()
                    self.c_cc.Divide(width,height,0.01,0.01)

                    if keys_to_draw:
                        self.c_cc.cd(width*height)
                        textbox=ROOT.TLatex()
                        textbox.SetTextSize(0.2)
                        textbox.SetTextSize(0.08)
                        textbox.DrawLatex(0,0.6,"Restriction parameter  "+str(round(self.r_par,3)))
                        textbox.Draw()
                        legend = ROOT.TLegend(0., 0., 1., 0.5)
                        legend.SetTextSize(0.09)
                        graph_name=keys_to_draw[0]
                        legend.AddEntry(self.time_evo_plots[keys_to_draw[0]][0],"Cesium constant","P")
                        HV_keys=list(self.HV_time_evo_plots.keys())
                        if HV_keys:
                            legend.AddEntry(self.HV_time_evo_plots[HV_keys[0]][0],"Expected","L")
                        legend.Draw()
                        ROOT.gPad.Modified()
                        ROOT.gPad.Update()

                    for p_id in range(np):
                        self.c_cc.cd(p_id+1)
                        if keys_to_draw:
                            graph_name=sorted(keys_to_draw)[0]   
                            ROOT.gPad.SetTopMargin(0.05)
                            color=self.frame_color_schema[self.time_evo_plots[graph_name][1]]
                            ROOT.gPad.SetFillColor(color)
                            ROOT.gPad.SetFrameFillColor(10)
                            self.time_evo_plots[graph_name][0].SetMarkerSize (0.3)
                            self.time_evo_plots[graph_name][0].Draw('AP')
                            self.time_evo_plots[graph_name][0].GetXaxis().SetTimeDisplay(1)
                            self.time_evo_plots[graph_name][0].GetXaxis().SetLabelSize(0.04)
                            self.time_evo_plots[graph_name][0].GetXaxis().SetLabelOffset(0.05)
                            self.time_evo_plots[graph_name][0].GetXaxis().SetTimeFormat("#splitline{%d/%m}{%Y}")
                            if graph_name in self.HV_time_evo_plots:
                                self.HV_time_evo_plots[graph_name][0].Draw('L')
                            textbox=ROOT.TLatex()
                            textbox.SetNDC()
                            textbox.DrawLatex(0.1,0.96,graph_name+" "+str(round(self.time_evo_plots[graph_name][2],3)))
                            textbox.Draw()
                            ROOT.gPad.Modified()
                            ROOT.gPad.Update()
                            keys_to_draw.remove(graph_name)
                    self.c_cc.Print("%s/%s.pdf" % (self.dir,self.plot_name))
                self.c_cc.Print("%s/%s.pdf]" % (self.dir,self.plot_name))
                        

            
        else:
            for ros in range(4):
                part=self.PMTool.get_partition_name(ros)
                for drawer in range(64):
                    module=drawer+1
                    do_plot=False
                    keys_to_draw=[]
                    for chan in range(48):
                        pmt=self.PMTool.get_PMT_index(ros,drawer,chan)
                        expected_graph_name="%s_m%02d_pmt%02d" % (part,module,pmt)
                        if expected_graph_name in self.time_evo_plots:
                            do_plot=True
                            keys_to_draw.append(expected_graph_name)                   
                    if do_plot:
                        c_w = int(800)
                        c_h = int(600)
                        tcanvas_name="c_cc_%s_m%d" % (part, module)
                        self.c_cc = ROOT.TCanvas(tcanvas_name,"canvas", c_w,c_h)
                        self.c_cc.SetWindowSize(2*c_w - self.c_cc.GetWw(), 2*c_h - self.c_cc.GetWh())
                        self.c_cc.Divide(8,6,0.01,0.01)
                        for i in range(len(keys_to_draw)):
                            graph_name=keys_to_draw[i]
                            pmt=int(graph_name.split('pmt')[1])
                            self.c_cc.cd(pmt)
                            ROOT.gPad.SetTopMargin(0.05)
                            color=self.frame_color_schema[self.time_evo_plots[graph_name][1]]
                            ROOT.gPad.SetFillColor(color)
                            ROOT.gPad.SetFrameFillColor(10)
                            self.time_evo_plots[graph_name][0].Draw('AP')
                            self.time_evo_plots[graph_name][0].GetXaxis().SetTimeDisplay(1)
                            self.time_evo_plots[graph_name][0].GetXaxis().SetLabelSize(0.04)
                            self.time_evo_plots[graph_name][0].GetXaxis().SetLabelOffset(0.05)
                            self.time_evo_plots[graph_name][0].GetXaxis().SetTimeFormat("#splitline{%d/%m}{%Y}")
                            if graph_name in self.HV_time_evo_plots:
                                self.HV_time_evo_plots[graph_name][0].Draw('L')
                            textbox=ROOT.TLatex()
                            textbox.SetNDC()
                            textbox.DrawLatex(0.1,0.96,graph_name)
                            textbox.Draw()
                            ROOT.gPad.Modified()
                            ROOT.gPad.Update()
                        self.c_cc.cd(32)
                        textbox=ROOT.TLatex()
                        modname="%s_m%d" % (part,module)
                        textbox.SetTextSize(0.2)
                        textbox.DrawLatex(0,0.8,modname)
                        textbox.SetTextSize(0.1)
                        textbox.DrawLatex(0,0.6,"Quality parameter "+str(self.quality_par))
                        textbox.Draw()
                        legend = ROOT.TLegend(0., 0., 1., 0.5)
                        legend.SetTextSize(0.09)
                        graph_name=keys_to_draw[0]
                        legend.AddEntry(self.time_evo_plots[graph_name][0],"Cesium constant","P")
                        HV_keys=list(self.HV_time_evo_plots.keys())
                        if HV_keys:
                            legend.AddEntry(self.HV_time_evo_plots[HV_keys[0]][0],"Expected","L")
                        legend.Draw()
                        ROOT.gPad.Modified()
                        ROOT.gPad.Update()
                        self.plot_name = "CsTimeEvoPlots_%s_m%d" % (part,module)
                        self.c_cc.Print("%s/%s.eps" % (self.dir,self.plot_name))

