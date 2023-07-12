from workers.noise.PedestalWorker import PedestalWorker
from src.MakeCanvas import MakeCanvas

class PedestalTimeEvolution(PedestalWorker):
    # Comparison modes
    _CompareRef = 0
    _ComparePrev = 1
    _CompareFirst = 2
    _CompareCurrentDB = 3

    # Modes
    _ModeAbsolute = 0
    _ModeRelative = 1

    """
    PedestalTimeEvolution
      Plot time evolution of changes.
    """
    def __init__(self, output, referenceRun, compareTo, plotPrefix, dataAttribute, diffThresholds, 
                 diffThresholdColors, showDates = True, dateFormat = "%Y-%m-%d",
                 title = "Pedestal abs difference", titleY = "Number of ADCs",
                 titleDetails = "Pedestal values", titleYDetails = "ADC counts",
                 legendTitle = '#Delta pedestal',
                 plotLogY = True, minY = 1, maxY = 1000, 
                 mode = 'absolute', sigmaAttribute = None, plotADCDetails=True, 
                 dbDataAttribute=None, dbSigmaAttribute=None, splitHiAndLow=False,
                 excludeBadChannels=False, plotBadChannels=False, plotIOVs=False, saveADCDetails=True):
        super(PedestalTimeEvolution, self).__init__(output)
        
        self.m_compareTo = 0
        if compareTo == 'reference':
            self.m_compareTo = PedestalTimeEvolution._CompareRef
        elif compareTo == 'previous':
            self.m_compareTo = PedestalTimeEvolution._ComparePrev
        elif compareTo == 'first':
            self.m_compareTo = PedestalTimeEvolution._CompareFirst
        elif compareTo == 'current_db':
            self.m_compareTo = PedestalTimeEvolution._CompareCurrentDB

        self.m_plotPrefix = plotPrefix
        self.m_referenceRun = referenceRun
        self.m_dataAttribute = dataAttribute
        self.m_dbDataAttribute = dbDataAttribute
        self.m_sigmaAttribute = sigmaAttribute
        self.m_dbSigmaAttribute = dbSigmaAttribute

        self.m_diffThresholds = list(diffThresholds)
        self.m_diffThresholdColors = list(diffThresholdColors)
        self.m_showDates = showDates
        self.m_dateFormat = dateFormat
        self.m_runDifferences = {}
        self.m_runInfo = {}
        self.m_title = title
        self.m_titleY = titleY
        self.m_plotLogY = plotLogY
        self.m_minY = minY
        self.m_maxY = maxY
        self.m_mode = 0
        self.m_plotADCDetails = plotADCDetails
        self.m_splitHiAndLow = splitHiAndLow
        self.m_titleDetails = titleDetails
        self.m_titleYDetails = titleYDetails
        self.m_legendTitle = legendTitle
        self.m_excludeBadChannels = excludeBadChannels
        self.m_plotBadChannels = plotBadChannels
        self.m_plotIOVs = plotIOVs
        self.m_saveDetailedData = saveADCDetails

        if plotIOVs and not showDates:
            output.print_log("ERROR: Plotting IOVs require showDate to be True")
            exit(1)

        if mode == 'absolute':
            self.m_mode = PedestalTimeEvolution._ModeAbsolute
        else:
            self.m_mode = PedestalTimeEvolution._ModeRelative
            if self.m_sigmaAttribute == None:
                self.m_output.print_log("ERROR: sigmaAttribute must be specified for relative mode")
            if self._DoCompareToCurrentDB() and self.m_dbSigmaAttribute == None:
                self.m_output.print_log("ERROR: dbSigmaAttribute must be specified for relative mode")

        if len(self.m_diffThresholds) != len(self.m_diffThresholdColors):
            self.m_output.print_log("ERROR: The number of thresholds (%d) and colors (%d) must be equal" % (len(self.m_diffThresholds), len(self.m_diffThresholdColors)))
        
        if self.m_plotBadChannels:
            self.m_diffThresholds.append(-1)
            self.m_diffThresholdColors.append(ROOT.kBlack)

        self.m_sortedRuns = None
        self.m_IOVStarts = {}
        self.m_output_data = {}

    def regions(self):
        yield 'TILECAL'
        for r in ['TILECAL_LBA', 'TILECAL_LBC', 'TILECAL_EBA', 'TILECAL_EBC']:
            yield r
            for m in range(1, 65):
                yield '%s_m%02d' % (r, m)

    def create_run_data(self):
        return [[0,0] for ii in range(len(self.m_diffThresholds))] if self._DoSplitHiAndLow() else [0] * len(self.m_diffThresholds)

    # **** Implementation of Worker ****
        
    def ProcessStart(self):
        pass
        
    def ProcessStop(self):
        canvas = MakeCanvas()
        canvas.cd()
        histograms = []
        rund = list(self.m_runDifferences.values())[0]
        for reg in rund:
            canvas.Clear()
            if 'gain' in reg:
                if self.m_plotADCDetails:
                    histograms += self._PlotTileADC(canvas, reg)
            else:
                if self._DoSplitHiAndLow():
                    histograms += self._PlotTileRegion(canvas, reg, 0)
                    histograms += self._PlotTileRegion(canvas, reg, 1)
                else:
                    histograms += self._PlotTileRegion(canvas, reg)
        # Dump
        self.m_output.print_log("Summary for TILECAL")
        for run in self.m_sortedRuns:
            res = "%d " % int(run)
            for i in range(len(self.m_diffThresholds)):
                res += "%d " % self.m_runDifferences[run]['TILECAL'][i]
            self.m_output.print_log(res)

        if self.m_saveDetailedData:
            json_output = {'data': self.m_output_data, 'runs': [[r, self.m_runInfo[r].getTimeSeconds()] for r in self.m_sortedRuns], 'thresholds': self.m_diffThresholds }
            self.m_output.add_json('%s_values' % self.m_dataAttribute, json_output)

        # cleanup
        self.m_sortedRuns = None
        self.m_runDifferences = None
        self.m_runInfo = None
        self.m_IOVStarts = None
        self.m_output_data = None
        
    def ProcessRegion(self, region):
        # we only care about ADCs
        if not self._IsADC(region):
            return
        
        [part, mod, chan, gain] = region.GetNumber()

        # build list of sorted runs, the result structure and store run info, once
        if self.m_sortedRuns == None:
            firstRun = lastRun = None
            for event in region.GetEvents():
                if not self.m_dataAttribute in event.data:
                    self.m_output.print_log("ERROR: No attribute '%s' in event" % self.m_dataAttribute)
                    continue
                if event.data[self.m_dataAttribute] == None:
                    continue

                runNumber = event.run.runNumber                
                if firstRun == None:
                    firstRun = lastRun = runNumber
                elif self.m_referenceRun != runNumber:
                    firstRun = min(firstRun, runNumber)
                    lastRun = max(lastRun, runNumber)
                self.m_output.print_log("PedestalTimeEvolution - Adding run %s" %(runNumber))

                if self.m_sortedRuns == None:
                    self.m_sortedRuns = []
                self.m_sortedRuns.append(runNumber)
                # store run info
                if runNumber not in self.m_runInfo:
                    self.m_runInfo[runNumber] = event.run
                # create struct for storing results
                if not runNumber in self.m_runDifferences:
                    self.m_runDifferences[runNumber] = dict((reg, self.create_run_data()) for reg in self.regions())
            if self.m_sortedRuns == None:
                self.m_output.print_log("WARNING: No runs for region: %s" % region.GetHash())
                self.m_sortedRuns = []
            # Handle reference run
            if self.m_referenceRun != None:
                if (self.m_referenceRun < firstRun) or (self.m_referenceRun > lastRun):
                    del self.m_runDifferences[self.m_referenceRun]
                    self.m_sortedRuns.remove(self.m_referenceRun)
            self.m_sortedRuns = sorted(self.m_sortedRuns)

        # get data for each run
        runData = {}
        dbData = {}
        isBad = {}
        iov_key = None
        for event in region.GetEvents():
            runNumber = event.run.runNumber
            if not runNumber in self.m_runInfo:
                continue

            # determine if the ADC is masked as bad in this run
            isBad[runNumber] = ('isBad' in event.data) and event.data['isBad']

            # store IOVs per partition/drawer
            if self.m_plotIOVs:
                iov_key = '%s_m%s' % (region.get_partition(), region.get_module())
                if not runNumber in self.m_IOVStarts:
                    self.m_IOVStarts[runNumber] = {}
                if not iov_key in self.m_IOVStarts[runNumber]:
                    self.m_IOVStarts[runNumber][iov_key] = event.data['ped_db_iov_start'] if 'ped_db_iov_start' in event.data else False

            runData[runNumber] = [event.data[self.m_dataAttribute], event.data[self.m_sigmaAttribute] if self.m_sigmaAttribute else 0.0]
            # get COOL data if needed
            if self._DoCompareToDB():
                dbData[runNumber] = [event.data[self.m_dbDataAttribute], event.data[self.m_dbSigmaAttribute] if self.m_dbSigmaAttribute else 0.0]

        if self.m_saveDetailedData:
            # Prepare storage
            partname = region.get_partition()
            if not partname in self.m_output_data:
                self.m_output_data[partname] = {}
            if not mod in self.m_output_data[partname]:
                self.m_output_data[partname][mod] = {}
            if not chan in self.m_output_data[partname][mod]:
                self.m_output_data[partname][mod][chan] = {}
            if not gain in self.m_output_data[partname][mod][chan]:
                self.m_output_data[partname][mod][chan][gain] = []
            
        # compute the difference with respect to the reference
        # for each defined region and threshold
        for runIdx in range(len(self.m_sortedRuns)):
            runNumber = self.m_sortedRuns[runIdx]

            # determine the value to compare to
            refval = runData[runNumber]
            if self._DoCompareToPrevious():
                if runIdx > 0:
                    refval = runData[self.m_sortedRuns[runIdx - 1]]
            elif self._DoCompareToFirst():
                refval = runData[self.m_sortedRuns[0]]
            elif self._DoCompareToCurrentDB():
                refval = dbData[runNumber]
            else:
                refval = runData[self.m_referenceRun]
            
            # compute
            if self._IsModeAbsolute():
                diffVal = abs(runData[runNumber][0] - refval[0])
            else:
                diffVal = 0 if refval[1] == 0.0 else abs((runData[runNumber][0] - refval[0])/refval[0])

            # loop over all regions
            for reg in self.regions():
                # Non ADC regions
                if region.GetHash().startswith(reg) and (region.GetHash() != reg):
                    for d in range(len(self.m_diffThresholds)):
                        # if bad channels should be excluded
                        exclude = self.m_excludeBadChannels and isBad[runNumber]

                        # diffval < 0 means that the number of excluded (bad) channels should be counted
                        if ((diffVal > self.m_diffThresholds[d]) and (self.m_diffThresholds[d] > 0) and not exclude) or ((self.m_diffThresholds[d] < 0) and isBad[runNumber]):
                            if self._DoSplitHiAndLow():
                                self.m_runDifferences[runNumber][reg][d][gain] += 1
                            else:
                                self.m_runDifferences[runNumber][reg][d] += 1
            # Prepare for detailed plots
            if self.m_plotADCDetails:
                do_store = (diffVal > self.m_diffThresholds[0]) or isBad[runNumber]
                self.m_runDifferences[runNumber][region.GetHash()] = [runData[runNumber][0], runData[runNumber][1], dbData[runNumber][0] if self._DoCompareToDB() else 0.0, do_store]
        # Save IOV starts and detailed data
        if self.m_saveDetailedData and iov_key and 'iov_start' not in self.m_output_data[partname][mod]:
            self.m_output_data[partname][mod]['iov_start'] = [self.m_IOVStarts[r][iov_key] for r in self.m_sortedRuns]
            self.m_output_data[partname][mod][chan][gain]= [[runData[r][0], dbData[r][0] if self._DoCompareToDB() else 0.0, isBad[r]] for r in self.m_sortedRuns]

    # **** protected methods ****
                                
    def _DoCompareToRef(self):
        return self.m_compareTo == PedestalTimeEvolution._CompareRef

    def _DoCompareToPrevious(self):
        return self.m_compareTo == PedestalTimeEvolution._ComparePrev

    def _DoCompareToFirst(self):
        return self.m_compareTo == PedestalTimeEvolution._CompareFirst

    def _DoCompareToCurrentDB(self):
        return self.m_compareTo == PedestalTimeEvolution._CompareCurrentDB

    def _DoCompareToDB(self):
        return self._DoCompareToCurrentDB()

    def _IsModeAbsolute(self):
        return self.m_mode == PedestalTimeEvolution._ModeAbsolute

    def _IsModeRelative(self):
        return self.m_mode == PedestalTimeEvolution._ModeRelative

    def _FirstRun(self):
        return self.m_runInfo[self.m_sortedRuns[0]]
    
    def _LastRun(self):
        return self.m_runInfo[self.m_sortedRuns[len(self.m_sortedRuns) - 1]]

    def _DoSplitHiAndLow(self):
        return self.m_splitHiAndLow == True

    def _PlotTileADC(self, canvas, reg, gain=None):
        if not self.m_sortedRuns:
            return []
        histograms = []
        plotName = '%sDetails-%s' % (self.m_plotPrefix, reg)

        # compute mean
        mean = 0.0
        sqsum = 0.0
        differences = 0
        n = float(len(self.m_sortedRuns))
        for runIdx in range(len(self.m_sortedRuns)):
            run = self.m_sortedRuns[runIdx]
            data = self.m_runDifferences[run][reg][0]
            # accumulate number of differences
            differences += self.m_runDifferences[run][reg][3]
            mean += data
            sqsum += data*data
        mean = mean / n

        # No differences, don't plot
        if differences == 0:
            return []

        # Start plotting by making the legend
        legend = ROOT.TLegend(0.65, 0.75, 1.0, 1.0)

        # error graph
        gr_err = ROOT.TGraphErrors(2)
        gr_err.SetName(plotName+'-err')
        histograms.append(gr_err)
        gr_err.SetTitle('')
        gr_err.SetPoint(0, self._FirstRun().getTimeSeconds(), mean)
        gr_err.SetPoint(1, self._LastRun().getTimeSeconds(), mean)
        gr_err.SetFillStyle(3005)

        if self._IsModeRelative():
            gr_err.SetPointError(0, 0.0, mean*0.1)
            gr_err.SetPointError(1, 0.0, mean*0.1)
            legend.AddEntry(gr_err, 'Mean of runs #pm 10%', "F")
            ymin = mean - 2
            ymax = mean + 2
        else:
            gr_err.SetPointError(0, 0.0, 2.0)
            gr_err.SetPointError(1, 0.0, 2.0)
            legend.AddEntry(gr_err, 'Mean of runs #pm 2 ADCc', "F")
            ymin = mean - 2
            ymax = mean + 2

        # draw run history        
        gr = ROOT.TGraphErrors(len(self.m_sortedRuns))
        gr.SetName(plotName)
        histograms.append(gr)
        gr.SetTitle('')
        gr.SetMarkerSize(1.2)
        gr.SetLineWidth(3)
        legend.AddEntry(gr, "Run value", "P")

        # draw DB history
        gr_db = None
        if self._DoCompareToDB():
            gr_db = ROOT.TGraph(len(self.m_sortedRuns))
            gr_db.SetName(plotName+'-db')
            histograms.append(gr_db)
            gr_db.SetTitle('')
            gr_db.SetMarkerStyle(23)
            gr_db.SetMarkerSize(1.2)
            gr_db.SetMarkerColor(2);
            legend.AddEntry(gr_db, "DB value", "P")

        for runIdx in range(len(self.m_sortedRuns)):
            run = self.m_sortedRuns[runIdx]
            content = self.m_runDifferences[run][reg][0]
            err = self.m_runDifferences[run][reg][1]
            ymin = min(ymin, content - err)
            ymax = max(ymax, content + err)

            gr.SetPoint(runIdx, self.m_runInfo[run].getTimeSeconds(), content)
            gr.SetPointError(runIdx, 0.0, err)
            if self._DoCompareToDB():
                db_val = self.m_runDifferences[run][reg][2]
                ymin = min(ymin, db_val)
                ymax = max(ymax, db_val)
                gr_db.SetPoint(runIdx, self.m_runInfo[run].getTimeSeconds(), db_val)

        gr_err.Draw("A3")
        gr_err.GetYaxis().SetTitle(self.m_titleYDetails)
        self._SetupGraphForTimeDisplay(gr_err)
        gr_err.SetMaximum(ymax * 1.05)
        gr_err.SetMinimum(ymin * 0.95)
        gr.Draw("PLSAME")
        self._SetupGraphForTimeDisplay(gr)

        if self._DoCompareToDB():
            gr_db.Draw("PLSAME")
            self._SetupGraphForTimeDisplay(gr_db)

        # Plot a title
        latexTitle = self._Draw4LineTitle(reg, self.m_titleDetails, self._GetRangeTitle(), "Mean of runs %.2f" % mean)

        lines = self._PlotIOVs(reg, ymin, ymax)

        self._CanvasStyle(canvas, 0)

        # Plot legend
        legend.SetBorderSize(0)
        legend.SetTextFont(42)
        legend.SetTextSize(0.040)
        legend.Draw()

        canvas.SetName(plotName+'_canvas')
        self.m_output.add_root_object(canvas)
        return histograms

    def _PlotTileRegion(self, canvas, reg, gain=None):
        """ Plot the time evolution for a Tile region. """
        regionName = reg
        if self._DoSplitHiAndLow():
            regionName += "-lowgain" if gain == 0 else "-highgain"

        if self._DoSplitHiAndLow() and (gain == None):
            self.m_output.print_log("ERROR: Split gains but gain is None")
            return

        maxy = self.m_maxY
        miny = maxy
        histograms = []
        legend = ROOT.TLegend(0.65, 0.75, 1.0, 1.0)
        for d in range(len(self.m_diffThresholds)):
            histoNameThreshold = ''
            legendLabelThreshold = ''
            if self.m_diffThresholds[d] < 0:
                histoNameThreshold = 'bad'
                legendLabelThreshold = 'Bad'
            else:
                histoNameThreshold = str(self.m_diffThresholds[d])
                legendLabelThreshold = "%s > %.2f" % (self.m_legendTitle, self.m_diffThresholds[d])

            histoName = 'Pedestal-%s-%s' % (regionName, histoNameThreshold)
            histogram = None
            if self.m_showDates:
                histogram = ROOT.TGraph(len(self.m_sortedRuns))
                histogram.SetTitle('')
                histogram.SetName(histoName)
            else:
                histogram = ROOT.TH1D(histoName, '', len(self.m_sortedRuns), 1, len(self.m_sortedRuns))
            # prevent GC
            histograms.append(histogram)
            legend.AddEntry(histogram, legendLabelThreshold, "L")
            for runIdx in range(len(self.m_sortedRuns)):
                run = self.m_sortedRuns[runIdx]

                # Get the content for the histogram
                if self._DoSplitHiAndLow():
                    content = self.m_runDifferences[run][reg][d][gain]
                else:
                    content = self.m_runDifferences[run][reg][d] 

                maxy = max(maxy, content)
                miny = min(miny, content)

                if self.m_showDates:
                    histogram.SetPoint(runIdx, self.m_runInfo[run].getTimeSeconds(), content) 
                else:
                    histogram.SetBinContent(runIdx + 1, content)
                    histogram.GetXaxis().SetBinLabel(runIdx + 1, str(run))
            if self.m_showDates:
                histogram.Draw('APL' if d == 0 else 'PLSAME')
                self._SetupGraphForTimeDisplay(histogram)
            else:
                histogram.Draw('PL' if d == 0 else 'PLSAME')
            histogram.GetYaxis().SetTitle(self.m_titleY)
            histogram.SetLineColor(self.m_diffThresholdColors[d])
            histogram.SetLineWidth(3)
            histogram.SetMinimum(self.m_minY)

        # set height of plot
        maxy = maxy * (2.0 if self.m_plotLogY else 1.1)
        miny = miny * 0.5 if miny > 0 else (0.0001 if self.m_plotLogY else 0.0)
        for histogram in histograms:
            histogram.SetMaximum(maxy)
            histogram.SetMinimum(miny)

        # Plot a title
        latexTitle = self._Draw4LineTitle(self._GetRegionTitle(reg, gain), self.m_title, self._GetRangeTitle(), self._GetCompareTitle())

        lines = self._PlotIOVs(reg, miny, maxy)

        # Plot legend
        legend.SetBorderSize(0)
        legend.SetTextFont(42)
        legend.Draw()

        self._CanvasStyle(canvas, 1 if self.m_plotLogY else 0)

        plotName = '%s-%s' % (self.m_plotPrefix, regionName)
        self._SaveCanvas(canvas, None, plotName)
        return histograms

    def _PlotIOVs(self, reg, ymin, ymax):
        lines = []
        if self.m_plotIOVs:
            regp = reg.split('_')
            IOVStarts = None
            if len(regp)>2:
                iov_key = '%s_%s' % (regp[1], regp[2])
                IOVStarts = {run: self.m_IOVStarts[run][iov_key] for run in self.m_sortedRuns}
            elif len(regp) == 2:
                IOVStarts = {run: sum(self.m_IOVStarts[run][k] for k in list(self.m_IOVStarts[run].keys()) if k.startswith(regp[1])) for run in self.m_sortedRuns}
            elif len(regp) == 1:
                IOVStarts = {run: sum(k for k in list(self.m_IOVStarts[run].values())) for run in self.m_sortedRuns}

            if IOVStarts:
                for runIdx in range(len(self.m_sortedRuns)):
                    run = self.m_sortedRuns[runIdx]
                    if IOVStarts[run]:
                        xv = self.m_runInfo[run].getTimeSeconds()
                        line = ROOT.TLine(xv, ymax, xv, ymin)
                        line.SetLineStyle(2)
                        line.SetLineWidth(2)
                        line.Draw()
                        lines.append(line)
        return lines

    def _GetRegionTitle(self, reg, gain):
        if self._DoSplitHiAndLow():
            return reg + (" lowgain" if gain == 0 else " highgain")
        else:
            return reg

    def _GetRangeTitle(self):
        if len(self.m_sortedRuns) > 1:
            return "Runs %s to %s" % (self.m_sortedRuns[0], self.m_sortedRuns[len(self.m_sortedRuns)-1])
        else:
            self.m_output.print_log("ERROR: no range of runs selected")
            return ""

    def _GetCompareTitle(self):
        if self._DoCompareToPrevious():
            return "Compared to previous run"
        elif self._DoCompareToFirst():
            return "Compared to first run %s " % (self.m_sortedRuns[0])
        elif self._DoCompareToCurrentDB():
            return "Compared to COOL history"
        else:
            return "Compared to run %s" % (self.m_referenceRun)

    def _Draw4LineTitle(self, l1, l2, l3, l4):
        title = ROOT.TLatex(0.12, 0.9, '#splitline{%s}{#splitline{%s}{#splitline{%s}{%s}}}' % (l1, l2, l3, l4))
        title.SetNDC()
        title.Draw()
        return title

    def _CanvasStyle(self, canvas, logy):
        canvas.Modified()
        canvas.SetLogy(logy)
        canvas.SetGridx()
        canvas.SetGridy()
        canvas.SetTopMargin(0.27)
        canvas.SetLeftMargin(0.12)
        canvas.SetBottomMargin(0.12)

    def _SetupGraphForTimeDisplay(self, histogram):
        histogram.GetXaxis().SetTimeDisplay(1)
        histogram.GetXaxis().SetTimeFormat(self.m_dateFormat)
        histogram.GetXaxis().SetTimeOffset(0, "gmt")
        histogram.GetXaxis().SetLabelSize(0.05)
        histogram.GetXaxis().SetNdivisions(505)
        histogram.GetXaxis().SetTitle("Run date")
