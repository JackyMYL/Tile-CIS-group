############################################################
#
# do_chan_plot.py
#
############################################################
#
# Author: Seb Viret <viret@in2p3.fr>
#
# January 15, 2010
#
# Goal: Do a plot for one given channel. This plot could be 
#       an history DQ plot, but also a linearity plot.
#       By default, .png and .C files are produced
#
# Input parameters are:
#
# -> part: the partition number (0=LBA, 1=LBC, 2=EBA, 3=EBC) you want to plot.
#
# -> mod: the module number.
#
# -> chan: the channel number.
#
# -> limit: the maximum tolerable variation (in %). Represented by two lines
#           
# -> option: could be either 'Lin' or 'History' (DEFAULT)
#
# -> doEps: provide eps plots in addition to default png graphics
#
# For more info on the LASER system : http://atlas-tile-laser.web.cern.ch
#
#############################################################

from src.GenericWorker import *
from src.oscalls import *
import src.MakeCanvas
import time

class do_chan_plot(GenericWorker):
    "Compute history plot"

    c1 = None

    def __init__(self, runType='Las', limit=1, part=0, mod=0, chan=0, doEps = False, option = 'History'):
        self.runType  = runType
        self.doEps    = doEps
        self.part     = part
        self.mod      = mod
        self.chan     = chan
        self.limit    = limit        
        self.ncut     = 2000  # Cut on number of events
        self.maxHG    = 10    # High gain max
        self.minHG    = 0.1   # High gain min

        self.outputTag = outputTag # global variable to tag output histogram file name
        self.dir    = getPlotDirectory(subdir=self.outputTag)
        self.PMTool   = LaserTools()

        self.option   = option
        self.index    = self.PMTool.get_index(part,mod,chan,0)
        self.origin   = ROOT.TDatime()

        self.LG_evts  = set() # Events with low gain info
        self.HG_evts  = set() # Events with high gain info

        self.time_max = 0
        self.time_min = 10000000000000000

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


        
    def ProcessRegion(self, region):
                          
        # First retrieve all the relevant partition infos

        for event in region.GetEvents():

            if 'calibration' not in event.data:
                continue
                        
#            [part_num, i, j, w] = self.PMTool.GetNumber(event.data['region'])
            [part_num, i, j, w] = event.region.GetNumber()
            part_num -= 1
            i        -= 1
            ind       = self.PMTool.get_index(part_num,i,j,w)

            if ind == self.index or ind == self.index+1:

                if ind == self.index:
                    self.LG_evts.add(event)

                if ind == self.index+1:
                    self.HG_evts.add(event)



   ##   def ProcessRegion(self, region):
##         # First retrieve all the relevant partition infos

##         numbers = region.GetNumber()

##         if len(numbers)!=4:
##             return

##         [part, module, chan, gain] = numbers        

##         ind       = self.PMTool.get_index(part-1, module-1, chan, 0)

##         if ind != self.index:
##             return
        
##         for event in region.GetEvents():
##             if event.run.runType!='Las':
##                 continue

##             if gain==0:
##                 self.LG_evts.append(event)

