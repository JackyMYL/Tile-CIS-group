from src.GenericWorker import *
from src.oscalls import *
from src.region import *
from src.run import *
from src.laser.toolbox import *
import src.MakeCanvas
import time
import numpy

# worker is called by getCoefficient.py in macros/mbias and executed after the worker GetLumiCoefficient
# it will collect the lumi coefficient information and plot vs eta
class PlotCoefficientVsEta(GenericWorker):
    "A plot Worker for Mbias: lumi coefficients vs eta"
    
    def __init__(self):
        self.dir = getPlotDirectory() #where to save the plots
        self.PMTool         = LaserTools()
            
        #will be histos later
        self.Acells = None
        self.BCcells = None
        self.Dcells = None
        self.Ecells = None 
        # used event data of coefficients
        self.Coeff = {} # dictionary
        self.CoeffError = {}
        

    def ProcessRegion(self, region):

        if region.GetEvents() == set():
            return
        
        for event in region.GetEvents():
            # and only look at laser runs, for now
            if event.run.runType == 'Las' or event.run.runType == 'Phys':
                # get information of coefficients
                    for key in list(event.data.keys()):
                        if "coeffErr" in key:
                            self.CoeffError[key] = event.data[key]
                        elif "coeff" in key and not "coeffErr" in key:
                            self.Coeff[key] = event.data[key]
                    
    def ProcessStop(self):
        if os.environ.get('TUCS'):
            ROOT.gROOT.LoadMacro("$TUCS/root_macros/AtlasStyle.C")
            ROOT.SetAtlasStyle()
            ROOT.gROOT.ForceStyle()

 
        c = ROOT.TCanvas('c','',800,600)
                
        #for histogram building
        self.Acells = ROOT.TH1F("Acells","Acells",32,-1.6,1.6 )
        self.BCcells = ROOT.TH1F("BCcells","BCcells",30,-1.5,1.5)
        self.Dcells = ROOT.TH1F("Dcells","Dcells",13 , -1.3,1.3)
        self.Ecells = ROOT.TH1F("Ecells","Ecells", 24,-1.2,1.2)

        
        for key in list(self.Coeff.keys()):
            print(key)
            # we need to map the cellname vs eta: we first convert the cellName back to Part_m_ch and then use map
            # here: get cellName --> need to extract from key name
            if 'coeff' in key and not '-' in key:
                detRegion = key.replace('coeff','')
            elif 'coeff-' in key:
                detRegion = key.replace('coeff-','')
                
            det_reg = self.PMTool.getRegionName(detRegion)
            Part = det_reg[0] #long barrel or extended barrel                                                                         
            PMTch = det_reg[1] #pmts belonging to cell, will use my own mapping for channel vs eta
            # using tower mapping from website: only using first pmt
            etamapLB = {0:0,1:0.05,2:0.05,5:0.15,6:0.15,9:0.25,11:0.25,13:0.2,15:0.35,16:0.35,19:0.45,21:0.45,23:0.55,24:0.4,27:0.55,33:0.65,29:0.65,35:0.75,36:0.85,39:0.75,41:0.6,42:0.85,45:0.95}
            # e cells added manually
            etamapEB = {0:1.05,12:1.05,1:1.15,13:1.15,2:0.85,4:0.95,6:1.15942,8:1.05869,10:1.25867,14:1.15803,16:1.00741,20:1.35795,22:1.25738,30:1.35678,31:1.45728,36:1.4562,37:1.20632,40:1.55665}
            
            # fill the four histograms, find eta first
            etaValue = -10.
            
            if Part[0]==0:
                etaValue= etamapLB[PMTch[0]]
            else:
                etaValue= etamapEB[PMTch[0]]

            #if c-side change sign of eta
            if "-" in key:
                etaValue=-1.*etaValue

            key_woMinus = key
            if "-" in key:
                key_woMinus = key.replace('-','')

            if "A" in detRegion:
                Acells.SetBinContent(Acells.FindBin(etaValue),self.Coeff[key])
                if etaValue<0.0:
                    Acells.SetBinError(Acells.FindBin(etaValue),self.CoeffError[key_woMinus+"Err-"])
                elif etaValue :
                    Acells.SetBinError(Acells.FindBin(etaValue),self.CoeffError[key_woMinus+"Err"])

            if "B" in detRegion or "C" in detRegion:
                BCcells.SetBinContent(BCcells.FindBin(etaValue),self.Coeff[key])
                if etaValue<0.0:
                    BCcells.SetBinError(BCcells.FindBin(etaValue),self.CoeffError[key_woMinus+"Err-"])
                else:
                    BCcells.SetBinError(BCcells.FindBin(etaValue),self.CoeffError[key_woMinus+"Err"])

            if "D" in detRegion:
                Dcells.SetBinContent(Dcells.FindBin(etaValue),self.Coeff[key])
                if etaValue<0.0:
                    Dcells.SetBinError(Dcells.FindBin(etaValue),self.CoeffError[key_woMinus+"Err-"])
                else:
                    Dcells.SetBinError(Dcells.FindBin(etaValue),self.CoeffError[key_woMinus+"Err"])

            if "E" in detRegion:
                Ecells.SetBinContent(Ecells.FindBin(etaValue),self.Coeff[key])
                if etaValue<0.0:
                    Ecells.SetBinError(Ecells.FindBin(etaValue),self.CoeffError[key_woMinus+"Err-"])
                else:
                    Ecells.SetBinError(Ecells.FindBin(etaValue),self.CoeffError[key_woMinus+"Err"])

