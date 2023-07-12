################################################################################
#
# do_time_plot.py
#
################################################################################
#
# Author: Henric, using Sebs stuff
#
# August 20, 2011
#
# Goal:
# Compute time plots for the pmts of a drawer
#
# Input parameters are:
#
# -> part: the partition number (1=LBA, 2=LBC, 3=EBA, 4=EBC) you want to plot.
#          DEFAULT VAL = 0 : produces all the plots
#
# -> drawer: the drawer number (from 1 to 64) you want to plot.
#            DEFAULT VAL = 0 : produces all the plots
#
# -> limit: the maximum tolerable variation (in %). If this variation
#           is excedeed the plots will have a RED background
#
# -> nDays: how many days before the last run do you want to check the pmt
#           variation
#           DEFAULT VAL = -1 : all the range
#
# -> doEps: provide eps plots in addition to default png graphics
#
# For more info on the LASER system : http://atlas-tile-laser.web.cern.ch
#
################################################################################
from __future__ import print_function
from src.GenericWorker import *
from src.laser.toolbox import *
from src.stats import *
import src.oscalls
import os.path
import ROOT
import math

from array import array

class do_time_plot(GenericWorker):

    "Compute time plot for the pmts of a drawer"

    def __init__(self, runType='Las', part=0, limit=7, doEps = False,nDays=-1):
        self.runType   = runType
        self.doEps     = doEps
        self.part      = part

        self.limit     = limit
        self.nDaysBef  = nDays

        self.drawer_list = []
        self.time_list    = []
        self.n_run       = 0

        self.outputTag = outputTag # global variable to tag output histogram file name
        self.dir    = getPlotDirectory(subdir=os.path.join(self.outputTag,'Time'))

        for i in range(256):
            self.drawer_list.append([])

        self.PMTool   = LaserTools()
        self.origin   = ROOT.TDatime()
        self.time_max = 0
        self.time_min = 10000000000000000

#        self.hhist  = []
        self.alltgraphs = []
        self.tgraphgood = []
        self.tgraphbad = []
        self.tgraphjump = []
#        self.hist  = []

        self.problemtxt = []
        for i_pmt in range(48):
            self.problemtxt.append(set())

        self.problembox = []

        for i_pmt in range(48):
            self.problembox.append(ROOT.TPaveText(0.32,0.9,.9,1.,"brNDC"))
            self.problembox[i_pmt].SetFillColor(623)
            self.problembox[i_pmt].SetTextSize(0.07)
            self.problembox[i_pmt].SetTextFont(42)
            self.problembox[i_pmt].SetBorderSize(0)

        self.part_names  = ["LBA", "LBC", "EBA", "EBC"]
        self.fit = []
        self.fit.append( ROOT.TF1('cst1', '[0]', 0. , 100000000.))
        self.fit[0].SetLineWidth(1)
        self.fit[0].SetLineColor(6)
        self.fit[0].SetLineWidth(1)

        self.fit.append( ROOT.TF1('cst2', '[0]', 0. , 100000000.))
        self.fit[1].SetLineWidth(1)
        self.fit[1].SetLineColor(7)
        self.fit[1].SetLineWidth(1)


    def ProcessStart(self):
        global run_list
        for run in run_list.getRunsOfType('Las'):
            time = run.time_in_seconds
            if self.time_min > time:
                self.time_min = time
                self.origin = ROOT.TDatime(run.time)

            if self.time_max < time:
                self.time_max = time

            if time not in self.time_list:
                self.time_list.append(time)

