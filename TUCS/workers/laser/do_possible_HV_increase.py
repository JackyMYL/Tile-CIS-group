############################################################
#
# do_possible_HV_increase.py
#
############################################################
#
# Author: Marco van Woerden (13/07/2012)
#
# Output:
# Calculates possible HV increases over all modules for a particular channel.
#
# Input parameters are:
# -> part: the partition number (1=LBA, 2=LBC, 3=EBA, 4=EBC) you want to plot.
# -> chan: the channel number.
#
# For more info on the LASER system : http://atlas-tile-laser.web.cern.ch
#
#############################################################

from src.GenericWorker import *
from src.oscalls import *
import src.MakeCanvas

class do_possible_HV_increase(GenericWorker):
    "Calculate possible HV increases over all modules for a particular channel."

    c1 = None
    c2 = None

    def __init__(self,  part=1, chan=0):
        self.part     = part
        self.mod      = -1
        self.chan     = chan

        self.outputTag = outputTag # global variable to tag output histogram file name
        self.dir    = getPlotDirectory(subdir=self.outputTag)

        self.name     = ''
        if chan == 0: self.name = 'E3'
        elif chan == 1: self.name = 'E4'
        elif chan == 2: self.name = 'D4'
        elif chan == 3: self.name = 'D4'
        elif chan == 4: self.name = 'E4'
        elif chan == 5: self.name = 'C10'
        elif chan == 6: self.name = 'C10'
        elif chan == 12: self.name = 'E1'
        elif chan == 13: self.name = 'E2'
        else: self.name = "chan%02i"%self.chan

        self.PMTool   = LaserTools()
        self.partname = self.PMTool.get_partition_name(self.part-1)

        self.LG_evts  = list() # Events with low gain info
        self.HG_evts  = list() # Events with high gain info

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
            if ind == self.PMTool.get_index(self.part-1,mod-1,self.chan,0):
                match_found = True
                self.mod = mod
                break
        if not match_found:
            return

        for event in region.GetEvents():
            if event.run.runType!='Las':
                continue

            if gain==0:
                self.LG_evts.append([event,self.mod])

            if gain==1:
                self.HG_evts.append([event,self.mod])


    def ProcessStop(self):

        ROOT.gStyle.SetOptStat(0)
        ROOT.gStyle.SetStatX(0.78)
        ROOT.gStyle.SetStatY(0.83)

        ROOT.gStyle.SetOptTitle(1)
        ROOT.gStyle.SetTitleX(0.15)
        ROOT.gStyle.SetTitleW(0.2)
        ROOT.gStyle.SetTitleBorderSize(0)
        ROOT.gStyle.SetTitleFontSize(0.1)
        ROOT.gStyle.SetEndErrorSize(0.)

        cadre_xmin = 1.
        cadre_xmax = 65.
        cadre_ymin = 0.
        cadre_ymax = 1.#400.
        cadre_ymin_LG = 0.
        cadre_ymax_LG = 1.#1600.
        cadre_ymin_HG = 0.
        cadre_ymax_HG = 1.#3200.
        cadre_hl_ratio = 0.15

        line_HV_LG = 99999.
        line_HV_LG_max = 0.

        temp = 1.;
        for mod in range(1,65):
            max_sighg = 0.
            max_siglg = 0.
            max_HV_hg = 0.
            max_HV_lg = 0.
            HV_hg     = 0.
            HV_lg     = 0.
            for a in self.LG_evts:
                if a[1] != mod:
                    continue
                event = a[0]
                if 'HVSet' in event.data:
                    if (event.data['HVSet'])!=0:
                        if max_HV_lg < math.fabs(event.data['HV']):
                            max_HV_lg = math.fabs(event.data['HV'])
                    HV_lg = event.data['HVSet']
                if 'signal' in event.data:
                    if max_siglg<math.fabs(event.data['signal']):
                        max_siglg = math.fabs(event.data['signal'])
            if max_siglg != 0.:
                if cadre_ymax_LG < ( pow(800./max_siglg,1./7.)*HV_lg)*2.2:
                    cadre_ymax_LG = ( pow(800./max_siglg,1./7.)*HV_lg)*2.2
                if cadre_ymax < ( pow(800./max_siglg,1./7.)*HV_lg-HV_lg )*2.2:
                    cadre_ymax = ( pow(800./max_siglg,1./7.)*HV_lg-HV_lg )*2.2
            for a in self.HG_evts:
                if a[1] != mod:
                    continue
                event = a[0]
                if 'HVSet' in event.data:
                    if (event.data['HVSet'])!=0:
                        if max_HV_hg < math.fabs(event.data['HV']):
                            max_HV_hg = math.fabs(event.data['HV'])
                    HV_hg = event.data['HVSet']
                if 'signal' in event.data:
                    if max_sighg<math.fabs(event.data['signal']):
                        max_sighg = math.fabs(event.data['signal'])
            if max_sighg != 0.:
                if temp < ( pow(800./max_sighg,1./7.)*HV_hg-HV_hg )*2.2:
                    temp = ( pow(800./max_sighg,1./7.)*HV_hg-HV_hg )*2.2
                if cadre_ymax_HG < ( pow(800./max_sighg,1./7.)*HV_hg)*2.2:
                    cadre_ymax_HG = ( pow(800./max_sighg,1./7.)*HV_hg)*2.2
        cadre_hl_ratio = cadre_ymax / temp

        self.hist_HV_increase = ROOT.TH2F('possible HV increase [%s_%s]'%(self.partname,self.name),'possible HV increase [%s_%s]'%(self.partname,self.name),\
                                          64,cadre_xmin,cadre_xmax ,400,cadre_ymin,cadre_ymax)
        self.hist_HV_increase.GetYaxis().SetTitleOffset(0.4)
        self.hist_HV_increase.GetYaxis().SetTitleSize(0.08)
        self.hist_HV_increase.GetXaxis().SetLabelOffset(0.03)
        self.hist_HV_increase.GetYaxis().SetLabelOffset(0.01)
        self.hist_HV_increase.GetXaxis().SetLabelSize(0.04)
        self.hist_HV_increase.GetYaxis().SetLabelSize(0.04)
        self.hist_HV_increase.GetYaxis().SetTitle("increase in voltage[V] (LG)")
        self.hist_HV_increase.GetXaxis().SetTitleOffset(0.5)
        self.hist_HV_increase.GetXaxis().SetTitleSize(0.08)
        self.hist_HV_increase.GetXaxis().SetTitle("module number")

        self.hist_HV_LG = ROOT.TH2F('LG HV per module [%s_%s]'%(self.partname,self.name),'low gain HV per module [%s_%s]'%(self.partname,self.name),\
                                    64,cadre_xmin,cadre_xmax ,400,cadre_ymin_LG,cadre_ymax_LG)
        self.hist_HV_LG.GetYaxis().SetTitleOffset(0.4)
        self.hist_HV_LG.GetYaxis().SetTitleSize(0.08)
        self.hist_HV_LG.GetXaxis().SetLabelOffset(0.03)
        self.hist_HV_LG.GetYaxis().SetLabelOffset(0.01)
        self.hist_HV_LG.GetXaxis().SetLabelSize(0.04)
        self.hist_HV_LG.GetYaxis().SetLabelSize(0.04)
        self.hist_HV_LG.GetYaxis().SetTitle("low gain voltage[V]")
        self.hist_HV_LG.GetXaxis().SetTitleOffset(0.5)
        self.hist_HV_LG.GetXaxis().SetTitleSize(0.08)
        self.hist_HV_LG.GetXaxis().SetTitle("module number")

        self.hist_HV_HG = ROOT.TH2F('HG HV per module [%s_%s]'%(self.partname,self.name),'high gain HV per module [%s_%s]'%(self.partname,self.name),\
                                    64,cadre_xmin,cadre_xmax ,400,cadre_ymin_HG,cadre_ymax_HG)
        self.hist_HV_HG.GetYaxis().SetTitleOffset(0.4)
        self.hist_HV_HG.GetYaxis().SetTitleSize(0.08)
        self.hist_HV_HG.GetXaxis().SetLabelOffset(0.03)
        self.hist_HV_HG.GetYaxis().SetLabelOffset(0.01)
        self.hist_HV_HG.GetXaxis().SetLabelSize(0.04)
        self.hist_HV_HG.GetYaxis().SetLabelSize(0.04)
        self.hist_HV_HG.GetYaxis().SetTitle("high gain voltage[V]")
        self.hist_HV_HG.GetXaxis().SetTitleOffset(0.5)
        self.hist_HV_HG.GetXaxis().SetTitleSize(0.08)
        self.hist_HV_HG.GetXaxis().SetTitle("module number")

        self.tgraph_HV_LG_increase         = ROOT.TGraphErrors()
        self.tgraph_HV_LG_increase_flagged = ROOT.TGraphErrors()
        self.tgraph_HV_HG_increase         = ROOT.TGraphErrors()
        self.tgraph_HV_HG_increase_flagged = ROOT.TGraphErrors()
        self.tgraph_HV_increase_phi_uni    = ROOT.TGraphErrors()

        self.tgraph_HV_LG                  = ROOT.TGraph()
        self.tgraph_HV_LG_flagged          = ROOT.TGraph()
        self.tgraph_HV_LG_possible         = ROOT.TGraphErrors()
        self.tgraph_HV_LG_possible_flagged = ROOT.TGraphErrors()

        self.tgraph_HV_HG                  = ROOT.TGraph()
        self.tgraph_HV_HG_flagged          = ROOT.TGraph()
        self.tgraph_HV_HG_possible         = ROOT.TGraphErrors()
        self.tgraph_HV_HG_possible_flagged = ROOT.TGraphErrors()

        resdir=getResultDirectory()
        f_HG = open('%s/%s_%s_HG_table'%(resdir,self.PMTool.get_partition_name(self.part-1),self.name), 'w')
        f_LG = open('%s/%s_%s_LG_table'%(resdir.PMTool.get_partition_name(self.part-1),self.name), 'w')
        f_HG.close()
        f_LG.close()
        f_HG = open('%s/%s_%s_HG_table'%(resdir.PMTool.get_partition_name(self.part-1),self.name), 'a')
        f_LG = open('%s/%s_%s_LG_table'%(resdir.PMTool.get_partition_name(self.part-1),self.name), 'a')

        for mod in range(1,65):
            max_sighg = 0.
            max_siglg = 0.
            HV_hg     = 0.
            HV_lg     = 0.
            HV_hg_db  = 0.
            HV_lg_db  = 0.
            max_HV_hg = 0.
            max_HV_lg = 0.
            LG_flag   = False
            HG_flag   = False

            f_cs_sum  = 0.
            f_cs_N    = 0.
            f_cs2_sum = 0.
            f_cs_ave  = 0.
            f_cs_err  = 0.

            max_LG = 0.
            max_HG = 0.
            for a in self.LG_evts:
                if a[1] != mod:
                    continue
                event = a[0]
                #print "LG event:",event.data
                if 'HVSet' in event.data:
                    if (event.data['HVSet'])!=0:
                        if max_LG < math.fabs(event.data['HV']):
                            max_LG = math.fabs(event.data['HV'])
                if 'f_cesium_db' in event.data:
                    f_cs_sum  += event.data['f_cesium_db']
                    f_cs_N    += 1.
                    f_cs2_sum += event.data['f_cesium_db'] * event.data['f_cesium_db']
                if 'signal' in event.data:
                    if max_siglg<math.fabs(event.data['signal']):
                        max_siglg = math.fabs(event.data['signal'])
                        HV_lg     = math.fabs(event.data['HVSet'])
                        HV_lg_db  = math.fabs(event.data['hv_db'])
                if 'status' in event.data:
                    if event.data['status']!=0 or 'problems' in event.data:
                        LG_flag = True
            if f_cs_N > 1:
                f_cs_ave = f_cs_sum / f_cs_N
                f_cs_err = math.sqrt(f_cs2_sum / (f_cs_N-1.) - f_cs_ave * f_cs_ave * f_cs_N / (f_cs_N-1.)) 
            if max_siglg != 0.:
                f_LG.write('%s \t %f \t %f \t %f \t %f \t %f \n'%\
                             (self.PMTool.get_pmt_name_index(self.PMTool.get_index(self.part-1,mod-1,self.chan,0)),max_siglg,HV_lg,\
                             max_HV_lg,HV_lg_db,pow(800./max_siglg,1./7.)*HV_lg))

                if line_HV_LG > pow(800./max_siglg,1./7.)*HV_lg-HV_lg:
                    if pow(800./max_siglg,1./7.)*HV_lg-HV_lg > 0.:
                        line_HV_LG = pow(800./max_siglg,1./7.)*HV_lg-HV_lg
                    else:
                        None #line_HV_LG = 0.
                if line_HV_LG_max < pow(800./max_siglg,1./7.)*HV_lg-HV_lg:
                    if pow(800./max_siglg,1./7.)*HV_lg-HV_lg > 0.:
                        line_HV_LG_max = pow(800./max_siglg,1./7.)*HV_lg-HV_lg
                    else:
                        None #line_HV_LG_max = 0.

                self.tgraph_HV_increase_phi_uni.SetPoint(mod,mod,50.*pow(f_cs_ave,1./7.))
                if f_cs_ave > 0:
                    self.tgraph_HV_increase_phi_uni.SetPointError(mod,mod,50./7.*pow(f_cs_ave,1./7.)*f_cs_err/f_cs_ave)

                if LG_flag:
                    self.tgraph_HV_LG_increase_flagged.SetPoint(mod,mod,pow(800./max_siglg,1./7.)*HV_lg-HV_lg)
                    self.tgraph_HV_LG_increase_flagged.SetPointError(mod,0.5,max(fabs(pow(800./max_siglg,1./7.)*HV_lg-pow(800./max_siglg,1./6.8)*HV_lg),\
                                                                                fabs(pow(800./max_siglg,1./7.)*HV_lg-pow(800./max_siglg,1./7.2)*HV_lg)))
                    self.tgraph_HV_LG_flagged.SetPoint(mod,mod,HV_lg)
                    self.tgraph_HV_LG_possible_flagged.SetPoint(mod,mod,pow(800./max_siglg,1./7.)*HV_lg)
                    self.tgraph_HV_LG_possible_flagged.SetPointError(mod,0.5,max(fabs(pow(800./max_siglg,1./7.)*HV_lg-pow(800./max_siglg,1./6.8)*HV_lg),\
                                                                                fabs(pow(800./max_siglg,1./7.)*HV_lg-pow(800./max_siglg,1./7.2)*HV_lg)))

                    self.tgraph_HV_LG_increase.SetPoint(mod,mod,-999.)
                    self.tgraph_HV_LG_increase.SetPointError(mod,0.5,-999.)
                    self.tgraph_HV_LG.SetPoint(mod,mod,-999.)
                    self.tgraph_HV_LG_possible.SetPoint(mod,mod,-999.)
                    self.tgraph_HV_LG_possible.SetPointError(mod,0.5,-999.)

                else:
                    self.tgraph_HV_LG_increase.SetPoint(mod,mod,pow(800./max_siglg,1./7.)*HV_lg-HV_lg)
                    self.tgraph_HV_LG_increase.SetPointError(mod,0.5,max(fabs(pow(800./max_siglg,1./7.)*HV_lg-pow(800./max_siglg,1./6.8)*HV_lg),\
                                                                        fabs(pow(800./max_siglg,1./7.)*HV_lg-pow(800./max_siglg,1./7.2)*HV_lg)))
                    self.tgraph_HV_LG.SetPoint(mod,mod,HV_lg)
                    self.tgraph_HV_LG_possible.SetPoint(mod,mod,pow(800./max_siglg,1./7.)*HV_lg)
                    self.tgraph_HV_LG_possible.SetPointError(mod,0.5,max(fabs(pow(800./max_siglg,1./7.)*HV_lg-pow(800./max_siglg,1./6.8)*HV_lg),\
                                                                        fabs(pow(800./max_siglg,1./7.)*HV_lg-pow(800./max_siglg,1./7.2)*HV_lg)))

                    self.tgraph_HV_LG_increase_flagged.SetPoint(mod,mod,-999.)
                    self.tgraph_HV_LG_increase_flagged.SetPointError(mod,0.5,-999.)
                    self.tgraph_HV_LG_flagged.SetPoint(mod,mod,-999.)
                    self.tgraph_HV_LG_possible_flagged.SetPoint(mod,mod,-999.)
                    self.tgraph_HV_LG_possible_flagged.SetPointError(mod,0.5,-999.)

            f_cs_sum  = 0.
            f_cs_N    = 0.
            f_cs2_sum = 0.
            f_cs_ave  = 0.
            f_cs_err  = 0.

            for a in self.HG_evts:
                if a[1] != mod:
                    continue
                event = a[0]
                if 'HVSet' in event.data:
                    if (event.data['HVSet'])!=0:
                        HV_hg = event.data['HVSet']
                        if max_HV_hg < math.fabs(event.data['HV']):
                            max_HV_hg = math.fabs(event.data['HV'])
                        if fabs(('HVSet' in event.data) - ('HV' in event.data)) > 10.:
                            HG_flag = True
                if 'f_cesium_db' in event.data:
                    f_cs_sum  += event.data['f_cesium_db']
                    f_cs_N    += 1.
                    f_cs2_sum += event.data['f_cesium_db'] * event.data['f_cesium_db']
                if 'signal' in event.data:
                    if max_sighg<math.fabs(event.data['signal']):
                        max_sighg = math.fabs(event.data['signal'])
                        HV_hg     = math.fabs(event.data['HVSet'])
                        HV_hg_db  = math.fabs(event.data['hv_db'])
                if 'status' in event.data:
                    if event.data['status']!=0 or 'problems' in event.data:
                        HG_flag = True
            if f_cs_N > 1:
                f_cs_ave = f_cs_sum / f_cs_N
                f_cs_err = math.sqrt(f_cs2_sum / (f_cs_N-1.) - f_cs_ave * f_cs_ave * f_cs_N / (f_cs_N-1.)) 

            if max_sighg != 0.:
                f_HG.write('%s \t %f \t %f \t %f \t %f \t %f \n'%\
                             (self.PMTool.get_pmt_name_index(self.PMTool.get_index(self.part-1,mod-1,self.chan,0)),max_sighg,HV_hg,\
                             max_HV_hg,HV_hg_db,pow(800./max_sighg,1./7.)*HV_hg))

                if HG_flag:
                    self.tgraph_HV_HG_increase_flagged.SetPoint(mod,mod,cadre_hl_ratio*(pow(800./max_sighg,1./7.)*HV_hg-HV_hg))
                    self.tgraph_HV_HG_increase_flagged.SetPointError(mod,0.5,max(fabs(pow(800./max_sighg,1./7.)*HV_hg-pow(800./max_sighg,1./6.8)*HV_hg),\
                                                                                fabs(pow(800./max_sighg,1./7.)*HV_hg-pow(800./max_sighg,1./7.2)*HV_hg)))
                    self.tgraph_HV_HG_flagged.SetPoint(mod,mod,HV_hg)
                    self.tgraph_HV_HG_possible_flagged.SetPoint(mod,mod,pow(800./max_sighg,1./7.)*HV_hg)
                    self.tgraph_HV_HG_possible_flagged.SetPointError(mod,0.5,max(fabs(pow(800./max_sighg,1./7.)*HV_hg-pow(800./max_sighg,1./6.8)*HV_hg),\
                                                                                fabs(pow(800./max_sighg,1./7.)*HV_hg-pow(800./max_sighg,1./7.2)*HV_hg)))

                    self.tgraph_HV_HG_increase.SetPoint(mod,mod,-999.)
                    self.tgraph_HV_HG_increase.SetPointError(mod,0.5,-999.)
                    self.tgraph_HV_HG.SetPoint(mod,mod,-999.)
                    self.tgraph_HV_HG_possible.SetPoint(mod,mod,-999.)
                    self.tgraph_HV_HG_possible.SetPointError(mod,0.5,-999.)
                else:
                    self.tgraph_HV_HG_increase.SetPoint(mod,mod,cadre_hl_ratio*(pow(800./max_sighg,1./7.)*HV_hg-HV_hg))
                    self.tgraph_HV_HG_increase.SetPointError(mod,0.5,max(fabs(pow(800./max_sighg,1./7.)*HV_hg-pow(800./max_sighg,1./6.8)*HV_hg),\
                                                                        fabs(pow(800./max_sighg,1./7.)*HV_hg-pow(800./max_sighg,1./7.2)*HV_hg)))
                    self.tgraph_HV_HG.SetPoint(mod,mod,HV_hg)
                    self.tgraph_HV_HG_possible.SetPoint(mod,mod,pow(800./max_sighg,1./7.)*HV_hg)
                    self.tgraph_HV_HG_possible.SetPointError(mod,0.5,max(fabs(pow(800./max_sighg,1./7.)*HV_hg-pow(800./max_sighg,1./6.8)*HV_hg),\
                                                                        fabs(pow(800./max_sighg,1./7.)*HV_hg-pow(800./max_sighg,1./7.2)*HV_hg)))

                    self.tgraph_HV_HG_increase_flagged.SetPoint(mod,mod,-999.)
                    self.tgraph_HV_HG_increase_flagged.SetPointError(mod,0.5,-999.)
                    self.tgraph_HV_HG_flagged.SetPoint(mod,mod,-999.)
                    self.tgraph_HV_HG_possible_flagged.SetPoint(mod,mod,-999.)
                    self.tgraph_HV_HG_possible_flagged.SetPointError(mod,0.5,-999.)
        for tgraph in [self.tgraph_HV_LG_increase,self.tgraph_HV_HG_increase,self.tgraph_HV_LG,\
                       self.tgraph_HV_LG_possible,self.tgraph_HV_HG,self.tgraph_HV_HG_possible]:
            tgraph.Sort()
            tgraph.SetMarkerColor(4)
        for tgraph in [self.tgraph_HV_LG_increase_flagged,self.tgraph_HV_HG_increase_flagged,self.tgraph_HV_LG_flagged,\
                       self.tgraph_HV_LG_possible_flagged,self.tgraph_HV_HG_flagged,self.tgraph_HV_HG_possible_flagged]:
            tgraph.Sort()
            tgraph.SetMarkerColor(2)
        for tgraph in [self.tgraph_HV_increase_phi_uni]:
            tgraph.Sort()
            tgraph.SetMarkerColor(8)
            tgraph.SetMarkerStyle(26)
        for tgraph in [self.tgraph_HV_LG_increase,self.tgraph_HV_LG,self.tgraph_HV_HG,\
                       self.tgraph_HV_LG_increase_flagged,self.tgraph_HV_LG_flagged,self.tgraph_HV_HG_flagged]:
            tgraph.SetMarkerStyle(29)
        for tgraph in [self.tgraph_HV_HG_increase,self.tgraph_HV_LG_possible,self.tgraph_HV_HG_possible,\
                       self.tgraph_HV_HG_increase_flagged,self.tgraph_HV_LG_possible_flagged,self.tgraph_HV_HG_possible_flagged]:
            tgraph.SetMarkerStyle(27)

        f_LG.close()
        f_HG.close()

        self.c1.Clear()
        self.c1.cd()
        self.c1.Divide(1,3)
        self.c1.cd(1)
        self.c1.cd(1).SetTicks(0,0)
        self.hist_HV_increase.Draw()
        legend1 = ROOT.TLegend(0.2,0.62,0.41,0.79)
        legend1.AddEntry(self.tgraph_HV_LG_increase,"HV increase LG (no. 6)","p")
        legend1.AddEntry(self.tgraph_HV_HG_increase,"HV increase HG (no. 8)","p")
        legend1.AddEntry(self.tgraph_HV_increase_phi_uni,"HV increase to absorb Cs constants")
        legend1.Draw()
        for tgraph in [self.tgraph_HV_LG_increase, self.tgraph_HV_HG_increase,self.tgraph_HV_LG_increase_flagged,self.tgraph_HV_HG_increase_flagged,self.tgraph_HV_increase_phi_uni]:
            if tgraph.GetN()>0:
                tgraph.Draw("P,same")
        axis = ROOT.TGaxis(cadre_xmax, cadre_ymin, cadre_xmax, cadre_ymax, cadre_ymin , cadre_ymax/cadre_hl_ratio,506,"+L" )
        axis.SetTitleFont(self.hist_HV_increase.GetTitleFont())
        axis.SetTitleSize(self.hist_HV_increase.GetTitleSize())
        axis.SetTitleOffset(self.hist_HV_increase.GetTitleOffset())
        axis.SetLabelSize(0.04)
        axis.SetLabelFont(self.hist_HV_increase.GetLabelFont())
        axis.SetTitle("increase in voltage[V] (HG)")
        axis.Draw()

        self.c1.cd(2)
        self.c1.cd(2).SetTicks(0,0)
        self.hist_HV_LG.Draw()
        legend2 = ROOT.TLegend(0.2,0.62,0.41,0.79)
        legend2.AddEntry(self.tgraph_HV_LG,         "LG voltage (filter 6)","p")
        legend2.AddEntry(self.tgraph_HV_LG_possible,"possible LG voltage","p")
        legend2.Draw()
        for tgraph in [self.tgraph_HV_LG,self.tgraph_HV_LG_possible,self.tgraph_HV_LG_flagged,self.tgraph_HV_LG_possible_flagged]:
            if tgraph.GetN()>0:
                tgraph.Draw("P,same")

        self.c1.cd(3)
        self.c1.cd(3).SetTicks(0,0)
        self.hist_HV_HG.Draw()
        legend3 = ROOT.TLegend(0.2,0.62,0.41,0.79)
        legend3.AddEntry(self.tgraph_HV_HG,         "HG voltage (filter 8)","p")
        legend3.AddEntry(self.tgraph_HV_HG_possible,"possible HG voltage","p")
        legend3.Draw()
        for tgraph in [self.tgraph_HV_HG, self.tgraph_HV_HG_possible,self.tgraph_HV_HG_flagged,self.tgraph_HV_HG_possible_flagged]:
            if tgraph.GetN()>0:
                tgraph.Draw("P,same")

        self.c1.cd()

        # hack
        self.c1.SetLeftMargin(0.14)
        self.c1.SetRightMargin(0.14)
        self.c1.Modified()
        self.c1.Update()

        self.plot_name = "cell_%s_%s_possible_HV_increase"%(self.PMTool.get_partition_name(self.part-1),self.name)
        ROOT.gStyle.SetPaperSize(26,20)
        self.c1.Print("%s/%s.eps" % (self.dir, self.plot_name))

        self.c2.Clear()
        self.c2.cd()
        self.hist_HV_increase.GetYaxis().SetTitleOffset(1.0)
        self.hist_HV_increase.GetYaxis().SetTitleSize(0.04)
        self.hist_HV_increase.GetXaxis().SetLabelOffset(0.03)
        self.hist_HV_increase.GetYaxis().SetLabelOffset(0.01)
        self.hist_HV_increase.GetYaxis().SetRangeUser(0.,self.hist_HV_increase.GetYaxis().GetXmax()/1.5)
        self.hist_HV_increase.GetXaxis().SetLabelSize(0.04)
        self.hist_HV_increase.GetYaxis().SetLabelSize(0.04)
        self.hist_HV_increase.GetYaxis().SetTitle("increase in voltage[V] (LG)")
        self.hist_HV_increase.GetXaxis().SetTitleOffset(1.0)
        self.hist_HV_increase.GetXaxis().SetTitleSize(0.04)
        self.hist_HV_increase.GetXaxis().SetTitle("module number")
        self.hist_HV_increase.Draw()
        legend4 = ROOT.TLegend(0.2,0.7,0.41,0.79)
        legend4.AddEntry(self.tgraph_HV_LG_increase,"LG voltage (filter 6)","p")
        legend4.AddEntry(self.tgraph_HV_LG_increase_flagged,"problematic module","p")
        legend4.Draw()
        if self.tgraph_HV_LG_increase.GetN()>0:
            self.tgraph_HV_LG_increase.Draw("P,same")
        if self.tgraph_HV_LG_increase_flagged.GetN()>0:
            self.tgraph_HV_LG_increase_flagged.Draw("P,same")
        line1 = ROOT.TF1("line1","[0]",-1.,66.)#0.,line_HV_LG,65.,line_HV_LG)
        line1.SetParameter(0,line_HV_LG)
        line1.SetLineColor(2)
        line1.SetLineWidth(2)
        line1.SetLineStyle(7)
        line1.Draw("SAME")
        line2 = ROOT.TF1("line2","[0]",-1.,66.)#0.,line_HV_LG,65.,line_HV_LG)
        line2.SetParameter(0,line_HV_LG_max)
        line2.SetLineColor(2)
        line2.SetLineWidth(2)
        line2.SetLineStyle(7)
        line2.Draw("SAME")
        self.plot_name = "cell_%s_%s_HV_LG_increase"%(self.PMTool.get_partition_name(self.part-1),self.name)
        ROOT.gStyle.SetPaperSize(26,20)
        self.c2.Print("%s/%s.eps" % (self.dir, self.plot_name))

        self.hist_HV_increase.Delete()

        for tgraph in [self.tgraph_HV_LG_increase,self.tgraph_HV_HG_increase,self.tgraph_HV_LG,self.tgraph_HV_LG_possible,self.tgraph_HV_HG,self.tgraph_HV_HG_possible]:
            tgraph.Delete()
        self.hist_HV_LG.Delete()
        self.hist_HV_HG.Delete()
