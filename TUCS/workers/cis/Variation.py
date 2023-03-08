# Author: Christopher Tunnell <tunnell@hep.uchicago.edu>
# Updated: Joshua Montgomery <joshuam@uchicago.edu>
# March 04, 2009
# Updated July 07, 2011
'''Display the relative variation of a channel's calibration over time.'''


from array import array
import collections
import os.path

import ROOT

from src.GenericWorker import GenericWorker
import src.MakeCanvas
import src.oscalls


class Variation(GenericWorker):
    "Compute the variation of a calibration constant over time"
    def __init__(self, region=[], runType='CIS', parameter='calibration',
                 all=False, exts=['ps', 'root']):
        super(Variation, self).__init__()
        self.runType = runType
        self.parameter = parameter
        self.all = all
        self.regions = region
        self.exts = exts

        self.dir = os.path.join(src.oscalls.getPlotDirectory(), 'Variation')
        src.oscalls.createDir(self.dir)

        self.c1 = src.MakeCanvas.MakeCanvas()

        ddict_factory = lambda: collections.defaultdict(list)
        self.calibs = collections.defaultdict(ddict_factory)

    def is_good(self, event):
        "Returns ``True`` if the event should be processed by ProcessRegion."
        runtype_match = (event.run.runType == self.runType)
        bad_event = event.data['isBad']
        return runtype_match and not bad_event

    def ProcessStop(self):
        '''Make variation plots.

        Plot title will be the name of the cell.

        '''
        ROOT.gStyle.SetOptStat(11111111)
        self.c1.cd()

        for cell in self.calibs:
            variations = {}
            graph = ROOT.TGraphErrors()
            graph.SetTitle(cell)

            for runtime in self.calibs[cell]:
                mean = ROOT.TMath.Mean(len(self.calibs[cell][runtime]),
                                       array('f', self.calibs[cell][runtime]))
                rms = ROOT.TMath.RMS(len(self.calibs[cell][runtime]),
                                       array('f', self.calibs[cell][runtime]))

                variations[runtime] = (mean, rms)

            first_time = min(variations)
            reference_calibration = variations[first_time][0]

            for point, runtime in enumerate(self.calibs[cell]):
                variation = ((variations[runtime][0] - reference_calibration) /
                                          reference_calibration)
                error = ((variations[runtime][1] /
                          len(self.calibs[cell][runtime])) /
                         reference_calibration)
                graph.SetPoint(point, runtime, variation)
                graph.SetPointError(point, 0, error)

            graph.GetYaxis().SetRangeUser(-2.0, 2.0)
            graph.SetMarkerStyle(20)
            graph.SetMarkerSize(1.3)
            graph.GetYaxis().SetTitle('% variation in CIS calibration')
            graph.SetMarkerColor(ROOT.kBlack)
            graph.Draw('AP')

            xaxis = graph.GetXaxis()
            xaxis.SetTimeDisplay(1)
            xaxis.SetTimeFormat("%d/%m/%y%F1970-01-01 00:00:00")

            for ext in self.exts:
                self.c1.Print('{0}/cis_{1}.{2}'.format(self.dir, cell, ext))

    def ProcessRegion(self, region):
        "Collect calibration information for the selected regions."
        if 'gain' not in region:
            return

        found = any(self.is_good(event) for event in region.events)

        if not found and not self.all:
            return

        for event in region.events:
            if not self.is_good(event):
                continue

            self.process_event(event, region)

    def process_event(self, event, region):
        "Collect the variation data"
        gain = str(region).split('_')[-1]
        time = event.run.time_in_seconds
        calib = event.data[self.parameter]

        for subregion in self.regions:
            if subregion in region:
                self.calibs['%s_%s' % (subregion, gain)][time].append(calib)
