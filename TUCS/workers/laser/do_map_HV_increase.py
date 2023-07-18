############################################################
#
# do_map_HV_increase.py
#
############################################################
#
# Author: Marco van Woerden (13/07/2012)
#
# Output:
# Calculates theoretical possible HV increase for the PMTs.
# The dynamical range is determined by the properties of the PMTs.
#
# Input parameters are:
# -> part: the partition number (1=LBA, 2=LBC, 3=EBA, 4=EBC) you want to plot.
#
# For more info on the LASER system : http://atlas-tile-laser.web.cern.ch
#
#############################################################

from src.GenericWorker import *
from src.oscalls import *
import src.MakeCanvas

class do_map_HV_increase(GenericWorker):
    "Calculate theoretical possible HV increase for the PMTs."

    c1 = None
    c2 = None

    def __init__(self,  part=1):
        self.part     = part
        self.mod      = -1
        self.chan     = -1
        self.PMTool   = LaserTools()
        self.LG_evts  = list() # Events with low gain info
        self.HG_evts  = list() # Events with high gain info
        self.lowest_signals = []

        self.outputTag = outputTag # global variable to tag output histogram file name
        self.dir    = getPlotDirectory(subdir=self.outputTag)

        if self.c1==None:
            self.c1 = src.MakeCanvas.MakeCanvas()
            #self.c1.SetTitle("Put here a nice title")

        if self.c2==None:
            self.c2 = src.MakeCanvas.MakeCanvas()
            #self.c2.SetTitle("Put here a nice title")


    def ProcessStart(self):
        global run_list

    def ProcessRegion(self, region):

        numbers = region.GetNumber()

        if len(numbers)!=4:
            return

        [part, module, chan, gain] = numbers        

        ind       = self.PMTool.get_index(part-1, module-1, chan, 0)

        match_found = False
        for mod in range(1,65):
            for ch in range(1,48):
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
        self.c1.Divide(2,3)

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

        self.h2Dhist_HV_LG_increase         = ROOT.TH2D("2Dhist_HV_LG_increase","possible HV increase (LG)",64,1,65,47,1,48)
        self.h2Dhist_HV_HG_increase         = ROOT.TH2D("2Dhist_HV_HG_increase","possible HV increase (HG)",64,1,65,47,1,48)
        self.h2Dhist_HV_LG                  = ROOT.TH2D("2Dhist_HV_LG","low gain HV",64,1,65,47,1,48)
        self.h2Dhist_HV_LG_possible         = ROOT.TH2D("2Dhist_HV_LG_possible","possible low gain HV",64,1,65,47,1,48)
        self.h2Dhist_HV_HG                  = ROOT.TH2D("2Dhist_HV_HG","high gain HV",64,1,65,47,1,48)
        self.h2Dhist_HV_HG_possible         = ROOT.TH2D("2Dhist_HV_HG_possible","possible high gain HV",64,1,65,47,1,48)
        for hist in [self.h2Dhist_HV_LG_increase,self.h2Dhist_HV_HG_increase,self.h2Dhist_HV_LG,\
                     self.h2Dhist_HV_LG_possible,self.h2Dhist_HV_HG,self.h2Dhist_HV_HG_possible]:
            hist.GetXaxis().SetTitle("module number")
            hist.GetYaxis().SetTitle("channel number")
            hist.GetZaxis().SetTitle("voltage [V]")
            hist.GetYaxis().SetTitleOffset(0.8)
            hist.GetYaxis().SetTitleSize(0.08)
            hist.GetYaxis().SetLabelOffset(0.01)
            hist.GetYaxis().SetLabelSize(0.04)
            hist.GetXaxis().SetLabelOffset(0.03)
            hist.GetXaxis().SetLabelSize(0.04)
            hist.GetXaxis().SetTitleOffset(0.8)

        resdir = getResultDirectory()
        f_HG = open('%s/%s_HG_table'% (resdir,self.PMTool.get_partition_name(self.part-1)), 'w')
        f_LG = open('%s/%s_LG_table'% (resdir,self.PMTool.get_partition_name(self.part-1)), 'w')
        f_HG.close()
        f_LG.close()
        f_HG = open('%s/%s_HG_table'% (resdir,self.PMTool.get_partition_name(self.part-1)), 'a')
        f_LG = open('%s/%s_LG_table'% (resdir,self.PMTool.get_partition_name(self.part-1)), 'a')

        for mod in range(1,65):
            for ch in range(1,48):
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

                for a in self.LG_evts:
                    if a[1] != mod or a[2] != ch:
                        continue
                    event = a[0]
                    if 'HVSet' in event.data:
                        if (event.data['HVSet'])!=0:
                            HV_lg = event.data['HVSet']
                            if max_HV_lg < math.fabs(event.data['HV']):
                                max_HV_lg = math.fabs(event.data['HV'])
                            if fabs(('HVSet' in event.data) - ('HV' in event.data)) > 10.:
                                LG_flag = True
                    if 'signal' in event.data:
                        if max_siglg<math.fabs(event.data['signal']):
                            max_siglg = math.fabs(event.data['signal'])
                            HV_lg     = math.fabs(event.data['HVSet'])
                            HV_lg_db  = math.fabs(event.data['hv_db'])
                        if len(self.lowest_signals) < 100 and \
                            [self.PMTool.get_pmt_name_index(self.PMTool.get_index(self.part-1,mod-1,ch,0)),math.fabs(event.data['signal'])] not in self.lowest_signals:
                            self.lowest_signals += [[self.PMTool.get_pmt_name_index(self.PMTool.get_index(self.part-1,mod-1,ch,0)),math.fabs(event.data['signal'])]]
                        elif [self.PMTool.get_pmt_name_index(self.PMTool.get_index(self.part-1,mod-1,ch,0)),math.fabs(event.data['signal'])] not in self.lowest_signals:
                            if math.fabs(event.data['signal']) < max(self.lowest_signals, key=lambda p: max(p[1:]))[1]:
                                self.lowest_signals.remove(max(self.lowest_signals, key=lambda p: max(p[1:])))
                                self.lowest_signals += [[self.PMTool.get_pmt_name_index(self.PMTool.get_index(self.part-1,mod-1,ch,0)),math.fabs(event.data['signal'])]]
                    if 'status' in event.data:
                        if event.data['status']!=0 or 'problems' in event.data:
                            LG_flag = True

                if max_siglg != 0.:
                    f_LG.write('%s \t %f \t %f \t %f \t %f \t %f \n'%\
                                 (self.PMTool.get_pmt_name_index(self.PMTool.get_index(self.part-1,mod-1,ch,0)),max_siglg,HV_lg,\
                                 max_HV_lg,HV_lg_db,pow(800./max_siglg,1./7.)*HV_lg))
                    if LG_flag:
                        self.h2Dhist_HV_LG_increase.Fill(mod,ch,-1.)
                        self.h2Dhist_HV_LG.Fill(mod,ch,-1.)
                        self.h2Dhist_HV_LG_possible.Fill(mod,ch,-1.)
                    else:
                        self.h2Dhist_HV_LG_increase.Fill(mod,ch,pow(800./max_siglg,1./7.)*HV_lg-HV_lg)
                        self.h2Dhist_HV_LG.Fill(mod,ch,HV_lg)
                        self.h2Dhist_HV_LG_possible.Fill(mod,ch,pow(800./max_siglg,1./7.)*HV_lg)

                for a in self.HG_evts:
                    if a[1] != mod or a[2] != ch:
                        continue
                    event = a[0]
                    if 'HVSet' in event.data:
                        if (event.data['HVSet'])!=0:
                            HV_hg = event.data['HVSet']
                            if max_HV_hg < math.fabs(event.data['HV']):
                                max_HV_hg = math.fabs(event.data['HV'])
                            if fabs(('HVSet' in event.data) - ('HV' in event.data)) > 10.:
                                HG_flag = True
                    if 'signal' in event.data:
                        if max_sighg<math.fabs(event.data['signal']):
                            max_sighg = math.fabs(event.data['signal'])
                            HV_hg     = math.fabs(event.data['HVSet'])
                            HV_hg_db  = math.fabs(event.data['hv_db'])
                    if 'status' in event.data:
                        if event.data['status']!=0 or 'problems' in event.data:
                            HG_flag = True

                if max_sighg != 0.:
                    f_HG.write('%s \t %f \t %f \t %f \t %f \t %f \n'%\
                                 (self.PMTool.get_pmt_name_index(self.PMTool.get_index(self.part-1,mod-1,self.chan,0)),max_sighg,HV_hg,\
                                 max_HV_hg,HV_hg_db,pow(800./max_sighg,1./7.)*HV_hg))
                    if HG_flag:
                        self.h2Dhist_HV_HG_increase.Fill(mod,ch,-1.)
                        self.h2Dhist_HV_HG.Fill(mod,ch,-1.)
                        self.h2Dhist_HV_HG_possible.Fill(mod,ch,-1.)
                    else:
                        self.h2Dhist_HV_HG_increase.Fill(mod,ch,pow(800./max_sighg,1./7.)*HV_hg-HV_hg)
                        self.h2Dhist_HV_HG.Fill(mod,ch,HV_hg)
                        self.h2Dhist_HV_HG_possible.Fill(mod,ch,pow(800./max_sighg,1./7.)*HV_hg)
        f_LG.close()
        f_HG.close()

        self.c1.cd(1)
        self.c1.cd(1).SetTicks(0,0)
        self.h2Dhist_HV_HG.Draw("colz")
        self.c1.cd(2)
        self.c1.cd(2).SetTicks(0,0)
        self.h2Dhist_HV_LG.Draw("colz")

        self.c1.cd(3)
        self.c1.cd(3).SetTicks(0,0)
        self.h2Dhist_HV_HG_possible.Draw("colz")
        self.c1.cd(4)
        self.c1.cd(4).SetTicks(0,0)
        self.h2Dhist_HV_LG_possible.Draw("colz")

        self.c1.cd(5)
        self.c1.cd(5).SetTicks(0,0)
        self.h2Dhist_HV_HG_increase.Draw("colz")
        self.c1.cd(6)
        self.c1.cd(6).SetTicks(0,0)
        self.h2Dhist_HV_LG_increase.Draw("colz")

        self.c1.cd()

        # hack
        self.c1.SetLeftMargin(0.14)
        self.c1.SetRightMargin(0.14)
        self.c1.Modified()
        self.c1.Update()

        self.plot_name = "tilemap_part_%s_possible_HV_increase"%(self.PMTool.get_partition_name(self.part-1))
        ROOT.gStyle.SetPaperSize(100,150)
        self.c1.Print("%s/%s.eps" % (self.dir, self.plot_name))


        self.c2.Clear()
        self.c2.cd()

        for hist in [self.h2Dhist_HV_LG_increase,self.h2Dhist_HV_HG_increase,self.h2Dhist_HV_LG,\
                     self.h2Dhist_HV_LG_possible,self.h2Dhist_HV_HG,self.h2Dhist_HV_HG_possible]:
            hist.Delete()
