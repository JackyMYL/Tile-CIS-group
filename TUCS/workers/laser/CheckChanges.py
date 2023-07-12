###############################################################################
# Author: Andry Kamenshchikov <akamensh@cern.ch>
#
# 27.05.2013
#
# Functionality:
#	Compare two defined HV from event.data and print
#	all event data if difference those HV exceed
#	defined criterion. Could draw the detector's map and print the file
#       with problem region if need.
#
# Options:
#	key1 (obligatory) - key of the first HV type from event.data (string);
#	key2 (obligatory) - key of the second HV type from event.data (string);
#	crit (obligatory) - criterion (in Volts) (float).
#	crit1 (obligatory) - second criterion (in Volts) (float).
#	draw_pic  - option for drowing detector's map (bool).
#	print_file  - option for printing problem regions in file (bool).
#       sep_plots - option for chose either print separate plots for each
#                    partition or single plot for 4 partitions (bool).
#
###############################################################################
import gc
import math
import ROOT

from src.GenericWorker import *
from src.run import *
import src.oscalls
import os.path

class CheckChanges(GenericWorker):
    "Check if changes between different kinds of HV exceed given threshold"

    def __init__(self, key1, key2, crit, crit1,draw_pic=True, print_file=True, sep_plots=False):
        self.key1=key1
        self.key2=key2
        (self.crit,self.crit1)=sorted((crit,crit1))
        self.PMTool    = LaserTools()
        self.draw_pic=draw_pic
        self.zero_crit=100.
        self.print_file=print_file
        self.sep_plots=sep_plots

    def ProcessStart(self):

        self.event_distrib={}
        self.bad_reg_txt={}
        self.warning_reg_txt={}
        self.switchedoff_reg_txt={}
        self.reg_set={}
        self.part_set={}
#        global run_list
        for run in run_list:
            if run.runType=='cesium' and run.runNumber<40000:
                continue
            self.part_set[run.runNumber]=set()
            self.reg_set[run.runNumber]=set()
            self.event_distrib[run.runNumber]=[]
            self.bad_reg_txt[run.runNumber]={}
            self.warning_reg_txt[run.runNumber]={}
            self.switchedoff_reg_txt[run.runNumber]={}
            for partition in range(4):
                self.event_distrib[run.runNumber].append([])
                self.event_distrib[run.runNumber][partition]=[]
                th2fstring_gl="good_layer_%d_%d" %(run.runNumber, partition)
                self.event_distrib[run.runNumber][partition].append(ROOT.TH2F(th2fstring_gl,self.PMTool.get_partition_name(partition),64,0,64,48,0,48))
                th2fstring_bl="bad_layer_%d_%d" %(run.runNumber, partition)
                self.event_distrib[run.runNumber][partition].append(ROOT.TH2F(th2fstring_bl,self.PMTool.get_partition_name(partition),64,0,64,48,0,48))
                th2fstring_wl="warning_layer_%d_%d" %(run.runNumber, partition)
                self.event_distrib[run.runNumber][partition].append(ROOT.TH2F(th2fstring_wl,self.PMTool.get_partition_name(partition),64,0,64,48,0,48))
                th2fstring_sl="switchedoff_layer_%d_%d" %(run.runNumber, partition)
                self.event_distrib[run.runNumber][partition].append(ROOT.TH2F(th2fstring_sl,self.PMTool.get_partition_name(partition),64,0,64,48,0,48))


    def ProcessRegion(self, region):

        for event in region.GetEvents():
            if len(event.region.GetNumber(1))==4:
                [part, module, pmt, gain] = event.region.GetNumber(1)
            elif len(event.region.GetNumber(1))==3:
                [part, module, pmt] = event.region.GetNumber(1)
            else:
                continue

            if (self.key1 in event.data and self.key2 in event.data):
                if part not in self.part_set[event.run.runNumber]:
                    self.part_set[event.run.runNumber].add(part)
                if (part,module,pmt) not in self.reg_set[event.run.runNumber]:
                    self.reg_set[event.run.runNumber].add((part,module,pmt))
                    if (math.fabs(event.data[self.key1])<=self.zero_crit) or (math.fabs(event.data[self.key2])<=self.zero_crit):
                        self.event_distrib[event.run.runNumber][part-1][3].Fill(module-1.+0.5,pmt-1.+0.5,1)
                        self.switchedoff_reg_txt[event.run.runNumber][region]={self.key1:event.data[self.key1], self.key2:event.data[self.key2]}
                    else:
                        c=math.fabs(event.data[self.key1]-event.data[self.key2])
                        if  c >= self.crit:
                            print(event.run.runType, ',',event.run.runNumber, ',', event.run.time, ',', event.run.endtime, ',', event.region)
                            print('Data: {')
                            for key, value in sorted(iter(event.data.items()),reverse=True):
                                print('\t',key,':\t', value)
                            print('}')
                            if self.draw_pic:
                                if c>=self.crit1:
                                    self.event_distrib[event.run.runNumber][part-1][1].Fill(module-1.+0.5,pmt-1.+0.5,1)
                                else:
                                    self.event_distrib[event.run.runNumber][part-1][2].Fill(module-1.+0.5,pmt-1.+0.5,1)

                            if self.print_file:
                                if c>=self.crit1:
                                    self.bad_reg_txt[event.run.runNumber][region]={self.key1:event.data[self.key1], self.key2:event.data[self.key2]}
                                else:
                                    self.warning_reg_txt[event.run.runNumber][region]={self.key1:event.data[self.key1], self.key2:event.data[self.key2]}
                        else:
                            if self.draw_pic:
                                self.event_distrib[event.run.runNumber][part-1][0].Fill(module-1.+0.5,pmt-1.+0.5,1)
                else:
                    continue
            else:
                continue


    def ProcessStop(self):
