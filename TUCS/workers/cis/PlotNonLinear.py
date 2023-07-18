#### Author: Dave Hollander <daveh@uchicago.edu>
#### Updated: John Dougherty <jdougherty@uchicago.edu>
####
#### December 8, 2010
####
#### This worker generates the following plots (in Tucs/plots/latest/cis):
####   non_lin_fit.eps
####       Comparison of the database non-linear correction factors with the
####       experimental ratios.

from src.GenericWorker import *
from src.oscalls import *
import src.MakeCanvas
import time
import datetime
from math import *

class PlotNonLinear(GenericWorker):
    '''Plot the CIS non-linear correction'''

    def __init__(self, nlcwrite=True):
        self.dir = os.path.join(getPlotDirectory(), "cis")
        createDir(self.dir)
        self.nlcwrite = nlcwrite          

        ROOT.gROOT.ProcessLine(".x style.C")

        self.c1 = src.MakeCanvas.MakeCanvas()

        orig=os.path.join(getTucsDirectory(),"data/nonLinCorr.txt")
        dest=os.path.join(getResultDirectory(),"data/nonLinCorr.txt")
        if not os.path.isdir(os.path.dirname(dest)):
            os.makedirs(os.path.dirname(dest))
        if not os.access(dest, os.R_OK): 
            shutil.copyfile(orig,dest)


    def ProcessStart(self):

        try: open(os.path.join(getResultDirectory(),"data/nonLinCorr.txt"), "r")
        except IOError:
            self.useDB = True
            print("data/nonLinCorr.txt not found")

        else:
            print("Using data/nonLinCorr.txt")
            self.useDB = False
            self.fout = open(os.path.join(getResultDirectory(),"data/nonLinCorr.txt"), "r")

        try: TileCalibTools.openDbConn('COOLOFL_TILE/CONDBR2', 'READONLY') 
        except Exception:
            print("ReadDB: Failed to open a database connection")
        else:
            self.db = TileCalibTools.openDbConn('COOLOFL_TILE/CONDBR2', 'READONLY')
            self.folderPath = os.path.join(TileCalibTools.getTilePrefix(), 'CALIB/CIS/NLN')
            self.folderTag = TileCalibUtils.getFullTag(self.folderPath, 'RUN2-HLT-UPD1-00')

            self.blobReader = TileCalibTools.TileBlobReader(self.db, 
                                                            self.folderPath,
                                                            self.folderTag)

        self.fit = {}
        self.fitOrig = {}
        

    def ProcessStop(self):
        self.c1.cd()
        
        for fit, fitOrig in [(self.fit, self.fitOrig)]:
            fitCorr      = ROOT.TGraphErrors()
            fitCorr.SetMarkerStyle(23)
            fitCorr.SetMarkerColor(2)
            
            fitCorrOrig  = ROOT.TGraphErrors()
           
            for i, amp in enumerate(sorted(fit)):
                calibs = fit[amp]
                mean = ROOT.TMath.Mean(len(calibs), array('f', calibs))
                rms = ROOT.TMath.RMS(len(calibs), array('f', calibs))
                
                fitCorr.SetPoint(i, amp, mean)
                fitCorr.SetPointError(i, 0, rms/sqrt(len(calibs)))

            for i, amp in enumerate(sorted(fitOrig)):
                calibs = fitOrig[amp]
                mean = ROOT.TMath.Mean(len(calibs), array('f', calibs))
                rms = ROOT.TMath.RMS(len(calibs), array('f', calibs))
                
                fitCorrOrig.SetPoint(i, amp, mean/amp)
                fitCorrOrig.SetPointError(i, 0, rms/sqrt(len(calibs)))
                                     
            Graph = fitCorr.GetHistogram()
            Graph.GetXaxis().SetRangeUser(0, 510)
            Graph.GetXaxis().SetTitle("Initial amplitude (pC)")
            Graph.GetYaxis().SetTitle("Corrected amplitude / Initial amplitude")
            

            Graph.Draw()
            fitCorrOrig.Draw("P")
            fitCorr.Draw("EP")
            
            leg = ROOT.TLegend(0.51,0.83,0.88,0.90, "", "brNDC")
            leg.SetTextSize(0.0275)
            leg.AddEntry(fitCorrOrig, "Non-linear correction", "P")
            leg.AddEntry(fitCorr, "Mean TileCal residual", "P")
            leg.Draw()
                        
            self.c1.Print("%s/non_lin_fit.eps" % (self.dir))

        if self.useDB:
            self.db.closeDatabase()
        else:
            self.fout.close()
            
    
    def ProcessRegion(self, region):
        run = 200000
        ros = 0
        drawer = 0
        
        self.flt = self.blobReader.getDrawer(ros, drawer,(run, 0))
        
        if 'gain' not in region.GetHash():
            return
        
        for event in region.GetEvents():
            if event.run.runType == 'CIS' and 'scan' in event.data:

                scan = event.data['scan']
                [x, y, z, w] = region.GetNumber()

                for i in range(scan.GetN()):
                    if 'hi' in region.GetHash() and not 3.<scan.GetX()[i]<10.:
                        continue
                    if 'lo' in region.GetHash() and not 10.<scan.GetX()[i]<700.:
                        continue

                    charge = float(scan.GetY()[i]/event.data['calibration'])
                    fitCharge = self.flt.getCalib(z, w, charge, True)
                    injection = scan.GetX()[i]
                                     
                    nlcfactor = ((event.data['calibration']*fitCharge)
                                         /scan.GetY()[i])

                    if 'low' in region.GetHash():
                        self.fit.setdefault(injection, []).append(nlcfactor)

                if self.useDB:
                    self.fopen = False
                    if self.nlcwrite:
                        self.fout = open(os.path.join(getResultDirectory(),"data/nonLinCorr.txt"), "w")
                        self.fopen = True
                    maxidx = self.flt.getObjSizeUint32()
                    for idx in range(int(maxidx/2)):
                        a = self.flt.getData(0, 0, idx)
                        b = self.flt.getData(0, 0, idx+42)

                        if self.fopen:
                            self.fout.write("%f %f\n" % (a, b))
                        
                        self.fitOrig.setdefault(a, []).append(b)                        
                    if self.nlcwrite:
                        self.nlcwrite = self.useDB = False
                        self.fout.close()

                if not self.useDB:
                    self.fout = open(os.path.join(getResultDirectory(),"data/nonLinCorr.txt"), "r")
                    for line in self.fout:
                        x = float(line.split(' ')[0])
                        y = float(line.split(' ')[1])
                        
                        self.fitOrig.setdefault(x, []).append(y)
