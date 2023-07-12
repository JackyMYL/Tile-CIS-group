###############################################################################
# Author: Andry Kamenshchikov <akamensh@cern.ch>
#
# 23.11.2013
#
# Functionality:
#	Produce cesium time evolution plots convoluted with m- index.
#
# Options:
#       quality_par - parameter to defind problem type ( 'problem' if |min-max|>=quality_par),
#                                                        'warning' if 0.5*quality_par<|min-max|<quality_par,
#                                                        'good' if |min-max|<=0.5*quality_par)
#       
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

class time_evolution_plots_mconvoluted(GenericWorker):
    "Produce cesium time evolution plots convoluted with m- index"

    def __init__(self, quality_par=0.1):
        self.PMTool    = LaserTools()
        self.quality_par = quality_par
        self.frame_color_schema={"good":kGreen-9, "warning":kYellow-9, "problem":kRed-9}
        self.deadpmtsign='Ignore Cesium'
        self.unstablepmtsign='Unstable Cesium'
        self.emergencypmtsign='Emergency'

    def ProcessStart(self):
        self.time_evo_plots_mconv={}
        self.time_dep_dict={} 
    
    def ProcessRegion(self, region):
        if (region.GetEvents() and len(region.GetNumber(1))==3):
            [part, module, pmt] = region.GetNumber(1)
            partname=self.PMTool.get_partition_name(part-1)
            reg_key="%s_pmt%02d" % (partname,pmt)
            if reg_key not in list(self.time_dep_dict.keys()):
                self.time_dep_dict[reg_key]={}
                
            for event in region.GetEvents():
                if 'problems' in event.data and ((self.deadpmtsign in event.data['problems']) or (self.unstablepmtsign in event.data['problems']) or (self.emergencypmtsign in event.data['problems'])):
                    print("Ignore %s in cs run %d" % (region,event.run))
                    continue
                current_time=datetime.datetime.strptime(event.run.time, '%Y-%m-%d %H:%M:%S')
                if current_time not in list(self.time_dep_dict[reg_key].keys()):
                    self.time_dep_dict[reg_key][current_time]=[]
                if 'calibration' in event.data:
                    current_data=event.data['calibration']
                    if (isinstance(current_data,float)):
                        self.time_dep_dict[reg_key][current_time].append(current_data)
        
    def ProcessStop(self):
        dirname='CsTimeEvoPlots'
        self.dir      =  os.path.join(src.oscalls.getPlotDirectory(),dirname)
        src.oscalls.createDir(self.dir)
        for ros in range(4):
            part=self.PMTool.get_partition_name(ros)
            pmt_to_draw={}
            for pmt_id in range(1,49):
                expected_reg_key="%s_pmt%02d" % (part,pmt_id)
                if expected_reg_key in list(self.time_dep_dict.keys()):
                    for time_point in list(self.time_dep_dict[expected_reg_key].keys()):
                        if self.time_dep_dict[expected_reg_key][time_point]:
                            if expected_reg_key not in list(pmt_to_draw.keys()):
                                pmt_to_draw[expected_reg_key]=[]
                            pmt_to_draw[expected_reg_key].append(time_point)

            if pmt_to_draw:
                c_w = int(800)
                c_h = int(600)
                tcanvas_name="c_cc_%s" % (part)
                self.c_cc = ROOT.TCanvas(tcanvas_name,"canvas", c_w,c_h)
                self.c_cc.SetWindowSize(2*c_w - self.c_cc.GetWw(), 2*c_h - self.c_cc.GetWh())
                self.c_cc.Divide(8,6,0.01,0.01)
                time_evo_plots={}
                for reg_key in list(pmt_to_draw.keys()):
                    graph_name=reg_key
                    pmt=int(graph_name.split('pmt')[1])
                    self.c_cc.cd(pmt)
                    ROOT.gPad.SetTopMargin(0.05)
                    time_list_prev=pmt_to_draw[reg_key]
                    mintime = sorted(time_list_prev)[0]
                    maxtime = sorted(time_list_prev)[len(time_list_prev)-1]
                    T0=ROOT.TDatime(mintime.year,mintime.month,mintime.day,mintime.hour,mintime.minute,mintime.second)
                    X0=T0.Convert()
                    ROOT.gStyle.SetTimeOffset(X0)
                    T1=ROOT.TDatime(mintime.year,mintime.month,mintime.day,mintime.hour,mintime.minute,mintime.second)
                    X1=T1.Convert()-X0
                    T2=ROOT.TDatime(maxtime.year,maxtime.month,maxtime.day,maxtime.hour,maxtime.minute,maxtime.second)
                    X2=T2.Convert()-X0

                    time_list=[ROOT.TDatime(timeprev.year,timeprev.month,timeprev.day,timeprev.hour,timeprev.minute,timeprev.second).Convert()-X0 for timeprev in time_list_prev]
                    data_list=[self.derive_stat(self.time_dep_dict[reg_key][time])[0] for time in time_list_prev]
                    dataerr_list=[self.derive_stat(self.time_dep_dict[reg_key][time])[1] for time in time_list_prev]
                    mindata = sorted(data_list)[0]
                    maxdata = sorted(data_list)[len(data_list)-1]                
                    time_evo_plots[graph_name]=ROOT.TGraphErrors()
                    for i in range(len(time_list)):
                        Xcurr=time_list[i]
                        cur_data=data_list[i]
                        cur_dataerr=dataerr_list[i]
                        npoints = time_evo_plots[graph_name].GetN()
                        time_evo_plots[graph_name].SetPoint(npoints,Xcurr,cur_data)
                        time_evo_plots[graph_name].SetPointError(npoints,0,cur_dataerr)
                    deltaY_prev=math.fabs(mindata-maxdata)
                    deltaX=math.fabs(0.1*(X1-X2)) if X1!=X2 else math.fabs(0.1*X0)
                    deltaY=math.fabs(0.1*(mindata-maxdata)) if mindata!=maxdata else math.fabs(0.1*mindata)
                    if (deltaY_prev<self.quality_par):
                        time_evo_plots[graph_name].SetMaximum((maxdata+mindata)/2.+self.quality_par*0.6)
                        time_evo_plots[graph_name].SetMinimum((maxdata+mindata)/2.-self.quality_par*0.6)
                        ROOT.gPad.SetFillColor(self.frame_color_schema["good"])
                        if (deltaY_prev>self.quality_par*0.5):
                            ROOT.gPad.SetFillColor(self.frame_color_schema["warning"])                            
                    else:
                        time_evo_plots[graph_name].SetMaximum(maxdata+deltaY)
                        time_evo_plots[graph_name].SetMinimum(mindata-deltaY)
                        ROOT.gPad.SetFillColor(self.frame_color_schema["problem"])
                    ROOT.gPad.SetFrameFillColor(10)
                    time_evo_plots[graph_name].GetXaxis().SetLimits(X1-deltaX,X2+deltaX)
                    time_evo_plots[graph_name].SetMarkerColor(2)
                    time_evo_plots[graph_name].SetLineColor(2)
                    time_evo_plots[graph_name].SetMarkerStyle(21)
                    time_evo_plots[graph_name].SetMarkerSize(0.2)
                    time_evo_plots[graph_name].Draw('AP')
                    time_evo_plots[graph_name].GetXaxis().SetTimeDisplay(1)
                    time_evo_plots[graph_name].GetXaxis().SetLabelSize(0.03)
                    time_evo_plots[graph_name].GetXaxis().SetLabelOffset(0.05)
                    time_evo_plots[graph_name].GetXaxis().SetTimeFormat("#splitline{%d/%m}{%Y}")
                    ROOT.gPad.Update()
                    textbox=ROOT.TLatex()
                    textbox.SetNDC()
                    textbox.DrawLatex(0.1,0.96,graph_name)
                    textbox.Draw()
                    ROOT.gPad.Modified()
                    ROOT.gPad.Update()
                    self.c_cc.cd(32)
                    textbox=ROOT.TLatex()
                    partname="%s" % (part)
                    textbox.SetTextSize(0.2)
                    textbox.DrawLatex(0,0.8,partname)
                    legend = ROOT.TLegend(0., 0., 1., 0.5)
                    legend.SetTextSize(0.09)
                    legend.AddEntry(time_evo_plots[graph_name],"Cesium constant","P")
                    legend.Draw()
                    ROOT.gPad.Modified()
                    ROOT.gPad.Update()
                self.plot_name = "CsTimeEvoPlots_mconv_%s" % (part)
                self.c_cc.Print("%s/%s.eps" % (self.dir,self.plot_name))                

    def derive_stat(self, points_list):
        result=None
        if points_list:
            mean=sum(points_list)/float(len(points_list))
            RMS = math.sqrt(sum([(x-mean)*(x-mean) for x in points_list])/float(len(points_list)))
            result=(mean,RMS)     
        return result
                