#        global run_list
        if self.print_file:

            for run_abstract in run_list:
                if run_abstract.runType=='cesium' and run_abstract.runNumber<40000:
                    continue
                run=run_abstract.runNumber
                runtype=run_abstract.runType
                dirname="CheckChanges/%s_vs_%s_crit_%s" %(self.key1,self.key2,self.crit)
                self.dir      =  os.path.join(src.oscalls.getPlotDirectory(),dirname)
                src.oscalls.createDir(self.dir)
                file_string="CheckChanges_%s_%i.txt" % (runtype,run)
                f=open("%s/%s" %(self.dir,file_string), 'w')
                for key in list(self.bad_reg_txt[run].keys()):
                    f.write('BAD CHANNEL: %s pmt%02i (' % (str(key).split("_")[1]+str(key).split("_")[2][-2:]+" "+str(key).split("_")[3], key.GetNumber(1)[2]))
                    for internal_key in list(self.bad_reg_txt[run][key].keys()):
                        f.write(' (%s = %f) ' % (internal_key, self.bad_reg_txt[run][key][internal_key]) )
                    f.write(')\n')
                for key in list(self.warning_reg_txt[run].keys()):
                    f.write('WARNING CHANNEL: %s pmt%02i (' % (str(key).split("_")[1]+str(key).split("_")[2][-2:]+" "+str(key).split("_")[3], key.GetNumber(1)[2]))
                    for internal_key in list(self.warning_reg_txt[run][key].keys()):
                        f.write(' (%s = %f) ' % (internal_key, self.warning_reg_txt[run][key][internal_key]) )
                    f.write(')\n')
                for key in list(self.switchedoff_reg_txt[run].keys()):
                    f.write('SWITCHEDOFF CHANNEL: %s pmt%02i (' % (str(key).split("_")[1]+str(key).split("_")[2][-2:]+" "+str(key).split("_")[3], key.GetNumber(1)[2]))
                    for internal_key in list(self.switchedoff_reg_txt[run][key].keys()):
                        f.write(' (%s = %f) ' % (internal_key, self.switchedoff_reg_txt[run][key][internal_key]) )
                    f.write(')\n')



        if (self.draw_pic and not self.sep_plots) :
            pad_ind=(lambda i: i+1 if i<2 else i+2)
