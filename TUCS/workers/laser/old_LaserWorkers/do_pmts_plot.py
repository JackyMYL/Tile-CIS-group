############################################################
#
# do_pmts_plot.py
#
############################################################
#
# Author: Seb Viret <viret@in2p3.fr>
#
# August 20, 2009
#
# Goal: 
# Compute an history plot for the pmts of a drawer variations
#
# Input parameters are:
#
# -> part: the partition number (0=LBA, 1=LBC, 2=EBA, 3=EBC) you want to plot.
#          DEFAULT VAL = -1 : produces all the plots 
#
# -> drawer: the drawer number (from 0 to 64) you want to plot.
#            DEFAULT VAL = -1 : produces all the plots 
#
# -> limit: the maximum tolerable variation (in %). If this variation
#           is excedeed the plots will have a RED background
#
# -> nDays: how many days before the last run do you want to check the pmt variation
#          DEFAULT VAL = -1 : all the range
#
# -> doWiki: used by laser experts to update the status webpage
#
# -> doEps: provide eps plots in addition to default png graphics
#
# For more info on the LASER system : http://atlas-tile-laser.web.cern.ch
#
#############################################################



from src.GenericWorker import *
from src.oscalls import *
import ROOT
import time
import math

class do_pmts_plot(GenericWorker):
    "Compute history plot for the pmts of a drawer"

    def __init__(self, runType='Las', part=-1, drawer=-1, limit=2.0, doWiki=False, doEps = False, filter='6',nDays=-1):
        self.runType   = runType
        self.doWiki    = doWiki
        self.doEps     = doEps
        self.part      = part
        self.drawer    = drawer
        self.limit     = limit
        self.nDaysBef  = nDays
        
        self.outputTag = outputTag # global variable to tag output histogram file name
        self.dir    = getPlotDirectory(subdir=self.outputTag)

        if filter=='6':
            self.filter   = 6
        elif filter=='8':
            self.filter   = 8
        else:
            self.filter   = 0

        self.drawer_list = []
        self.run_list    = []
        self.n_run       = 0

        for i in range(256):
            self.drawer_list.append([])            

        self.PMTool   = LaserTools()
        self.origin   = ROOT.TDatime()
        self.time_max = 0
        self.time_min = 10000000000000000



    
    def ProcessRegion(self, region):
                          
        for event in region.GetEvents():
                                        
            if 'deviation' in event.data:

                [part_num, module, j, w] = region.GetNumber(1)

                part_num -= 1
                drawer = module-1
     
                if self.part != -1 and part_num != self.part: # if you just want one part
                    continue

                if self.drawer != -1 and drawer != self.drawer: 
                    continue
                
                index = 64*part_num+drawer
                self.drawer_list[index].append(event) 
                    
                if self.time_min>event.run.time_in_seconds:
                    self.time_min = event.run.time_in_seconds
                    self.origin = ROOT.TDatime(event.run.time)
                            
                if self.time_max<event.run.time_in_seconds:
                    self.time_max = event.run.time_in_seconds

                if event.run.time_in_seconds not in self.run_list:
                    self.run_list.append(event.run.time_in_seconds)


    def ProcessStop(self):


        # Write some info if requested

        if self.doWiki:

            if self.filter==6:
                self.file_name = "Laser_stab_history_lg.txt"
            elif self.filter==8:
                self.file_name = "Laser_stab_history_hg.txt"
            else:
                self.file_name = "Laser_stab_history.txt"
            self.wiki      = open(os.path.join(getResultDirectory(),self.file_name),"a")
            self.wiki.write("\n")
            self.wiki.write("!!!! PMT-level shifts\n")
            self.wiki.write("\n")
                
            text = "*Stability limit for PMT shifts is fixed at '''+/-%.1f%s'''\n"%(self.limit,"%")                
            self.wiki.write(text)
            self.wiki.write("\n")
                
        # Cosmetics (Part 1): the lines which shows the maximum acceptable variation

        self.line_down = ROOT.TLine(0,-self.limit,self.time_max-self.time_min+1,-self.limit)
        self.line_down.SetLineColor(4)
        self.line_down.SetLineWidth(2)
        
        self.line_up = ROOT.TLine(0,self.limit,self.time_max-self.time_min+1,self.limit);
        self.line_up.SetLineColor(4)
        self.line_up.SetLineWidth(2)

        self.nDaysBef = self.time_max - self.nDaysBef*86400
        
        c_w = 1100
        c_h = 900

        for r_time in self.run_list: # Number of runs in the window of interest
            if r_time >= self.nDaysBef:
                self.n_run += 1
        
        # Then we do the graphs for all the requested modules
                
        for i_part in range(4):

            if self.doWiki:
 
                self.wiki.write("\n")
                self.wiki.write("!!!!! %s partition\n"%(self.PMTool.get_partition_name(i_part)))
                self.wiki.write("\n")
                
                self.wiki.write("(:table align=center border=1 cellpadding=5 cellspacing=0 :)\n")
            
            if self.part != -1 and i_part != self.part: # if you just want one part
                print("skipping parts ", i_part, self.part)
                continue

            n_chan = 0
            n_warn = 0                
            n_bad  = 0
            n_unkn = 0

            for i_drawer in range(64):

                if self.drawer != -1 and i_drawer != self.drawer: 
                    continue
            
                self.c1 = ROOT.TCanvas("c1","acanvas",c_w,c_h)
                self.c1.SetWindowSize(2*c_w - self.c1.GetWw(), 2*c_h - self.c1.GetWh())
                
                self.c1.Range(0,0,1,1)
                self.c1.SetFillColor(0)
                self.c1.SetBorderMode(0)
                    
                self.c1.cd()
                self.c1.Divide(6,8)
                
                ROOT.gStyle.SetTimeOffset(self.origin.Convert());
                
                drawer_events = self.drawer_list[64*i_part+i_drawer]
                
                self.plot_name = "%s_history_%d" % (self.PMTool.get_module_name(i_part,i_drawer),self.filter)
                
                self.hhist  = []
                self.pt     = []
                n_pmt       = 0
                n_orange    = 0
                n_red       = 0
                n_black     = 0
                pmt_list    = []
                
                for i in range(48):
                    pmt_list.append([])

                for event in drawer_events:
                                              
                    #[part_num, module, channel, gain] = self.PMTool.GetNumber(event.data['region'])
                    [part_num, module, channel, gain] = event.region.GetNumber()
                    ros = part_num-1
                    drawer = module-1
                    pmt = self.PMTool.get_PMT_index(ros,drawer,channel)                                           
                    pmt_list[pmt-1].append(event)

                for i_pmt in range(48):

                    # Don't go further if the channel is not instrumented 
                    if self.PMTool.is_instrumented(i_part,i_drawer,i_pmt+1) == False:
                        #print i_part,"Hole ",i_pmt+1," is not instrumented"
                        continue

                    pmt_events   = pmt_list[i_pmt]
                    max_var      = 0
                    n_points     = 0
                    self.problem = False
                    
                    for event in pmt_events:
      
                        if max_var<math.fabs(event.data['deviation']):
                            max_var = math.fabs(event.data['deviation'])

                        # Look for an outing during the last days, this is annoying
                        if event.run.time_in_seconds > self.nDaysBef:
                            n_points+=1

                            if math.fabs(event.data['deviation']) > self.limit: 
                                self.problem = True

                    # Cosmetics (Part 2): the pmt graph itself
                        
                    graph_lim = max(1.1*max_var,5*self.limit)
                      
                    tmp = "PMT evolution %s" % ('(in %)')
                    histname = 'pmt_%0d' % (i_pmt+1)
                    
                    self.hhist.append(ROOT.TH2F(histname, '',\
                                                100, 0, self.time_max-self.time_min+1, 100, -graph_lim, graph_lim))

                    self.c1.cd(i_pmt+1).SetFrameFillColor(0)
                    self.c1.cd(i_pmt+1).SetLeftMargin(0.17);
                    self.c1.cd(i_pmt+1).SetRightMargin(0.13);
                    self.c1.cd(i_pmt+1).SetTopMargin(0.04);
                    self.c1.cd(i_pmt+1).SetBottomMargin(0.25);
                    
                    # Then we do the different channel classification

                    if max_var == 0 or n_points != self.n_run: # Missing or no data : this is very bad
                        self.c1.cd(i_pmt+1).SetFrameFillColor(14)
                        n_black += 1
                        n_unkn  += 1

                        
                    if max_var > self.limit and n_points == self.n_run and self.problem:  # Out of range : annoying...
                        self.c1.cd(i_pmt+1).SetFrameFillColor(796)
                        n_orange += 1
                        n_warn   += 1
                        
                        if max_var > 3*self.limit: # 3 sigma out of range : bad
                            self.c1.cd(i_pmt+1).SetFrameFillColor(623)
                            n_red += 1
                            n_bad += 1
                            n_orange -= 1
                            n_warn   -= 1
                            
                    self.hhist[n_pmt].GetXaxis().SetTimeDisplay(1)
                    self.hhist[n_pmt].GetXaxis().SetLabelOffset(0.1)
                    self.hhist[n_pmt].GetXaxis().SetLabelFont(42)
                    self.hhist[n_pmt].GetYaxis().SetTitleFont(42)
                    self.hhist[n_pmt].GetYaxis().SetLabelFont(42)                        
                    self.hhist[n_pmt].GetYaxis().SetTitleSize(0.1)
                    self.hhist[n_pmt].GetYaxis().SetTitleOffset(0.7)
                    self.hhist[n_pmt].GetXaxis().SetLabelSize(0.1)
                    self.hhist[n_pmt].GetYaxis().SetLabelSize(0.1)           
                    self.hhist[n_pmt].GetXaxis().SetTimeFormat("#splitline{%Y}{%d/%m}")
                    self.hhist[n_pmt].GetXaxis().SetNdivisions(-503)
                    self.hhist[n_pmt].GetYaxis().SetTitle(tmp)
                    self.hhist[n_pmt].SetMarkerStyle(20)
                    self.hhist[n_pmt].SetMarkerSize(.6);
                
                    for event in pmt_events: # fill the histogram
                    
                        self.hhist[n_pmt].Fill(event.run.time_in_seconds-self.time_min,event.data['deviation'])

                        #print i_pmt,n_pmt,event.data['deviation']

                            
                    # Then draw it...
                
                    self.c1.cd(i_pmt+1)
                    ROOT.gStyle.SetOptStat(0)
                    ROOT.gStyle.SetStatX(0.78)
                    ROOT.gStyle.SetStatY(0.83)
                    self.hhist[n_pmt].Draw()
                    self.line_up.Draw("same")
                    self.line_down.Draw("same")
                    
                    self.pt.append(ROOT.TPaveText(0.71,0.75,0.98,0.98,"brNDC"))
                    self.pt[n_pmt].SetFillColor(5)
                    self.pt[n_pmt].SetTextSize(0.13)
                    self.pt[n_pmt].SetTextFont(42)                        
                    self.pt[n_pmt].AddText("PMT %d" % (i_pmt+1))
                    self.pt[n_pmt].Draw()
                    
                    # hack
                    self.c1.cd(i_pmt+1).SetLeftMargin(0.14)
                    self.c1.cd(i_pmt+1).SetRightMargin(0.14)
                    self.c1.cd(i_pmt+1).Modified()

                    n_pmt += 1
                    n_chan+= 1

                name = self.PMTool.get_module_name(i_part,i_drawer);

                if self.doWiki:
                    self.wiki.write("(:cell")
                    if i_drawer%8 == 0:
                        self.wiki.write("nr")

                    if n_black > 30:
                        text_s = " width=90 id=BlackCell :) %newwin%[[Path:Images/Stability"
                    elif n_red > 0:
                        text_s = " width=90 id=RedCell :) %newwin%[[Path:Images/Stability"
                    elif n_orange > 0:
                        text_s = " width=90 id=OrangeCell :) %newwin%[[Path:Images/Stability"
                    else:
                        text_s = " width=90 id=GreenCell :) %newwin%[[Path:Images/Stability"

                    text = "%s/%d/%s.png|%s]] %d/%d/%d/%d\n"%(text_s,self.filter,self.plot_name,name,\
                                                                  n_pmt-n_red-n_orange-n_black,n_orange,n_red,n_black) 
                    self.wiki.write(text)
                    

                self.c1.cd()
                l = ROOT.TLatex()
                l.SetNDC()
                l.SetTextFont(72)
                l.DrawLatex(0.1922,0.32,"LASER")
                
                l2 = ROOT.TLatex()
                l2.SetNDC()
                l2.DrawLatex(0.1922,0.26,"Gain Variation")
                
                self.c1.Modified()  
                
                self.c1.Print("%s/%s.png" % (self.dir,self.plot_name))
                
                if self.doEps:
                    self.c1.Print("%s/%s.eps" % (self.dir,self.plot_name))
                #self.c1.Print("%s/%s.root" % (self.dir,self.plot_name))

                self.c1.Delete()

            if self.doWiki:
                self.wiki.write("(:tableend:)\n")
                self.wiki.write("\n")
                
                self.wiki.write("%d channels have been processed\\\\\n"%n_chan)
                self.wiki.write("%d channels have missing info\\\\\n"%n_unkn)
                self.wiki.write("%d channels have bad points \\\\\n"%n_bad)
                self.wiki.write("%d channels have slightly out of range points \\\\\n"%n_warn)
                self.wiki.write( "\n")
                self.wiki.write("\n")

        if self.doWiki:

            self.wiki.write( "\n")
            self.wiki.write( "...This page was generated automatically on '''%s'''...\n"%ROOT.TDatime().AsString())
            self.wiki.write( "\n")
            
            self.wiki.close()
