from src.GenericWorker import *
import src.MakeCanvas
import time
import numpy
import src.stats
import math
from src.region import *
from src.run import *
from src.laser.toolbox import *



# this worker reads a txt file created by the worker do_chan_plot_henric
# the txt contains info on time, variation, part, mod, ch, a scatter plot is created, the profile can be interpreted as average response variation
class GetLaserVariations(GenericWorker):
    "A plot worker for MBias"
    
    def __init__(self, cellname="E1"):
        self.dir = getPlotDirectory() #where to save the plots
 
        self.dir      =  os.path.join(src.oscalls.getPlotDirectory(),'mbias2015','ResponseVariation')
        self.PMTool         = LaserTools()
        #will be histos later
        # used events (one per run)
        self.eventsList = []
        #detector region
        #corresponding name
        self.regionName = None
        self.plot_name = None
        #self.Runnumber = None
        self.cellname = cellname

    def ProcessRegion(self, region):
        
        if region.GetEvents() == set():
            return
                
        Name = region.GetHash()
        self.regionName = Name[8:19] # shorter name without TILECAL_ in front
        
        for event in region.GetEvents():
            # and only look at laser runs, for now
            if event.run.runType == 'Las' or event.run.runType == 'Phys':
                if 'LumiBlock' in  list(event.run.data.keys()):# valid entries in run?? some files seem buggy for 2015  
                    self.eventsList.append(event)
                #print 'Run ', event.run.runNumber
                    
                    
    def ProcessStop(self):
        if os.environ.get('TUCS'):
            ROOT.gROOT.LoadMacro("$TUCS/root_macros/AtlasStyle.C")
            ROOT.SetAtlasStyle()
            ROOT.gROOT.ForceStyle()
                
        ROOT.gStyle.SetPalette(1)
        #self.c1.Clear()
        #self.c1.cd()
        # all cells

        RunNumber = None

        PMTCurrent = None
        LumiBlock = None



        det_reg = self.PMTool.getChannelsLaser(self.cellname)
        PartA = det_reg[0][0] #long barrel or extended barrel
        PartC = det_reg[0][1]
        PMTch = det_reg[1] #pmts belonging to cell
        print(PMTch)        
        # now: need to read in information from response variation
        FullInfo = [] # time, variation, eta, lumiCoeff
#        f.open('Mbias_variation_2015.txt','r')

        MbiasInfo = [] # same as in file: time, variation, name, mod

        GraphAll = TGraph()

        time = []# array('d',[])
        variation = []#array('d',[])
        
        print("reading file")
        D6variation = []

        with open('Laser_D6_variation_2016_25oct.txt') as f:
            data = f.readlines()
            for line in data:
                responseinfo = line.split() # this will have  date, variation, part, module, channel (EBA or EBC)
                if float(responseinfo[4])==37:
                    D6variation.append([float(responseinfo[0]), float(responseinfo[1]),responseinfo[2],float(responseinfo[3]),float(responseinfo[4])])

        with open('Laser_A13Ecells_variation_2016_25oct.txt') as f:
            data = f.readlines()
            for line in data:
                responseinfo = line.split() # this will have  date, variation, part, module, channel (EBA or EBC)
#                print responseinfo
                # we need to subtract the laser component from mbias first
                channel = int(responseinfo[4]) # extract channel number (actually PMT)
                module = int(responseinfo[3]) # module number
                if not channel in PMTch:
                    continue
                if self.cellname == "E1":
                    if "EBA" in responseinfo[2] and (module==28 or module==31 or module==33 or module==36 or module==7 or module==23 or module==42 or module==53 or module==6 or module==24 or module==43 or module==52):
                        continue
                    if "EBC" in responseinfo[2] and (module==28 or module==31 or module==33 or module==36 or module==7 or module==23 or module==42 or module==53 or module==6 or module==24 or module==43 or module==52 or module==27 or module==30 or module==34 or module==37):
                        continue
                for i in range(len(D6variation)):
                    if module==D6variation[i][3] and  float(responseinfo[0])==D6variation[i][0] and responseinfo[2]==D6variation[i][2]: #match information
                        print("here")
                        GraphAll.SetPoint(GraphAll.GetN(), float(responseinfo[0]), float(responseinfo[1])-D6variation[i][1])# just add all information together
                        break# match found