#            global run_list
            for run_abstract in run_list:
                if run_abstract.runType=='cesium' and run_abstract.runNumber<40000:
                    continue
                run=run_abstract.runNumber
                runtype=run_abstract.runType
                c_w = int(1366)
                c_h = int(768)
                ROOT.gStyle.SetOptStat(0)
                tcanvas_name="c_cc_%d" %(run)
                self.c_cc = ROOT.TCanvas(tcanvas_name,"canvas", c_w,c_h)
                self.c_cc.SetWindowSize(2*c_w - self.c_cc.GetWw(), 2*c_h - self.c_cc.GetWh())
                self.c_cc.Divide(3,2,0.01,0.01)
                pad=[]
                empty_layer=[]
                dead_layer=[]
                X_layers=[]

                for i in range(4):
                    pad.append(self.c_cc.cd(pad_ind(i)))
                    th2fstring_el="empty_layer_%d_%d" %(run, i)
                    empty_layer.append(ROOT.TH2F(th2fstring_el,self.PMTool.get_partition_name(i),64,0,64,48,0,48))
                    empty_layer[i].SetFillColor(4)
                    empty_layer[i].GetXaxis().SetLabelSize(0.03);
                    empty_layer[i].GetYaxis().SetLabelSize(0.03);
                    for indx in range(64):
                        empty_layer[i].GetXaxis().SetBinLabel(indx+1,str(indx+1))
                    for indy in range(48):
                        empty_layer[i].GetYaxis().SetBinLabel(indy+1,str(indy))
                    for j in range(64):
                        for k in range(48):
                            empty_layer[i].Fill(j+0.5,k+0.5,1)
                    empty_layer[i].Draw("BOX1")
                    empty_layer[i].SetXTitle(self.PMTool.get_partition_name(i)+" Module#")
                    empty_layer[i].SetYTitle(self.PMTool.get_partition_name(i)+" Channel#")

                for i in range(4):
                    self.c_cc.cd(pad_ind(i))
                    th2fstring_dl="dead_layer_%d_%d" %(run, i)
                    dead_layer.append(ROOT.TH2F(th2fstring_dl,self.PMTool.get_partition_name(i),64,0,64,48,0,48))
                    dead_layer[i].SetFillColor(390)
                    for j in range(64):
                        for k in range(48):
                            if not (is_instrumented(i,j,k+1)):
                                dead_layer[i].Fill(j+0.5,k+0.5,1)
                    dead_layer[i].Draw("SAMEBOX1")

                colormap={0:3,1:2,2:5,3:1}
                for layer in range(4):
                    X_layers.append([])
                    for partition in range(4):
                        self.c_cc.cd(pad_ind(partition))
                        X_layers[layer].append(self.event_distrib[run][partition][layer])
                        X_layers[layer][partition].SetFillColor(colormap[layer])
                        X_layers[layer][partition].Draw("SAMEBOX1")

                goodstring="Good region: |%s - %s| < %s" %(self.key1,self.key2,self.crit)
                badstring="Bad region: %s<=|%s - %s|" %(self.crit1,self.key1,self.key2)
                warningstring="Warning region: %s <= |%s - %s| < %s" %(self.crit, self.key1,self.key2,self.crit1)
                switchedoffstring="Switched off region: %s < %d or %s < %d" %(self.key1, self.zero_crit, self.key2, self.zero_crit )

                self.c_cc.cd(3)
                leg_title="%d %s:" % (run, runtype)
                self.legend0 = ROOT.TLegend(0,0,1,1,leg_title)
                self.legend0.AddEntry("", self.key1+" vs "+self.key2,"")
                self.legend0.AddEntry("", "criterion = "+str(self.crit),"")
                self.legend0.AddEntry(empty_layer[0], "Unused region", "F")
                self.legend0.AddEntry(dead_layer[0], "Uninstrumented region", "F")
                self.legend0.Draw()

                self.c_cc.cd(6)
                self.legend = ROOT.TLegend(0,0,1,1,"")
                self.legend.AddEntry(X_layers[0][0], goodstring, "F")
                self.legend.AddEntry(X_layers[1][0], badstring, "F")
                self.legend.AddEntry(X_layers[2][0], warningstring, "F")
                self.legend.AddEntry(X_layers[3][0], switchedoffstring, "F")
                self.legend.Draw()

                self.c_cc.Modified()
                self.c_cc.Update()
                dirname='CheckChanges/%s_vs_%s_crit_%s' %(self.key1,self.key2,self.crit)
                self.dir      =  os.path.join(src.oscalls.getPlotDirectory(),dirname)
                src.oscalls.createDir(self.dir)
                self.plot_name = "CheckChanges_%s_%i" % (runtype,run)
                self.c_cc.Print("%s/%s.eps" % (self.dir,self.plot_name))
                
        elif (self.draw_pic and self.sep_plots) :
