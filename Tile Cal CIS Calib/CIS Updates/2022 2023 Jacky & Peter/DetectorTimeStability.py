#Author: Noah Wasserman
#August 6th, 2012

# stlib imports
import datetime
import calendar
import time

# 3rd party imports, ROOT
import ROOT

# TUCS imports
import src.ReadGenericCalibration
import src.MakeCanvas
from src.oscalls import *
from src.region import *
#from array import array

class DetectorTimeStability(ReadGenericCalibration):
    #Make public plot of time stability of detector averages

    def __init__(self, dateLabel, mindate=1293750000.0, maxdate=False, exts=['pdf','eps', 'png', 'root', 'C']):

        self.rundictlowgain={}
        self.rundicthighgain={}
        self.rundictdem={}

        self.singchanlo=[]
        self.singchanhi=[]
        self.singchandem=[]

        self.dateLabel = dateLabel
        self.date_format = '%m/%d/%y'
        self.mindate = mindate
        self.maxdate = maxdate
        self.exts = exts

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
        self.dir = '%s/DetectorTimeStability' % self.dir
        createDir(self.dir)
        
        self.c1 = src.MakeCanvas.MakeCanvas()
        
    def ProcessStart(self):
        print("MIN AND MAX DATES")
        print(self.mindate)
        print(self.maxdate)
        self.hist = ROOT.TH2D("throw away histo", "", 1, self.mindate,self.maxdate,1,0,1)
        print(self.c1.GetTickx())
        print(self.c1.GetTicky())

    def ProcessStop(self):
        datahigh = self.rundicthighgain
        datalow = self.rundictlowgain
        datadem = self.rundictdem
        
        highgainaverages = []
        lowgainaverages = []
        demaverages = []

        for run in self.rundicthighgain:
        
            highgainaverages.append((run, float(datahigh[run][0])/float(datahigh[run][1]), datahigh[run][1]))
        
        for run in self.rundictlowgain:
        
            lowgainaverages.append((run, float(datalow[run][0])/float(datalow[run][1]), datalow[run][1]))
        
        for run in self.rundictdem:
        
            demaverages.append((run, float(datadem[run][0])/float(datadem[run][1]), datadem[run][1]))
        
        # Low gain
        runs1 = []
        calibs = []
        ey = []
        ex = []
        Nchan = []
        
        for number, entry in enumerate(sorted(lowgainaverages)):
            if number%2 == 0:
                runs1.append(entry[0])
                calibs.append(entry[1])
                ey.append(0)
                ex.append(0)
                Nchan.append(entry[2])   
        mean = ROOT.TMath.Mean(len(calibs), array('f', calibs))
        minrun = sorted(lowgainaverages)[0][0]
        

        self.graphlow = ROOT.TGraphErrors(len(calibs), array('f', runs1), array('f', calibs), array('f',ex), array('f', ey))
        
        calibs = []
        ey = []
        ex = []
        runs2 = []
        
        for singentry in sorted(self.singchanlo):
            
            if singentry[0] in runs1:
                calibs.append(singentry[1])
                runs2.append(singentry[0])
                ey.append(singentry[1]*.007)
                ex.append(0)  
                              

        self.graphlowsing = ROOT.TGraphErrors(len(calibs), array('f', runs2),array('f', calibs),array('f', ex),array('f', ey)) 
        #title = '#bf{Average Low-gain CIS Stability: Oct-Dec 2014}'
        title = '#bf{Average Low-gain CIS Stability}'
        Nchanmax = max(Nchan)
        self.process_graph(self.graphlow, self.graphlowsing, title, 'LowgainDetAvg', Nchanmax, mean, minrun)

        # High gain        
        calibs = []
        runs1 = []
        ey = []
        ex = []
        Nchan = []
        for number, entry in enumerate(sorted(highgainaverages)):
            if number%2 == 0:
                if (entry[0] > 1330000000.0) or (entry[0] < 1324508400.0 and entry[0] > 1294614000.0):
                    calibs.append(entry[1])
                    runs1.append(entry[0])
                    ex.append(0)
                    ey.append(0)   
                    Nchan.append(entry[2])
                            
        mean = ROOT.TMath.Mean(len(calibs), array('f', calibs))
        minrun = sorted(highgainaverages)[0][0]
             
        self.graphhigh = ROOT.TGraphErrors(len(calibs), array('f', runs1), array('f', calibs), array('f', ex),array('f',ey))
        
        calibs = []
        ey = []
        ex = []
        runs2 = []
        
        for singentry in sorted(self.singchanhi):
            
            if singentry[0] in runs1:
                calibs.append(singentry[1])
                runs2.append(singentry[0])
                ey.append(singentry[1]*.007)
                ex.append(0)                
        
        
        self.graphhighsing = ROOT.TGraphErrors(len(calibs), array('f', runs2),array('f', calibs),array('f', ex),array('f', ey))
        
        #title = '#bf{Average High-gain CIS Stability: Oct-Dec 2014}'
        title = '#bf{Average High-gain CIS Stability}'
        Nchanmax = max(Nchan)
        self.process_graph(self.graphhigh, self.graphhighsing, title, 'HighgainDetAvg', Nchanmax, mean, minrun)

    
        # Demonstrator
        calibs = []
        runs1 = []
        ey = []
        ex = []
        Nchan = []
        for number, entry in enumerate(sorted(demaverages)):
            if number%2 == 0:
                if (entry[0] > 1330000000.0) or (entry[0] < 1324508400.0 and entry[0] > 1294614000.0): # What does this do
                    calibs.append(entry[1])
                    runs1.append(entry[0])
                    ex.append(0)
                    ey.append(0)   
                    Nchan.append(entry[2])
                            
        mean = ROOT.TMath.Mean(len(calibs), array('f', calibs))
        minrun = sorted(demaverages)[0][0]
             
        self.graphdem = ROOT.TGraphErrors(len(calibs), array('f', runs1), array('f', calibs), array('f', ex),array('f',ey))
        
        calibs = []
        ey = []
        ex = []
        runs2 = []
        
        for singentry in sorted(self.singchandem):
            
            if singentry[0] in runs1:
                calibs.append(singentry[1])
                runs2.append(singentry[0])
                ey.append(singentry[1]*.007)
                ex.append(0)                
        
        
        self.graphdemsing = ROOT.TGraphErrors(len(calibs), array('f', runs2),array('f', calibs),array('f', ex),array('f', ey))
        
        #title = '#bf{Average High-gain CIS Stability: Oct-Dec 2014}'
        title = '#bf{Demonstrator CIS Stability}'
        Nchanmax = max(Nchan)
        self.process_graph(self.graphdem, self.graphdemsing, title, 'HighgainDetAvg', Nchanmax, mean, minrun)

            
    def process_graph(self, graph, graphsing, title, filename, Nchannels, mean, min):
        
        print("test 1")
        print(title, filename)
        print("test 2")
        
        self.c1.Clear()
        ROOT.gPad.SetTickx()
        ROOT.gPad.SetTicky()                  
        description = 'BAD FILENAME' 
        #monthstr = "Aug 2015-Nov 2018"
        #monthstr = "Aug 2015-Oct 2015"
        monthstr = "Apr 2016-Nov 2016"
        #monthstr = "May 2017-Nov 2017"
        #monthstr = "Aug 2015-Nov 2018"
        if filename[:2] == 'Hi' and "High" in title:
            description = 'HG ADCs'
        elif filename[:2] == 'Hi' and "High" not in title:
            desciption = "Demonstrator ADCs"

        
        if filename[:2] == 'Lo':
           description = 'LG ADCs'

       
        # format the axes
        x_axis = self.hist.GetXaxis()
        timerange = x_axis.GetXmax() - x_axis.GetXmin()
        if timerange <= (10512000/2): # two months
            print('TIME1')
            nweeks = int(timerange/657000)
            x_axis.SetNdivisions(nweeks, 5, 10, ROOT.kTRUE)
            x_axis.SetTimeDisplay(1)
            x_axis.SetTimeFormat('#splitline{%b %d}{%Y} %F1970-01-01 00:00:00')
            x_axis.SetLabelOffset(0.025)
        elif timerange <= (13140000): # five months
            print('TIME2')
            nbiweeks = int(timerange/(1314000)) + 1
            print(nbiweeks)
            x_axis.SetNdivisions(nbiweeks, 5, 10, ROOT.kTRUE)
            x_axis.SetTimeDisplay(1)
            x_axis.SetTimeFormat('#splitline{%b %d}{%Y} %F1970-01-01 00:00:00')
            x_axis.SetLabelOffset(0.025)
        elif timerange <= (21024000): # 8 months
            print('TIME3')
            nmonths = int(timerange/(2628000))
            x_axis.SetNdivisions(nmonths, 5, 10, ROOT.kTRUE)
            x_axis.SetTimeDisplay(1)
            x_axis.SetTimeFormat('#splitline{%b}{%Y} %F1970-01-01 00:00:00')
            x_axis.SetLabelOffset(0.025)
        else:
            ntwomonths = int((timerange/5256000))
            print('TIME4')
            x_axis.SetNdivisions(ntwomonths, 5, 10, ROOT.kTRUE)
            x_axis.SetTimeDisplay(1)
            x_axis.SetTimeFormat('#splitline{%b}{%Y} %F1970-01-01 00:00:00')
            x_axis.SetLabelOffset(0.025)
        x_axis.SetLabelSize(0.025)
        x_axis.SetTickLength(0.04) 
        x_axis.SetRangeUser(self.mindate, self.maxdate)

        y_axis = self.hist.GetYaxis()
        y_axis.SetTitleOffset(1.2)
        y_axis.SetTitle('CIS Calibration [ADC count/pC]')
        y_axis.CenterTitle(True)
        y_axis.SetNdivisions(10, 5, 0, ROOT.kTRUE)
        self.hist.SetBins(1, self.mindate, self.maxdate, 1, mean * 0.97, mean * 1.03)
        self.hist.Draw()
        self.hist.SetStats(0)