#        try:
#            self.HistFile.cd()
#        except:
#            self.initHistFile("output/Tucs.Time.root")
#        self.HistFile.cd()
#        ROOT.gDirectory.mkdir("Laser")
#        ROOT.gDirectory.cd("Laser")


    def ProcessRegion(self, region):

        for event in region.GetEvents():
            if event.run.runType!='Las':
                continue

            if 'cellTime' in event.data and event.data['is_OK']: # and event.data.has_key('cellTimeErr'):

                [part, module, channel, gain] = region.GetNumber()

                if self.part != 0 and part != self.part: # if you just want one part
                    continue

                index = 64*(part-1) + (module-1)
                self.drawer_list[index].append(event)


    def ProcessStop(self):

        graph_lim=12.5
        # Cosmetics (Part 1): the lines which shows the maximum acceptable variation
        if self.nDaysBef==-1:
            self.nDaysBef =  self.time_min
        else:
            self.nDaysBef = self.time_max - self.nDaysBef*86400

        ROOT.gStyle.SetPaperSize(20,26)

        c_w = int(2600)
        c_h = int(2000)

        for r_time in self.time_list: # Number of runs in the window of interest
            if r_time >= self.nDaysBef:
                self.n_run += 1

        # Then we do the graphs for all the requested modules
        c1 = ROOT.TCanvas("c1","acanvas",c_w,c_h)
        c1.SetWindowSize(2*c_w - c1.GetWw(), 2*c_h - c1.GetWh())



        self.h1 = ROOT.TH1F('timeFiber','Fibre offsets', 200, -5., 5.)
        self.h2 = ROOT.TH1F('RMStimes','RMS(time) per channel',
                            100, 0, 1.)
        self.h3 = ROOT.TH1F('pmtsInDigitiser ','PMTs v.s Digitser',
                            100, -5., 5.)
        self.h4 = ROOT.TH1F('LHGain','low gain time - high gain time',
                            100, -15, 15.)

        for i_pmt in range(48):

            self.tgraphgood.append([ROOT.TGraphErrors(),ROOT.TGraphErrors()])
            self.tgraphbad.append([ROOT.TGraphErrors(),ROOT.TGraphErrors()])
            self.tgraphjump.append([ROOT.TGraphErrors(),ROOT.TGraphErrors()])

            for adc in [0, 1]:
                self.alltgraphs.append(self.tgraphgood[i_pmt][adc])

                self.alltgraphs.append(self.tgraphbad[i_pmt][adc])
                self.tgraphbad[i_pmt][adc].SetMarkerColor(2)
                self.tgraphbad[i_pmt][adc].SetLineColor(2)

                self.alltgraphs.append(self.tgraphjump[i_pmt][adc])
                self.tgraphjump[i_pmt][adc].SetMarkerColor(95)
                self.tgraphjump[i_pmt][adc].SetLineColor(95)
            


        for tgraph in self.alltgraphs:
            tgraph.SetMarkerStyle(7)
            tgraph.SetMarkerSize(20)            
            tgraph.GetXaxis().SetLabelOffset(0.1)
            
            tgraph.GetXaxis().SetLabelFont(42)
            tgraph.GetXaxis().SetLabelSize(0.1)
            
            tgraph.GetYaxis().SetLabelFont(42)
            tgraph.GetYaxis().SetLabelSize(0.1)
            
            tgraph.GetYaxis().SetTitleFont(42)
            tgraph.GetYaxis().SetTitleSize(0.2)
            tgraph.GetYaxis().SetTitleOffset(0.7)

            tgraph.GetXaxis().SetTimeDisplay(1)


        fibre_list  = [stats() for x in range(384)]

        for i_part in range(4):

            for i_drawer in range(64):

                drawer_events = self.drawer_list[64*i_part+i_drawer]

                if len(drawer_events)==0:
                    continue

                for event in drawer_events:
                    [part, module, pmt, gain] = event.region.GetNumber(1)

                    indice = self.PMTool.get_fiber_index(part-1,module-1,pmt)

                    if 'cellTime' in event.data and 'cellTimeErr' in event.data:
                        if (event.data['status']==0 or event.data['status']==1 or event.data['status']==2) and math.fabs(event.data['cellTime'])<20:
                            fibre_list[indice].fill(event.data['cellTime'])


        for indice in range(384):
            if fibre_list[indice].entries!=0:
                self.h1.Fill(fibre_list[indice].mean())

        self.h1.Fit("gaus","LV"," ",-5., 5.)

        self.PrepareCanvasModule(c1)

        for i_part in range(4):

            if self.part != 0 and i_part != self.part-1: # if you just want one part
                continue

            for i_drawer in range(64):

                drawer_events = self.drawer_list[64*i_part+i_drawer]

                if len(drawer_events)==0:
                    continue

                ymin = array('f',(-2.,)*8)
                ymax = array('f',(+2.,)*8)

                n_orange    = 0
                n_red       = 0
                n_black     = 0
                pmt_list    = []

                timeoffsets = array('f',(0.0,)*48)

                # Clear pmt list for this module
                for i_pmt in range(48):
                    pmt_list.append([])

                for event in drawer_events:
                    [part, module, pmt, gain] = event.region.GetNumber(1)
                    pmt_list[pmt-1].append(event)

                for tgraph in self.alltgraphs:
                    tgraph.Set(0)

                fibre1 = self.PMTool.get_fiber_index(i_part, i_drawer, 1) # Fibre for PMT 1 
                fibre2 = self.PMTool.get_fiber_index(i_part, i_drawer, 2) # Fibre for PMT 2
                
                t_fib1 = fibre_list[fibre1].mean()
                t_fib2 = fibre_list[fibre2].mean()

                if not t_fib1: t_fib1=0.
                if not t_fib2: t_fib2=0.
                t_corr = (t_fib1-t_fib2)/2.

                for i_pmt in range(48):
                                        
                    histtitle = "PMT %02d %s" % (i_pmt+1, self.PMTool.get_pmt_layer(i_part,i_drawer+1,i_pmt+1))
                    if i_part==0 and i_drawer==13:
                        histtitle = "DEMO %02d %s" % (i_pmt+1, self.PMTool.get_pmt_layer(i_part,i_drawer+1,i_pmt+1))
                    histname = histtitle.replace(" ","_")

                    gainName = ["_low","_high"]
                    for adc in [0,1]:
                        self.tgraphgood[i_pmt][adc].SetTitle(histtitle)
                        self.tgraphgood[i_pmt][adc].SetName(histname+gainName[adc])
                        self.tgraphbad[i_pmt][adc].SetTitle(histtitle)
                        self.tgraphbad[i_pmt][adc].SetName(histname+gainName[adc]+"_bad")
                        self.tgraphjump[i_pmt][adc].SetTitle(histtitle)
                        self.tgraphjump[i_pmt][adc].SetName(histname+gainName[adc]+"_jump")


                    self.problembox[i_pmt].Clear()

                    # Don't go further if the channel is not instrumented
                    if self.PMTool.is_instrumented(i_part,i_drawer,i_pmt+1) == False:
                        continue

                    iDigit = self.PMTool.getDigitizer(i_part,i_pmt+1)
                    for event in sorted(pmt_list[i_pmt], key=lambda evt: evt.run.runNumber):
                        # fill the histogram
                        if 'cellTime' in event.data and 'cellTimeErr' in event.data:
                            gain = event.region.GetNumber()[3]