#            global run_list
            for run_abstract in run_list:
                if run_abstract.runType=='cesium' and run_abstract.runNumber<40000:
                    continue
                run=run_abstract.runNumber
                runtype=run_abstract.runType
                for part_id in self.part_set[run]:
                    c_w = int(1366)
                    c_h = int(768)
                    ROOT.gStyle.SetOptStat(0)
                    tcanvas_name="c_cc_%d_%d" %(run,part_id)
                    self.c_cc = ROOT.TCanvas(tcanvas_name,"canvas", c_w,c_h)
                    self.c_cc.SetWindowSize(2*c_w - self.c_cc.GetWw(), 2*c_h - self.c_cc.GetWh())
                    self.c_cc.Divide(2,1,0.01,0.01)
                    pad=[]
                    X_layers=[]

                    pad.append(self.c_cc.cd(1))
                    th2fstring_el="empty_layer_%d_%d" %(run, part_id)
                    empty_layer=ROOT.TH2F(th2fstring_el,self.PMTool.get_partition_name(part_id-1),64,0,64,48,0,48)
                    empty_layer.SetFillColor(4)
                    empty_layer.GetXaxis().SetLabelSize(0.03);
                    empty_layer.GetYaxis().SetLabelSize(0.03);
                    for indx in range(64):
                        empty_layer.GetXaxis().SetBinLabel(indx+1,str(indx+1))
                    for indy in range(48):
                        empty_layer.GetYaxis().SetBinLabel(indy+1,str(indy))
                    for j in range(64):
                        for k in range(48):
                            empty_layer.Fill(j+0.5,k+0.5,1)
                    empty_layer.Draw("BOX1")
                    empty_layer.SetXTitle(self.PMTool.get_partition_name(part_id-1)+" Module#")
                    empty_layer.SetYTitle(self.PMTool.get_partition_name(part_id-1)+" Channel#")
                    
                    self.c_cc.cd(1)
                    th2fstring_dl="dead_layer_%d_%d" %(run, part_id)
                    dead_layer=ROOT.TH2F(th2fstring_dl,self.PMTool.get_partition_name(part_id-1),64,0,64,48,0,48)
                    dead_layer.SetFillColor(390)
                    for j in range(64):
                        for k in range(48):
                            if not (is_instrumented(part_id-1,j,k+1)):
                                dead_layer.Fill(j+0.5,k+0.5,1)
                    dead_layer.Draw("SAMEBOX1")

                    colormap={0:3,1:2,2:5,3:1}
                    for layer in range(4):
                        X_layers.append(self.event_distrib[run][part_id-1][layer])
                        X_layers[layer].SetFillColor(colormap[layer])
                        self.c_cc.cd(1)
                        X_layers[layer].Draw("SAMEBOX1")

                    goodstring="Good region: |%s - %s| < %s" %(self.key1,self.key2,self.crit)
                    badstring="Bad region: %s<=|%s - %s|" %(self.crit1,self.key1,self.key2)
                    warningstring="Warning region: %s <= |%s - %s| < %s" %(self.crit, self.key1,self.key2,self.crit1)
                    switchedoffstring="Switched off region: %s < %d or %s < %d" %(self.key1, self.zero_crit, self.key2, self.zero_crit )

                    self.c_cc.cd(2)
                    leg_title="%d %s %s:" % (run, runtype, self.PMTool.get_partition_name(part_id-1))
                    self.legend = ROOT.TLegend(0,0,1,1,leg_title)
                    self.legend.AddEntry("", self.key1+" vs "+self.key2,"")
                    self.legend.AddEntry("", "criterion = "+str(self.crit),"")
                    self.legend.AddEntry(empty_layer, "Unused region", "F")
                    self.legend.AddEntry(dead_layer, "Uninstrumented region", "F")

                    self.legend.AddEntry(X_layers[0], goodstring, "F")
                    self.legend.AddEntry(X_layers[1], badstring, "F")
                    self.legend.AddEntry(X_layers[2], warningstring, "F")
                    self.legend.AddEntry(X_layers[3], switchedoffstring, "F")
                    self.legend.Draw()

                    self.c_cc.Modified()
                    self.c_cc.Update()
                    dirname='CheckChanges/%s_vs_%s_crit_%s' %(self.key1,self.key2,self.crit)
                    self.dir      =  os.path.join(src.oscalls.getPlotDirectory(),dirname)
                    src.oscalls.createDir(self.dir)
                    self.plot_name = "CheckChanges_%s_%i_%s" % (runtype,run,self.PMTool.get_partition_name(part_id-1))
                    self.c_cc.Print("%s/%s.eps" % (self.dir,self.plot_name))
        else:
            return

