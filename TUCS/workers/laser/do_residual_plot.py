############################################################
#
# do_residual_plot.py
#
############################################################
#
# Author: Seb Viret <viret@in2p3.fr>
#
# November 26, 2009, modified March 22nd, 2010
#
# Goal: 
# Compute linearity residuals plots for all the pmts of a drawer
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
#           is excedeed the plots will have a RED or ORANGE background
#           , depending on how critical is the problem
#
# -> doWiki: used by laser experts to update the status webpage
#
# -> doEps: provide eps plots in addition to default png graphics
#
# -> useBoxPMT: take the LASER box PMT signal instead of PMT/BoxPMT ratio 
#
# For more info on the LASER system : http://atlas-tile-laser.web.cern.ch
#
#############################################################



from src.GenericWorker import *
from src.oscalls import *
import ROOT
import time
import math

class do_residual_plot(GenericWorker):
    "Creates residual plots for the pmts of a drawer"

    def __init__(self, useBoxPMT=False, part=-1, limit=2, drawer=-1, doWiki=False, doEps = False, verbose=False):
        self.usePM       = useBoxPMT
        self.doWiki      = doWiki
        self.doEps       = doEps
        self.limit       = limit
        self.part        = part
        self.drawer      = drawer
        self.PMTool      = LaserTools()
        self.drawer_list = []
        self.run_list    = []
        self.n_run       = 0
        self.ncut        = 2000
        self.verbose     = verbose

        self.outputTag = outputTag # global variable to tag output histogram file name
        self.dir    = getPlotDirectory(subdir=self.outputTag)
        
        for i in range(256):
            self.drawer_list.append([])            

        # Initialize the text files

        self.bclist = open(os.path.join(getResultDirectory(),"Linearity_pb_run.txt"), 'w')
        self.listHeader(self.bclist)

        if self.doWiki:
            self.wiki      = open(os.path.join(getResultDirectory(),"Linearity_wiki_run.txt"),"w")
            self.wikiHeader(self.wiki,"Linearity_pb_run.txt")


    def ProcessRegion(self, region):

        for event in region.GetEvents():

            if 'requamp' in event.data and 'is_OK' in event.data:
                
                # Store the events in container depending on their drawer
                
                #[part_num, i, j, w] = self.PMTool.GetNumber(event.data['region'])
                [part_num, i, j, w] = event.region.GetNumber()
                part_num -= 1
                
                index = 64*part_num+i-1
                self.drawer_list[index].append(event) 
                
                if event.runNumber not in self.run_list:
                    self.run_list.append(event.runNumber)
                    self.n_run+=1
                    
                    
    #
    # At the end we produce the plots
    #
    
    def ProcessStop(self):

        self.run_list.sort()

        # Write the used run list in the wiki script


        if self.doWiki:

            self.wiki.write("(:toggle init=hide show=usedRunList run_part button=1:)\n") 
            self.wiki.write(">>id=run_part<<\n") 

            for run in self.run_list:
                text_s = "* Run %newwin%[[http://tileinfo.web.cern.ch/tileinfo/commselect.php?select=select%20*%20from%20comminfo%20where%20run"
                text = "%s=%d|'''%d''']]\n" % (text_s,run,run)
                self.wiki.write(text)

            self.wiki.write(">><<\n") 


        # Some container which will contain the particular channels
            
        sat_las_list    = []
        sat_las_event   = []
        warn_las_list   = []
        warn_las_event  = []
        bad_las_list    = []
        bad_las_event   = []
        no_las_list     = []
        no_las_event    = []
        bad_ADC_list     = []
        bad_ADC_event    = []


        # Cosmetics (Part 1): the lines which shows the maximum acceptable variation
          
        self.line_down = ROOT.TLine(0,-self.limit,2100,-self.limit)
        self.line_down.SetLineColor(4)
        self.line_down.SetLineWidth(2)
        
        self.line_up = ROOT.TLine(0,self.limit,2100,self.limit);
        self.line_up.SetLineColor(4)
        self.line_up.SetLineWidth(2)
        
        c_w = 1100
        c_h = 900

        # Then we do the graphs for all the requested modules
                
        for i_part in range(4):
                
            if self.doWiki:
 
                self.wiki.write("\n")
                self.wiki.write("!!!!! %s partition\n"%(self.PMTool.get_partition_name(i_part)))
                self.wiki.write("\n")                    
                self.wiki.write("(:table align=center border=1 cellpadding=5 cellspacing=0 :)\n")
                    
            if self.part != -1 and i_part != self.part: # if you just want one part
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
                
                drawer_events = self.drawer_list[64*i_part+i_drawer]
                            
                self.plot_name = "%s_linearity" % (self.PMTool.get_module_name(i_part,i_drawer))
                    
                self.hhist  = []
                self.hhist2 = []
                self.pt     = []
                self.text   = []
                n_pmt       = 0
                n_orange    = 0
                n_red       = 0
                n_black     = 0
                pmt_list    = []

                for i in range(48):
                    pmt_list.append([])

                for event in drawer_events:
                    
