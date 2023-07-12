from workers.noise.PedestalWorker import PedestalWorker

class PedestalComparison2D(PedestalWorker):
    # comparison mode
    _ComparisonAbsolute = 1
    _ComparisonRelative = 2
    
    def __init__(self, referenceRun, comparisonRun, output,
                 maxDiff = 5.0, minDiff = -5.0, 
                 mode = 'absolute', useSimpleColors=False, markBadChannels=False,
                 referenceRunAttribute='ped', comparisonRunAttribute='ped',
                 plotTitle='Pedestal',
                 referenceRunType='Ped', comparisonRunType='Ped', diffDistMax=5):
        super(PedestalComparison2D, self).__init__(output)
        self.m_referenceRun = referenceRun
        self.m_maxDiff = maxDiff
        self.m_minDiff = minDiff
        self.m_comparisonRun = comparisonRun
        self.m_referenceRunType = referenceRunType
        self.m_comparisonRunType = comparisonRunType
        self.m_useSimpleColors = useSimpleColors
        self.m_palette = None
        self.m_markBadChannels = markBadChannels
        self.m_plotTitle = plotTitle

        self.m_referenceRunAttribute = referenceRunAttribute
        self.m_comparisonRunAttribute = comparisonRunAttribute

        if self.m_useSimpleColors:
            self.m_palette = array('i', [ROOT.kWhite, ROOT.kGreen, ROOT.kOrange-3, ROOT.kRed])
            self.m_maxDiff = 4
            self.m_minDiff = 0

        namePrefix = ''
        if mode == 'absolute':
            self.m_mode = PedestalComparison2D._ComparisonAbsolute
            namePrefix = '%s-difference' % plotTitle
        else:
            self.m_mode = PedestalComparison2D._ComparisonRelative
            namePrefix = '%s-relative-difference' % plotTitle
        
        self.m_diffPlots = {}
        self.m_diffDist = {}
        self.m_badChPlots = {}

        # create histograms
        part_names = self._PartitionNames()
        for part_name in part_names:
            for gain in ['LG', 'HG']:
                hiname = '%s-%s-%s' % (namePrefix, part_name, gain)
                if gain == 'LG':
                    hititle = '%s low gain' % part_name
                    part_id = "%s_%s" % (part_name, 'lowgain')
                else:
                    hititle = '%s high gain' % part_name
                    part_id = "%s_%s" % (part_name, 'higain');

                self.m_diffPlots[part_id] = ROOT.TH2D(hiname, hititle, 64, 1, 64, 48, 1, 48)
                self.m_diffDist[part_id] = ROOT.TH1D('dist-%s' % hiname, 'Dist %s' % hititle, 100, -diffDistMax, diffDistMax)
                if self.m_markBadChannels:
                    self.m_badChPlots[part_id] = ROOT.TH2D(hiname+'_isbad', '', 64, 1, 64, 48, 1, 48)
        # Overall diff
        for gain in ['LG', 'HG']:
            part_name = 'TILECAL'
            hiname = '%s-%s-%s' % (namePrefix, part_name, gain)
            if gain == 'LG':
                hititle = '%s low gain' % part_name
                part_id = "%s_%s" % (part_name, 'lowgain')
            else:
                hititle = '%s high gain' % part_name
                part_id = "%s_%s" % (part_name, 'higain');
            self.m_diffDist[part_id] = ROOT.TH1D('dist-%s' % hiname, 'Dist %s' % hititle, 100, -diffDistMax, diffDistMax)
        # prepare plots
        for hiname, hi in list(self.m_diffPlots.items()):
            self._Prepare2DHistogram(hi)

    def _Prepare2DHistogram(self, histogram):
        if self.m_useSimpleColors:
            histograms.SetContour(4)
        histogram.GetXaxis().SetTitle("Drawer")
        histogram.GetYaxis().SetTitle("Channel")
        histogram.SetMinimum(self.m_minDiff)
        histogram.SetMaximum(self.m_maxDiff)

    # **** Implementation of Worker ****

    def ProcessStart(self):
        pass
        
    def ProcessStop(self):
        if self._IsComparisonAbsolute():
            title = "Absolute difference between run %s and run %s" % (self.m_referenceRun, self.m_comparisonRun)
        else:
            title = "Relative difference between run %s and run %s" % (self.m_referenceRun, self.m_comparisonRun)

        plots = []
        # plot 2D histograms
        for part_id in list(self.m_diffPlots.keys()):
            opts = {'title':title, 'palette':self.m_palette, 'plot':self.m_diffPlots[part_id]}
            if self.m_markBadChannels:
                opts['mask'] = self.m_badChPlots[part_id]
            plots.append(opts)
        self._Make2DPlots(plots)
        
        # Plot 1D histograms
        plots = list(self.m_diffDist.values())
        for p in plots:
            p.Fit('gaus')
            f = p.GetFunction('gaus')
            if f:
                p.SetTitle('%s mean: %f sigma: %f' % (p.GetTitle(), f.GetParameter(1), f.GetParameter(2)))
            else:
                p.SetTitle('%s' % (p.GetTitle()))
        self._Make1DPlots(plots, {'logy':1, 'title':title, 'addoverflow':1})
        
    def ProcessRegion(self, region):
        # we only care about ADCs
        if not self._IsADC(region):
            return
        [part, mod, chan, gain] = region.GetNumber()
        isBad = {}

        # fetch run data
        comparisonRunData = None
        referenceRunData = None
        for event in region.GetEvents():
            runNumber = event.run.runNumber

            if runNumber == self.m_comparisonRun and event.run.runType == self.m_comparisonRunType:
                comparisonRunData = event.data
            if runNumber == self.m_referenceRun and event.run.runType == self.m_referenceRunType:
                referenceRunData = event.data
            # determine if the ADC is masked as bad in this run
            isBad[runNumber] = ('isBad' in event.data) and event.data['isBad']

        # Determine which histogram to update
        histo = None
        distHisto = None
        
        part_id = "%s_%s" % (region.get_partition(), 'lowgain' if gain==0 else 'higain')
        histo = self.m_diffPlots[part_id]
        distHisto = self.m_diffDist[part_id]
        badChHisto = None
        if self.m_markBadChannels:
            badChHisto = self.m_badChPlots[part_id]
            if isBad[self.m_comparisonRun] or isBad[self.m_referenceRun]:
                badChHisto.SetBinContent(mod, chan, (self.m_maxDiff + self.m_minDiff)/2)
            else:
                badChHisto.SetBinContent(mod, chan, -100000)

        if not comparisonRunData:
            self.m_output.print_log("Error: No comparison data for %s" % region.GetHash())
        if not referenceRunData:
            self.m_output.print_log("Error: No reference data for %s" % region.GetHash())
        
        if not comparisonRunData or not referenceRunData:
            return

        content = None
        if self._IsComparisonAbsolute():
            content = comparisonRunData[self.m_comparisonRunAttribute] - referenceRunData[self.m_referenceRunAttribute]
            if self.m_useSimpleColors:
                if comparisonRunData[self.m_comparisonRunAttribute] == 0.0 or referenceRunData[self.m_referenceRunAttribute] == 0.0:
                    content = 0.5
                elif abs(content) > 2:
                    content = 3.5
                elif abs(content) > 1:
                    content = 2.5
                else:
                    content = 1.5
        else:
            if referenceRunData[self.m_referenceRunAttribute] != 0.0:
                content = (comparisonRunData[self.m_comparisonRunAttribute] - referenceRunData[self.m_referenceRunAttribute])/referenceRunData[self.m_referenceRunAttribute]
        if content != None:
            histo.SetBinContent(mod, chan, abs(content))
            distHisto.Fill(content)
            self.m_diffDist['TILECAL_%s' % ('lowgain' if gain==0 else 'higain')].Fill(content)

    def _IsComparisonAbsolute(self):
        return self.m_mode == self._ComparisonAbsolute
