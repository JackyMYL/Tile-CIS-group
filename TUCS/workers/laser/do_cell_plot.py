############################################################
#
# do_cell_plot.py
#
############################################################
#
# Author: Djamel Boumediene <djamel.boumediene@cern.ch>
#
# January 15 november 2011
#
# Goal: Do a plot for one given cell (mean over the modules).
#       This plot could be an history DQ plot, but also a linearity plot.
#
# Input parameters are:
#
#
# -> cell : the cell number (A=100, B=200, C=300, D=400)+(cell number)
#    for ex. A10 = 110, D5 = 405
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

class do_cell_plot(GenericWorker):
    "Compute history plot for a given cell"

    c1 = None

    def __init__(self, runType='Las', limit=1, cell=0, doEps = False, option = 'History'):
        self.runType  = runType
        self.doEps    = doEps
        self.cell     = cell
        self.limit    = limit        

        self.outputTag = outputTag # global variable to tag output histogram file name
        self.dir    = getPlotDirectory(subdir=self.outputTag)
        self.PMTool   = LaserTools()

        self.option   = option
        self.origin   = ROOT.TDatime()

        self.LG_evts  = set()
        self.HG_evts  = set()

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
                        
            #[part_num, i, j, w] = self.PMTool.GetNumber(event.data['region'])
            [part_num, i, j, w] = event.region.GetNumber()
            part_num -= 1
            i        -= 1
            ind       = self.PMTool.get_index(part_num,i,j,w)

            pmt = self.PMTool.get_PMT_index(part_num,i,j)
            i += 1
            indcell   = self.PMTool.get_cell_index(part_num,i,pmt) #Get cell index needs a PMT number starting from 1
            


            
            if indcell == self.cell:

#                if self.time_min>event.data['time']:
#                    self.time_min = event.data['time']
#                    self.origin = ROOT.TDatime(event.time)
                    
#                if self.time_max<event.data['time']:
#                    self.time_max = event.data['time']

                if indcell == self.cell:
                    self.LG_evts.add(event)

                if indcell == self.cell:
                    self.HG_evts.add(event)
                                    


    def ProcessStop(self):

        # Then we do the graphs

        
        max_var = 0
                    
        for event in self.LG_evts:

            if 'deviation' not in event.data:
                continue

            if self.option == 'History':                              
                if max_var<math.fabs(event.data['deviation']):
                    max_var = math.fabs(event.data['deviation'])

            if self.option == 'Lin':                                              
                for i in range(8):
                    if event.data['number_entries_l'][i] != 0\
                           and event.data['BoxDiode'][i] != 0:
                        if max_var<math.fabs(self.getRes_l(event,True,i)):
                            max_var = math.fabs(self.getRes_l(event,True,i))
                    if event.data['number_entries_h'][i] != 0\
                           and event.data['BoxDiode'][i] != 0:
                        if max_var<math.fabs(self.getRes_h(event,True,i)):
                            max_var = math.fabs(self.getRes_h(event,True,i))

        for event in self.HG_evts:

            if 'deviation' not in event.data:
                continue
                  
            if self.option == 'History':   
                if max_var<math.fabs(event.data['deviation']):
                    max_var = math.fabs(event.data['deviation'])


        # Cosmetics (Part 2): the partition graph itself
        if self.option == 'History':
            if math.fabs(max_var) < 100:
                graph_lim = 1.1*(math.fabs(max_var))
            else:
                graph_lim = 40
        else:
            graph_lim = 40

                      
        tmp = "Gain variation [%]" 
                    
        self.plot_name = "cells_%d_history"%(self.cell)
        self.plot_name_lg = "cells_%d_history_lg"%(self.cell)
        self.plot_name_hg = "cells_%d_history_hg"%(self.cell)

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
                                   1000, 0, self.time_max-self.time_min+1, 10000, -graph_lim, graph_lim)
            
#            self.hhist_lg = ROOT.TH2F('Channel_hist_lg', '',\
#                                      100, 0, self.time_max-self.time_min+1, 100, -graph_lim+1, graph_lim+1)

            self.hhist_lg = ROOT.TProfile(self.plot_name_lg, '',\
                                      1000, 0, self.time_max-self.time_min+1)            

            self.hhist_hg = ROOT.TProfile(self.plot_name_hg, '',\
                                      1000, 0, self.time_max-self.time_min+1)

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
            self.cadre.GetXaxis().SetTitle('date')
        

            self.hhist_hg.SetMarkerStyle(30)
            self.hhist_lg.SetMarkerStyle(29)
                             
            for event in self.LG_evts : # fill the histogram
                if 'deviation' not in event.data:
                    continue
                if ((event.data['region'].find('LBA_m54')!=-1) or (event.data['region'].find('LBC_m28')!=-1) or (event.data['region'].find('EBC_m01')!=-1) or (event.data['region'].find('LBA_m13')!=-1)):
                    continue
                if event.run.time_in_seconds-self.time_min==0:
                    event.data['deviation'] = event.data['deviation'] + 0.000001
                self.hhist_lg.Fill(event.run.time_in_seconds-self.time_min,event.data['deviation'])

 
