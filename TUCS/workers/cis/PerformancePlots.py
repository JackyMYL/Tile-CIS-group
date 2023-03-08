# Author: Joshua Montgomery <joshua.montgomery@cern.ch>
# Oct. 13, 2011
# This Worker Generates the Performance Plots which plot against time
# The number of channels with no CIS calibration, with Bad CIS calibration, and Totals
# As well as a plot looking specifically at the 6 CIS Quality flags.
# This worker is called by the Performance_Macro.py macro.

# stdlib imports
import datetime
import calendar
import time

# 3rd party imports
import ROOT

# TUCS imports
import src.GenericWorker
import src.MakeCanvas
from src.oscalls import *
from src.region import *



class PerformancePlots(GenericWorker):

    def __init__(self, mindate=1293750000.0, maxdate=False, ext=['eps', 'root']):

        self.date_format = '%d/%m/%y'
        self.mindate = mindate
        self.maxdate = maxdate
        self.ext = ext
        
        if isinstance(self.mindate, str):
            self.mindate = time.mktime(time.strptime(self.mindate, self.date_format))
        if self.maxdate:
            if isinstance(self.maxdate, str):
                self.maxdate = time.mktime(time.strptime(self.maxdate, self.date_format))        

        self.dir = getPlotDirectory()
        self.dir = '%s/cis' % self.dir
        createDir(self.dir)
        self.dir = '%s/Public_Plots' % self.dir
        createDir(self.dir)
        self.dir = '%s/Performance_Plots' % self.dir
        createDir(self.dir)
        self.c1 = src.MakeCanvas.MakeCanvas()
        
        
        startdir    = getPlotDirectory()
        editdir     = startdir.split('/')
        plotindex   = editdir.index('plots')
        newstartdir = editdir[:plotindex]
        newdir = []
        for entry in newstartdir:
            newdir.append(entry)
        newdir.append('Performance_Plot_Data')
        PerfDir  = '/'.join(newdir)
        self.wiki_log_path = '{0}/Wiki_Status_Log.txt'.format(PerfDir)
       


    def ProcessStart(self):
        ## This is for us the combined macros ##
 
        Channel_Lists = self.Read_Wiki_Log()
        Standard_graphs, CIS_graphs = self.Fill_Perform_Plots(Channel_Lists)
        self.Draw_Perform_Plot(Standard_graphs)
        self.Draw_Perform_CIS_Plot(CIS_graphs)


    def Read_Wiki_Log(self):

        Wiki_log = open(self.wiki_log_path, 'r')
        linelist = []
        for line in Wiki_log:
            
            linelist.append(line.split('|')[1:10])

        dpts_list = list(range(len(linelist)))

        flag_Bad = [] #Number flagged as bad per date
        flag_DBDev = [] # Number flagged with DB Deviation flag per date
        flag_Likely_Calib = [] #Number flagged with Likely Calib flag per date
        flag_Max_Value = [] # Number flagged with Max Value flag per date
        flag_Low_Chi2 = [] # Number flagged with low Chi Sqr per date
        flag_Large_RMS = [] # Number flagged with large RMS per date
        flag_Digi_Err = [] # Number flagged with digital errors per date
        Num_No_Calibration = [] # Total number receiving calibrations
        Num_Failing_Flags = []
        
        for cnt in dpts_list:
            
            linelist[cnt][0] = linelist[cnt][0].strip(' ')
            linelist[cnt][0] = time.mktime(time.strptime(linelist[cnt][0], self.date_format))

            #########  Apply the requested Range #######
            
            if linelist[cnt][0]<self.mindate:
                continue
            if self.maxdate:
                if linelist[cnt][0]>self.maxdate:
                    continue
                
            linelist[cnt][1] = linelist[cnt][1].strip(' ')
            linelist[cnt][8] = linelist[cnt][8].strip(' ')

            ######### Parse and build the lists of data #######
            flag_Bad.append((linelist[cnt][0], int(linelist[cnt][1])))
            flag_DBDev.append((linelist[cnt][0], int(linelist[cnt][2].split('(-')[1].split(')')[0])))
            flag_Likely_Calib.append((linelist[cnt][0], int(linelist[cnt][3].split('(-')[1].split(')')[0])))
            flag_Max_Value.append((linelist[cnt][0], int(linelist[cnt][4].split('(-')[1].split(')')[0])))
            flag_Low_Chi2.append((linelist[cnt][0], int(linelist[cnt][5].split('(-')[1].split(')')[0])))
            flag_Large_RMS.append((linelist[cnt][0], int(linelist[cnt][6].split('(-')[1].split(')')[0])))
            flag_Digi_Err.append((linelist[cnt][0], int(linelist[cnt][7].split('(-')[1].split(')')[0])))
            Num_No_Calibration.append((linelist[cnt][0], 19704-int(linelist[cnt][8]))) # There are 19704 ADC Channels
            Num_Failing_Flags.append((linelist[cnt][0], int(linelist[cnt][1])-19704+int(linelist[cnt][8])))

        Performance_List = [flag_Bad, flag_DBDev, flag_Likely_Calib, flag_Max_Value,
                            flag_Low_Chi2, flag_Large_RMS, flag_Digi_Err, Num_No_Calibration, Num_Failing_Flags]

        Wiki_log.close()
        
        return Performance_List


    def Fill_Perform_Plots(self, Performance_List):

        ################  Make some Constants ##################
        self.t_min = min(Performance_List[0], key=lambda x: x[0])[0]
        self.t_max = max(Performance_List[0], key=lambda x: x[0])[0]
        self.t_num = len(Performance_List[0])
        self.t_tot_width = self.t_max - self.t_min       

        self.bad_chan_min = min(Performance_List[0], key=lambda x: x[1])[1]
        self.bad_chan_max = max(Performance_List[0], key=lambda x: x[1])[1]
        
        self.fail_chan_min = min(Performance_List[8], key=lambda x: x[1])[1]
        self.fail_chan_max = max(Performance_List[8], key=lambda x: x[1])[1]

        self.no_chan_min = min(Performance_List[7], key=lambda x: x[1])[1]
        self.no_chan_max = max(Performance_List[7], key=lambda x: x[1])[1]

        self.DB_chan_min = min(Performance_List[1], key=lambda x: x[1])[1]
        self.DB_chan_max = max(Performance_List[1], key=lambda x: x[1])[1]

        self.Likely_chan_min = min(Performance_List[2], key=lambda x: x[1])[1]
        self.Likely_chan_max = max(Performance_List[2], key=lambda x: x[1])[1]

        self.Max_chan_min = min(Performance_List[3], key=lambda x: x[1])[1]
        self.Max_chan_max = max(Performance_List[3], key=lambda x: x[1])[1]

        self.Chi2_chan_min = min(Performance_List[4], key=lambda x: x[1])[1]
        self.Chi2_chan_max = max(Performance_List[4], key=lambda x: x[1])[1]

        self.RMS_chan_min = min(Performance_List[5], key=lambda x: x[1])[1]
        self.RMS_chan_max = max(Performance_List[5], key=lambda x: x[1])[1]

        self.Digi_chan_min = min(Performance_List[6], key=lambda x: x[1])[1]
        self.Digi_chan_max = max(Performance_List[6], key=lambda x: x[1])[1]

        perform_max = [self.bad_chan_max, self.fail_chan_max, self.no_chan_max]
        perform_min = [self.bad_chan_min, self.fail_chan_min, self.no_chan_min]
        self.Perform_max = max(perform_max)
        self.Perform_min = min(perform_min)
        perform_cis_max = [self.DB_chan_max, self.Likely_chan_max, self.Max_chan_max, self.Chi2_chan_max, self.RMS_chan_max, self.Digi_chan_max]
        perform_cis_min = [self.DB_chan_min, self.Likely_chan_min, self.Max_chan_min, self.Chi2_chan_min, self.RMS_chan_min, self.Digi_chan_min]        
        self.Perform_cis_max = max(perform_cis_max)
        self.Perform_cis_min = min(perform_cis_min)   

        if self.Perform_min < 20:
            self.Perform_min = 0
        if self.Perform_cis_min < 20:
            self.Perform_cis_min = 0

        self.Perform_min = self.Perform_min*0.75
        self.Perform_cis_min = self.Perform_cis_min*0.75
        self.Perform_max = self.Perform_max*1.25
        self.Perform_cis_max = self.Perform_cis_max*1.25

        ############# Instantiate the TGraphs ##############

        graph_Bad = ROOT.TGraph()
        graph_No_Calib = ROOT.TGraph()
        graph_Num_Fail = ROOT.TGraph()

        graph_DBDev = ROOT.TGraph()
        graph_Likely = ROOT.TGraph()
        graph_Max = ROOT.TGraph()
        graph_Chi2 = ROOT.TGraph()
        graph_RMS = ROOT.TGraph()
        graph_Digi_Err = ROOT.TGraph()


        ##############  ASSEMBLE REGULAR GRAPHS ###############
        for point, (time, channels) in enumerate(Performance_List[0]):          
                graph_Bad.SetPoint(point, time, channels)

                
        for point, (time, channels) in enumerate(Performance_List[7]):
                graph_No_Calib.SetPoint(point, time, channels)

        for point, (time, channels) in enumerate(Performance_List[8]):
                graph_Num_Fail.SetPoint(point, time, channels)

        ############## ASSEMBLE CIS GRAPHS  #################

        for point, (time, channels) in enumerate(Performance_List[1]):
                graph_DBDev.SetPoint(point, time, channels)

        for point, (time, channels) in enumerate(Performance_List[2]):
                graph_Likely.SetPoint(point, time, channels)

        for point, (time, channels) in enumerate(Performance_List[3]):
                graph_Max.SetPoint(point, time, channels)

        for point, (time, channels) in enumerate(Performance_List[4]):
                graph_Chi2.SetPoint(point, time, channels)

        for point, (time, channels) in enumerate(Performance_List[5]):
                graph_RMS.SetPoint(point, time, channels)

        for point, (time, channels) in enumerate(Performance_List[6]):
                graph_Digi_Err.SetPoint(point, time, channels)

                
        Performance_Graphs = [graph_Bad, graph_No_Calib, graph_Num_Fail]
        Performance_CIS_Graphs = [graph_DBDev, graph_Likely, graph_Max, graph_Chi2, graph_RMS, graph_Digi_Err]

        return Performance_Graphs, Performance_CIS_Graphs

            
    def Draw_Perform_Plot(self, Performance_Graphs):
        'Draws the Basic Performance Plot (No Specific CIS Flag Information)'
        
        Performance_Graphs = Performance_Graphs

        badgraph = Performance_Graphs[0]
        nograph = Performance_Graphs[1]
        failgraph = Performance_Graphs[2]

        self.c1.Clear()
        ROOT.gStyle.SetOptStat(0)


        #### format the axes ####
        x_axis = badgraph.GetXaxis()
        timerange = x_axis.GetXmax() - x_axis.GetXmin()
        if timerange <= (10512000/2): # two months
            nweeks = int(timerange/657000)
            x_axis.SetNdivisions(nweeks, 5, 10, ROOT.kTRUE)
            x_axis.SetTimeDisplay(1)
            x_axis.SetTimeFormat('#splitline{%b %d}{%Y} %F1970-01-01 00:00:00')
            x_axis.SetLabelOffset(0.015)
        elif timerange <= (13140000): # five months
            nbiweeks = int(timerange/(1314000))
            x_axis.SetNdivisions(nbiweeks, 5, 10, ROOT.kTRUE)
            x_axis.SetTimeDisplay(1)
            x_axis.SetTimeFormat('#splitline{%b %d}{%Y} %F1970-01-01 00:00:00')
            x_axis.SetLabelOffset(0.015)
        elif timerange <= (21024000): # 8 months
            nmonths = int(timerange/(2628000))
            x_axis.SetNdivisions(nmonths, 5, 10, ROOT.kTRUE)
            x_axis.SetTimeDisplay(1)
            x_axis.SetTimeFormat('#splitline{%b}{%Y} %F1970-01-01 00:00:00')
            x_axis.SetLabelOffset(0.015)
        else:
            ntwomonths = int((timerange/5256000))
            x_axis.SetNdivisions(ntwomonths, 5, 10, ROOT.kTRUE)
            x_axis.SetTimeDisplay(1)
            x_axis.SetTimeFormat('#splitline{%b}{%Y} %F1970-01-01 00:00:00')
            x_axis.SetLabelOffset(0.015)
        x_axis.SetLabelSize(0.025)
        x_axis.SetTickLength(0.04)          

        y_axis = badgraph.GetYaxis()                
        y_axis.CenterTitle()
        y_axis.SetTitleOffset(1.25)
        y_axis.SetLabelSize(0.03)
        y_axis.SetLabelOffset(0.015)
        y_axis.SetRangeUser(self.Perform_min, self.Perform_max+30)        
        y_axis.SetTitleSize()
        y_axis.SetNdivisions(10, 5, 0, ROOT.kTRUE)
        
        #### format the graph ####

        badgraph.SetMarkerStyle(21)
        badgraph.SetMarkerSize(1)
        badgraph.GetYaxis().SetTitle('Number of ADC Channels')
        badgraph.SetMarkerColor(ROOT.kBlack)

        #badgraph.SetTitle('Performance Plot')    
        badgraph.Draw('AP')        

        nograph.SetMarkerStyle(22)
        nograph.SetMarkerSize(1)
        nograph.SetMarkerColor(ROOT.kBlue)
        nograph.Draw('psame')

        failgraph.SetMarkerStyle(23)
        failgraph.SetMarkerSize(1)
        failgraph.SetMarkerColor(ROOT.kRed)
        #failgraph.SetTitle('Performance Plot')    
        failgraph.Draw('psame')
    
        l3 = ROOT.TLatex()
        l3.SetNDC()
        l3.SetTextSize(0.04)
        l3.DrawLatex(0.3,0.96,"CIS Performance at Status Updates");


        ######### add maintenance periods ################
        
