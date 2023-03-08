# Author: Christopher Tunnell <tunnell@hep.uchicago.edu>
#
# March 04, 2009
#
'''Investigate the stability of CIS calibrations.

This worker provides plots of absolute calibration over time.  To investigate
the % variation, similar to Laser plots, use the :mod:`Variation` worker.  This
worker produces the following plots:

    $TUCS/plots/latest/time_stability/time_stab_rms.root
        X Axis: RMS

        A plot of the RMS of CIS response measurements over the given time
        period.

    $TUCS/plots/latest/time_stability/timestab_$REGION.root
        Title: $REGION
        Y Axis: CIS Constant (ADC count/pC)
        X Axis: date

        A plot of the CIS response over time for the provided region.  When
        running over many regions, you might want to pass ``savePlot=False`` to
        TimeStability, to turn off these plots.

'''

# stdlib imports
import os.path

# 3rd party imports
import ROOT

# TUCS imports
import src.GenericWorker
import src.MakeCanvas
import src.oscalls

# CIS imports
import workers.cis.common as common


class TimeStability_Depreciated(src.GenericWorker.GenericWorker):
    "Compute the time stability of a calibration constant"

    def __init__(self, plotvariations, plottimestab,
                 runType='CIS', savePlot=True, all=False, cal_type="measured",
                 exts=['eps', 'root']):
        
        super(TimeStability_Depreciated, self).__init__()
        self.plotvariations = plotvariations
        self.plottimestab = plottimestab
        self.runType = runType
        self.save_plot = savePlot
        self.all = all
        self.cal_type = cal_type
        self.exts = exts

        # set up the plots
        self.dir = os.path.join(src.oscalls.getPlotDirectory(),
                                'time_stability')
        src.oscalls.createDir(self.dir)

        self.c1 = src.MakeCanvas.MakeCanvas()
        self.rms_plots = {'lowgain': ROOT.TH1F('hlotime', 'RMS/mean (%) per ADC', 20, 0, 1),
                          'highgain': ROOT.TH1F('hhitime', 'RMS/mean (%) per ADC', 20, 0, 1)}

    def ProcessStop(self):
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
        ptstats = TPaveStats(0.7688442,0.8041958,0.9296,0.9230769,"brNDC")
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
        hlotime.GetListOfFunctions().Add(ptstats)
        ptstats.SetParent(hlotime.GetListOfFunctions())
        
        ## Lowgain stats
        ptstats2 = TPaveStats(0.7688442,0.6611189,0.9296,0.78,"brNDC")
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
        hlotime.GetListOfFunctions().Add(ptstats2)
        ptstats2.SetParent(hlotime.GetListOfFunctions())

        latex = ROOT.TLatex()
        latex.SetTextAlign(12)
        latex.SetTextSize(0.04)
        latex.SetNDC()
        latex.DrawLatex(0.1670854, 0.9685315, 'Time Stability RMS Histogram')

        # print
        for ext in self.exts:
            self.c1.Print('{path}/time_stab_rms.{ext}'.format(path=self.dir,
                                                              ext=ext))
       

    def process_graph(self, graph, title, filename):
        "format and print a time stability graph"

        gain = title.split()[-1]
        self.c1.Clear()

        rms = graph.GetRMS(2)
        mean = graph.GetMean(2)

        if not self.save_plot:
            return mean, rms

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

        # add a legend
        leg = ROOT.TLegend(0.646, 0.9003, 0.9485, 1, "", "brNDC")
        leg.SetBorderSize(0)
        leg.SetFillColor(0)
        leg.AddEntry(box2, "\pm2% of default val", "f")
        leg.AddEntry(box, "\pm1% of mean", "f")
        leg.Draw()

        latex = ROOT.TLatex()
        latex.SetTextAlign(12)
        latex.SetTextSize(0.04)
        latex.SetNDC()

        latex.DrawLatex(0.19, 0.85, "Mean = %0.2f" % mean)
        #latex.DrawLatex(0.15, 0.80,"RMS = %f" % rms)
        #latex.DrawLatex(0.15, 0.75, "RMS / default calib = %f"
        #                % (rms / common.DEF_CALIB[gain] * 100))
        #if default:
        #    latex.DrawLatex(0.15, 0.70,"Default Calibration in DB")

        latex.DrawLatex(0.1670854, 0.9685315, title)

        # print them out
        if (rms / common.DEF_CALIB[gain] * 100 > 0.1) or self.all:
            if plottimestab:
                for ext in self.exts:
                    self.c1.Print('{path}/{name}.{ext}'.format(path=self.dir,
                                                           name=filename,
                                                           ext=ext))

        return mean, rms

    def is_good(self, event):
        "Returns ``True`` if the event should be processed by ProcessRegion."
        runtype_match = (event.runType == self.runType)
        bad_event = event.data['isBad']
        return runtype_match and not bad_event

    
    def ProcessRegion(self, region):
        "Plot the stability of a region."
        if 'gain' not in region.GetHash():
            return

        det, partition, module, channel, gain = region.GetHash().split('_')
        pmt = region.GetHash(1)[16:19]

        # check if there's anything to look at in the region
        found = False
        for event in region.GetEvents():

            if (event.runType == self.runType
                and 'calibratableEvent' in event.data):

                found = True

        if not found and not self.all:
            return

        graph = ROOT.TGraph()
        graphvar = ROOT.TGraph()

        # fill the graph
        for point, event in enumerate(region.GetEvents()):

            if event.runType != self.runType:
                    continue
            if not self.is_good(event):
                    continue
            if self.cal_type == "database":
                    calib = event.data['f_cis_db']
            elif self.cal_type == "measured":
                    calib = event.data['calibration']
            if point == 0:
                    firstevent = calib

            graph.SetPoint(point, event.getTimeSeconds(), calib)
            variation = ((calib - firstevent) / firstevent) * 100 # In Percent
            graphvar.SetPoint(point, event.getTimeSeconds(), variation)

        # format/print the graph
        
        if graph.GetN():
                title = ''.join([partition, module[1:], ' ', channel, '/', pmt,
                             ' ', gain])
                mean, rms = self.process_graph(graph, title, 'timestab_%s'
                                                         % region.GetHash())
                self.rms_plots[gain].Fill(rms / common.DEF_CALIB[gain] * 100)
        else:
                mean = rms = 0
        
        if graphvar.GetN():
                title = ''.join([partition, module[1:], ' ', channel, '/', pmt,
                                 ' ', gain])
                self.Process_Vgraphs(graphvar, title, 'timestab_%s'
                                                          % region.GetHash())

        newevents = set()
        for event in region.GetEvents():
            if event.runType == self.runType:
                event.data['mean'] = mean
                event.data['rms'] = rms
            newevents.add(event)

        region.SetEvents(newevents)

    def Process_Vgraphs(self, graph, title, filename):
        '''
        Make variation plots.
        Plot title will be the name of the cell.
        '''
        ROOT.gStyle.SetOptStat(11111111)
        gain = title.split()[-1]
        self.c1.Clear()

        graph.SetTitle(title)


        graph.GetYaxis().SetRangeUser(-1.5, 1.5)
        graph.SetMarkerStyle(20)
        graph.SetMarkerSize(1.3)
        graph.GetYaxis().SetTitle('% variation in CIS calibration')
        graph.SetMarkerColor(ROOT.kBlack)
        graph.Draw('AP')

        xaxis = graph.GetXaxis()
        xaxis.SetTimeDisplay(1)
        xaxis.SetTimeFormat("%d/%m/%y%F1970-01-01 00:00:00")
        xaxis.SetLabelSize(0.04)
        xaxis.SetNdivisions(505)
        
        latex = ROOT.TLatex()
        latex.SetTextAlign(12)
        latex.SetTextSize(0.04)
        latex.SetNDC()
        latex.DrawLatex(0.1670854, 0.9685315, title)
        
        if plotvariations:
            for ext in self.exts:
                self.c1.Print('{path}/vars_{name}.{ext}'.format(path=self.dir,
                                                     name=filename, ext=ext))
            
