############################################################
#
# do_part_plot.py
#
############################################################
#
# Author: Seb Viret <viret@in2p3.fr>
#
# August 20, 2009
#
# Goal: 
# Compute an history plot for the partitions variation
#
# Input parameters are:
#
# -> part: the partition number (0=LBA, 1=LBC, 2=EBA, 3=EBC) you want to plot.
#         DEFAULT VAL = -1 : produces all the plots 
#
# -> limit: the maximum tolerable variation (in %). If this variation
#           is excedeed the plots will have a RED background
#
# -> doWiki: used by laser experts to update the status webpage
#
# -> doEps: provide eps plots in addition to default png graphics
#
# -> nDays: how many days before the last run do you want to check the partition
#          DEFAULT VAL = -1 : all the range
#
# For more info on the LASER system : http://atlas-tile-laser.web.cern.ch
#
#############################################################

from src.GenericWorker import *
from src.oscalls import *
import src.MakeCanvas
import time

class do_part_plot(GenericWorker):
    "Compute history plot"

    c1 = None
    
    def __init__(self, runType='Las', limit=1, part=-1, doWiki=False, doEps = False, filter = '6', nDays = -1):
        self.runType  = runType
        self.doWiki   = doWiki
        self.doEps    = doEps
        self.part     = part
        self.limit    = limit        
        self.events    = set()
        self.run_list  = []
        self.part_list = set()
        self.PMTool    = LaserTools()
        self.origin    = ROOT.TDatime()
        self.nDaysBef  = nDays

        self.outputTag = outputTag # global variable to tag output histogram file name
        self.dir    = getPlotDirectory(subdir=self.outputTag)

        self.time_max  = 0
        self.time_min  = 10000000000000000
        
        if filter=='6':
            self.filter   = 6
        elif filter=='8':
            self.filter   = 8
        else:
            self.filter   = 0

        # Initialize the wiki page information, if requested
        if self.doWiki:

            if self.filter==6:
                self.file_name = "Laser_stab_history_lg.txt"
            elif self.filter==8:
                self.file_name = "Laser_stab_history_hg.txt"
            else:
                self.file_name = "Laser_stab_history.txt"
                
            self.wiki      = open(os.path.join(getResultDirectory(),self.file_name),"w")

            self.wiki.write("This page present the most recent stability results")
            self.wiki.write("\n")
            self.wiki.write("!!! %newwin%[[Stab_HowTo|How to read this page ?]]\n")
            self.wiki.write("\n")
            text_s = "A complete list of the runs having the same characteristics is accessible by clicking %newwin%[[http://tileinfo.web.cern.ch/tileinfo/commselect.php?select=select+run,date,lasfilter,lasreqamp,events+from+comminfo+where+lasfilter="
            text = "%s'%d'+and+lasreqamp='23000'+and+events>'9000'+order+by+run+desc&rows=200 |here.]]\n"%(text_s,self.filter)
            self.wiki.write(text)

        if self.c1==None:
            self.c1 = src.MakeCanvas.MakeCanvas()
            #self.c1.SetTitle("Put here a nice title")
            

    def ProcessStart(self):
        
        global run_list
        for run in run_list.getRunsOfType('Las'):
            time = run.time_in_seconds
            if self.time_min > time:
                self.time_min = time
                self.origin = ROOT.TDatime(run.time)
                
            if self.time_max < time:
                self.time_max = time


   


    #
    # Here we collect all the relevant information
    #
        
    def ProcessRegion(self, region):
                          
        for event in region.GetEvents():
            
            #[part_num, i, j, w] = self.PMTool.GetNumber(event.data['region'])
            [part_num, i, j, w] = region.GetNumber(1)
            part_num -= 1

            if event.run.runNumber not in self.run_list:
                self.run_list.append(event.run.runNumber)

            index_val = 10*event.run.runNumber + part_num
            
            if index_val in self.part_list:
                continue
                                        
            if 'part_var' in event.data:

                self.events.add(event)
                self.part_list.add(index_val)
                    
##                 if self.time_min>event.data['time']:
##                     self.time_min = event.data['time']
##                     self.origin = ROOT.TDatime(event.time)
                            
