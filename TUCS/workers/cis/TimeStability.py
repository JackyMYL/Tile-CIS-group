# Author: Christopher Tunnell <tunnell@hep.uchicago.edu>
# March 04, 2009
# Updated: Joshua Montgomery <Joshua.J.Montgomery@gmail.com>
# November-ish, 2011

'''Investigate the stability of CIS calibrations.

This worker produces the following plots:

    $TUCS/plots/latest/time_stability/time_stab_rms.root
        X Axis: RMS

        A plot of the RMS of CIS response measurements over the given time
        period.

    $TUCS/plots/latest/time_stability/timestab_$REGION.root
        Title: $REGION
        Y Axis: CIS Constant (ADC count/pC)
        X Axis: date

        A plot of the CIS response over time for the provided region.
        Or a plot of the CIS DB Values over time for the provided region.
        Or a composite plot showing both of the above.
        
This worker is controlled with macros/cis/StudyFlag.py -- further instructions
can be found using > python macros/cis/StudyFlag.py -h

'''

# stdlib imports
import os.path
import itertools
# 3rd party imports
import ROOT

# TUCS imports
import src.GenericWorker
import src.MakeCanvas
import src.oscalls
import src.Get_Consolidation_Date

# CIS imports
import workers.cis.common as common



class TimeStability(src.GenericWorker.GenericWorker):
    "Compute the time stability of a calibration constant"

    def __init__(self, plottimestab, runType='CIS', savePlot=True, all=False, 
                 cal_type="measured", exts=['png', 'eps', 'root'], flagtype='DB Deviation', 
                 only_all_flags=False, only_chosen_flag=False, plotdirectory='StudyFlag', 
                 rundate='No_Specified_Date', only_good_events=True, adc_problems=None,
                 preprocessing=False, IOV=999999):
        
        super(TimeStability, self).__init__()
        self.plottimestab     = plottimestab
        self.runType          = runType
        self.save_plot        = savePlot
        self.all              = all
        self.cal_type         = cal_type
        self.exts             = exts
        self.flag             = flagtype
        self.only_all_flags   = only_all_flags
        self.only_chosen_flag = only_chosen_flag
        self.plotdirectory    = plotdirectory
        self.rundate          = rundate
        self.only_good_events = only_good_events
        self.adc_problems     = adc_problems
        self.preprocessing    = preprocessing
        self.iov              = IOV
                
        if self.only_chosen_flag:
            if self.flag == 'all':
                self.only_all_flags = True
                self.only_chosen_flag = False
                
        if self.adc_problems:
            adc_title = str()
            if len(self.adc_problems) > 1:
                adc_seps = []            
                for xiter in range(len(self.adc_problems)):
                    adc_seps.append('_')
                adczip = list(zip(self.adc_problems, adc_seps))
                titlechain = itertools.chain.from_iterable(adczip)
                adc_title = adc_title.join(list(titlechain))
            else:
                adc_title = adc_title.join(self.adc_problems)

        # set up the plots
        if self.plotdirectory == 'TimeStability': 
            self.dir = os.path.join(src.oscalls.getPlotDirectory(), 'cis', self.plotdirectory,'TimeStability', self.cal_type)
        else:
            if self.adc_problems and not 'ADC' in self.flag:
                self.dir = os.path.join(src.oscalls.getPlotDirectory(), 'cis', self.plotdirectory,
                                        'TimeStability', self.rundate, '{0}_{1}'.format(self.flag, adc_title), self.cal_type)
            elif not self.adc_problems:
                self.dir = os.path.join(src.oscalls.getPlotDirectory(), 'cis', self.plotdirectory,
                                    'TimeStability', self.rundate, self.flag, self.cal_type)
            elif 'ADC' in self.flag:
                self.dir = os.path.join(src.oscalls.getPlotDirectory(), 'cis', self.plotdirectory,
                                    'TimeStability', self.rundate, adc_title, self.cal_type)
            
            
        src.oscalls.createDir(self.dir)
        self.c1 = src.MakeCanvas.MakeCanvas()
        self.rms_plots = {'lowgain': ROOT.TH1F('hlotime', 'RMS/mean (%) per ADC', 20, 0, 1),
                          'highgain': ROOT.TH1F('hhitime', 'RMS/mean (%) per ADC', 20, 0, 1)}
    def ProcessStart(self):
        if self.preprocessing:
            self.iovfile=open(os.path.join(src.oscalls.getResultDirectory(),'Preprocessing Output.txt'), 'w')
            self.iovfile.write(self.rundate+' '+str(self.iov[1:-1])+':\n')
            
    def ProcessStop(self):
        
        if self.preprocessing:
            self.iovfile.write('\n')
            self.iovfile.close()
        
        self.c1.Clear()
        self.c1.SetLogy(1)

        # format the plots
        ROOT.gStyle.SetOptStat(0)
        self.rms_plots['lowgain'].SetLineColor(ROOT.kBlue)
        self.rms_plots['highgain'].SetLineColor(ROOT.kRed)
        for gain in self.rms_plots:
            self.rms_plots[gain].GetXaxis().SetTitle('RMS/mean (%)')
            self.rms_plots[gain].GetYaxis().SetTitle('Number of ADC Counts')
            self.rms_plots[gain].SetStats(1)
        self.c1.SetTitle('RMS/mean (%) per ADC')

      
        # draw them
        if self.rms_plots['lowgain'].GetEntries():
            self.rms_plots['lowgain'].Draw('')
            if self.rms_plots['highgain'].GetEntries():
                self.rms_plots['highgain'].Draw('SAME')

        elif self.rms_plots['highgain'].GetEntries():
            self.rms_plots['highgain'].Draw()

        # add a legend
        leg = ROOT.TLegend(0.548995,0.8181818,0.7675879,0.9178322,
                           "", "brNDC")
        leg.SetBorderSize(0)
        leg.SetFillColor(0)
        for gain in self.rms_plots:
            leg.AddEntry(self.rms_plots[gain], gain, "l")
        leg.Draw()


        ## Add the cutoff line
        line = ROOT.TLine()
        line.SetLineWidth(2)
        line.SetLineStyle(2)
        lm = self.c1.GetLeftMargin()
        rm = 1. - self.c1.GetRightMargin()
        tm = 1. - self.c1.GetTopMargin()
        bm = self.c1.GetBottomMargin()
        xndc = (rm-lm)*(.389) + lm
        line.DrawLineNDC(xndc,bm,xndc,tm)

        ## Add "Stats" Boxes
        ## Highgain stats
        ptstats = ROOT.TPaveStats(0.7688442,0.8041958,0.9296,0.9230769,"brNDC")
        ptstats.SetOptStat(1111)
        ptstats.SetName("stats")
        ptstats.SetBorderSize(2)
        ptstats.SetFillColor(19)
        ptstats.SetTextAlign(12)
        text = ptstats.AddText("Highgain Statistics")
        text.SetTextSize(0.02734266)
        text = ptstats.AddText('{0}  =  {1:g}'.format('Entries:',(self.rms_plots['highgain'].GetEntries())))
        text = ptstats.AddText("Mean   = %.4g " % (self.rms_plots['highgain'].GetMean(1)))
        text = ptstats.AddText("RMS   = %.4g " % (self.rms_plots['highgain'].GetRMS(1)))
        ptstats.SetOptFit(0)
        ptstats.Draw()
        self.rms_plots['highgain'].GetListOfFunctions().Add(ptstats)
        ptstats.SetParent(self.rms_plots['highgain'].GetListOfFunctions())
        
        ## Lowgain stats
        ptstats2 = ROOT.TPaveStats(0.7688442,0.6611189,0.9296,0.78,"brNDC")
        ptstats2.SetOptStat(1111)
        ptstats2.SetName("stats2")
        ptstats2.SetBorderSize(2)
        ptstats2.SetFillColor(19)
        ptstats2.SetTextAlign(12)
        text2 = ptstats2.AddText("Lowgain Statistics")
        text2.SetTextSize(0.02734266)
        text2 = ptstats2.AddText('{0}  =  {1:g}'.format('Entries:',(self.rms_plots['lowgain'].GetEntries())))
        text2 = ptstats2.AddText("Mean   = %.4g " % (self.rms_plots['lowgain'].GetMean(1)))
        text2 = ptstats2.AddText("RMS   = %.4g " % (self.rms_plots['lowgain'].GetRMS(1)))
        ptstats2.SetOptFit(0)
        ptstats2.Draw()
        self.rms_plots['lowgain'].GetListOfFunctions().Add(ptstats2)
        ptstats2.SetParent(self.rms_plots['lowgain'].GetListOfFunctions())

        latex = ROOT.TLatex()
        latex.SetTextAlign(12)
        latex.SetTextSize(0.04)
        latex.SetNDC()
        latex.DrawLatex(0.1670854, 0.9685315, 'Time Stability RMS Histogram')

        # print
        for ext in self.exts:
            self.c1.Print('{path}/time_stab_rms.{ext}'.format(path=self.dir,
                                                              ext=ext))

    def process_graph(self, rms, mean, graph, title, filename, partition, module, graphDB=False,roi=False,maxval=False,minval=False,maxrun=False,minrun=False):
        "format and print a time stability graph"

        gain = title.split()[-1]
        self.c1.Clear()

        #rms = graph.GetRMS(2)
        #mean = graph.GetMean(2)

        if graphDB:
            rmsDB = graphDB.GetRMS(2)
            meanDB = graphDB.GetMean(2)

        if not self.save_plot:
            return mean, rms
        
        print("mean=%s" % mean)
        print("rms=%s" % rms)

        # format the axes
        x_axis = graph.GetXaxis()
        x_axis.SetTimeDisplay(1)
        x_axis.SetTimeFormat('%d/%m/%y%F1970-01-01 00:00:00')
        x_axis.SetLabelSize(0.04)
        x_axis.SetNdivisions(505)
        xmax = x_axis.GetXmax()
        xmin = x_axis.GetXmin()

        y_axis = graph.GetYaxis()
        ymax = y_axis.GetXmax()
        ymin = y_axis.GetXmin()

        # format the graph
        graph.SetMinimum(ymin * 0.9)
        graph.SetMaximum(ymax * 1.1)
        graph.SetMarkerStyle(20)
        graph.SetMarkerSize(1.3)
        graph.GetYaxis().SetTitle('CIS Constant (ADC count/pC)')
        graph.SetMarkerColor(ROOT.kBlack)
        graph.Draw('AP')

        # +/- 2% and 1% lines around detector wide average
        box2 = ROOT.TBox(xmin, common.DEF_CALIB[gain] * 0.98,
                         xmax, common.DEF_CALIB[gain] * 1.02)
        box2.SetFillColor(ROOT.kRed - 2)
        box2.Draw()

        box = ROOT.TBox(xmin, mean * 0.99,
                        xmax, mean * 1.01)
        box.SetFillColor(ROOT.kGreen - 5)
        box.Draw()

        line = ROOT.TLine()
        line.SetLineWidth(3)
        line.DrawLine(xmin, common.DEF_CALIB[gain],
                      xmax, common.DEF_CALIB[gain])
        line.DrawLine(xmin, mean, xmax, mean)

        graph.Draw("P")  # Draw points over box
        
        if graphDB:
            graphDB.SetMarkerStyle(23)
            graphDB.SetMarkerSize(1)
            graphDB.SetMarkerColor(ROOT.kBlue)
            graphDB.Draw('psame')
        if roi:
            roi.SetMarkerStyle(20)
            roi.SetMarkerSize(1.3)
            roi.SetMarkerColor(ROOT.kRed)
            roi.Draw('psame')

        # add a legend
        leg = ROOT.TLegend(0.646, 0.8163636, 0.9485, 1, "", "brNDC")
        leg.SetBorderSize(0)
        leg.SetFillColor(0)
        leg.AddEntry(box2, "+/-2% of detector avg", "f")
        leg.AddEntry(box, "+/-1% of mean", "f")
        leg.AddEntry(graph, "calibration", "P")
        leg.AddEntry(graphDB, "database", "P")
        leg.Draw()

        # Add the event line and event label
        if len(event_line) > 1:
            if event_line == 'Consolidation':
                cons_status = src.Get_Consolidation_Date.IsModCons(partition + '_' + module)
                if cons_status == True:
                    cons_date = src.Get_Consolidation_Date.GetConsDate(partition + '_' + module)
                    year = int(float(cons_date[:4]))
                    month = int(float(cons_date[5:7]))
                    day = int(float(cons_date[8:]))
                    event = TDatime(year,month,day,00,00,00).Convert()
                else:
                    event = False
            else:   
                for event1, label1 in itertools.zip_longest(event_line,event_label):
                    year = int(float(event1[:4]))
                    month = int(float(event1[5:7]))
                    day = int(float(event1[8:]))
                    event = TDatime(year,month,day,00,00,00).Convert()
                    if event != False:
                        line = ROOT.TLine()
                        line.SetLineWidth(2)
                        line.SetLineStyle(2)
                        lm = self.c1.GetLeftMargin()
                        rm = 1. - self.c1.GetRightMargin()
                        tm = 1. - self.c1.GetTopMargin()
                        bm = self.c1.GetBottomMargin()
                        xndc = ((double(event)-double(xmin))/(double(xmax)-double(xmin)))*(double(rm)-double(lm))+double(lm)
                        line.DrawLineNDC(xndc,bm,xndc,0.76)
                        if label1 != None:
                            label = ROOT.TLatex()
                            label.SetTextSize(0.04)
                            label.SetNDC()
                            label.SetTextAngle(270)
                            if xndc >= (rm-lm)/2 + lm:
                                label.SetTextAlign(31)
                                xlabel = xndc - .01*(rm-lm)
                            else:
                                label.SetTextAlign(11)
                                xlabel = xndc + .01*(rm-lm)
                            label.DrawLatex(xlabel, (bm-.005), label1)
            
        
        latex = ROOT.TLatex()
        latex.SetTextAlign(12)
        latex.SetTextSize(0.03)
        latex.SetNDC()

        latex.DrawLatex(0.19, 0.75, "Mean = %0.2f" % mean)
        if mean > 0:
                latex.DrawLatex(0.68, 0.75, "RMS/Mean = %0.2f %%" % (100*rms/mean))
        if graphDB:
             latex.DrawLatex(0.34, 0.75, "DB Mean = %0.2f" % meanDB)
             latex.DrawLatex(0.50, 0.75, "Deviation = {0:.2f} %".format(abs(100*(1-float(mean)/float(meanDB)))))
        if maxmin:
                latex.DrawLatex(0.19, 0.85, "Max = %0.2f @run %s" % (maxval,maxrun))
                latex.DrawLatex(0.19, 0.80, "Min = %0.2f @run %s" % (minval,minrun))
                


        latex.DrawLatex(0.1670854, 0.9685315, title)
        

        # print them out
        #if (rms / common.DEF_CALIB[gain] * 100 > 0.1) or self.all:
        if self.plottimestab:
            for ext in self.exts:
                self.c1.Print('{path}/{name}.{ext}'.format(path=self.dir,
                                                       name=filename,
                                                       ext=ext))

        #return mean, rms

    def is_good(self, event):
        "Returns ``True`` if the event should be processed by ProcessRegion."
        runtype_match = (event.run.runType == self.runType)
        bad_event = event.data['isBad']
        return runtype_match and not bad_event
    
    def ProcessRegion(self, region):

        "Plot the stability of a region."
        
        if 'gain' not in region.GetHash():
            return
        calibs = []
        maxrunlist = []
        #maxmin = True

        #parse channel name
        det, partition, module, channel, gain = region.GetHash().split('_') 
        pmt = region.GetHash(1)[16:19]

        for event in region.GetEvents(): #To print out a list of unstable channels
            #calibs.append(event.data['calibration'])
                if event.run.runType == 'CIS' and event.data['CIS_problems']['No Response'] == False:
                        calibs.append(event.data['calibration'])
                        if maxmin:
                                maxrunlist.append(event.run.runNumber)
        if len(calibs) > 0:
                mean = ROOT.TMath.Mean(len(calibs), array('f', calibs))
                rms  = ROOT.TMath.RMS(len(calibs), array('f', calibs))
                print("mean!=%s"%mean, "rms=%s"%rms)
                if maxmin:
                        maxrun = maxrunlist[ROOT.TMath.LocMax(len(calibs), array('f', calibs))]
                        minrun = maxrunlist[ROOT.TMath.LocMin(len(calibs), array('f', calibs))]
                        maxval = ROOT.TMath.MaxElement(len(calibs), array('f', calibs))
                        minval = ROOT.TMath.MinElement(len(calibs), array('f', calibs))
                        roilist1 = [str(maxrun),str(minrun)]
                        print("max %s:%s"%(maxval,maxrun), "min %s:%s"%(minval,minrun))
                else:
                        roilist1 = roilist
                        maxrun = False
                        minrun = False
                        maxval = False
                        minval = False
        else:
            mean = 0
            rms = 0
            roilist1 = roilist

        # check if there's anything to look at in the region
        found    = 0
        tentries = 0
        tratio   = 0
        for event in region.GetEvents():
            if (event.run.runType == self.runType and 'calibratableEvent' in event.data):
                
                    if self.only_all_flags:
                        if 'moreInfo' not in event.data and not self.all:
                            continue
                        if not self.all and not event.data['moreInfo']:
                            continue
                        if self.adc_problems:
                            if 'problems' not in event.data and not self.all:
                                continue
                            if not event.data['problems'] and not self.all:
                                continue

                    if self.only_chosen_flag:
                        global stablist
                        self.stablist = stablist
                        if region.GetHash() not in self.stablist:
                            return
                        

        graph = ROOT.TGraph()
        graphDB = ROOT.TGraph()
        roi = ROOT.TGraph()
        
        # fill the graph
        bad_run = False
        for point, event in enumerate(region.GetEvents()):
            if event.run.runType != self.runType:
                continue
            if event.run.runNumber == 262248 and 'LBC' in region.GetHash():
                bad_run = True
                continue
            if not self.is_good(event) and self.only_good_events:
                continue
            if self.cal_type == "database":
                calib = event.data['f_cis_db']
            elif self.cal_type == "measured":
                calib = event.data['calibration']
            elif self.cal_type == "composite":
                calib_DB = event.data['f_cis_db']
                calib = event.data['calibration']

            if bad_run:
                point -= 1                     
            if self.cal_type == 'composite':
                if str(event.run.runNumber) in roilist1:
                    roi.SetPoint(point,event.run.time_in_seconds,calib)
                    graph.SetPoint(point, event.run.time_in_seconds, calib)
                    graphDB.SetPoint(point, event.run.time_in_seconds, calib_DB)
            else:
                graph.SetPoint(point, event.run.time_in_seconds, calib)
                
            #print calib, calib_DB, event.run.runNumber


        if graph.GetN():
                title = ''.join([partition, module[1:], ' ', channel, '/', pmt,
                             ' ', gain])
                self.process_graph(rms, mean, graph, title, 'TimeStability_%s'
                                                         % region.GetHash(), partition, module, graphDB=graphDB, roi=roi, maxval=maxval,minval=minval,maxrun=maxrun,minrun=minrun)
                self.rms_plots[gain].Fill(rms / common.DEF_CALIB[gain] * 100)
                
                if self.preprocessing:
                    print(region.GetHash())
                    self.iovfile.write(str(region.GetHash())[8:]+'\n')
                    
                    
        #else:
         #       mean = rms = 0

        newevents = set()
        for event in region.GetEvents():
            if event.run.runType == self.runType:
                event.data['mean'] = mean
                event.data['rms'] = rms
            newevents.add(event)

        region.SetEvents(newevents)

