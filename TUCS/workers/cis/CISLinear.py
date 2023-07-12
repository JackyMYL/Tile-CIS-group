#### Author: Dave Hollander <daveh@uchicago.edu>
#### Update: John Dougherty <jdougherty@uchicago.edu>
####
#### December 8, 2010
####

#### This worker generates the following plots (in Tucs/plots/latest/cis):
####   linearity/Corr_TILECAL_<region>.ps
####       Per-gain residual distribution with non-linear correction applied
####
####   linearity/unCorr_TILECAL_<region>.ps
####       Per-gain residual distribution without correction
####
####   mean_low_linearity.eps
####       Mean residual distribution for the low gains of the entire selected 
####       region, both corrected and uncorrected
####
####   mean_low_linearity_corr.eps
####       Mean residual distribution for the low gains of the entire selected 
####       region, corrections applied
####       
####   mean_low_linearity_uncorr.eps
####       Mean residual distribution for the low gains of the entire selected 
####       region, corrections not applied
####

from src.GenericWorker import *
from src.oscalls import *
import src.MakeCanvas
from math import *

from TileCalibBlobPython import TileCalibTools, TileBchTools
from TileCalibBlobPython.TileCalibTools import MINRUN, MINLBK, MAXRUN, MAXLBK, LASPARTCHAN, UNIX2COOL
from TileCalibBlobObjs.Classes import TileCalibDrawerFlt
from TileCalibBlobObjs.Classes import *

## For turning off annoying logging
import logging
from TileCalibBlobPython.TileCalibLogger import TileCalibLogger, getLogger

class CISLinear(ReadGenericCalibration):
    """Look at the linearity of each channel with and without correction"""


    def __init__(self, useSqlite=True, SingleGain=False, sqlfn='tileSqlite.db'):
        self.i = 0
        self.useSqlite = useSqlite
        self.dbPath=os.path.join(getResultDirectory(), sqlfn)
        self.sgain = SingleGain
        self.dir = os.path.join(getPlotDirectory(), "cis")
        self.dir2 = self.dir
        if self.sgain:
            createDir('%s/linearity' % self.dir)
            self.dir = '%s/linearity' % self.dir

        self.c1 = src.MakeCanvas.MakeCanvas()

        self.data = 0
        self.tag2 = 'RUN2-HLT-UPD1-00'
        ROOT.gROOT.ProcessLine(".x style.C")


    def ProcessStart(self):
        self.low = {}
        self.low_corr = {}

        self.low_2 = {}
        self.low_corr_2 = {}

        self.hist = {}
        
        self.db = None

        print("Use SQLite file?", self.useSqlite)
        if self.useSqlite:
            if not os.path.exists(self.dbPath):
                print('ReadDB: Failed to find',self.dbPath)

            self.db = TileCalibTools.openDb('SQLITE', 'CONDBR2', 'READONLY', sqlfn=self.dbPath)
        else:
            self.db = TileCalibTools.openDbConn('COOLOFL_TILE/CONDBR2', 'READONLY')
        
        if not self.db:
            print("ReadDB: Failed to open a database connection")
        else:
            self.folderPath = os.path.join(TileCalibTools.getTilePrefix(), 'CALIB/CIS/NLN')
            self.folderTag = TileCalibUtils.getFullTag(self.folderPath,  'RUN2-HLT-UPD1-00')

