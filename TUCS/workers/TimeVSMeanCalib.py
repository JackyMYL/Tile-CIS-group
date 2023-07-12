# Author: Christopher Tunnell <tunnell@hep.uchicago.edu>
#
# March 04, 2009
#
# Modified: Dave Hollander <daveh@uchicago.edu>
#
# November 3, 2009
'''Investigate the stability of the detector's calibration.

This worker provides a plot of the detector-wide average calibration over time
and compares it to the calibration of a particular channel, chosen by the
``example`` keyword argument.  It prints the following plot:

    $TUCS/plots/latest/cis/calib_stability_$REGION.root
    Title: Average $GAIN-Gain CIS Calibration Stability
    Y Axis: CIS Calibration (ADC counts/pC)
    X Axis: date

    A plot of the detector-wide average CIS response over time, compared to the
    average CIS response of $REGION.

'''

from array import array
import collections
from math import sqrt, ceil
import os.path
import string
import time

import ROOT

import src.GenericWorker
import src.MakeCanvas
import src.oscalls


class TimeVSMeanCalib(src.GenericWorker.GenericWorker):
    "Compute the time stability of a calibration constant"

    def __init__(self, runType='CIS', example='EBC_m10_c14', syst=0.007,
                 exts=['eps', 'root']):
        super(TimeVSMeanCalib, self).__init__()
        self.runType = runType
        self.example = example
        self.syst = syst
        self.exts = exts

        self.dir = os.path.join(src.oscalls.getPlotDirectory(), 'cis')
        src.oscalls.createDir(self.dir)

        self.c1 = src.MakeCanvas.MakeCanvas()

        self.data = {'highgain': collections.defaultdict(list),
                     'lowgain': collections.defaultdict(list)}
        self.example_data = {'highgain': {},
                             'lowgain': {}}

    def ProcessStop(self):
        "Fill and print the time stability plot."
        self.c1.cd()

        for gain in ['lowgain', 'highgain']:
            graph = ROOT.TGraphErrors()
            graph.SetTitle('Average %s-Gain CIS Calibration Stability'
                           % string.capwords(gain)[:-4])

            points = enumerate(self.data[gain].items())
            for point, (event_time, calibs) in points:

                mean = ROOT.TMath.Mean(len(calibs), array('f', calibs))
                rms = ROOT.TMath.RMS(len(calibs), array('f', calibs))

                graph.SetPoint(point, event_time, mean)
                graph.SetPointError(point, 0, rms / sqrt(len(calibs)))

            example_graph = ROOT.TGraphErrors()
            example_graph.SetMarkerStyle(23)
            example_graph.SetMarkerColor(2)

            points = enumerate(self.example_data[gain].items())
            for point, (event_time, calib) in points:
                example_graph.SetPoint(point, event_time, calib)

            # Axis formatting set to recreate approved public plot
            x_axis = graph.GetXaxis()
            x_axis.SetTimeDisplay(1)
            x_axis.SetTimeFormat('%b %y%F1970-01-01 00:00:00')
            x_axis.SetLabelSize(0.04)
            xmax = x_axis.GetXmax()
            xmin = x_axis.GetXmin()
            months = int(ceil((xmax - xmin) / 2592000))
            x_axis.SetNdivisions(months)

            y_axis = graph.GetYaxis()
            y_axis.SetTitle("CIS Calibration (ADC counts/pC)")
            y_axis.SetNdivisions(203)
            ymax = y_axis.GetXmax()
            ymin = y_axis.GetXmin()

            if gain == 'lowgain':
                graph.SetMinimum(min(1.26, ymin))
                graph.SetMaximum(max(1.34, ymax))
            else:
                graph.SetMinimum(min(79, ymin))
                graph.SetMaximum(max(84, ymax))

            graph.Draw('AP')
            example_graph.Draw('P')

            line = ROOT.TLine()
            line.SetLineStyle(2)
            line.SetLineWidth(4)

            # draw the +/- 0.7% systematic uncertainty lines
            line.DrawLine(xmin, (1 + self.syst) * example_graph.GetMean(2),
                          xmax, (1 + self.syst) * example_graph.GetMean(2))
            line.DrawLine(xmin, (1 - self.syst) * example_graph.GetMean(2),
                          xmax, (1 - self.syst) * example_graph.GetMean(2))

            # # Uncomment this section to print the "maintenance period" box.
            # # XXX: currently non-functioning
            # m_begin = time.mktime(time.strptime("20 Dec 2010", "%d %b %Y"))
            # m_end = time.mktime(time.strptime("17 Jan 2011", "%d %b %Y"))
            #
            # line2 = ROOT.TLine()
            # line2.SetLineColor(2)
            #
            # if m_end > xmin:
            #     print "drawing line"
            #     line2.DrawLine(m_end, ymin, m_end, ymax)
            #
            #     latex = ROOT.TLatex()
            #     latex.SetNDC()
            #     latex.SetTextSizePixels(8)
            #     latex.SetTextColor(2)
            #     latex.DrawLatex(0.395, 0.5, "Maintenance Period")
            #
            #     if m_begin > xmin:
            #         line2.DrawLine(m_begin, ymin, m_begin, ymax)

            latex = ROOT.TLatex()
            latex.SetNDC()

            latex.SetTextFont(72)
            latex.DrawLatex(0.1922, 0.867, "ATLAS preliminary")

            latex.SetTextFont(42)
            latex.DrawLatex(0.1922, 0.811, "Tile calorimeter")

            legend = ROOT.TLegend(0.531407, 0.192308, 0.920854, 0.34965,
                                  "", "brNDC")
            legend.AddEntry(graph, "TileCal average", "P")
            legend.AddEntry(example_graph, "Typical channel", "P")
            legend.AddEntry(line, "\pm 0.7% channel systematic uncertainty", "L")
            legend.Draw()

            for ext in self.exts:
                self.c1.Print("%s/calib_stability_%s_%s.%s" % (self.dir,
                                                               self.example,
                                                               gain, ext))

    def ProcessRegion(self, region):
        "Read and store the calibration values."
        if 'gain' not in region.GetHash():
            return

        gain = region.GetHash().split('_')[-1]

        for event in region.GetEvents():
            if event.run.runType != self.runType:
                continue

            if 'goodRegion' not in event.data or not event.data['goodRegion']:
                continue

            if 'goodEvent' not in event.data or not event.data['goodEvent']:
                continue

            event_time = event.run.getTimeSeconds()

            if self.example in region.GetHash():
                self.example_data[gain][event_time] = event.data['calibration']

            self.data[gain][event_time].append(event.data['calibration'])