#################### 2011/2012 Maintenance Period ######################
        if self.t_min < 1335780000:
            if self.t_max > 1323946800:
                t_maint_2011_min = 1323946800 + 600000
                t_maint_2011_max = 1335780000 - 3100000
                t_maint_2011_width = t_maint_2011_max - t_maint_2011_min
                t_maint_2011_mid = ((t_maint_2011_max - t_maint_2011_min) * (0.65)) + t_maint_2011_min
                t_maint_perc = t_maint_2011_width/self.t_tot_width
                
                lm_Dec_2011 = ROOT.TLine(t_maint_2011_min, self.Perform_min, t_maint_2011_min, self.Perform_max)
                lm_Dec_2011.SetLineColor(ROOT.kRed+2)
                lm_Dec_2011.SetLineWidth(1)
                lm_Dec_2011.SetLineStyle(2)
                lm_Dec_2011.Draw("same")

                lm_Jan_2012 = ROOT.TLine(t_maint_2011_max, self.Perform_min, t_maint_2011_max, self.Perform_max)
                lm_Jan_2012.SetLineColor(ROOT.kRed+2)
                lm_Jan_2012.SetLineWidth(1)
                lm_Jan_2012.SetLineStyle(2)
                lm_Jan_2012.Draw("same")

                if t_maint_perc > 0.07:
                    mcoordinate_2011 = (0.47/2)*(self.Perform_max - self.Perform_min) + self.Perform_min
                    maint_2012 = ROOT.TLatex()
                    maint_2012.SetTextFont(72)
                    maint_2012.SetTextAngle(90)
                    maint_2012.SetTextSize(0.04)
                    maint_2012.DrawLatex(t_maint_2011_mid, mcoordinate_2011,"Maintenance Period")

                elif t_maint_perc > 0.03:
                    mcoordinate_2010 = (0.75/2)*(self.Perform_max - self.Perform_min) + self.Perform_min
                    maint_2012 = ROOT.TLatex()
                    maint_2012.SetTextFont(72)
                    maint_2012.SetTextAngle(90)
                    maint_2012.SetTextSize(0.025)
                    maint_2012.DrawLatex(t_maint_2011_mid, mcoordinate_2011,"Maintenance Period")
        