#            for event in self.HG_evts : # fill the histogram
#                if not event.data.has_key('deviation'):
#                    continue
#                self.hhist_hg.Fill(event.run.time_in_seconds-self.time_min,event.data['deviation'])



        if self.option == 'Lin':


            # Cosmetics (Part 1): the lines which shows the maximum acceptable variation
            
            self.line_down = ROOT.TLine(0,-self.limit,2100,-self.limit)
            self.line_down.SetLineColor(4)
            self.line_down.SetLineWidth(2)
            
            self.line_up = ROOT.TLine(0,self.limit,2100,self.limit);
            self.line_up.SetLineColor(4)
            self.line_up.SetLineWidth(2)
        

            self.cadre = ROOT.TH2F('Cadre', '',\
                                   1000, 0, 2100, 100, -graph_lim*100, graph_lim*100)
            
            self.hhist_lg = ROOT.TH2F('Channel_hist_lg', '',\
                                   1000, 0, 2100, 100, -graph_lim*100, graph_lim*100)

            self.hhist_hg = ROOT.TH2F('Channel_hist_hg', '',\
                                   1000, 0, 2100, 100, -graph_lim*100, graph_lim*100)
                  
            self.cadre.GetXaxis().SetLabelOffset(0.01)
            self.cadre.GetYaxis().SetTitleOffset(1.1)
            self.cadre.GetXaxis().SetLabelSize(0.04)
            self.cadre.GetYaxis().SetLabelSize(0.04)
            self.cadre.GetXaxis().SetNdivisions(503)
            self.cadre.GetXaxis().SetNoExponent()
            self.cadre.GetYaxis().SetTitle("Norm. residual %s" % ('(in %)'))
            self.cadre.GetXaxis().SetTitle("PMT signal (in pC)")
            self.c1.SetLogx()
##            self.cadre.GetXaxis().SetRangeUser(0.01,3000)

            self.hhist_hg.SetMarkerStyle(30)
            self.hhist_lg.SetMarkerStyle(29)
            
            
            for event in self.LG_evts: # fill the histogram
                for i in range(8):
                    if event.data['number_entries_l'][i] != 0\
                           and event.data['BoxDiode'][i] != 0:
                        norm_res = self.getRes_l(event,True,i)
                        self.hhist_lg.Fill(event.data['PMT_signal_l'][i],norm_res)
                        print(event.data['PMT_signal_l'][i],norm_res)
                        
                for i in range(8):
                    if event.data['number_entries_h'][i] != 0\
                           and event.data['BoxDiode'][i] != 0:
                        norm_res = self.getRes_h(event,True,i)
                        self.hhist_hg.Fill(event.data['PMT_signal_h'][i],norm_res)
                


        # Then draw it...
                
        self.c1.cd()
        ROOT.gStyle.SetOptStat(0)
        ROOT.gStyle.SetStatX(0.78)
        ROOT.gStyle.SetStatY(0.83)
        self.cadre.Draw()
        self.hhist_lg.Draw("same")
        #self.hhist_hg.Draw("same")

        self.line_up.Draw("same")
        self.line_down.Draw("same")
        
        # hack
        self.c1.SetLeftMargin(0.14)
        self.c1.SetRightMargin(0.14)
        self.c1.Modified()
        
        l = ROOT.TLatex()
        l.SetNDC();
        l.SetTextFont(72);
        
        l2 = ROOT.TLatex()
        l2.SetNDC();

        
        self.c1.Modified()  
        
        self.c1.Print("%s/%s.png" % (self.dir,self.plot_name))
        self.c1.Print("%s/%s.C" % (self.dir,self.plot_name))
        if self.doEps:
            self.c1.Print("%s/%s.eps" % (self.dir,self.plot_name))



    # Method computing the normalized residual value (in %)            
    def getRes_l(self,event,PM,filt):               
        if not PM:
            residu = event.data['PMT_signal_l'][filt]\
                     -(event.data['BoxDiode'][filt]*event.data['slope']\
                       +event.data['intercept'])
            norm_res = 100.*residu/(event.data['BoxDiode'][filt]*event.data['slope']+event.data['intercept']) 
        else:
            residu = event.data['PMTvP_signal_l'][filt]\
                     -(event.data['BoxPMT'][filt]*event.data['slope']\
                       +event.data['intercept'])
            norm_res = 100.*residu/(event.data['BoxPMT'][filt]*event.data['slope']+event.data['intercept']) 
        return norm_res
    
    # Method computing the normalized residual value (in %)            
    def getRes_h(self,event,PM,filt):               
        if not PM:
            residu = event.data['PMT_signal_h'][filt]\
                     -(event.data['BoxDiode'][filt]*event.data['slope']\
                       +event.data['intercept'])
            norm_res = 100.*residu/event.data['PMT_signal_h'][filt]                            
        else:
            residu = event.data['PMTvP_signal_h'][filt]\
                     -(event.data['BoxPMT'][filt]*event.data['slope']\
                       +event.data['intercept'])
            norm_res = 100.*residu/(event.data['BoxPMT'][filt]*event.data['slope']+event.data['intercept']) 
        return norm_res
