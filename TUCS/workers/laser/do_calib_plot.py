############################################################
#
# do_calib_plot.py
#
############################################################
#
# Author: Henric
#
#
# Input parameters are:
#
# -> part: the partition number (1=LBA, 2=LBC, 3=EBA, 4=EBC) you want to plot.
#
# -> mod: the module number.
#
# -> chan: the channel number.
#
# -> limit: the maximum tolerable variation (in %). Represented by two lines
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

class do_calib_plot(GenericWorker):
    "Compute history plot corrected from COOL"
    c1 = None
    LG_evts  = [] # Events with low gain info
    HG_evts  = [] # Events with high gain info

    def __init__(self,  limit=0.1, part=1, mod=1, chan=0, doEps = False):
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
        self.PMTool = LaserTools()

        self.index    = self.PMTool.get_index(part-1,mod-1,chan,0)

        if self.c1==None:
            self.c1 = src.MakeCanvas.MakeCanvas()
            #self.c1.SetTitle("Put here a nice title")

        self.time_max = 0
        self.time_min = 10000000000000000
#        self.c1 = src.MakeCanvas.MakeCanvas()
        print(self.c1.GetName())
        self.c1.cd()

        self.origin = ROOT.TDatime()
        self.tgraph_lg = ROOT.TGraphErrors()
        self.tgraph_lg_bad = ROOT.TGraphErrors()
        self.tgraph_hg = ROOT.TGraphErrors()
        self.tgraph_hg_bad = ROOT.TGraphErrors()
        self.tgraph_lg_calib = ROOT.TGraphErrors()
        self.tgraph_lg_calib_bad = ROOT.TGraphErrors()
        self.tgraph_hg_calib = ROOT.TGraphErrors()
        self.tgraph_hg_calib_bad = ROOT.TGraphErrors()
        self.tgraph_hv = ROOT.TGraphErrors()
        

    def ProcessStart(self):
        
        global run_list
        for run in run_list.getRunsOfType('Las'):
            time = run.time_in_seconds
            if self.time_min > time:
                self.time_min = time
                self.origin = ROOT.TDatime(run.time)
                
            if self.time_max < time:
                self.time_max = time

        del self.LG_evts[:]
        del self.HG_evts[:]


    def ProcessRegion(self, region):                          
        # First retrieve all the relevant partition infos
        numbers = region.GetNumber()

        if len(numbers)!=4:
            return

        [part, module, chan, gain] = numbers        

        ind = self.PMTool.get_index(part-1, module-1, chan, 0)

        if ind != self.index:
            return
        
        for event in region.GetEvents():

            if event.run.runType!='Las':
                continue

            if 'deviation' not in event.data:
                continue

            if 'f_laser_db' not in event.data:
                continue

            if gain==0:
                self.LG_evts.append(event)

            if gain==1:
                self.HG_evts.append(event)


    def ProcessStop(self):
        # Then we do the graphs
        self.c1.Clear()
        self.c1.cd()
        
