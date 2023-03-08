############################################################
#
# do_henrics_plot.py
#
############################################################
#
# Author: Henric Wilkens
#
# Mai 3rd, 2011
#

#
############################################################

from src.GenericWorker import *
from src.oscalls import *
import ROOT

class do_henrics_plot(GenericWorker):
    "Produce plots for diferrent tilecal samplings."


    def __init__(self, runType='Las'):
        self.runType   = runType

        self.drawer_list = []
        for i in range(256):
            self.drawer_list.append([])

        self.PMTool = LaserTools()        
        self.mean  = []
        self.rms   = []
        self.hist  = []
        self.hists = []
        self.part_name = ["LBA", "LBC", "EBA", "EBC"]
        self.gain  = 0

        self.outputTag = outputTag # global variable to tag output histogram file name
        self.dir    = getPlotDirectory(subdir=self.outputTag)


    def ProcessStart(self):
        
        for i_part in range(4):
            print("ProcessStart for part ",i_part)
            if  i_part == 0 or i_part == 1:
                self.hists.append(ROOT.TH1F(self.part_name[i_part]+"_A",self.part_name[i_part]+"_A" , 50, -5., 5.))
                self.hists.append(ROOT.TH1F(self.part_name[i_part]+"_BC",self.part_name[i_part]+"_BC" , 50, -5., 5.))
                self.hists.append(ROOT.TH1F(self.part_name[i_part]+"_D",self.part_name[i_part]+"_D" , 50, -5., 5.))

            if i_part == 2 or i_part == 3:
                self.hists.append(ROOT.TH1F(self.part_name[i_part]+"_A",self.part_name[i_part]+"_A" , 50, -5., 5.))
                self.hists.append(ROOT.TH1F(self.part_name[i_part]+"_B",self.part_name[i_part]+"_B" , 50, -5., 5.))
                self.hists.append(ROOT.TH1F(self.part_name[i_part]+"_C",self.part_name[i_part]+"_C" , 50, -5., 5.))
                self.hists.append(ROOT.TH1F(self.part_name[i_part]+"_D",self.part_name[i_part]+"_D" , 50, -5., 5.))
                self.hists.append(ROOT.TH1F(self.part_name[i_part]+"_E",self.part_name[i_part]+"_E" , 50, -5., 5.))
            
#            self.mean.append(ROOT.TH1F(self.part_name[i_part]+" MEAN",self.part_name[i_part]+" MEAN", 50, -5., 5.))
#            self.rms.append(ROOT.TH1F(self.part_name[i_part]+" RMS",self.part_name[i_part]+" RMS" , 50, 0, 5.))


        


    def ProcessRegion(self, region):

        for event in region.GetEvents():
            if event.run.runType == 'Las':
                if 'is_OK' not in event.data:
                    continue
                if event.data['is_OK'] and 'deviation' in event.data:
                    [part_num, mod, chan, gain] = region.GetNumber()
                    index = 64*(part_num-1)+ (mod-1)
                    self.drawer_list[index].append(event)
                    self.gain=gain
        

    def ProcessStop(self):

        self.do_canvas()
        
        for i_part in range(4):
            for i_drawer in range(64):
                drawer_events = self.drawer_list[64*i_part+i_drawer]

                if len(drawer_events) == 0:
                    continue

                

                pmt_list    = []                
                for i in range(48):
                    pmt_list.append([])
                    
                
                for event in drawer_events:
                    [part_num, module, pmt, gain] = event.region.GetNumber()
                    part_num -= 1
                    pmt_list[pmt].append(event)

                for i_pmt in range(48):
                    if self.PMTool.is_instrumented(i_part,i_drawer,i_pmt+1) == False:
                        continue
                    
                    pmt_events   = pmt_list[i_pmt]
                    if len(pmt_events) == 0:
                        continue
                    histname = "%s%02d_%02d" % (self.part_name[i_part],i_drawer+1,i_pmt+1)
                    
                    hist = ROOT.TH1F(hitname,'', 100, -10., 10.)
                    self.hist.append(hist)

                    for event in pmt_events:
                        if event.data['is_OK'] and 'deviation' in event.data and 'problems' not in event.data:
                            hist.Fill(event.data['deviation'])

                    layer = self.PMTool.get_pmt_layer(i_part,i_drawer+1,i_pmt+1)
                    hist = ROOT.gDirectory.FindObject("%s_%s" % (self.part_name[i_part],layer))

                    if layer!='':                    
                        for event in pmt_events:
                            if event.data['is_OK'] and 'deviation' in event.data and 'problems' not in event.data:
                                hist.Fill(event.data['deviation'])
#                    else:
#                        print "Null layer for: ",i_part,i_drawer+1,i_pmt+1


#            print "Mean for ", self.part_name[i_part], ": ", self.mean[i_part].GetMean()
#            print "Rms  for ", self.part_name[i_part], ": ", self.rms[i_part].GetMean()

#            self.c2.cd(i_part+1)
#            self.mean[i_part].Draw()



        i=0
        for hist in self.hists:
            i+=1
            self.c2.cd(i).SetLogy()
            hist.Draw()
                    
        self.c2.Print("%s/Henric_gain%d.png" % (self.dir,self.gain))

            
    def do_canvas(self):
        c_w = 1100
        c_h = 900
        
        ROOT.gStyle.SetOptStat(1)
        ROOT.gStyle.SetOptFit()
        ROOT.gStyle.SetStatX(0.78)
        ROOT.gStyle.SetStatY(0.83)

        self.c2 = ROOT.TCanvas("PartitionLayer", "Partition layer CANVAS", c_w, c_h)
        self.c2.SetWindowSize(2*c_w - self.c2.GetWw(), 2*c_h - self.c2.GetWh())
        
        self.c2.Range(0,0,1,1)
        self.c2.SetFillColor(0)
        self.c2.SetBorderMode(0)

        self.c2.cd()
        self.c2.Divide(4,4)