##OLD VERSION
       # # format the graph
       # graph.SetMarkerStyle(20)
       # graph.SetMarkerSize(1.3)
       # graph.SetMarkerColor(ROOT.kBlack)
       # graph.Draw('sameP')
       # graphsing.SetMarkerStyle(23)
       # graphsing.SetMarkerSize(1.3)
       # graphsing.SetMarkerColor(Root.kBlue)
       # graphsing.SetLineColor(Root.kBlue)
       # graphsing.Draw("sameP")
       #

##NEW VERSION

        graph.SetMarkerStyle(20)
        graph.SetMarkerSize(1.3)
        graph.SetMarkerColor(ROOT.kBlack)
        graphsing.SetMarkerStyle(23)
        graphsing.SetMarkerSize(1.3)
        graphsing.SetMarkerColor(ROOT.kBlue)
        graphsing.SetLineColor(ROOT.kYellow)
        graphsing.SetFillColor(ROOT.kYellow)
 #       graphsing.Draw("sameP")
        graphsing.Draw("sameE3")
        graphsing.Draw("sameP")
        graph.Draw("sameP")
 
        maintenance = False
                    
        maintline = ROOT.TLine(1294614000.0, mean * .97, 1294614000.0, mean * 1.03)
        maintline.SetLineColor(ROOT.kRed+2)
        maintline.SetLineWidth(1)
        maintline.SetLineStyle(2)
        if self.mindate <= 1294614000.0 and self.maxdate >= 1294614000.0:
            maintline.Draw("same")
            maintenance = True
        
        maintlinestart = ROOT.TLine(1324508400.0, mean * .97, 1324508400.0, mean * 1.03)
        maintlinestart.SetLineColor(ROOT.kRed+2)
        maintlinestart.SetLineWidth(1)
        maintlinestart.SetLineStyle(2)
        atlastext2 = ROOT.TLatex()
        if self.mindate <= 1294614000.0 and self.maxdate >= 1294614000.0:
            maintline.Draw("same")
            maintenance = True
        
        maintlinestart = ROOT.TLine(1324508400.0, mean * .97, 1324508400.0, mean * 1.03)
        maintlinestart.SetLineColor(ROOT.kRed+2)
        maintlinestart.SetLineWidth(1)
        maintlinestart.SetLineStyle(2)
        if self.mindate <= 1324508400.0 and self.maxdate >= 1324508400.0:
            maintlinestart.Draw("same")
            maintenance = True
        
        maintlineend = ROOT.TLine(1328828400.0, mean * .97, 1328828400.0, mean * 1.03)
        maintlineend.SetLineColor(ROOT.kRed+2)
        maintlineend.SetLineWidth(1)
        maintlineend.SetLineStyle(2)
        if self.mindate <= 1328828400.0 and self.maxdate >= 1328828400.0:
            maintlineend.Draw("same")
            maintenance = True
        
        # add a legend
        leg2 = ROOT.TLegend(0.20, .230, 0.60, .280, "", "brNDC")
        leg2.SetBorderSize(0)
        leg2.SetFillColor(0)
        leg2.SetTextSize(.032)
        leg2.AddEntry(graphsing, "Absolute Systematic Uncertainty #pm0.7%", "F")