#         for tgraph in [ self.tgraph_lg,       self.tgraph_lg_bad,
#                         self.tgraph_hg,       self.tgraph_hg_bad,
#                         self.tgraph_lg_calib, self.tgraph_lg_calib_bad,
#                         self.tgraph_hg_calib, self.tgraph_hg_calib_bad,
#                         self.tgraph_hv ]:
#             tgraph = ROOT.TGraphErrors()

        ymax = 1.1 # The maximum variation, in % (gain or normalized residuals)
        ymin = .9
        
        cadre_hl_ratio = 1.
        
        for event in self.LG_evts: # fill the histogram
            if event.data['status']&0x4 or event.data['status']&0x10:
                tgraph = self.tgraph_lg_bad
            else:
                tgraph = self.tgraph_lg
            npoints = tgraph.GetN()

            y = 1+0.01*event.data['deviation']
            ey = 0.01*event.data['deverr']               
            if y > ymax: ymax = y
            if y < ymin: ymin = y
            
            tgraph.SetPoint(npoints,event.run.time_in_seconds-self.time_min,y)
            tgraph.SetPointError(npoints,0,ey)
            
            if event.data['status']&0x4 or event.data['status']&0x10:
                tgraph = self.tgraph_lg_calib_bad             
            else:
                tgraph = self.tgraph_lg_calib
            npoints = tgraph.GetN()
            
            y = y/event.data['f_laser_db']
            ey = ey/event.data['f_laser_db']
            if y > ymax: ymax = y
            if y < ymin: ymin = y
            
            tgraph.SetPoint(npoints,event.run.time_in_seconds-self.time_min,y)
            tgraph.SetPointError(npoints,0,ey)

        for event in self.HG_evts: # fill the histogram
            if event.data['status']&0x4 or event.data['status']&0x10:
                tgraph = self.tgraph_hg_bad
            else:
                tgraph = self.tgraph_hg
            npoints = tgraph.GetN()

            y = 1+0.01*event.data['deviation']
            ey = 0.01*event.data['deverr']

            if y > ymax: ymax = y
            if y < ymin: ymin = y
            
            tgraph.SetPoint(npoints,event.run.time_in_seconds-self.time_min,y)
            tgraph.SetPointError(npoints,0,ey)

            if event.data['status']&0x4 or event.data['status']&0x10:
                tgraph = self.tgraph_hg_calib_bad
            else:
                tgraph = self.tgraph_hg_calib
            npoints = tgraph.GetN()
            
            y = y/event.data['f_laser_db']
            ey = ey/event.data['f_laser_db']
            if y > ymax: ymax = y
            if y < ymin: ymin = y
            
            tgraph.SetPoint(npoints,event.run.time_in_seconds-self.time_min,y)
            tgraph.SetPointError(npoints,0,ey)

        message = ''
        self.problemtxt =[]
        for event in self.HG_evts + self.HG_evts: # fill the histogram
            if 'problems' in event.data:
                for problem in event.data['problems']:
                    if problem not in self.problemtxt:
                        self.problemtxt.append(problem)
                        message = message+" "+problem

            if 'HV' in event.data:
                if (event.data['HVSet'])!=0:
                    npoints = self.tgraph_hv.GetN()
                    beta = 6.9
                    if 'beta' in event.region.GetParent().data:
                        beta = event.region.GetParent().data['beta']
                                
                    #hvgain = 1.+700.*(event.data['HV']-event.data['HVSet'])/event.data['HVSet']
                    hvgain = pow(event.data['HV']/event.data['HVSet'],beta)
                    self.tgraph_hv.SetPoint(npoints, event.run.time_in_seconds-self.time_min, hvgain)

        graph_lim = max(1.2*ymax,5*self.limit)

#        print ymin, ymax
        
        histtitle = self.PMTool.get_pmt_name_index(self.index)
        cadre_xmin = -43200
        cadre_xmax = self.time_max-self.time_min+43200
        
        cadre_ymin = min(0.8*ymin,1.2*ymin)
        cadre_ymax = 1.2*ymax
        self.cadreCalib = ROOT.TH2F('CadreSignal', histtitle,\
                                     100, cadre_xmin, cadre_xmax , 100, cadre_ymin, cadre_ymax)
          
        # Then draw it...
        ROOT.gStyle.SetOptStat(0)
        ROOT.gStyle.SetStatX(0.78)
        ROOT.gStyle.SetStatY(0.83)

        ROOT.gStyle.SetOptTitle(1)
        ROOT.gStyle.SetTitleX(0.15)
        ROOT.gStyle.SetTitleW(0.2)
        ROOT.gStyle.SetTitleBorderSize(0)                                          
        ROOT.gStyle.SetTitleFontSize(0.1)
        ROOT.gStyle.SetEndErrorSize(0.)
        ROOT.gStyle.SetTimeOffset(self.origin.Convert())


        self.c1.SetFrameFillColor(0)
        self.c1.SetFillColor(0);
#        self.c1.SetBorderMode(0); 
        self.c1.SetGridx(1);
        self.c1.SetGridy(1);

        self.cadreCalib.GetXaxis().SetTimeDisplay(1)
        self.cadreCalib.GetYaxis().SetTitleOffset(1.1)
        self.cadreCalib.GetXaxis().SetLabelOffset(0.03)
        self.cadreCalib.GetYaxis().SetLabelOffset(0.01)
        self.cadreCalib.GetXaxis().SetLabelSize(0.04)
        self.cadreCalib.GetYaxis().SetLabelSize(0.04)           
        self.cadreCalib.GetXaxis().SetTimeFormat("#splitline{%Y}{%d/%m}")
        self.cadreCalib.GetXaxis().SetNdivisions(-503)
        self.cadreCalib.GetYaxis().SetTitle("calibration factor")
            
        self.cadreCalib.Draw()
            
            