#################### 2010/2011 Maintenance Period ######################
        if self.t_min < 1289779200:
            if self.t_max > 1296518400:
                t_maint_2010_min = 1290816000 + 600000
                t_maint_2010_max = 1296172800 - 1100000
                t_maint_2010_width = t_maint_2010_max - t_maint_2010_min
                t_maint_2010_mid = ((t_maint_2010_max - t_maint_2010_min) * (0.60)) + t_maint_2010_min
                t_maint_perc = t_maint_2010_width/self.t_tot_width
                
                lm_Nov_2010 = ROOT.TLine(t_maint_2010_min, self.Perform_min, t_maint_2010_min, self.Perform_max)
                lm_Nov_2010.SetLineColor(ROOT.kRed+2)
                lm_Nov_2010.SetLineWidth(1)
                lm_Nov_2010.SetLineStyle(2)
                lm_Nov_2010.Draw("same")

                lm_Jan_2011 = ROOT.TLine(t_maint_2010_max, self.Perform_min, t_maint_2010_max, self.Perform_max)
                lm_Jan_2011.SetLineColor(ROOT.kRed+2)
                lm_Jan_2011.SetLineWidth(1)
                lm_Jan_2011.SetLineStyle(2)
                lm_Jan_2011.Draw("same")

                if t_maint_perc > 0.07:
                    mcoordinate_2010 = (0.55/2)*(self.Perform_max - self.Perform_min) + self.Perform_min
                    maint_2011 = ROOT.TLatex()
                    maint_2011.SetTextFont(72)
                    maint_2011.SetTextAngle(90)
                    maint_2011.SetTextSize(0.04)
                    maint_2011.DrawLatex(t_maint_2010_mid, mcoordinate_2010,"Maintenance Period")

                elif t_maint_perc > 0.03:
                    mcoordinate_2010 = (0.75/2)*(self.Perform_max - self.Perform_min) + self.Perform_min
                    maint_2011 = ROOT.TLatex()
                    maint_2011.SetTextFont(72)
                    maint_2011.SetTextAngle(90)
                    maint_2011.SetTextSize(0.025)
                    maint_2011.DrawLatex(t_maint_2010_mid, mcoordinate_2010,"Maintenance Period")
                    