#                        time.append(float(responseinfo[0]))
 #                       variation.append(float(responseinfo[1]))

        print("done")

        # 2d histogram --> want to build profile
#        histo2d = ROOT.TH2F("histo2d", "histo2d", int(max(time)-min(time)) , min(time)-1, max(time)+1, 500,-0.20,0.2)
#        for i in range(len(time)):
#            histo2d.Fill(time[i],variation[i])

#        profile = histo2d.ProfileX()

#        chisto2d = TCanvas("chisto2d", 'chisto2d', 800, 600)
#        histo2d.Draw()
#        profile.SetMarkerColor(ROOT.kRed)
#        profile.SetLineColor(ROOT.kRed)
#        profile.Draw("same")


#        histo2d.GetXaxis().SetTimeDisplay(1);
#        histo2d.GetXaxis().SetNdivisions(-505);
#        histo2d.GetXaxis().SetTimeFormat("#splitline{%d/%m}{%Y}");
#        histo2d.GetXaxis().SetTimeOffset(0,"gmt");
#        histo2d.GetXaxis().SetTitle("Time")
#        histo2d.GetXaxis().SetTitleOffset(1.6)
#        histo2d.GetXaxis().SetLabelOffset(0.033)
#        histo2d.GetYaxis().SetTitle("Relative variation of %s cell response" % (self.cellname))


#        chisto2d.Print("%s/AllPointsVariationProfile_2015_%s.root" % (self.dir, self.cellname) )
#        chisto2d.Print("%s/AllPointsVariationProfile_2015_%s.eps" % (self.dir, self.cellname) )
#        chisto2d.Print("%s/AllPointsVariationProfile_2015_%s.C" % (self.dir, self.cellname) )


        GraphAll.SetMarkerSize(0.2)

        c = TCanvas("c","c", 800,600)
        GraphAll.Draw("ap")
        GraphAll.GetXaxis().SetTimeDisplay(1);
        GraphAll.GetXaxis().SetNdivisions(-505);
        GraphAll.GetXaxis().SetTimeFormat("#splitline{%d/%m}{%Y}");
        GraphAll.GetXaxis().SetTimeOffset(0,"gmt");
        GraphAll.GetXaxis().SetTitle("Time")
        GraphAll.GetXaxis().SetTitleOffset(1.6)
        GraphAll.GetXaxis().SetLabelOffset(0.033)
        GraphAll.GetYaxis().SetTitle("Relative variation of %s cell response" % (self.cellname))

        Leg1 = TLatex()
        Leg1.SetNDC()
        Leg1.SetTextAlign( 11 )
        Leg1.SetTextFont( 42 )
        Leg1.SetTextSize( 0.035 )
        Leg1.SetTextColor( 1 )
#        Leg1.DrawLatex(0.19,0.75, "#scale[1.2]{#sqrt{s}=13 TeV, 4.34 fb^{-1}}")

        Leg2 =  TLatex()
        Leg2.SetNDC()
        Leg2.SetTextAlign( 11 )
        Leg2.SetTextSize( 0.05 )
        Leg2.SetTextColor( 1 )
        Leg2.SetTextFont(42)
#        Leg2.DrawLatex(0.32,0.88," Internal")

#        Leg2.DrawLatex(0.19,0.82, "Tile Calorimeter")

        atlasLabel =  TLatex()
        atlasLabel.SetNDC()
        atlasLabel.SetTextFont( 72 )
        atlasLabel.SetTextColor( 1 )
        atlasLabel.SetTextSize( 0.05 )
#        atlasLabel.DrawLatex(0.19,0.88, "ATLAS")


#        c.Print("AllPointsVariation_2015_%s.root" % (self.dir, self.cellname) )
#        c.Print("AllPointsVariation_2015_%s.eps" % (self.dir, self.cellname) )
        c.Print("AllPointsVariationLaser_2016_%s.C" % (self.cellname) )
