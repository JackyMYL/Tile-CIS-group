from src.GenericWorker import GenericWorker
from src.MakeCanvas import MakeCanvas
import os
import ROOT

class PedestalWorker(GenericWorker):
    def __init__(self, output):
        self.m_output = output

    # **** Protected methods ****

    def _PartitionNames(self):
        """ Return a list of partition names in the same order as partition index. """
        return ['LBA', 'LBC', 'EBA', 'EBC']

    def _Make1DPlots(self, plots, opts):
        for plot in plots:
            # handle under/overflow
            if 'addoverflow' in opts:
                u = plot.GetBinContent(0)
                plot.AddBinContent(1, u)
                o = plot.GetBinContent(plot.GetNbinsX() + 1)
                plot.AddBinContent(plot.GetNbinsX(), o)

            canvas = MakeCanvas()
            canvas.Clear()
            partStr = plot.GetTitle()
            plot.SetTitle('')
            plot.Draw()

            title = self._PrepareCanvas(canvas, plot, opts['title'], partStr, False, 'logy' in opts)
            self._SaveCanvas(canvas, None, plot.GetName())

    def _Make2DPlots(self, plots):
        for plot_opts in plots:
            plot = plot_opts['plot']
            if plot_opts['palette']:
                palette = opts['palette']
                ROOT.gStyle.SetPalette(len(palette), palette)

            canvas = MakeCanvas()
            canvas.Clear()
            partStr = plot.GetTitle()
            plot.SetTitle('')
            plot.Draw("COLZ")

            if 'mask' in plot_opts:
                maskHi = plot_opts['mask']
                maskHi.SetFillColor(1)
                maskHi.Draw("BOX SAME")

            title = self._PrepareCanvas(canvas, plot, plot_opts['title'], partStr, True)
            self._SaveCanvas(canvas, plot)

    def _SaveCanvas(self, canvas, plot, plotName=None):
        canvas.Modified()
        canvas.Update()
        plotName = plot.GetName() if (not plotName and plot) else plotName
        self.m_output.plot(canvas, plotName)
        canvas.SetName("%s_canvas" % plotName)
        self.m_output.add_root_object(canvas)
        if plot:
            self.m_output.add_root_object(plot)

    def _PrepareCanvas(self, canvas, plot, titleStr, partStr, fixPalette=False, logy=False):                    
        title = ROOT.TLatex(0.12, 0.9, "#splitline{%s}{%s}" % (titleStr, partStr))
        title.SetNDC()
        title.Draw()

        canvas.Modified()
        canvas.SetTopMargin(0.2)
        canvas.SetLeftMargin(0.10)
        canvas.SetBottomMargin(0.10)
        canvas.SetRightMargin(0.2 if fixPalette else 0.1)
        canvas.SetTicks(2, 2)
        canvas.SetLogy(1 if logy else 0)
        plot.GetYaxis().SetTitleOffset(0.9)
        plot.GetXaxis().SetTitleOffset(0.9)
        canvas.Update()

        # move the palette
        if fixPalette:
            palette = plot.GetListOfFunctions().FindObject('palette')
            palette.SetX1NDC(0.89)
            palette.SetX2NDC(0.94)
            # palette.GetAxis().SetNdivisions(-4)

        # make sure the title object is not GC'd
        return title

    def _IsADC(self, region):
        return 'gain' in region.GetHash()