##                 if self.time_max<event.data['time']:
##                     self.time_max = event.data['time']


    #
    # At the end we produce the plots
    #
    
    def ProcessStop(self):


        self.run_list.sort()

        # Write some info if requested

        if self.doWiki:

            self.wiki.write("\n")
            self.wiki.write("(:toggle init=hide show=usedRunList run_part button=1:)\n") 
            self.wiki.write(">>id=run_part<<\n") 

            for run in self.run_list:
                text_s = "* Run %newwin%[[http://tileinfo.web.cern.ch/tileinfo/commselect.php?select=select%20*%20from%20comminfo%20where%20run"
                text = "%s=%d|'''%d''']]\n" % (text_s,run,run)
                self.wiki.write(text)

            self.wiki.write(">><<\n") 
                    
            self.wiki.write("\n")
            self.wiki.write("!!! Results\n")
            self.wiki.write("\n")
            
            self.wiki.write("\n")
            self.wiki.write("!!!! Overall shifts\n")
            self.wiki.write("\n")
            
            self.wiki.write("(:toggle hide box_part button=1:)\n")
            self.wiki.write(">>id=box_part<<\n")
            
            text = "*Stability limit for global shifts is fixed at '''+/-%.1f%s'''\n"%(self.limit,"%")
            
            self.wiki.write(text)
            self.wiki.write("\n")
            
            self.wiki.write("(:table align=center border=1 cellpadding=5 cellspacing=0 :)\n")

            
        # Cosmetics (Part 1): the lines which shows the maximum acceptable variation

        self.line_down = ROOT.TLine(0,-self.limit,self.time_max-self.time_min+1,-self.limit)
        self.line_down.SetLineColor(4)
        self.line_down.SetLineWidth(2)
                
        self.line_up = ROOT.TLine(0,self.limit,self.time_max-self.time_min+1,self.limit);
        self.line_up.SetLineColor(4)
        self.line_up.SetLineWidth(2)

        self.nDaysBef = self.time_max - self.nDaysBef*86400

        # Then we do the graphs for all the partitions
                
        for i_part in range(4):

            if self.doWiki:
                self.wiki.write("(:cell")
                if i_part == 0:
                    self.wiki.write("nr")

            if self.part != -1 and i_part != self.part: # if you just want one partition
                continue

            part_events  = set()
            max_var      = 0
            self.problem = False
                    
            for event in self.events:
                                              
                #[part_num, i, j, w] = self.PMTool.GetNumber(event.data['region'])
                [part_num, i, j, w] = event.region.GetNumber(1)
                part_num -= 1

                if part_num != i_part:
                    continue

                part_events.add(event)
      
                if max_var<math.fabs(event.data['part_var']):
                    max_var = math.fabs(event.data['part_var'])

                # Look for an outing during the last days, this is annoying
                #if event.data['time'] > self.nDaysBef and\
                if event.run.time_in_seconds > self.nDaysBef and\
                       math.fabs(event.data['part_var']) > self.limit: 
                    self.problem = True

            self.events = self.events - part_events

            if max_var == 0: # No events there
                continue

            # Cosmetics (Part 2): the partition graph itself

            graph_lim = max(1.1*max_var,5*self.limit)

            tmp = "%s evolution %s" % (self.PMTool.get_partition_name(i_part),'(in %)')
            self.plot_name = "%s_history_%d" % (self.PMTool.get_partition_name(i_part),self.filter)
                      
            self.hhist = ROOT.TH2F(self.PMTool.get_partition_name(i_part), '',\
                                   100, 0, self.time_max-self.time_min+1, 100, -graph_lim, graph_lim)

            self.c1.SetFrameFillColor(0)
            if max_var > self.limit and self.problem:
                self.c1.SetFrameFillColor(623)

            if self.doWiki:
                name   = self.PMTool.get_partition_name(i_part)
                if max_var > self.limit and self.problem:
                    text_s = " width=90 id=RedCell :) %newwin%[[Path:Images/Stability"
                else:
                    text_s = " width=90 id=GreenCell :) %newwin%[[Path:Images/Stability"
                text = "%s/%d/%s.png|%s]]\n"%(text_s,self.filter,self.plot_name,name) 
                self.wiki.write(text)

            self.c1.SetFillColor(0);
            self.c1.SetBorderMode(0); 
            self.c1.SetGridx(1);
            self.c1.SetGridy(1);
            
            ROOT.gStyle.SetTimeOffset(self.origin.Convert());
            
            self.hhist.GetXaxis().SetTimeDisplay(1)
            self.hhist.GetYaxis().SetTitleOffset(1.)
            self.hhist.GetXaxis().SetLabelOffset(0.03)
            self.hhist.GetYaxis().SetLabelOffset(0.01)
            self.hhist.GetXaxis().SetLabelSize(0.04)
            self.hhist.GetYaxis().SetLabelSize(0.04)           
            self.hhist.GetXaxis().SetTimeFormat("#splitline{%Y}{%d/%m}")
            self.hhist.GetXaxis().SetNdivisions(-503)
            self.hhist.GetYaxis().SetTitle(tmp)
            self.hhist.SetMarkerStyle(20)
                
            for event in part_events: # fill the histogram
                    
                self.hhist.Fill(event.run.time_in_seconds-self.time_min,event.data['part_var'])


            # Then draw it...
                
            self.c1.cd()
            ROOT.gStyle.SetOptStat(0)
            ROOT.gStyle.SetStatX(0.78)
            ROOT.gStyle.SetStatY(0.83)
            self.hhist.Draw()
            self.line_up.Draw("same")
            self.line_down.Draw("same")
                    
            # hack
            self.c1.SetLeftMargin(0.14)
            self.c1.SetRightMargin(0.14)
            self.c1.Modified()
            
            l = ROOT.TLatex()
            l.SetNDC();
            l.SetTextFont(72);
            l.DrawLatex(0.1922,0.867,"ATLAS");
            
            l2 = ROOT.TLatex()
            l2.SetNDC();
            l2.DrawLatex(0.1922,0.811,"Preliminary");
            
            self.c1.Modified()  
                
            self.c1.Print("%s/%s.png" % (self.dir,self.plot_name))
            if self.doEps:
                self.c1.Print("%s/%s.eps" % (self.dir,self.plot_name))
            #self.c1.Print("%s/%s.root" % (self.dir,self.plot_name))
        
        if self.doWiki:
            self.wiki.write("(:tableend:)\n")
            self.wiki.write(">><<\n")
            self.wiki.close()