################  09/10 Maintenance period ###############################
                    
        if self.t_min < 1259366400:
            if self.t_max > 1266192000:
                t_maint_2009_min = 1259884800 + 800000
                t_maint_2009_max = 1264982400 - 750000
                t_maint_2009_width = t_maint_2009_max - t_maint_2009_min
                t_maint_2009_mid = ((t_maint_2009_max - t_maint_2009_min) * (0.60)) + t_maint_2009_min               
                t_maint_perc = t_maint_2009_width/self.t_tot_width
                
                lm_Nov_2009 = ROOT.TLine(t_maint_2009_min, self.Perform_min, t_maint_2009_min, self.Perform_max)
                lm_Nov_2009.SetLineColor(ROOT.kRed+2)
                lm_Nov_2009.SetLineWidth(1)
                lm_Nov_2009.SetLineStyle(2)
                lm_Nov_2009.Draw("same")

                lm_Jan_2010 = ROOT.TLine(t_maint_2009_max, self.Perform_min, t_maint_2009_max, self.Perform_max)
                lm_Jan_2010.SetLineColor(ROOT.kRed+2)
                lm_Jan_2010.SetLineWidth(1)
                lm_Jan_2010.SetLineStyle(2)
                lm_Jan_2010.Draw("same")

                if t_maint_perc > 0.07:
                    mcoordinate_2009 = (0.55/2)*(self.Perform_max - self.Perform_min) + self.Perform_min
                    maint_2010 = ROOT.TLatex()
                    maint_2010.SetTextFont(72)
                    maint_2010.SetTextAngle(90)
                    maint_2010.SetTextSize(0.04)
                    maint_2010.DrawLatex(t_maint_2009_mid, mcoordinate_2009,"Maintenance Period")
                    
                elif t_maint_perc > 0.03:
                    mcoordinate_2009 = (0.75/2)*(self.Perform_max - self.Perform_min) + self.Perform_min
                    maint_2010 = ROOT.TLatex()
                    maint_2010.SetTextFont(72)
                    maint_2010.SetTextAngle(90)
                    maint_2010.SetTextSize(0.025)
                    maint_2010.DrawLatex(t_maint_2009_mid, mcoordinate_2009,"Maintenance Period")