#
                            if (event.data['status']==0 or event.data['status']==1 or event.data['status']==2):
                                tgraph = self.tgraphgood[i_pmt][gain]
                            else:
                                tgraph = self.tgraphbad[i_pmt][gain]

                            n = tgraph.GetN()
                            
                            if i_pmt%2: # Even PMTs
                                time = event.data['cellTime']+t_corr
                            else:       # Odd PMTs
                                time = event.data['cellTime']-t_corr
                            
                            tgraph.SetPoint(n,event.run.time_in_seconds-self.time_min,time)
                            tgraph.SetPointError(n,20,math.sqrt(event.data['cellTimeErr']*event.data['cellTimeErr']+2.5e-3)) # 50ps systematic

                            y = time+event.data['cellTimeErr']+0.5
                            if y > ymax[iDigit-1]:
                                ymax[iDigit-1] = y

                            y = time-event.data['cellTimeErr']-0.5
                            if y < ymin[iDigit-1]:
                                ymin[iDigit-1] = y


                        # fill the problems
                        if 'problems' in event.data:
                            for problem in event.data['problems']:
                                if problem not in self.problemtxt[i_pmt]:
                                    self.problemtxt[i_pmt].add(problem)

                        if 'TimeOffset' in event.data:
                            timeoffsets[i_pmt] = event.data['TimeOffset']

                # Then Analyse it ...
                    for gain in [0, 1]:

                        self.tgraphgood[i_pmt][gain].SetMaximum(ymax[iDigit-1])
                        self.tgraphgood[i_pmt][gain].SetMinimum(ymin[iDigit-1])

                        if self.tgraphgood[i_pmt][gain].GetN():

                            xlist = self.tgraphgood[i_pmt][gain].GetX()
                            ylist = self.tgraphgood[i_pmt][gain].GetY()
                            ylist, xlist  = zip(*sorted(zip(ylist,xlist)))
                            yvals = [[ylist[0]]]
                            xvals = [[xlist[0]]]
                            nvals = [1] 
                            jumps = 0
                            for i in range(1,len(ylist)):
                                if (ylist[i]-ylist[i-1]>0.3):
                                    jumps = jumps+1
                                    yvals.append([])
                                    xvals.append([])
                                    nvals.append(0)
                                
                                nvals[jumps] = nvals[jumps]+1
                                yvals[jumps].append(ylist[i])
                                xvals[jumps].append(xlist[i])
                        
                            best = 0
                            if jumps: # if find largest cluster of points
                                for j in range(jumps+1): 
                                    if nvals[j]>nvals[best]:
                                        best=j
                        
                                self.tgraphgood[i_pmt][gain].Set(0)
                                self.tgraphjump[i_pmt][gain].Set(0)

                                for j in range(jumps+1):
                                    if j==best: # Best cluster goes in tgraphgood
                                        tgraph = self.tgraphgood[i_pmt][gain]
                                    else:       # Other points to tgraphjump
                                        tgraph = self.tgraphjump[i_pmt][gain]
                                
                                    for i in range(nvals[j]):
                                        point = tgraph.GetN()
                                        tgraph.SetPoint(point, xvals[j][i],yvals[j][i])
                                                                