#            maximum = 0.0
#            minimum = 10000.0

#            for j in range(len(PMTCurrent)): # find extreme values for building histograms
#                if PMTCurrent[j]>maximum:
#                    maximum = PMTCurrent[j]
#                if PMTCurrent[j]<minimum:
#                    minimum = PMTCurrent[j]                      
           
#            Maximum.append(maximum)
#            Minimum.append(minimum)                      
                                       
                
#        minimum = min(Minimum)
#        maximum = max(Maximum)

        # draw the histograms
        self.Acells.SetLineColor(kBlack)
        self.Acells.SetMarkerStyle(20)
        self.Acells.SetMarkerColor(kBlack)
        self.BCcells.SetLineColor(ROOT.kRed)
        self.BCcells.SetMarkerStyle(21)
        self.BCcells.SetMarkerColor(ROOT.kRed)
        self.Dcells.SetLineColor(kBlue)
        self.Dcells.SetMarkerStyle(22)
        self.Dcells.SetMarkerColor(kBlue)
        self.Ecells.SetLineColor(418)
        self.Ecells.SetMarkerStyle(23)
        self.Ecells.SetMarkerColor(418)
        

        self.Acells.Draw("ep")
        self.BCcells.Draw("epsame")
        self.Dcells.Draw("epsame")
        self.Ecells.Draw("epsame")

        self.Acells.GetXaxis().SetTitle("#eta_{cell}")
        self.Acells.GetYaxis().SetTitle("Coefficient [nA#times cm^{2}s]")
        self.Acells.GetYaxis().SetTitleOffset(1.2)

        legend = TLegend(0.5,0.6,0.7,0.8)
        legend.SetFillStyle(0)
        legend.SetFillColor(0)
        legend.SetBorderSize(0)
        legend.AddEntry(self.Acells,"A cells","ep")
        legend.AddEntry(self.BCcells,"BC cells", "ep")
        legend.AddEntry(self.Dcells,"D cells","ep")
        legend.AddEntry(self.Ecells,"E cells","ep")
        legend.Draw()


        c.Modified()
        c.Update()
           
        plot_name = "LumiCoeffVsEta_cells" 
        # save plot, several formats...
        c.Print("%s/%s.C" % (self.dir, plot_name))
        c.Print("%s/%s.eps" % (self.dir, plot_name))
        c.Print("%s/%s.png" % (self.dir, plot_name))

        del c, self.Coeff, self.CoeffError
        del self.Acells, self.BCcells, self.Dcells, self.Ecells

            