######################  08/09 Maintenance Period ###############################
        
        if self.t_min < 1228348800:
            if self.t_max > 1236643200:
                t_maint_2008_min = 1228867200 + 750000
                t_maint_2008_max = 1236384000 - 750000
                t_maint_2008_width = t_maint_2008_max - t_maint_2008_min
                t_maint_2008_mid = ((t_maint_2008_max - t_maint_2008_min) * (0.60)) + t_maint_2008_min               
                t_maint_perc = t_maint_2008_width/self.t_tot_width
                
                lm_Dec_2008 = ROOT.TLine(t_maint_2008_min, self.Perform_min, t_maint_2008_min, self.Perform_max)
                lm_Dec_2008.SetLineColor(ROOT.kRed+2)
                lm_Dec_2008.SetLineWidth(1)
                lm_Dec_2008.SetLineStyle(2)
                lm_Dec_2008.Draw("same")

                lm_Mar_2009 = ROOT.TLine(t_maint_2008_max, self.Perform_min, t_maint_2008_max, self.Perform_max)
                lm_Mar_2009.SetLineColor(ROOT.kRed+2)
                lm_Mar_2009.SetLineWidth(1)
                lm_Mar_2009.SetLineStyle(2)
                lm_Mar_2009.Draw("same")

                if t_maint_perc > 0.07:
                    mcoordinate_2008 = (0.55/2)*(self.Perform_max - self.Perform_min) + self.Perform_min
                    maint_2009 = ROOT.TLatex()
                    maint_2009.SetTextFont(72)
                    maint_2009.SetTextAngle(90)
                    maint_2009.SetTextSize(0.04)
                    maint_2009.DrawLatex(t_maint_2008_mid, mcoordinate_2008,"Maintenance Period")

                elif t_maint_perc > 0.03:
                    mcoordinate_2008 = (0.75/2)*(self.Perform_max - self.Perform_min) + self.Perform_min
                    maint_2009 = ROOT.TLatex()
                    maint_2009.SetTextFont(72)
                    maint_2009.SetTextAngle(90)
                    maint_2009.SetTextSize(0.025)
                    maint_2009.DrawLatex(t_maint_2008_mid, mcoordinate_2008,"Maintenance Period")

        #### Add Legend ####
        leg = ROOT.TLegend(0.20, 0.80, 0.27, 0.9, "", "brNDC")
        leg.SetBorderSize(0)
        leg.SetFillColor(0)
        leg.SetTextSize(0.037);
        leg.AddEntry(failgraph,"Channels failing quality flags","P");
        leg.AddEntry(nograph,"Channels giving no data","P");
        leg.AddEntry(badgraph,"Total Channels with bad status","P");
        leg.Draw()

        #### Put print out info here ####
        for exts in self.ext:
            self.c1.Print('{path}/{name}.{ext}'.format(path=self.dir,
                                    name='Performance Plot', ext=exts))


    def Draw_Perform_CIS_Plot(self, Performance_CIS_Graphs):
        'Draws the Basic Performance Plot with CIS Flag Information'
        Performance_CIS_Graphs = Performance_CIS_Graphs

        DBgraph = Performance_CIS_Graphs[0]
        Likelygraph = Performance_CIS_Graphs[1]
        Maxgraph = Performance_CIS_Graphs[2]
        Chi2graph = Performance_CIS_Graphs[3]
        RMSgraph = Performance_CIS_Graphs[4]
        Digigraph = Performance_CIS_Graphs[5]
        
        self.c1.Clear()

        #DBgraph.SetTitle('Performance CIS Plot')

        #### format the axes ####
        x_axis = DBgraph.GetXaxis()

        timerange = x_axis.GetXmax() - x_axis.GetXmin()
        if timerange <= (10512000/2): # two months
            nweeks = int(timerange/657000)
            x_axis.SetNdivisions(nweeks, 5, 5, ROOT.kTRUE)
            x_axis.SetTimeDisplay(1)
            x_axis.SetTimeFormat('#splitline{%b %d}{%Y} %F1970-01-01 00:00:00')
            x_axis.SetLabelOffset(0.015)
        elif timerange <= (13140000): # five months
            nbiweeks = int(timerange/(1314000))
            x_axis.SetNdivisions(nbiweeks, 5, 10, ROOT.kTRUE)
            x_axis.SetTimeDisplay(1)
            x_axis.SetTimeFormat('#splitline{%b %d}{%Y} %F1970-01-01 00:00:00')
            x_axis.SetLabelOffset(0.015)
        elif timerange <= (21024000): # 8 months
            nmonths = int(timerange/(2628000))
            x_axis.SetNdivisions(nmonths, 5, 10, ROOT.kTRUE)
            x_axis.SetTimeDisplay(1)
            x_axis.SetTimeFormat('#splitline{%b}{%Y} %F1970-01-01 00:00:00')
            x_axis.SetLabelOffset(0.015)
        else:
            ntwomonths = int((timerange/5256000))
            x_axis.SetNdivisions(ntwomonths, 5, 10, ROOT.kTRUE)
            x_axis.SetTimeDisplay(1)
            x_axis.SetTimeFormat('#splitline{%b}{%Y} %F1970-01-01 00:00:00')
            x_axis.SetLabelOffset(0.015)
        x_axis.SetLabelSize(0.025)
        x_axis.SetTickLength(0.04)

        y_axis = DBgraph.GetYaxis()
        y_axis.CenterTitle()
        y_axis.SetTitleOffset(1.25)
        y_axis.SetTitleSize()
        y_axis.SetLabelSize(0.03)
        y_axis.SetLabelOffset(0.015)
        y_axis.SetRangeUser(self.Perform_cis_min, self.Perform_cis_max+30)        
        y_axis.SetNdivisions(10, 5, 0, ROOT.kTRUE)
        
        #### format the graph ####
        DBgraph.SetMarkerStyle(23)
        DBgraph.SetMarkerSize(1)
        DBgraph.GetYaxis().SetTitle('Number of ADC Channels')
        DBgraph.SetMarkerColor(ROOT.kBlack)
        DBgraph.Draw('AP')

        Likelygraph.SetMarkerStyle(23)
        Likelygraph.SetMarkerSize(1)
        Likelygraph.SetMarkerColor(ROOT.kBlue)
        Likelygraph.Draw('psame')

        Maxgraph.SetMarkerStyle(23)
        Maxgraph.SetMarkerSize(1)
        Maxgraph.SetMarkerColor(ROOT.kRed)
        Maxgraph.Draw('psame')

        Chi2graph.SetMarkerStyle(23)
        Chi2graph.SetMarkerSize(1)
        Chi2graph.SetMarkerColor(ROOT.kGreen)
        Chi2graph.Draw('psame')

        RMSgraph.SetMarkerStyle(23)
        RMSgraph.SetMarkerSize(1)
        RMSgraph.SetMarkerColor(ROOT.kOrange)
        RMSgraph.Draw('psame')

        Digigraph.SetMarkerStyle(23)
        Digigraph.SetMarkerSize(1)
        Digigraph.SetMarkerColor(ROOT.kViolet)
        Digigraph.Draw('psame')

        l4 = ROOT.TLatex()
        l4.SetNDC()
        l4.SetTextSize(0.04)
        l4.DrawLatex(0.25,0.96,"Detailed CIS Performance at Status Updates");


        ######### add maintenance periods ################   
        