#                        self.fit[gain].SetParameter(0, yvals[best][0])
                               
                        if self.tgraphgood[i_pmt][gain].GetN()>0:
                            rms = self.tgraphgood[i_pmt][gain].GetRMS(2)
                            self.h2.Fill(rms)
                            self.fit[gain].SetParameter(0, self.tgraphgood[i_pmt][gain].GetMean(2))
                            self.tgraphgood[i_pmt][gain].Fit(self.fit[gain],"Q","", 0., (self.time_max-self.time_min))

                    # a = self.fit[0].GetParameter(0)
                    # b = self.fit[1].GetParameter(0)
                    # sa = self.fit[0].GetParError(0)
                    # sb = self.fit[1].GetParError(0)
                    # s = math.sqrt(sa*sa+sb*sb)

                    for gain in [0,1]:
                        n = self.tgraphjump[i_pmt][gain].GetN()
                        if n:
                            print()
                        for i in range(n):
                            y = self.tgraphjump[i_pmt][gain].GetY()[i]
                            ey = self.tgraphjump[i_pmt][gain].GetEY()[i]
                            fit = self.fit[gain].GetParameter(0)
                            efit= self.fit[gain].GetParError(0)
                            print("%s %2d %2d %5.2f %5.2f %5.2f %6.3f %6.3f %6.3f" % 
                                  ( self.part_names[i_part], i_drawer+1, i_pmt+1, y,
                                    fit, y-fit, math.sqrt(ey*ey+efit*efit),
                                    ey, efit ))


                mean_digitizer = [stats() for x in range(8)]
                for i_pmt in range(48):                     
                    iDigit = self.PMTool.getDigitizer(part,i_pmt+1)

                    for adc in [0,1]:
                        if self.tgraphgood[i_pmt][adc].GetN()>0:
                            mean_digitizer[iDigit-1].fill( self.tgraphgood[i_pmt][adc].GetMean(2) )
                
                # Now we have the means per digitizer, lets use them
                for i_pmt in range(48):                     
                    iDigit = self.PMTool.getDigitizer(part,i_pmt+1)
                    if self.tgraphgood[i_pmt][0].GetN()>0:
                        time = self.tgraphgood[i_pmt][0].GetFunction("cst1").GetParameter(0)
                        self.h3.Fill( time - mean_digitizer[iDigit-1].mean())
                
                    if self.tgraphgood[i_pmt][1].GetN()>0:
                        time = self.tgraphgood[i_pmt][1].GetFunction("cst2").GetParameter(0)
                        self.h3.Fill( time - mean_digitizer[iDigit-1].mean())


                        #                if mean_digitizer[iDigit-1].mean()!=None:
                        #                    timeoffsets[i_pmt] = mean_digitizer[iDigit-1].mean()

                        
                    if self.tgraphgood[i_pmt][0].GetN() and  self.tgraphgood[i_pmt][1].GetN():
                        self.h4.Fill( self.fit[0].GetParameter(0) - self.fit[1].GetParameter(0) )
                        
                # Finaly  draw it...
                # Prepare the canvas for new module

                self.DrawCanvasModule(c1, i_part, i_drawer, ymin, ymax, mean_digitizer)
                


#                lines = []


#                self.HistFile.cd("Laser")
#                ROOT.gDirectory.mkdir("%s"%self.plot_name)
#                ROOT.gDirectory.cd("%s"%self.plot_name)