#            self.folderPath = '/TILE/OFL02/CALIB/CIS/NLN'
#            self.folderTag = 'TileOfl02CalibCisNln-RUN2-HLT-UPD1-00'
            print(self.folderPath, self.folderTag)
            
            self.blobReader = TileCalibTools.TileBlobReader(self.db, 
                                                            self.folderPath, 
                                                            self.folderTag)
               

    def ProcessStop(self):
        self.c1.cd()
        
        fitCorr = ROOT.TGraphErrors()

        fitUnCorr = ROOT.TGraphErrors()
        fitUnCorr.SetMarkerStyle(23)
        fitUnCorr.SetMarkerColor(2)

        fitCorr2 = ROOT.TGraphErrors()
        fitCorr2.SetMarkerStyle(20)
        fitCorr2.SetMarkerColor(3)

        fitUnCorr2 = ROOT.TGraphErrors()
        fitUnCorr2.SetMarkerStyle(21)
        fitUnCorr2.SetMarkerColor(4)
                    
        ###  Fill the comparison plots
        for i, injection in enumerate(sorted(self.low_corr)):
            corr = self.low_corr[injection]                
            mean = ROOT.TMath.Mean(len(corr), array('f', corr))
            rms = ROOT.TMath.RMS(len(corr), array('f', corr))
            fitCorr.SetPoint(i, injection, mean)
            fitCorr.SetPointError(i, 0, rms/sqrt(len(corr)))
            
            uncorr = self.low[injection]
            mean3 = ROOT.TMath.Mean(len(uncorr), array('f', uncorr))
            rms3 = ROOT.TMath.RMS(len(uncorr), array('f', uncorr)) 
            fitUnCorr.SetPoint(i, injection, mean3)
            fitUnCorr.SetPointError(i, 0, rms3/sqrt(len(corr)))
            
            if len(self.low_corr_2) != 0 and len(self.low_2) != 0:
                corr2 = self.low_corr_2[injection]
                mean2 = ROOT.TMath.Mean(len(corr2), array('f', corr2))
                rms2 = ROOT.TMath.RMS(len(corr2), array('f', corr2))
                fitCorr2.SetPoint(i, injection, mean2)
                fitCorr2.SetPointError(i, 0, rms2/sqrt(len(corr2)))

                uncorr2 = self.low_2[injection]
                mean4 = ROOT.TMath.Mean(len(uncorr2), array('f', uncorr2))
                rms4 = ROOT.TMath.RMS(len(uncorr2), array('f', uncorr2))
                fitUnCorr2.SetPoint(i, injection, mean4)
                fitUnCorr2.SetPointError(i, 0, rms4/sqrt(len(corr2)))

            else:
                pass                   

                        
        ###  Draw both corrected and uncorrected superimposed  
        AllHist = fitCorr.GetHistogram()
        AllHist.SetMinimum(-2)
        AllHist.SetMaximum(1)
        AllHist.GetXaxis().SetTitle("Injected charge (pC)")
        AllHist.GetYaxis().SetTitle("Mean (Data - Fit) / Fit * 100 (%)")

        fitCorr.Draw("APE")
        fitUnCorr.Draw("PE")
        if len(self.low_2) != 0: 
            fitCorr2.Draw("PE")
            fitUnCorr2.Draw("PE")
                    
        leg = ROOT.TLegend(0.35, 0.8, 0.92, 0.92, "", "brNDC")
        leg.AddEntry(fitCorr, ("Corrected mean residual, run %i" % (self.run1)),
                     "P")
        leg.AddEntry(fitUnCorr, 
                     ("Uncorrected mean residual, run %i" % (self.run1)), "P")
        if len(self.low_2) != 0: 
            leg.AddEntry(fitCorr2, 
                         ("Corrected mean residual, run %i" % (self.run2)), "P")
            leg.AddEntry(fitUnCorr2, 
                         ("Uncorrected mean residual, run %i" % (self.run2)), 
                         "P")
        leg.Draw()
                                
        self.c1.Print("%s/mean_low_linearity.eps" % (self.dir2))

        ###  Draw just the corrected fits
        CorrHist = fitCorr.GetHistogram()
        CorrHist.SetMinimum(-1)
        CorrHist.SetMaximum(1)
        CorrHist.GetXaxis().SetTitle("Injected charge (pC)")
        CorrHist.GetYaxis().SetTitle("Mean (Data - Fit) / Fit * 100 (%)")

        fitCorr.Draw("APE")
        if len(self.low_2) != 0: 
            fitCorr2.Draw("PE")

        leg = ROOT.TLegend(0.35, 0.85, 0.95, 0.92, "", "brNDC")
        leg.AddEntry(fitCorr, ("Corrected mean residual, run %i" % (self.run1)),
                     "P")
        if len(self.low_2) != 0: 
            leg.AddEntry(fitCorr2,
                         ("Corrected mean residual, run %i" % (self.run2)),"P")
        leg.Draw()
      
        self.c1.Print("%s/mean_low_linearity_corr.eps" % (self.dir2))

        ###  Draw just the uncorrected fits
        UnCorrHist = fitUnCorr.GetHistogram()
        UnCorrHist.SetMinimum(-2.5)
        UnCorrHist.SetMaximum(1)
        UnCorrHist.GetXaxis().SetTitle("Injected charge (pC)")
        UnCorrHist.GetYaxis().SetTitle("Mean (Data - Fit) / Fit * 100 (%)")

        fitUnCorr.Draw("APE")
        if len(self.low_2) != 0: 
            fitUnCorr2.Draw("PE")

        leg = ROOT.TLegend(0.25, 0.85, 0.85, 0.92, "", "brNDC")
        leg.SetTextSize(0.045)
        leg.AddEntry(fitUnCorr, 
                     ("Uncorrected mean residual, run %i" % (self.run1)), "P")
        if len(self.low_2) != 0: 
            leg.AddEntry(fitUnCorr2, 
                         ("Uncorrected mean residual, run %i" % (self.run2)), 
                         "P")
        leg.Draw()
        
        self.c1.Print("%s/mean_low_linearity_uncorr.eps" % (self.dir2))
        
        if self.db:
            self.db.closeDatabase()
        
        
    def ProcessRegion(self, region):
        run = 200000
        #run = 120000
        ros = 0
        drawer = 0

        self.flt = self.blobReader.getDrawer(ros, drawer, (run, 0))
        if 'gain' not in region.GetHash():
            return

        self.runs = []
        for event in region.GetEvents():
            if event.run.runType == 'CIS':
                self.runs.append(event.run.runNumber)
                self.run1 = min(self.runs)
                self.run2 = max(self.runs)

        for event in region.GetEvents():
            if event.run.runType == 'CIS' and 'scan' in event.data:

                if self.i == 0:
                    self.i += 1
                scan = event.data['scan']
                gnlnCorr = ROOT.TGraphErrors()
                gnln = ROOT.TGraphErrors()
                gnlni = 0

                [x, y, z, w] = region.GetNumber()

                for i in range(scan.GetN()):
                
                    ###  Process range data
                    if 'high' in region.GetHash() and not 3<scan.GetX()[i]<10:
                        continue
                    if 'low' in region.GetHash() and not 10<scan.GetX()[i]<700:
                        continue
                                      
                    charge = float(scan.GetY()[i]/event.data['calibration'])
                    fitCharge = self.flt.getCalib(z, w, charge, True)
                    
                    injection = scan.GetX()[i]

                    factor =((fitCharge - injection)
                                 /(injection))
                    factor2 = ((scan.GetY()[i] - 
                                event.data['calibration']*injection)
                                /(event.data['calibration']*injection))

                    ##  Fill ./linearity plots
                    if self.sgain and event.run.runNumber == self.run2:
                        gnlnCorr.SetPoint(gnlni, scan.GetX()[i], factor*100)
                        gnln.SetPoint(gnlni, scan.GetX()[i], factor2*100)

                    ###  Fill arrays for module-wide plots
                    if 'low' in region.GetHash():
                        if event.run.runNumber == self.run2:
                            self.low_corr.setdefault(injection, []).append(
                                                                     factor*100)
                            self.low.setdefault(injection, []).append(
                                                                   factor2*100)
                        elif event.run.runNumber == self.run1 and(
                             self.run1 != self.run2):
                            self.low_corr_2.setdefault(injection, []).append(
                                                                     factor*100)
                            self.low_2.setdefault(injection, []).append(
                                                                    factor2*100)
                    gnlni += 1
                                  
                ###  Format and print ./linearity plots
                if self.sgain and event.run.runNumber == self.run2:

                    self.c1.cd()
                    ROOT.gStyle.SetOptTitle(1)

                    for plot in [gnln, gnlnCorr]:
                        plot.SetTitle("Run: %s\t %s" % (event.run.runNumber, 
                                                        region.GetHash()))
                        plot.SetMaximum(10)
                        plot.SetMinimum(-10)
                        plot.SetFillColor(0)
                        plot.SetLineWidth(1)
                        plot.SetMarkerStyle(20)
    
                        plot.GetXaxis().SetTitle("Injected Charge (pC)")
                        plot.GetXaxis().SetLabelOffset(0.02)
                        plot.GetXaxis().SetLabelOffset(0.01)
                        plot.GetXaxis().SetTitleOffset(0.93)
    
                        plot.GetYaxis().SetTitle("(Data - Fit) / Fit * 100 (%)")
                        plot.GetYaxis().CenterTitle(True)
        
                        plot.Draw('AP')
    
                        if plot == gnln:
                           self.c1.Print("%s/Corr_%s.ps" % (self.dir, 
                                                            region.GetHash()))
                        else:
                           self.c1.Print("%s/unCorr_%s.ps" % (self.dir, 
                                                              region.GetHash()))