#################### 2011/2012 Maintenance Period ######################
        if self.t_min < 1335780000:
            if self.t_max > 1323946800:
                t_maint_2011_min = 1323946800 + 600000
                t_maint_2011_max = 1335780000 - 3100000
                t_maint_2011_width = t_maint_2011_max - t_maint_2011_min
                t_maint_2011_mid = ((t_maint_2011_max - t_maint_2011_min) * (0.60)) + t_maint_2011_min
                t_maint_perc = t_maint_2011_width/self.t_tot_width
                
                lm_Dec_2011 = ROOT.TLine(t_maint_2011_min, self.Perform_cis_min, t_maint_2011_min, self.Perform_cis_max)
                lm_Dec_2011.SetLineColor(ROOT.kRed+2)
                lm_Dec_2011.SetLineWidth(1)
                lm_Dec_2011.SetLineStyle(2)
                lm_Dec_2011.Draw("same")

                lm_Jan_2012 = ROOT.TLine(t_maint_2011_max, self.Perform_cis_min, t_maint_2011_max, self.Perform_cis_max)
                lm_Jan_2012.SetLineColor(ROOT.kRed+2)
                lm_Jan_2012.SetLineWidth(1)
                lm_Jan_2012.SetLineStyle(2)
                lm_Jan_2012.Draw("same")

                if t_maint_perc > 0.07:
                    mcoordinate_2011 = (0.55/2)*(self.Perform_cis_max - self.Perform_cis_min) + self.Perform_cis_min
                    maint_2012 = ROOT.TLatex()
                    maint_2012.SetTextFont(72)
                    maint_2012.SetTextAngle(90)
                    maint_2012.SetTextSize(0.04)
                    maint_2012.DrawLatex(t_maint_2011_mid, mcoordinate_2011,"Maintenance Period")

                elif t_maint_perc > 0.03:
                    mcoordinate_2010 = (0.75/2)*(self.Perform_cis_max - self.Perform_cis_min) + self.Perform_cis_min
                    maint_2012 = ROOT.TLatex()
                    maint_2012.SetTextFont(72)
                    maint_2012.SetTextAngle(90)
                    maint_2012.SetTextSize(0.025)
                    maint_2012.DrawLatex(t_maint_2011_mid, mcoordinate_2011,"Maintenance Period")
        