#                    [part_num, i, j, w] = self.PMTool.GetNumber(event.data['region'])

#                    part_num -= 1
#                    pmt = self.PMTool.get_PMT_index(part_num,i-1,j)

                    
                    [part_num, i, pmt, w] = event.region.GetNumber(1)
                    if 'slope' in event.data:
                        pmt_list[pmt].append(event)

                for i_pmt in range(48):

                    # Don't go further if the channel is not instrumented 
                    if self.PMTool.is_instrumented(i_part,i_drawer,i_pmt) == False:
                        #print i_part,"Hole ",i_pmt+1," is not instrumented"
                        continue

                    pmt_events = pmt_list[i_pmt] # The list of events attached to this PMT
                    max_var    = 0               # The largest residual (in the non-sat area)
                    max_lg     = 0               # The highest LG signal
                    max_lg_res = 0               # The corresponding residual
                    n_pts      = 0.              # The number of measurement points
                    n_pts_lg   = 0.              # The number of points in the HG/LG transition area
                    n_bad_pts  = 0.              # The number of bad points in this area 
                    n_over_lim = 0.              # The total number of bad points (sat. zone excluded)

                    is_bad_ADC = False           # The channel is bad because of the ADC uncertainty
                    is_bad     = False           # The channel is bad for another reason
                    is_wrong   = False           # The channel is nasty 
                        
                    # Cosmetics (Part 2): the pmt graph itself
                      
                    for event in pmt_events:
      
                        for i in range(8):
                            if event.data['number_entries'][i] > self.ncut\
                                   and event.data['BoxPMT'][i] != 0 \
                                   and event.data['PMT_signal'][i] > .5\
                                   and event.data['PMT_signal'][i] < 2100.:


                                # First compute the normalised residual w.r.t. the fit
                                norm_res = self.getRes(event,True,i)
                                n_pts    += 1                                

                                if self.verbose:
                                    print(event.data['PMT_signal'][i],norm_res)

                                # Getting the maximum variation in the not-saturating area
                                if max_var<math.fabs(norm_res) \
                                       and event.data['PMT_signal'][i] < 650.:
                                    max_var = math.fabs(norm_res)

                                # Look for the maximum signal (for saturation correction)
                                if max_lg<event.data['PMT_signal'][i]:
                                    max_lg     = event.data['PMT_signal'][i]
                                    max_lg_res = norm_res 

                                # Do we have a point over limit (in a specified range)?
                                if math.fabs(norm_res) >= self.limit:

                                    # Low gain case
                                    if event.data['PMT_signal'][i] < 650. and event.data['gain'][i]==0:
                                        n_over_lim += 1

                                        if event.data['PMT_signal'][i] < 100.:
                                            n_bad_pts += 1

                                    # High gain case
                                    if event.data['PMT_signal'][i] < 8. and event.data['gain'][i]==1:
                                        n_over_lim += 1
                                        
                                # Compute the total number of LG points in the transition area
                                if event.data['PMT_signal'][i] < 100. and event.data['gain'][i]==0:
                                    n_pts_lg += 1

                    # End of loop over all the events
                    # Time to summarize the info
                    
                    # To decide if a channel is bad we ask for at least two points over the limit
                    if n_over_lim>2:
                        is_bad = True

                        # If we are 5 times over the limit, there is a real problem
                        if max_var>=5.*self.limit:
                            is_wrong = True

                    # Then look if there is a problem in the LG/HG transition
                    if n_bad_pts != 0 and n_bad_pts == n_over_lim and not is_wrong:
                        
                        if is_bad and n_bad_pts==n_over_lim:
                            is_bad = False
                            is_bad_ADC = True

                        if n_bad_pts>3:
                            is_bad_ADC = True


                    if self.verbose:
                        print("")
                        print("--> Summary for channel %s :" % (self.PMTool.get_channel_name(i_part,i_drawer,i_pmt)))
                        print("")
                        print("--> Number of points (total/bad): %d/%d"% (n_pts,n_over_lim))
                        print("--> In the HG/LG area (total/bad): %d/%d"% (n_pts_lg,n_bad_pts))
                        print("--> Max. signal/residual (pC/%s): %d/%.2f"% ('%',max_lg,max_lg_res))
                        print("--> Max. residual (in %s): %.2f"% ('%',max_var))


                    # Cosmetics (Part 2): the pmt graph itself
                        
                    graph_lim = max(1.1*max_var,5*self.limit)                   
                    tmp = "PMT linearity"

                    self.hhist.append(ROOT.TH2F(self.PMTool.get_channel_name(i_part,i_drawer,i_pmt)+'_l', 'l',\
                                                1000, 0, 2100., 100, -graph_lim, graph_lim))
                    self.hhist2.append(ROOT.TH2F(self.PMTool.get_channel_name(i_part,i_drawer,i_pmt)+'_h', 'h',\
                                                 1000, 0, 2100., 100, -graph_lim, graph_lim))
                        
                    self.c1.cd(i_pmt+1).SetFrameFillColor(0)
                    self.c1.cd(i_pmt+1).SetLeftMargin(0.17);
                    self.c1.cd(i_pmt+1).SetRightMargin(0.13);
                    self.c1.cd(i_pmt+1).SetTopMargin(0.04);
                    self.c1.cd(i_pmt+1).SetBottomMargin(0.25);
                    
                    # Then we do the different channel classification
                    
                    self.hhist[n_pmt].GetXaxis().SetLabelOffset(0.01)
                    self.hhist[n_pmt].GetXaxis().SetLabelFont(42)
                    self.hhist[n_pmt].GetYaxis().SetTitleFont(42)
                    self.hhist[n_pmt].GetYaxis().SetLabelFont(42)                        
                    self.hhist[n_pmt].GetYaxis().SetTitleSize(0.1)
                    self.hhist[n_pmt].GetXaxis().SetTitleSize(0.1)
                    self.hhist[n_pmt].GetYaxis().SetTitleOffset(0.7)
                    self.hhist[n_pmt].GetXaxis().SetLabelSize(0.1)
                    self.hhist[n_pmt].GetYaxis().SetLabelSize(0.1)
                    self.hhist[n_pmt].GetXaxis().SetNdivisions(503)
                    self.hhist[n_pmt].GetXaxis().SetNoExponent()
                    self.hhist[n_pmt].GetYaxis().SetTitle("Norm. residual %s" % ('(in %)'))
                    self.hhist[n_pmt].GetXaxis().SetTitle("PMT signal (in pC)")
                    self.hhist[n_pmt].SetMarkerStyle(20)
                    self.hhist[n_pmt].SetMarkerSize(0.6)
                    self.hhist2[n_pmt].SetMarkerStyle(20)
                    self.hhist2[n_pmt].SetMarkerSize(0.6)
                    self.hhist2[n_pmt].SetMarkerColor(4)

                    if max_var == 0: # We have no data for this one

                        index = self.PMTool.get_index(i_part, i_drawer, i_pmt, 0)

                        if index not in no_las_list: # Check that the channel has not been recorded already
                            self.c1.cd(i_pmt+1).SetFrameFillColor(14)
                            n_black += 1
                            n_unkn  += 1
                            no_las_list.append(index)
                            no_las_event.append(event)


                    for event in pmt_events: # fill the histogram

                        self.prob = event.data['prob']
                            
                        [p, i, j, w] = event.region.GetNumber()
                        index        = self.PMTool.get_index(p-1, i-1, j, w)

              
                        # First case, the PMT is OK, it's just the ADC
                        # which is saturating
                        if fabs(max_lg_res) > self.limit and not is_wrong \
                               and max_lg > 600. \
                               and index not in sat_las_list:  
                            sat_las_list.append(index)
                            sat_las_event.append(event)
                            
                        # Then if the mismatch between LG and HG is consequent
                        # or if the Chisquare/dof is clearly problematic
                        # we flag the channel WARNING
                        #elif (delta > self.limit or is_wrong)\
                        elif is_bad\
                                 and index not in warn_las_list \
                                 and index not in bad_las_list:
                              self.c1.cd(i_pmt+1).SetFrameFillColor(796)
                              n_orange += 1
                              n_warn   += 1

                              # Last case is for the really bad channels
                              if is_wrong\
                                     and index not in bad_las_list: # 3 sigma out of range : bad
                                  self.c1.cd(i_pmt+1).SetFrameFillColor(623)
                                  n_red += 1
                                  n_bad += 1
                                  n_orange -= 1
                                  n_warn   -= 1
                                  bad_las_list.append(index)
                                  bad_las_event.append(event)
                              else:
                                  warn_las_list.append(index)
                                  warn_las_event.append(event)
                        elif is_bad_ADC\
                                 and index not in bad_ADC_list:
                            #self.c1.cd(i_pmt+1).SetFrameFillColor(401)
                            bad_ADC_list.append(index)
                            bad_ADC_event.append(event)
                                                   
              
            
                        for i in range(8):
                            if event.data['number_entries'][i] > self.ncut\
                                   and event.data['BoxPMT'][i] != 0 \
                                   and event.data['PMT_signal'][i] > 0.5\
                                   and event.data['PMT_signal'][i] < 2100.:

                                norm_res = self.getRes(event,self.usePM,i)

                                if norm_res == 0:
                                    continue

                                
                                if event.data['gain'][i] == 0 and event.data['PMT_signal'][i] >= 15:
                                    self.hhist[n_pmt].Fill(event.data['PMT_signal'][i],norm_res)
                                elif event.data['gain'][i] == 1 and event.data['PMT_signal'][i] <= 8:
                                    self.hhist2[n_pmt].Fill(event.data['PMT_signal'][i],norm_res)

                            
                    # Then draw it...
                
                    self.c1.cd(i_pmt+1)
                    self.c1.cd(i_pmt+1).SetLogx()
                    self.hhist[n_pmt].GetXaxis().SetRangeUser(0.01,2100)
                    ROOT.gStyle.SetOptStat(0)
                    ROOT.gStyle.SetStatX(0.78)
                    ROOT.gStyle.SetStatY(0.83)
                    self.hhist[n_pmt].Draw()
                    if max_var!=0:
                        self.hhist2[n_pmt].Draw("same")
                        self.line_up.Draw("same")
                        self.line_down.Draw("same")
                        
                    self.pt.append(ROOT.TPaveText(0.71,0.83,0.98,0.99,"brNDC"))
                    self.pt[n_pmt].SetFillColor(5)
                    self.pt[n_pmt].SetTextSize(0.1)
                    self.pt[n_pmt].SetTextFont(42)                        
                    self.pt[n_pmt].AddText("PMT %d" % (i_pmt+1))
                    self.pt[n_pmt].Draw()
                    self.text.append(ROOT.TPaveText(0.2,0.79,0.5,1.01,"NDC"))
                    
                    if is_wrong:
                        self.text[n_pmt].SetFillColor(623)
                        
                    #if is_bad:
                    #    if is_wrong:
                    #        self.text[n_pmt].SetFillColor(623)
                    #    else:
                    #        self.text[n_pmt].SetFillColor(796)

                    self.text[n_pmt].SetTextSize(0.1)
                    self.text[n_pmt].SetTextFont(42)
                    if max_var!=0:
                        self.text[n_pmt].AddText("#chi^{2} = %.3f" % (self.prob))
                        #self.text[n_pmt].Draw()
                        
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

                    if n_black > 0:
                        text_s = " width=90 id=BlackCell :) %newwin%[[Path:Images/Linearity"
                    elif n_red > 0:
                        text_s = " width=90 id=RedCell :) %newwin%[[Path:Images/Linearity"
                    elif n_orange > 0:
                        text_s = " width=90 id=OrangeCell :) %newwin%[[Path:Images/Linearity"
                    else:
                        text_s = " width=90 id=GreenCell :) %newwin%[[Path:Images/Linearity"

                    text = "%s/%s.png|%s]] %d/%d/%d/%d\n"%(text_s,self.plot_name,name,\
                                                           n_pmt-n_red-n_orange-n_black,n_orange,n_red,n_black) 
                    self.wiki.write(text)
               
                self.c1.cd()
                l = ROOT.TLatex()
                l.SetNDC()
                l.SetTextFont(72)
                l.DrawLatex(0.1922,0.32,"ATLAS")
                
                l2 = ROOT.TLatex()
                l2.SetNDC()
                l2.DrawLatex(0.1922,0.26,"Preliminary")
                
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
                self.wiki.write("%d channels have bad linearity \\\\\n"%n_bad)
                self.wiki.write("%d channels have problematic linearity \\\\\n"%n_warn)
                self.wiki.write( "\n")
                self.wiki.write("\n")

        if self.doWiki:
            
            self.wiki.write( "\n")
            self.wiki.write( "...This page was generated automatically on '''%s'''...\n"%ROOT.TDatime().AsString())
            self.wiki.write( "\n")
            
            self.wiki.close()

        # Time to write the bad channel lists

        sat_las_list.sort()
        warn_las_list.sort()
        bad_las_list.sort()
        no_las_list.sort()
            
        self.bclist.write("1. List of seriously problematic channels (chisquare probabilities values):\n")
        self.processBC(self.bclist,bad_las_list,bad_las_event,True)
        
        self.bclist.write("2. List of not very good channels (chisquare probabilities values):\n")
        self.processBC(self.bclist,warn_las_list,warn_las_event,True)
                
        self.bclist.write("3. List of good channels with no information:\n")
        self.processBC(self.bclist,no_las_list,no_las_event,False)

        self.bclist.write("4. List of good channels with saturating ADC:\n")
        self.processBC(self.bclist,sat_las_list,sat_las_event,False)
            
        self.bclist.write("5. List of channels with bad ADC:\n")
        self.processBC(self.bclist,bad_ADC_list,bad_ADC_event,False)
        
        self.bclist.close() 
        




    ####################################################################################
    #
    # Tools used along the worker
    #

    # Method writing the header of the twiki page            
    def wikiHeader(self, file, bcname):
        file.write("This page present the most recent linearity results")
        file.write("\n")
        file.write("!!! %newwin%[[Lin_HowTo|How to read this page ?]]\n")
        file.write("\n")
        file.write("!!! Linearity runs\n")
        file.write("\n")
        text = "A list of the runs usable for linearity analysis is accessible by clicking %newwin%[[http://tileinfo.web.cern.ch/tileinfo/commselect.php?select=select+run,date,lasfilter,lasreqamp,events+from+comminfo+where+lasfilter+like+%27%%28%%27+and+lasreqamp+not+like+%27%%28%%27+and+events%3E%279000%27+order+by+run+desc&rows=200 |here.]]\n"
        file.write(text)

        file.write("\n")
        file.write("!!! Preliminary results\n")
        file.write("\n")
        
        text = "*Normalized residuals limit for PMT linearity is fixed at '''+/-%.1f%s'''\n"%(self.limit,"%")                
        file.write(text)
        file.write("\n")
        text = "*A summary of the different problems encountered is available %snewwin%s[[Path:Images/Linearity/%s|here]]\n" % ("%","%",bcname)
        file.write(text)
        file.write("\n")


    # Method writing the header of the bad channel list            
    def listHeader(self, file):
        file.write('##########################################\n') 
        file.write('#\n')
        text = "# This is the LASER linearity DQ summary\n"
        file.write(text)
        file.write('#\n')
        text = "# Maximum relative variation accepted: +/-%.1f%s\n" % (self.limit,'%')
        file.write(text)
        file.write('#\n')
        file.write('#\n')
        text = "# LASER expert contact number: 160480\n"
        file.write(text)     
        file.write('##########################################\n')
        file.write('\n')
        file.write('\n')
        file.write('\n')


    # Write a list of bad channels, with or without chisquare information
    def processBC(self, file, index, events, printChi):
        file.write('\n')
        for ind in index:

            [p, i, j, w] = self.PMTool.get_rev_index(ind)
                
            if i<9:
                name = "%s0%d : Channel %d" % (self.PMTool.get_partition_name(p),i+1,j)
            else:
                name = "%s%d : Channel %d" % (self.PMTool.get_partition_name(p),i+1,j)

            if not printChi:
                text = "%s\n" % (name)
                file.write(text)
            else:
                for event in events:
                    if event.region.GetNumber() == [p+1, i+1, j, w]:

                        text = "%s : %.3f" % (name,event.data['prob'])
                        file.write(text)
                        if event.data['isBad']:
                            probs = event.data['problems'].pop()
                            file.write(' ==> KNOWN as problematic : ')
                            file.write(probs)
                        file.write('\n')
                        break

        file.write('\n')
        file.write('\n')
        

   
    def getRes(self,event,PM,filt):
        signal = event.data['BoxPMT'][filt]*event.data['slope']+event.data['intercept']
        residu = event.data['PMT_signal'][filt] - signal

        #print signal,event.data['BoxPMT'][filt],event.data['PMT_signal'][filt],residu
        
        norm_res = event.data['residual'][filt]                           
        #return norm_res
        return 100*residu/signal