##             if gain==1:
##                 self.HG_evts.append(event)
                                    

    # Then we do the graphs

    def ProcessStop(self):

        max_var = 0 # The maximum variation, in % (gain or normalized residuals)
                    
        for event in self.LG_evts:

            if self.option == 'History':                                              
                if max_var<math.fabs(event.data['deviation']-1):
                    max_var = math.fabs(event.data['deviation']-1)

            if self.option == 'Lin': # In this case everything is put in the low gain container  

                if 'slope' not in event.data:
                    continue

                for i in range(8):

                    if not self.selector(event,i):
                        continue
                    
                    norm_res = self.getRes(event,True,i)
                    if norm_res==0:
                        continue
                        
                    if max_var<math.fabs(norm_res):
                        max_var = math.fabs(norm_res)

        for event in self.HG_evts:
                  
            if self.option == 'History':                                              
                if max_var<math.fabs(event.data['deviation']-1):
                    max_var = math.fabs(event.data['deviation']-1)
              
        # Cosmetics (Part 2): the partition graph itself
        if self.option == 'History': 
            graph_lim = max(1.3*max_var,5*self.limit)
        else:
            #graph_lim = 20
            graph_lim = max(1.3*max_var,5*self.limit)
            
        tmp = "Gain variation [%]" 
            
        self.plot_name = "channel_%d_history"%(self.index)

        self.c1.SetFrameFillColor(0)
        self.c1.SetFillColor(0);
        self.c1.SetBorderMode(0); 
        self.c1.SetGridx(1);
        self.c1.SetGridy(1);


        if self.option == 'History': 

            # Cosmetics (Part 1): the lines which shows the maximum acceptable variation
            
            self.line_down = ROOT.TLine(0,-self.limit,self.time_max-self.time_min+1,-self.limit)
            self.line_down.SetLineColor(4)
            self.line_down.SetLineWidth(2)
            
            self.line_up = ROOT.TLine(0,self.limit,self.time_max-self.time_min+1,self.limit);
            self.line_up.SetLineColor(4)
            self.line_up.SetLineWidth(2)
        

            self.cadre = ROOT.TH2F('Cadre', '',\
                                   100, 0, self.time_max-self.time_min+1, 100, -graph_lim-1, graph_lim+1)
            
            #self.hhist_lg = ROOT.TH2F('Channel_hist_lg', '',\
            #                          100, 0, self.time_max-self.time_min+1, 100, -graph_lim+1, graph_lim+1)

            #self.hhist_hg = ROOT.TH2F('Channel_hist_hg', '',\
            #                          100, 0, self.time_max-self.time_min+1, 100, -graph_lim+1, graph_lim+1)
            self.hhist_lg = ROOT.TGraph()
            self.hhist_hg = ROOT.TGraph()
                
            ROOT.gStyle.SetTimeOffset(self.origin.Convert());
        
            self.cadre.GetXaxis().SetTimeDisplay(1)
            self.cadre.GetYaxis().SetTitleOffset(1.1)
            self.cadre.GetXaxis().SetLabelOffset(0.001)
            self.cadre.GetYaxis().SetLabelOffset(0.01)
            self.cadre.GetXaxis().SetLabelSize(0.04)
            self.cadre.GetYaxis().SetLabelSize(0.04)           
            self.cadre.GetXaxis().SetTimeFormat("%Y/%d/%m")
            self.cadre.GetXaxis().SetNdivisions(-503)
            self.cadre.GetYaxis().SetTitle(tmp)



            self.hhist_hg.SetMarkerStyle(30)
            self.hhist_lg.SetMarkerStyle(29)
            
            for event in self.LG_evts: # fill the histogram
                npoints = self.hhist_lg.GetN()
                #print "f_laser :",event.data['f_laser'],"time :",event.run.time_in_seconds-self.time_min,"points :",npoints,"time max :",self.time_max-self.time_min+1
                self.hhist_lg.SetPoint(npoints,event.run.time_in_seconds-self.time_min,event.data['deviation'])