#################### 2010/2011 Maintenance Period ######################

        if self.t_min < 1288569600:
            if self.t_max > 1296518400:
                t_maint_2010_min = 1290816000 + 600000
                t_maint_2010_max = 1296172800 - 1100000
                t_maint_2010_width = t_maint_2010_max - t_maint_2010_min
                t_maint_2010_mid = ((t_maint_2010_max - t_maint_2010_min) * (0.60)) + t_maint_2010_min
                t_maint_perc = t_maint_2010_width/self.t_tot_width
                
                lm_Nov_2010 = ROOT.TLine(t_maint_2010_min, self.Perform_cis_min, t_maint_2010_min, self.Perform_cis_max)
                lm_Nov_2010.SetLineColor(ROOT.kRed+2)
                lm_Nov_2010.SetLineWidth(1)
                lm_Nov_2010.SetLineStyle(2)
                lm_Nov_2010.Draw("same")

                lm_Jan_2011 = ROOT.TLine(t_maint_2010_max, self.Perform_cis_min, t_maint_2010_max, self.Perform_cis_max)
                lm_Jan_2011.SetLineColor(ROOT.kRed+2)
                lm_Jan_2011.SetLineWidth(1)
                lm_Jan_2011.SetLineStyle(2)
                lm_Jan_2011.Draw("same")

                if t_maint_perc > 0.07:
                    mcoordinate_2010 = (0.55/2)*(self.Perform_cis_max - self.Perform_cis_min) + self.Perform_cis_min
                    maint_2011 = ROOT.TLatex()
                    maint_2011.SetTextSize(0.04)
                    maint_2011.SetTextFont(72)
                    maint_2011.SetTextAngle(90)
                    
                    maint_2011.DrawLatex(t_maint_2010_mid, mcoordinate_2010,"Maintenance Period")

                elif t_maint_perc > 0.03:
                    mcoordinate_2010 = (0.75/2)*(self.Perform_cis_max - self.Perform_cis_min) + self.Perform_cis_min
                    maint_2011 = ROOT.TLatex()
                    maint_2011.SetTextFont(72)
                    maint_2011.SetTextAngle(90)
                    maint_2011.SetTextSize(0.025)
                    maint_2011.DrawLatex(t_maint_2010_mid, mcoordinate_2010,"Maintenance Period")
                    
