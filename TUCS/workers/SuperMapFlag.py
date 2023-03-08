########################################################################################
# Author : Jeff Shahinian <jeffrey.david.shahinian@cern.ch>                            #
# Date   : November, 2013                                                              #
#                                                                                      #
# This worker produces a map of channels failing CIS flags, Laser flags, and both.     # 
# The flags in question are determined by the user-input to the SuperStudyFlags macro. #
# If no channels fail CIS or no channels fail Laser, then no plots are produced.       #
# You should not use --printopt 'Print_All' when producing these plots.                #
########################################################################################

from src.GenericWorker import *
from array import *
import ROOT
import src.MakeCanvas
from array import array
import src.oscalls
import os.path

class SuperMapFlag(GenericWorker):
    "This worker produces a map of bad Laser and CIS channels"

    def __init__(self,cis_flag = 'DB Deviation',las_flag = 'all', plotdirectory = None, region = None):

        self.c4            = src.MakeCanvas.MakeCanvas()
        self.graphs0       = [ROOT.TH2D('graphs0','',64,1,65,48,0,48) for i in range(4)]  # Lowgain plots
        self.graphs1       = [ROOT.TH2D('graphs1','',64,1,65,48,0,48) for i in range(4)]  # Highgain plots
        self.region        = region
        self.plotdirectory = plotdirectory
        self.cis_flag      = cis_flag
        self.las_flag      = las_flag[0]
        self.dir           = src.oscalls.getPlotDirectory()
        self.dir           = os.path.join(self.dir, 'CombinedFlags', self.plotdirectory, self.cis_flag+'_'+self.las_flag)
        self.x             = 0
        self.y             = 0
        self.colors        = array('i',[2,800,1]) #Set the Bad CIS, Bad Laser, and Bad CIS and Laser colors, respectively
        
        src.oscalls.createDir(self.dir)

    def ProcessStart(self):

        global bad_las_list
        global bad_cis_list

        try:
            bad_las_list
            self.bad_las_list = bad_las_list
        except:
            print('NO BAD LASER CHANNELS - NOT PRODUCING PLOTS')
            self.bad_las_list = []
        try:
            bad_cis_list
            self.bad_cis_list = bad_cis_list
        except:
            print('NO BAD CIS CHANNELS - NOT PRODUCING PLOTS')
            self.bad_cis_list = []

        for cis_entry in self.bad_cis_list: # Fill bad CIS bins
            if   cis_entry["partition"] == 'LBA': self.y = 0
            elif cis_entry["partition"] == 'LBC': self.y = 1
            elif cis_entry["partition"] == 'EBA': self.y = 2
            elif cis_entry["partition"] == 'EBC': self.y = 3

            if 'lowgain' in cis_entry["gain"]:
                self.graphs0[self.y].SetBinContent(cis_entry["module"], cis_entry["channel"]+1,0.1)
            if 'highgain' in cis_entry["gain"]:
                self.graphs1[self.y].SetBinContent(cis_entry["module"], cis_entry["channel"]+1,0.1)

        for las_entry in self.bad_las_list: # Fill bad Laser bins
            if   las_entry["partition"] == 'LBA': self.x = 0
            elif las_entry["partition"] == 'LBC': self.x = 1
            elif las_entry["partition"] == 'EBA': self.x = 2
            elif las_entry["partition"] == 'EBC': self.x = 3
            
            if 'lowgain' in las_entry["gain"]:
                self.graphs0[self.x].SetBinContent(las_entry["module"], las_entry["channel"]+1,0.5)
            if 'highgain' in las_entry["gain"]:
                self.graphs1[self.x].SetBinContent(las_entry["module"], las_entry["channel"]+1,0.5)
            if 'both' in las_entry["gain"]:
                self.graphs0[self.x].SetBinContent(las_entry["module"], las_entry["channel"]+1,0.5)
                self.graphs1[self.x].SetBinContent(las_entry["module"], las_entry["channel"]+1,0.5)

        print(('Channels Failing CIS (%s) and Laser (%s):' % (self.cis_flag,self.las_flag)))
        for las_entry in self.bad_las_list: # Fill bad CIS and Laser bins
            for cis_entry in self.bad_cis_list:
                if   las_entry["partition"] == 'LBA': self.x = 0
                elif las_entry["partition"] == 'LBC': self.x = 1
                elif las_entry["partition"] == 'EBA': self.x = 2
                elif las_entry["partition"] == 'EBC': self.x = 3

                if cis_entry["partition"]   == las_entry["partition"] and \
                       cis_entry["module"]  == las_entry["module"]    and \
                       cis_entry["channel"] == las_entry["channel"]   and \
                       cis_entry["gain"]    == las_entry["gain"]:
                    print(("%s_m%s_c%s_%s" % (cis_entry["partition"],\
                                             str("%02d"%cis_entry["module"]),\
                                             str("%02d"%cis_entry["channel"]),\
                                             cis_entry["gain"])))
                    if 'lowgain' in cis_entry["gain"]:
                        self.graphs0[self.x].SetBinContent(cis_entry["module"], cis_entry["channel"]+1,1.0)
                    if 'highgain' in cis_entry["gain"]:
                        self.graphs1[self.x].SetBinContent(cis_entry["module"], cis_entry["channel"]+1,1.0)
                        
                
        self.c4.cd()
        ROOT.gStyle.SetOptStat(0)
        ROOT.TColor.CreateColorWheel        
        ROOT.gStyle.SetPalette(3, self.colors)
        self.c4.SetLeftMargin(0.14)
        self.c4.SetRightMargin(0.05)

        for i in range(4):
            if   i == 0: name = 'LBA'
            elif i == 1: name = 'LBC'
            elif i == 2: name = 'EBA'
            elif i == 3: name = 'EBC'

            for region in self.region:
                if name in region:
                    graph0 = self.graphs0[i]
                    graph0.SetMaximum(1.0)
                    graph0.GetXaxis().SetTitle("Module")
                    graph0.GetYaxis().SetTitle("Channel number")
                    graph0.Draw("COL")
                
                    cis_box0 = ROOT.TBox(1,1,1,1)     #Dummy box to give attributes to Legend
                    cis_box0.SetFillColor(ROOT.kRed)
                    las_box0 = ROOT.TBox(1,1,1,1)     #Dummy box to give attributes to Legend
                    las_box0.SetFillColor(ROOT.kOrange)
                    both_box0 = ROOT.TBox(1,1,1,1)    #Dummy box to give attributes to Legend
                    both_box0.SetFillColor(ROOT.kBlack)
                    leg0 = ROOT.TLegend(0.4, 0.9507, 1.0, 1.0, "", "brNDC")
                    leg0.SetNColumns(3)
                    leg0.SetBorderSize(0)
                    leg0.SetFillColor(0)
                    leg0.AddEntry(cis_box0, "Bad CIS", "f")
                    leg0.AddEntry(las_box0, "Bad Laser", "f")
                    leg0.AddEntry(both_box0, "Bad CIS and Laser", "f")
                    leg0.Draw()                
        
                    pt = ROOT.TPaveText(0.1017812,0.96,0.3053435,1.0, "brNDC")
                    pt.AddText("%s Low Gain Status" % name)
                    pt.SetBorderSize(0)
                    pt.SetFillColor(0)
                    pt.Draw()
                        
                    self.c4.Print("%s/%s_CombinedMapFlag_lowgain.eps" % (self.dir, name))

                    graph1 = self.graphs1[i]
                    graph1.SetMaximum(1.0)
                    graph1.SetFillColor(0)
                    graph1.GetXaxis().SetTitle("Module")
                    graph1.GetYaxis().SetTitle("Channel number")
                    graph1.Draw("COL")

                    cis_box1 = ROOT.TBox(1,1,1,1)     #Dummy box to give attributes to Legend
                    cis_box1.SetFillColor(ROOT.kRed)
                    las_box1 = ROOT.TBox(1,1,1,1)     #Dummy box to give attributes to Legend
                    las_box1.SetFillColor(ROOT.kOrange)
                    both_box1 = ROOT.TBox(1,1,1,1)    #Dummy box to give attributes to Legend
                    both_box1.SetFillColor(ROOT.kBlack)
                    leg1 = ROOT.TLegend(0.4, 0.9507, 1.0, 1.0, "", "brNDC")
                    leg1.SetNColumns(3)
                    leg1.SetBorderSize(0)
                    leg1.SetFillColor(0)
                    leg1.AddEntry(cis_box1, "Bad CIS", "f")
                    leg1.AddEntry(las_box1, "Bad Laser", "f")
                    leg1.AddEntry(both_box1, "Bad CIS and Laser", "f")
                    leg1.Draw()
        
                    pt = ROOT.TPaveText(0.1017812,0.96,0.3053435,1.0, "brNDC")
                    pt.AddText("%s High Gain Status" % name)
                    pt.SetBorderSize(0)
                    pt.SetFillColor(0)
                    pt.Draw()

                    self.c4.Print("%s/%s_CombinedMapFlag_highgain.eps" % (self.dir, name))

        self.c4.Clear()

    def ProcessRegion(self, region):
        pass

    def ProcessStop(self):
        pass 

        