##                self.cadre.GetXaxis().SetTitle(event.data['region'])
                self.cadre.GetXaxis().SetTitle('date')

                #print " 2 deviation :",event.data['deviation'],"time :",event.run.time_in_seconds-self.time_min,"points :",npoints
                #self.hhist_lg.Fill(event.run.time_in_seconds-self.time_min,event.data['f_laser'])

            for event in self.HG_evts: # fill the histogram
                npoints = self.hhist_hg.GetN()
                print("f_laser :",event.data['f_laser'],"time :",event.run.time_in_seconds-self.time_min,"points :",npoints,"time max :",self.time_max-self.time_min+1)
                self.hhist_hg.SetPoint(npoints,event.run.time_in_seconds-self.time_min,event.data['deviation'])
                #self.hhist_hg.Fill(event.run.time_in_seconds-self.time_min,event.data['f_laser'])
            

 


        if self.option == 'Lin':


            # Cosmetics (Part 1): the lines which shows the maximum acceptable variation
            
            self.line_down = ROOT.TLine(0,-self.limit,2100,-self.limit)
            self.line_down.SetLineColor(4)
            self.line_down.SetLineWidth(2)
            
            self.line_up = ROOT.TLine(0,self.limit,2100,self.limit);
            self.line_up.SetLineColor(4)
            self.line_up.SetLineWidth(2)
        

            self.cadre = ROOT.TH2F('Cadre', '',\
                                   1000, 0, 2100, 100, -graph_lim, graph_lim)
            
            self.hhist_lg = ROOT.TH2F('Channel_hist_lg', '',\
                                   1000, 0, 2100, 100, -graph_lim, graph_lim)

            self.hhist_hg = ROOT.TH2F('Channel_hist_hg', '',\
                                   1000, 0, 2100, 100, -graph_lim, graph_lim)
                  
            self.cadre.GetXaxis().SetLabelOffset(0.01)
            self.cadre.GetYaxis().SetTitleOffset(1.1)
            self.cadre.GetXaxis().SetLabelSize(0.04)
            self.cadre.GetYaxis().SetLabelSize(0.04)
            self.cadre.GetXaxis().SetNdivisions(503)
            self.cadre.GetXaxis().SetNoExponent()
            self.cadre.GetYaxis().SetTitle("Norm. residual %s" % ('(in %)'))
            self.cadre.GetXaxis().SetTitle("PMT signal (in pC)")
            self.c1.SetLogx()
            self.cadre.GetXaxis().SetRangeUser(0.01,3000)

            self.hhist_hg.SetMarkerStyle(20)
            self.hhist_hg.SetMarkerColor(4)            
            self.hhist_lg.SetMarkerStyle(21)
            
            for event in self.LG_evts: # fill the histogram

                if 'slope' not in event.data:
                    continue

                for i in range(8):

                    if not self.selector(event,i):
                        continue

                    norm_res = self.getRes(event,True,i)
                    if norm_res==0:
                        continue

                    if event.data['gain'][i] == 0:
                        self.hhist_lg.Fill(event.data['PMT_signal'][i],norm_res)
                        
                    if event.data['gain'][i] == 1:
                        self.hhist_hg.Fill(event.data['PMT_signal'][i],norm_res)

                    #print event.data['PMT_signal'][i],norm_res
            
        # Then draw it...
                
        self.c1.cd()
        ROOT.gStyle.SetOptStat(0)
        ROOT.gStyle.SetStatX(0.78)
        ROOT.gStyle.SetStatY(0.83)
        self.cadre.Draw()
        self.hhist_lg.Draw("P,same")
        self.hhist_hg.Draw("P,same")

        if self.option == 'Lin':
            self.line_up.Draw("same")
            self.line_down.Draw("same")
        
        # hack
        self.c1.SetLeftMargin(0.14)
        self.c1.SetRightMargin(0.14)
        self.c1.Modified()

        self.pt_ch = ROOT.TPaveText(0.64,0.85,0.82,0.95,"NDC")
        self.pt_ch.SetFillColor(1)
        self.pt_ch.SetFillStyle(0)
        self.pt_ch.SetTextSize(0.05)
        self.pt_ch.SetTextFont(42)
        self.pt_ch.SetShadowColor(0)
        self.pt_ch.SetBorderSize(0)

        #pmt_region = even

        x = str(event.region).split("_")

        label = x[1]+x[2][1:]+' ch'+x[3][1:]
        
        self.pt_ch.AddText(label)
        self.pt_ch.Draw()
        
        self.c1.Print("%s/%s.png" % (self.dir,self.plot_name))
        self.c1.Print("%s/%s.C" % (self.dir,self.plot_name))
        if self.doEps:
            self.c1.Print("%s/%s.eps" % (self.dir,self.plot_name))


    # Method computing the normalized residual value (in %)            
    
    def getRes(self,event,PM,filt):
        signal = event.data['BoxPMT'][filt]*event.data['slope']+event.data['intercept']
        residu = event.data['PMT_signal'][filt] - signal

        #print signal,event.data['BoxPMT'][filt],event.data['PMT_signal'][filt],residu
        
        norm_res = event.data['residual'][filt]                           
        #return norm_res
        return 100*residu/signal
    

    
    # Method for event selection
    def selector(self,event,i):

        # Sanity check 1
        if event.data['BoxPMT'][i] == 0:
            return False   

        # Sanity check 2
        if event.data['gain'][i] == -1:
            return False

        # Cut on the number of events
        if event.data['number_entries'][i] < self.ncut:
            return False   

        # Select events belonging to the correct HG window
        if (event.data['PMT_signal'][i] < self.minHG or event.data['PMT_signal'][i] > self.maxHG) \
               and event.data['gain'][i] == 1:
            return False

        return True