################  09/10 Maintenance period ###############################
                    
        if self.t_min < 1259366400:
            if self.t_max > 1266192000:
                t_maint_2009_min = 1259884800 + 750000
                t_maint_2009_max = 1264982400 - 650000
                t_maint_2009_width = t_maint_2009_max - t_maint_2009_min
                t_maint_2009_mid = ((t_maint_2009_max - t_maint_2009_min) * (0.60)) + t_maint_2009_min               
                t_maint_perc = t_maint_2009_width/self.t_tot_width
                
                lm_Nov_2009 = ROOT.TLine(t_maint_2009_min, self.Perform_cis_min, t_maint_2009_min, self.Perform_cis_max)
                lm_Nov_2009.SetLineColor(ROOT.kRed+2)
                lm_Nov_2009.SetLineWidth(1)
                lm_Nov_2009.SetLineStyle(2)
                lm_Nov_2009.Draw("same")

                lm_Jan_2010 = ROOT.TLine(t_maint_2009_max, self.Perform_cis_min, t_maint_2009_max, self.Perform_cis_max)
                lm_Jan_2010.SetLineColor(ROOT.kRed+2)
                lm_Jan_2010.SetLineWidth(1)
                lm_Jan_2010.SetLineStyle(2)
                lm_Jan_2010.Draw("same")

                if t_maint_perc > 0.07:
                    mcoordinate_2009 = (0.35/2)*(self.Perform_cis_max - self.Perform_cis_min) + self.Perform_cis_min
                    maint_2010 = ROOT.TLatex()
                    maint_2010.SetTextFont(72)
                    maint_2010.SetTextAngle(90)
                    maint_2010.SetTextSize(0.04)
                    maint_2010.DrawLatex(t_maint_2009_mid, mcoordinate_2009,"Maintenance Period")

                elif t_maint_perc > 0.03:
                    mcoordinate_2009 = (0.75/2)*(self.Perform_cis_max - self.Perform_cis_min) + self.Perform_cis_min
                    maint_2010 = ROOT.TLatex()
                    maint_2010.SetTextFont(72)
                    maint_2010.SetTextAngle(90)
                    maint_2010.SetTextSize(0.025)
                    maint_2010.DrawLatex(t_maint_2009_mid, mcoordinate_2009,"Maintenance Period")

######################  08/09 Maintenance Period ###############################
        
        if self.t_min < 1228348800:
            if self.t_max > 1236643200:
                t_maint_2008_min = 1228867200 + 750000
                t_maint_2008_max = 1236384000 - 750000
                t_maint_2008_width = t_maint_2008_max - t_maint_2008_min
                t_maint_2008_mid = ((t_maint_2008_max - t_maint_2008_min) * (0.60)) + t_maint_2008_min               
                t_maint_perc = t_maint_2008_width/self.t_tot_width
                
                lm_Dec_2008 = ROOT.TLine(t_maint_2008_min, self.Perform_cis_min, t_maint_2008_min, self.Perform_cis_max)
                lm_Dec_2008.SetLineColor(ROOT.kRed+2)
                lm_Dec_2008.SetLineWidth(1)
                lm_Dec_2008.SetLineStyle(2)
                lm_Dec_2008.Draw("same")

                lm_Mar_2009 = ROOT.TLine(t_maint_2008_max, self.Perform_cis_min, t_maint_2008_max, self.Perform_cis_max)
                lm_Mar_2009.SetLineColor(ROOT.kRed+2)
                lm_Mar_2009.SetLineWidth(1)
                lm_Mar_2009.SetLineStyle(2)
                lm_Mar_2009.Draw("same")

                if t_maint_perc > 0.07:
                    mcoordinate_2008 = (0.35/2)*(self.Perform_cis_max - self.Perform_cis_min) + self.Perform_cis_min
                    maint_2009 = ROOT.TLatex()
                    maint_2009.SetTextFont(72)
                    maint_2009.SetTextAngle(90)
                    maint_2009.SetTextSize(0.04)
                    maint_2009.DrawLatex(t_maint_2008_mid, mcoordinate_2008,"Maintenance Period")

                if t_maint_perc > 0.03:
                    mcoordinate_2008 = (0.75/2)*(self.Perform_cis_max - self.Perform_cis_min) + self.Perform_cis_min
                    maint_2009 = ROOT.TLatex()
                    maint_2009.SetTextFont(72)
                    maint_2009.SetTextAngle(90)
                    maint_2009.SetTextSize(0.025)
                    maint_2009.DrawLatex(t_maint_2008_mid, mcoordinate_2008,"Maintenance Period")

        #### add a legend ####
        leg = ROOT.TLegend(0.45, 0.71, 0.6, 0.91, "", "brNDC")        
        leg.SetBorderSize(0)
        leg.SetFillColor(0)
        leg.SetTextSize(0.037);
        leg.AddEntry(DBgraph, "Channels failing DB Dev flag", "P");
        leg.AddEntry(Likelygraph, "Channels failing Likely Calib flag", "P");
        leg.AddEntry(Maxgraph, "Channels failing Max Point flag", "P");
        leg.AddEntry(Chi2graph, "Channels failing Chi2 flag", "P");
        leg.AddEntry(RMSgraph, "Channels failing RMS flag", "P");
        leg.AddEntry(Digigraph, "Channels failing Digital Errors flag", "P");
        leg.Draw()

     

        #### Put print out info here ####
        for exts in self.ext:
            self.c1.Print('{path}/{name}.{ext}'.format(path=self.dir,
                                    name='Performance CIS Plot', ext=exts))

    def ProcessRegion(self, region):

        pass

    def ProcessStop(self):

        pass