#                for tgraph in self.alltgraphs:
#                    if tgraph.GetN():
#                        tgraph.Write()




    
#        self.HistFile.Close()
        ROOT.gROOT.cd()
        ROOT.gROOT.pwd()
        ROOT.gROOT.ls()
#        for tgraph in self.alltgraphs:
#            print("delete ", tgraph.GetTitle())
#            tgraph.Delete()

        print("here 2 ")
        # self.alltgraphs = []
        # self.tgraphgood = []
        # self.tgraphbad = []
        # self.tgraphjump = []

#        for textbox in self.problembox:
#            textbox.Delete()
        self.problembox = []
        print("here 3 ")

        self.DrawCanvasAnna(c1)

        c1.Close()

        print("this is the end...")



    def DrawCanvasAnna(self,c1):
        c1.Clear()
        c1.Range(0,0,1,1)
        c1.SetFillColor(0)
        c1.SetBorderMode(0)
        c1.Divide(2,2)

        ROOT.gStyle.SetOptStat(1100)
        ROOT.gStyle.SetOptFit(111111)

        ROOT.gStyle.SetStatX(1.)
        ROOT.gStyle.SetStatY(1.)
        ROOT.gStyle.SetStatW(.2)
        ROOT.gStyle.SetStatH(.2)

        #self.h1.GetListOfFunctions().Find("stats").SetOptStat(1100)

        c1.cd(1).SetLogy()
        self.h1.GetXaxis().SetTitleOffset(1.2)
        self.h1.GetXaxis().SetTitle("time difference [ns]")
        self.h1.GetYaxis().SetTitle("Nb of entries")

        self.h1.Draw()

        c1.cd(2).SetLogy()
        self.h2.GetXaxis().SetTitleOffset(1.2)
        #        self.h2.Fit("expo","V"," ",-1., 1.)
        self.h2.GetXaxis().SetTitle("rms [ns]")
        self.h2.GetYaxis().SetTitle("Nb of entries")
        self.h2.Draw()

        c1.cd(3).SetLogy()
        self.h3.GetXaxis().SetTitleOffset(1.2)
        self.h3.GetXaxis().SetTitle("pmt-<pmt>_{digitiser} [ns]")
        self.h3.GetYaxis().SetTitle("Nb of entries")
        self.h3.Draw()

        c1.cd(4).SetLogy()
        self.h4.GetXaxis().SetTitleOffset(1.2)
        self.h4.GetXaxis().SetTitle("time diff [ns]")
        self.h4.GetYaxis().SetTitle("Nb of entries")
        self.h4.Draw()

        c1.Modified()
        c1.Update()

        self.plot_name = "Time_distributions"
        c1.Print("%s/%s.ps" % (self.dir,self.plot_name))


    def PrepareCanvasModule(self, c1):
        # Title stuff
        ROOT.gStyle.SetOptTitle(1)
        ROOT.gStyle.SetTitleX(0.05)
        ROOT.gStyle.SetTitleW(0.4)
        ROOT.gStyle.SetTitleBorderSize(0)
        ROOT.gStyle.SetTitleFontSize(0.1)
        ROOT.gStyle.SetTitleOffset(0.1)
        ROOT.gStyle.SetTitleFillColor(0)
        ROOT.gStyle.SetOptStat(0)
        ROOT.gStyle.SetEndErrorSize(0.)
        ROOT.gStyle.SetTimeOffset(self.origin.Convert())
        ROOT.gStyle.SetOptStat(0)
        ROOT.gStyle.SetOptFit(0)

        ROOT.gROOT.cd()

        c1.Clear()

        c1.Range(0,0,1,1)
        c1.SetFillColor(0)
        c1.SetBorderMode(0)
        c1.cd()
        c1.Divide(6,8,0.002,0.004)

        self.l1 = ROOT.TLatex()
        self.l2 = ROOT.TLatex()
        self.l1.SetNDC()
        self.l2.SetNDC()



    def DrawCanvasModule(self, c1, part, drawer, ymin, ymax, mean_digitizer):
        c1.cd()
        LatexFontSize=0.05
        
        x = 0.18
        y = 0.32
        l1 = self.l1.DrawLatex(x, y,'%s%02d' % (self.part_names[part],(drawer+1)))
        l2 = self.l2.DrawLatex(x, y-LatexFontSize, "Time[ns]")
        
        latext = ROOT.TLatex()
        latext.SetTextSize(0.12)


        if part < 2:
            x = 0.34
        else:
            x = 0.01
                    
        legend = ROOT.TLegend(x, y+LatexFontSize, x+.15, y-LatexFontSize)
        legend.AddEntry(self.fit[0],"Low gain","L")
        legend.AddEntry(self.fit[1],"High gain","L")
        legend.AddEntry(self.tgraphbad[0][0],"Bad status","P")
        legend.AddEntry(self.tgraphjump[0][0],"Timing jump","P")
        legend.Draw()

        # Clear all pads list for this module

        for i_pmt in range(48):
            self.problemtxt[i_pmt].clear()
            pad = c1.cd(i_pmt+1)
            pad.Clear()

            if self.PMTool.is_instrumented(part,drawer,i_pmt+1) == False:
                continue

            iDigit = self.PMTool.getDigitizer(part,i_pmt+1)

            pad.SetFrameFillColor(0)
            pad.SetLeftMargin(0.14);
            pad.SetRightMargin(0.07);
            pad.SetTopMargin(0.04);
            pad.SetBottomMargin(0.25);


            histtitle = "PMT %d %s" % (i_pmt+1, self.PMTool.getCellName(part, drawer+1, i_pmt+1) )

            hist = pad.DrawFrame(-86400, ymin[iDigit-1], 
                                 self.time_max-self.time_min+86400, ymax[iDigit-1], histtitle)

            
            hist.GetXaxis().SetTimeDisplay(1)
            
            hist.GetXaxis().SetLabelOffset(0.05)
            hist.GetXaxis().SetLabelFont(42)
            hist.GetXaxis().SetLabelSize(0.1)


            hist.GetXaxis().SetTimeFormat("%d/%m")
            hist.GetXaxis().SetNdivisions(-503)
            
            hist.GetYaxis().SetLabelFont(42)
            hist.GetYaxis().SetLabelSize(0.1)

            if ( i_pmt%6 == 0 ):
                hist.GetYaxis().SetTitleFont(42)
                hist.GetYaxis().SetTitleSize(0.1)
                hist.GetYaxis().SetTitleOffset(0.7)
                hist.GetYaxis().SetTitle("Time [ns]")

            option = 'P,same'

            for adc in [0,1]:
                if self.tgraphgood[i_pmt][adc].GetN()>0:
                    self.tgraphgood[i_pmt][adc].Draw(option)

                if self.tgraphbad[i_pmt][adc].GetN()>0:
                    self.tgraphbad[i_pmt][adc].Draw(option)
                            
                if self.tgraphjump[i_pmt][adc].GetN()>0:
                    self.tgraphjump[i_pmt][adc].Draw(option)

                    
                    problems=False

                    # for problem in self.problemtxt[i_pmt]:
                    #     problems = True
                    #     self.problembox[i_pmt].AddText(problem)

                    #     if problem == 'Channel masked (unspecified)' or problem == 'No PMT connected' or \
                    #        problem == 'No HV' or problem == 'Wrong HV' or \
                    #        problem == 'ADC masked (unspecified)' or problem == 'ADC dead' or \
                    #        problem == 'Severe stuck bit' or problem == 'Severe data corruption' or \
                    #        problem == 'Very Large HF noise':
                    #         c1.cd(i_pmt+1).SetFrameFillColor(17)
                    # if problems:
                    #     self.problembox[i_pmt].Draw()
                        

                                        #
                    ##  Blue line with time correction from DB

                    #                    line = ROOT.TLine(-43200,timeoffsets[i_pmt],self.time_max-self.time_min+43200,timeoffsets[i_pmt])
                #                    line.SetLineColor(4)
                #                    line.SetLineWidth(1)
                #                    line.Draw('same')
                #                    lines.append(line)
    
#        textout = open(os.path.join(src.oscalls.getResultDirectory(),"LaserOutOfTime.txt"),'w')
        for iDigit in range(8):
            if mean_digitizer[iDigit].mean()!=None:
                c1.cd(6*(8-iDigit))
                latext.DrawLatexNDC(0.45, 0.,'Digitiser %d: %4.1f ns' % (iDigit+1,mean_digitizer[iDigit].mean() ))

        c1.Modified()
        c1.Update()


        self.plot_name = "%s_time" % (self.PMTool.get_module_name(part,drawer))
        c1.Print("%s/%s.ps" % (self.dir,self.plot_name),"Landscape")

        legend.Delete()
        l1.Delete()
        l2.Delete()