#         # Then draw it...
#         if message!='':
# #            self.c1.cd(0)
#             problembox=ROOT.TPaveText(0.15,0.49,.90,0.54,"brNDC")
            
            
#             problembox.SetFillColor(623)
#             problembox.SetTextSize(0.040)
#             problembox.SetTextFont(42)
#             problembox.SetBorderSize(0)
            
#             #        text1="Here will come the problems from database"
#             problembox.AddText(message)
#             problembox.Draw()


#        self.c1.cd(1)

        
        self.tgraph_lg.SetMarkerStyle(29)
        self.tgraph_lg_bad.SetMarkerStyle(29)
        self.tgraph_lg_bad.SetMarkerColor(2)
        self.tgraph_hg.SetMarkerStyle(30)
        self.tgraph_hg_bad.SetMarkerStyle(30)
        self.tgraph_hg_bad.SetMarkerColor(2)
        
        self.tgraph_lg_calib.SetMarkerStyle(22)
        self.tgraph_lg_calib_bad.SetMarkerStyle(22)
        self.tgraph_lg_calib_bad.SetMarkerColor(2)
        self.tgraph_hg_calib.SetMarkerStyle(26)
        self.tgraph_hg_calib_bad.SetMarkerStyle(26)
        self.tgraph_hg_calib_bad.SetMarkerColor(2)

        legend1 = ROOT.TLegend(0.2,0.65,0.41,0.82)
        legend1.AddEntry(self.tgraph_lg,"Low gain (filter 6)","p")
        legend1.AddEntry(self.tgraph_hg,"high gain (filter 8)","p")
        legend1.AddEntry(self.tgraph_lg_calib,"Low gain, corrected","p")
        legend1.AddEntry(self.tgraph_hg_calib,"high gain, corrected","p")
        legend1.AddEntry(self.tgraph_hg_bad,"bad status","p")
        legend1.Draw()
        
        for tgraph in [self.tgraph_lg, self.tgraph_lg_bad, self.tgraph_hg, self.tgraph_hg_bad,
                       self.tgraph_lg_calib, self.tgraph_lg_calib_bad, self.tgraph_hg_calib, self.tgraph_hg_calib_bad]:
            if tgraph.GetN()>0:
                tgraph.Draw("P,same")

        if self.tgraph_hv.GetN()>0:
            self.tgraph_hv.Sort()
            self.tgraph_hv.Draw("L,same")


#        axis = ROOT.TGaxis(cadre_xmax, cadre_ymin, cadre_xmax, cadre_ymax, cadre_ymin/cadre_hl_ratio , cadre_ymax/cadre_hl_ratio,506,"+L" )
#        axis.SetTitleFont(self.cadreCalib.GetTitleFont())
#        axis.SetTitleSize(self.cadreCalib.GetTitleSize())
#        axis.SetLabelSize(0.04)
#        axis.SetLabelFont(self.cadreCalib.GetLabelFont())
#        axis.SetTitle("high gain calibration")
#        axis.Draw()
                
        
        # hack
#        self.c1.SetLeftMargin(0.14)
#        self.c1.SetRightMargin(0.14)
        self.c1.Modified()
        self.c1.Update()

        self.plot_name = "calib_%s_history"%(self.PMTool.get_pmt_name_index(self.index))
        self.c1.Print("%s/%s.root" % (self.dir, self.plot_name))
        if self.doEps:
            ROOT.gStyle.SetPaperSize(26,20)
            self.c1.Print("%s/%s.eps" % (self.dir, self.plot_name))
        else:
            self.c1.Print("%s/%s.png" % (self.dir,self.plot_name))
            self.c1.Print("%s/%s.C" % (self.dir,self.plot_name))    

        self.cadreCalib.Delete()

        for tgraph in [ self.tgraph_lg, self.tgraph_lg_bad,
                        self.tgraph_hg, self.tgraph_hg_bad,
                        self.tgraph_lg_calib, self.tgraph_lg_calib_bad,
                        self.tgraph_hg_calib, self.tgraph_hg_calib_bad,
                        self.tgraph_hv]:
            tgraph.Delete()


        print(self.c1.GetName())

    