#        if maintenance:
#            leg2.AddEntry(maintlinestart, "Maintenance Period Boundary", "l")
        leg2.Draw()

        leg = ROOT.TLegend(0.20, 0.2793, 0.65, .3793, "", "brNDC")
        leg.SetBorderSize(0)
        leg.SetFillColor(0)
        leg.SetTextSize(.032)
        if "Low" in title:
            leg.AddEntry(graph, str(Nchannels)+" Channel Average (RMS=.03%)", "p")
            leg.AddEntry(graphsing, "Typical Channel (Long Barrel, C-Side) (RMS=.02%)", "ep")
        if "High" in title:
            leg.AddEntry(graph, str(Nchannels)+" channel average (RMS=.04%)", "p")
            leg.AddEntry(graphsing, "Typical Channel (Long Barrel, C-Side) (RMS=.03%)", "ep")
        if "Dem" in title:
            leg.AddEntry(graph, str(Nchannels)+" channel average (RMS=.04%)", "p")
            leg.AddEntry(graphsing, "Typical Channel (Demonstrator Module, LBA 14) (RMS=.03%)", "ep")
        leg.Draw("same")
        '''
        titletext = ROOT.TLatex()
        titletext.SetTextAlign(12)
        titletext.SetTextSize(0.04)
        titletext.SetNDC()
        titletext.SetTextAlign(22)
        titletext.DrawLatex(0.52, 0.91, title)
        ''' 
        #atlastext = ROOT.TLatex()
        #atlastext2.SetNDC()
        #atlastext2.DrawLatex(0.27,0.797,"Tile Calorimeter")
        
        
        # l = ROOT.TLatex()
        # l.SetNDC()
        # l.SetTextFont(72)
        # l.DrawLatex(0.20,0.880,"ATLAS") 

        # l2 = ROOT.TLatex()
        # l2.SetNDC()
        # l2.DrawLatex(0.33,0.880,"Preliminary")
 
        l3 = ROOT.TLatex()
        l3.SetNDC()
        l3.DrawLatex(0.20, 0.832, "Tile Calorimeter")
                

        l4 = ROOT.TLatex()
        l4.SetNDC()
        l4.DrawLatex(0.20, 0.774, description)


        l5 = ROOT.TLatex()
        l5.SetNDC()
        l5.DrawLatex(0.20, 0.716, self.dateLabel)

 
        mainttext = ROOT.TLatex()
        mainttext.SetNDC()
        mainttext.SetTextSizePixels(8)
        mainttext.SetTextColor(ROOT.kRed+2)
        mainttext.SetTextAngle(90)
        mainttext.SetTextAlign(22)
        #mainttext.DrawLatex(0.21, 0.55, "Maintenance Period")
        
        for ext in self.exts:
                self.c1.Print('{path}/{name}.{ext}'.format(path=self.dir,
                                                       name=filename,
                                                       ext=ext))
                                                       
    def ProcessRegion(self, region):
        print("test proces region")
        # Sample Channel: Module = 20 (14), Channel = 33

        runinfohigh=[]
        runinfolow=[]
        runinfodem=[]
        if 'gain' not in region.GetHash():
            return
        
        for event in region.GetEvents():
            if event.run.runType == 'CIS':

                if 'calibration' in event.data\
                and\
                'goodEvent' in event.data and event.data['goodEvent']:
#                event.data.has_key('calibratableRegion') and event.data['calibratableRegion'] and\

                    if 'highgain' in region.GetHash() and "LBA14" not in region.GetHash():
                        runinfohigh.append((event.run.time_in_seconds,event.data['calibration']))
                         
                        if 'LBC_m20_c33' in region.GetHash():
                            self.singchanhi.append((event.run.time_in_seconds, event.data['calibration']))
                        
                        #print("HG")

                    
                    if 'lowgain' in region.GetHash():     
                        runinfolow.append((event.run.time_in_seconds,event.data['calibration']))
                        
                        if 'LBC_m20_c33' in region.GetHash():
                            self.singchanlo.append((event.run.time_in_seconds, event.data['calibration']))
                        
                        #print("LG")

                    if "highgain" in region.GetHash() and "LBA14" in region.GetHash():
                        runinfodem.append((event.run.time_in_seconds,event.data['calibration']))
                        
                        if 'LBA_m14_c33' in region.GetHash():
                            self.singchandem.append((event.run.time_in_seconds, event.data['calibration']))
                        
                        print("DEM")
        print("test process region 2")
        for run in runinfohigh:
        
            if run[0] in self.rundicthighgain:
            
                self.rundicthighgain[run[0]][0]+=run[1]
                self.rundicthighgain[run[0]][1]+=1
    
            else:
        
                self.rundicthighgain[run[0]]=[run[1], 1]
            
        for run in runinfolow:
            
            if run[0] in self.rundictlowgain:
        
                self.rundictlowgain[run[0]][0]+=run[1]
                self.rundictlowgain[run[0]][1]+=1
            
            else:
        
                self.rundictlowgain[run[0]]=[run[1], 1]

        for run in runinfodem:
            
            if run[0] in self.rundictdem:
        
                self.rundictdem[run[0]][0]+=run[1]
                self.rundictdem[run[0]][1]+=1
            
            else:
        
                self.rundictdem[run[0]]=[run[1], 1]
        
        del runinfohigh
        del runinfolow
        del runinfodem
    
    
    
    
    
    
    
    
    
