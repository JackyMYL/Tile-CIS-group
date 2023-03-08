# Author: Bernardo Sotto-Maior Peralva <bernardo@cern.ch>
#
# March 04, 2010
#
from __future__ import print_function
from src.GenericWorker import *
from src.oscalls import *
import src.MakeCanvas
import datetime
import ROOT

class PrintTriggerBadChannels(GenericWorker):
    "Print Trigger Bad Channels with the 'print' data variable set"

    def __init__(self, zeroGainCutValue = 0.1, lowGainCutValue = 0.5):

        ROOT.gStyle.SetOptTitle(1)
        
        #create histograms
        self.histDeadTile = ROOT.TH2F("histDeadTile", "", 32, -16, 16, 64, 0, 64);
        self.histDeadL1Calo = ROOT.TH2F("histDeadL1Calo", "", 32, -16, 16, 64, 0, 64);
        self.histLowGainTile = ROOT.TH2F("histLowGainTile", "", 32, -16, 16, 64, 0, 64);
        self.histLowGainL1Calo = ROOT.TH2F("histLowGainL1Calo", "", 32, -16, 16, 64, 0, 64);
        self.histBadChan = ROOT.TH2F("histBadChan", "", 32, -16, 16, 64, 0, 64);
        self.histBadL1Calo = ROOT.TH2F("histBadL1Calo", "", 32, -16, 16, 64, 0, 64);
        self.histBadTile = ROOT.TH2F("histBadTile", "", 32, -16, 16, 64, 0, 64);
        self.histAllTile = ROOT.TH2F("histAllTile", "", 32, -16, 16, 64, 0, 64);
        self.histAllL1Calo = ROOT.TH2F("histAllL1Calo", "", 32, -16, 16, 64, 0, 64);
        
        self.lowGainCutValue =  lowGainCutValue
        self.zeroGainCutValue = zeroGainCutValue

        self.c1 = src.MakeCanvas.MakeCanvas()
        self.dir = getPlotDirectory()
        createDir('%s/print' % self.dir)
        self.dir = '%s/print' % self.dir

        self.subdirs = []

        #create grid
        
        self.grid = ROOT.TPad("histDeadTilegrid", "",0,0,1,1)

       #create root file
       #self.outfile = TFile(self.dir+"/output.root","recreate")



       #keep track of bad channels: eta, phi, pmt
        self.TileBad = []
        self.TileHalf = []
        self.L1CaloBad = []
        self.L1CaloHalf = []
        self.BadL1CaloGoodTile = []
       
    def ProcessStart(self):
        global run_list
        for run in run_list.getRunsOfType('L1Calo'):
            self.subdirs += [ self.dir + '/RunNumber%s' %run.runNumber ]
        for subdir in self.subdirs:
            createDir(subdir)
        if len(self.subdirs)==0:
            self.subdirs += [ self.dir ]
        
    def ProcessRegion(self, region):
        
        newevents = set()

        if 'gain' not in region.GetHash():
            for event in region.GetEvents():
                if event.run.runType != 'staging':
                    newevents.add(event)
            region.SetEvents(newevents)
            return
        
         # Either lowgain or highgain should work
        if 'lowgain' in region.GetHash():
            for event in region.GetEvents():
                [part, mod, chan, gain] = region.GetNumber()
                self.zeroGainCut = self.zeroGainCutValue*event.data['DACvalue']
                self.lowGainCut  = self.lowGainCutValue*event.data['DACvalue']

                #Get the tower number (1-9 for LB, 1-6 for EB) from the eta values
                if ((part == 1) or (part == 2)):   #LB modules first
                    tower = abs(event.data['ietaTile']) + 1
                if ((part == 3) or (part == 4)):   #EB modules first
                    if ( (event.data['ietaTile']==0 ) and (event.data['iphiTile']==0 ) ):
                        tower =0  # gap/crack NOT used for L1Calo
                    else:
                        tower = abs(event.data['ietaTile']) - 8
                
                
                if ((part == 1) or (part == 3)):
                    # Filling histograms for Tile bad channels
                    if (event.data['nEvtTile'] != 0):
                        self.histAllTile.Fill(event.data['ietaTile'], event.data['iphiTile'])
                        if (event.data['meanTile'] < self.zeroGainCut):
                            self.histDeadTile.Fill(event.data['ietaTile'], event.data['iphiTile'])
                            self.TileBad += [ [event.data['ietaTile'], event.data['iphiTile'], event.data['ipmtTile'] , part, mod, chan, tower] ]
                        if ((event.data['meanTile'] >= self.zeroGainCut) and (event.data['meanTile'] < self.lowGainCut)):
                            self.histLowGainTile.Fill(event.data['ietaTile'], event.data['iphiTile'])
                            self.TileHalf += [ [event.data['ietaTile'], event.data['iphiTile'], event.data['ipmtTile'] , part, mod, chan, tower ] ]
                    # Filling histograms for L1Calo bad channels
                    if (event.data['nEvtL1Calo'] != 0):
                        self.histAllL1Calo.Fill(event.data['ietaL1Calo'], event.data['iphiL1Calo'])
                        if (event.data['meanL1Calo'] < self.zeroGainCut):
                            self.histDeadL1Calo.Fill(event.data['ietaL1Calo'], event.data['iphiL1Calo'])
                            self.L1CaloBad += [ [event.data['ietaL1Calo'], event.data['iphiL1Calo'], event.data['ipmtL1Calo'], part, mod, chan, tower ]]
                            event.data['isNoGainL1'] = 1
                        if ((event.data['meanL1Calo'] >= self.zeroGainCut) and (event.data['meanL1Calo'] < self.lowGainCut)):
                            self.histLowGainL1Calo.Fill(event.data['ietaL1Calo'], event.data['iphiL1Calo'])
                            self.L1CaloHalf += [ [event.data['ietaL1Calo'], event.data['iphiL1Calo'], event.data['ipmtL1Calo'], part, mod, chan, tower ]]
                            event.data['isHalfGainL1'] = 1

                    # Filling histogram for Bad channels in both systems
                    if ((event.data['nEvtTile'] != 0) and (event.data['nEvtL1Calo'] != 0)):
                        if ((event.data['meanTile'] < self.lowGainCut) and (event.data['meanL1Calo'] < self.lowGainCut)):
                            self.histBadChan.Fill(event.data['ietaL1Calo'], event.data['iphiL1Calo'])

                    # Filling histogram for Bad channels in Tile and Good in L1Calo
                    if ((event.data['nEvtTile'] != 0) and (event.data['nEvtL1Calo'] != 0)):
                        if ((event.data['meanTile'] < self.lowGainCut) and (event.data['meanL1Calo'] >= self.lowGainCut)):
                            self.histBadTile.Fill(event.data['ietaL1Calo'], event.data['iphiL1Calo'])

                    # Filling histogram for Bad channels in L1Calo and Good in Tile
                    if ((event.data['nEvtTile'] != 0) and (event.data['nEvtL1Calo'] != 0)):
                        if ((event.data['meanTile'] >= self.lowGainCut) and (event.data['meanL1Calo'] < self.lowGainCut)):
                            self.histBadL1Calo.Fill(event.data['ietaL1Calo'], event.data['iphiL1Calo'])
                            self.BadL1CaloGoodTile += [ [event.data['ietaL1Calo'], event.data['iphiL1Calo'], event.data['ipmtL1Calo'], part, mod, chan, tower ] ]

                if ((part == 2) or (part == 4)):
                    # Filling histograms for Tile bad channels
                    if (event.data['nEvtTile'] != 0):
                        self.histAllTile.Fill(-event.data['ietaTile']-.1, event.data['iphiTile'])
                        if (event.data['meanTile'] < self.zeroGainCut):
                            self.histDeadTile.Fill(-event.data['ietaTile']-.1, event.data['iphiTile'])
                            self.TileBad += [ [ -event.data['ietaTile']-.1, event.data['iphiTile'], event.data['ipmtTile'] , part, mod, chan, tower] ]
                        if ((event.data['meanTile'] >= self.zeroGainCut) and (event.data['meanTile'] < self.lowGainCut)):
                            self.histLowGainTile.Fill(-event.data['ietaTile']-.1, event.data['iphiTile'])
                            self.TileHalf += [ [-event.data['ietaTile']-.1, event.data['iphiTile'], event.data['ipmtTile'] , part, mod, chan, tower ] ]
                       
                    # Filling histograms for L1Calo bad channels
                    if (event.data['nEvtL1Calo'] != 0):
                        self.histAllL1Calo.Fill(-event.data['ietaL1Calo']-.1, event.data['iphiL1Calo'])
                        if (event.data['meanL1Calo'] < self.zeroGainCut):
                            self.histDeadL1Calo.Fill(-event.data['ietaL1Calo']-.1, event.data['iphiL1Calo'])
                            self.L1CaloBad += [ [ -event.data['ietaL1Calo']-.1, event.data['iphiL1Calo'], event.data['ipmtL1Calo'], part, mod, chan, tower ]]
                            event.data['isNoGainL1'] = 1
                        if ((event.data['meanL1Calo'] >= self.zeroGainCut) and (event.data['meanL1Calo'] < self.lowGainCut)):
                            self.histLowGainL1Calo.Fill(-event.data['ietaL1Calo']-.1, event.data['iphiL1Calo'])
                            event.data['isHalfGainL1'] = 1
                            self.L1CaloHalf += [ [ -event.data['ietaL1Calo']-.1, event.data['iphiL1Calo'], event.data['ipmtL1Calo'], part, mod, chan, tower ]]
                    # Filling histogram for Bad channels in both systems
                    if ((event.data['nEvtTile'] != 0) and (event.data['nEvtL1Calo'] != 0)):
                        if ((event.data['meanTile'] < self.lowGainCut) and (event.data['meanL1Calo'] < self.lowGainCut)):
                            self.histBadChan.Fill(-event.data['ietaL1Calo']-.1, event.data['iphiL1Calo'])

                    # Filling histogram for Bad channels in Tile and Good in L1Calo
                    if ((event.data['nEvtTile'] != 0) and (event.data['nEvtL1Calo'] != 0)):
                        if ((event.data['meanTile'] < self.lowGainCut) and (event.data['meanL1Calo'] >= self.lowGainCut)):
                            self.histBadTile.Fill(-event.data['ietaL1Calo']-.1, event.data['iphiL1Calo'])

                    # Filling histogram for Bad channels in L1Calo and Good in Tile
                    if ((event.data['nEvtTile'] != 0) and (event.data['nEvtL1Calo'] != 0)):
                        if ((event.data['meanTile'] >= self.lowGainCut) and (event.data['meanL1Calo'] < self.lowGainCut)):
                            self.histBadL1Calo.Fill(-event.data['ietaL1Calo']-.1, event.data['iphiL1Calo'])
                            self.BadL1CaloGoodTile += [ [ -event.data['ietaL1Calo']-.1, event.data['iphiL1Calo'], event.data['ipmtL1Calo'], part, mod, chan, tower ] ]


    def ProcessStop(self):

        print("test print")
        title_size = 0.035
        colz_size = 0.03
        ### --- histDeadTile ---
        #self.outfile.cd()
        self.c1.cd()
        #self.histDeadTile.SetTitle()
        #self.histDeadTile.GetXaxis().SetNdivisions(32)
        #self.histDeadTile.GetYaxis().SetNdivisions(16)
        self.histDeadTile.Divide(self.histAllTile)

        #Readability
        self.histDeadTile.GetXaxis().SetNdivisions(8)
        self.histDeadTile.GetYaxis().SetNdivisions(16)
        self.grid.Draw()
        self.grid.cd()
        self.grid.SetGrid()
        self.grid.SetFillStyle(4000)

        self.histDeadTile.Draw("colz")


        self.histDeadTile.SetXTitle("iEta")
        self.histDeadTile.SetYTitle("Phi")
        self.histDeadTile.SetStats(0)
        src.MakeCanvas.myText(0.2,0.96,1,"Tile No Gain Channels (% per tower)", size=title_size)

        #self.axislabel = ROOT.TLatex(0.95,0.05,"Fraction of\nAll Modules")
        src.MakeCanvas.myText(x=0.86,y=0.05,color=ROOT.kBlack,text="Fraction of", size=colz_size)
        src.MakeCanvas.myText(x=0.86,y=0.029,color=ROOT.kBlack,text="Tower Modules", size=colz_size)
        #self.axislabel.SetNDC(1)
        #self.axislabel.SetTextFont(42)
        #self.axislabel.SetStatFontSize(0.01) # Check to see if this works
        #self.axislabel.Draw()


        self.c1.SetName("histDeadTile")
        self.c1.Print("%s/PMTscanResults.pdf(" % (self.subdirs[0]), "pdf")
        self.c1.Print("%s/TileNoGain.png" % (self.subdirs[0]), "png")

        #self.c1.Print("%s/PMTscanResults.ps(" % (self.subdirs[0]))
        #self.c1.Write()

        ### --- histDeadL1Calo ---
        self.c1.cd()
        self.histDeadL1Calo.Divide(self.histAllL1Calo)

        #Readability
        self.histDeadL1Calo.GetXaxis().SetNdivisions(8)
        self.histDeadL1Calo.GetYaxis().SetNdivisions(16)
        self.grid.Draw()
        self.grid.cd()
        self.grid.SetGrid()
        self.grid.SetFillStyle(4000)

        self.histDeadL1Calo.Draw("colz")
        self.histDeadL1Calo.SetXTitle("iEta")
        self.histDeadL1Calo.SetYTitle("Phi")
        self.histDeadL1Calo.SetStats(0)
        self.c1.SetName("histDeadL1Calo")
        src.MakeCanvas.myText(0.2,0.96,1,"L1Calo No Gain Channels (% per tower)", size=title_size)
        src.MakeCanvas.myText(x=0.86,y=0.05,color=ROOT.kBlack,text="Fraction of", size=colz_size)
        src.MakeCanvas.myText(x=0.86,y=0.029,color=ROOT.kBlack,text="Tower Modules", size=colz_size)
        self.c1.Print("%s/PMTscanResults.pdf" % (self.subdirs[0]), "pdf")
        self.c1.Print("%s/L1CaloNoGain.png" % (self.subdirs[0]), "png")

        #self.c1.Print("%s/PMTscanResults.ps" % (self.subdirs[0]))
        #self.c1.Write()

        ### --- histLowGainTile ---
        self.c1.cd()
        self.histLowGainTile.Divide(self.histAllTile)

        #Readability
        self.histLowGainTile.GetXaxis().SetNdivisions(8)
        self.histLowGainTile.GetYaxis().SetNdivisions(16)
        self.grid.Draw()
        self.grid.cd()
        self.grid.SetGrid()
        self.grid.SetFillStyle(4000)

        self.histLowGainTile.Draw("colz")
        self.histLowGainTile.SetXTitle("iEta")
        self.histLowGainTile.SetYTitle("Phi")
        self.histLowGainTile.SetStats(0)
        self.c1.SetName("histLowGainTile")
        src.MakeCanvas.myText(0.2,0.96,1,"Tile Half Gain Channels (% per tower)", size=title_size)
        src.MakeCanvas.myText(x=0.86,y=0.05,color=ROOT.kBlack,text="Fraction of", size=colz_size)
        src.MakeCanvas.myText(x=0.86,y=0.029,color=ROOT.kBlack,text="Tower Modules", size=colz_size)
        self.c1.Print("%s/PMTscanResults.pdf" % (self.subdirs[0]), "pdf")
        self.c1.Print("%s/TileHalfGain.png" % (self.subdirs[0]), "png")

        #self.c1.Print("%s/PMTscanResults.ps" % (self.subdirs[0]))
        #self.c1.Write()

        ### --- histLowGainL1Calo ---
        self.c1.cd()
        self.histLowGainL1Calo.Divide(self.histAllL1Calo)

        #Readability
        self.histLowGainL1Calo.GetXaxis().SetNdivisions(8)
        self.histLowGainL1Calo.GetYaxis().SetNdivisions(16)
        self.grid.Draw()
        self.grid.cd()
        self.grid.SetGrid()
        self.grid.SetFillStyle(4000)

        self.histLowGainL1Calo.Draw("colz")
        self.histLowGainL1Calo.SetXTitle("iEta")
        self.histLowGainL1Calo.SetYTitle("Phi")
        self.histLowGainL1Calo.SetStats(0)
        self.c1.SetName("histLowGainL1Calo")
        src.MakeCanvas.myText(0.2,0.96,1,"L1Calo Half Gain Channels (% per tower)", size=title_size)
        src.MakeCanvas.myText(x=0.86,y=0.05,color=ROOT.kBlack,text="Fraction of", size=colz_size)
        src.MakeCanvas.myText(x=0.86,y=0.029,color=ROOT.kBlack,text="Tower Modules", size=colz_size)
        self.c1.Print("%s/PMTscanResults.pdf" % (self.subdirs[0]), "pdf")
        self.c1.Print("%s/L1CaloHalfGain.png" % (self.subdirs[0]), "png")

        #self.c1.Print("%s/PMTscanResults.ps" % (self.subdirs[0]))
        #self.c1.Write()
  
        ### --- histBadChannel ---
        self.c1.cd()
        self.histBadChan.Divide(self.histAllTile)

        #Readability
        self.histBadChan.GetXaxis().SetNdivisions(8)
        self.histBadChan.GetYaxis().SetNdivisions(16)
        self.grid.Draw()
        self.grid.cd()
        self.grid.SetGrid()
        self.grid.SetFillStyle(4000)

        self.histBadChan.Draw("colz")
        self.histBadChan.SetXTitle("iEta")
        self.histBadChan.SetYTitle("Phi")
        self.histBadChan.SetStats(0)
        self.c1.SetName("histBadChan")
        src.MakeCanvas.myText(0.2,0.96,1,"Bad Channels in Tile and L1Calo (% per tower)", size=title_size)
        src.MakeCanvas.myText(x=0.86,y=0.05,color=ROOT.kBlack,text="Fraction of", size=colz_size)
        src.MakeCanvas.myText(x=0.86,y=0.029,color=ROOT.kBlack,text="Tower Modules", size=colz_size)
        self.c1.Print("%s/PMTscanResults.pdf" % (self.subdirs[0]), "pdf")
        self.c1.Print("%s/BadChannelBoth.png" % (self.subdirs[0]), "png")

        #self.c1.Print("%s/PMTscanResults.ps" % (self.subdirs[0]))
        #self.c1.Write()

        ### --- histBadTile ---
        self.c1.cd()
        self.histBadTile.Divide(self.histAllTile)

        #Readability
        self.histBadTile.GetXaxis().SetNdivisions(8)
        self.histBadTile.GetYaxis().SetNdivisions(16)
        self.grid.Draw()
        self.grid.cd()
        self.grid.SetGrid()
        self.grid.SetFillStyle(4000)

        self.histBadTile.Draw("colz")
        self.histBadTile.SetXTitle("iEta")
        self.histBadTile.SetYTitle("Phi")
        self.histBadTile.SetStats(0)
        self.c1.SetName("histBadTile")
        src.MakeCanvas.myText(0.2,0.96,1,"Bad Channels in Tile and NOT in L1Calo (% per tower)", size=title_size)
        src.MakeCanvas.myText(x=0.86,y=0.05,color=ROOT.kBlack,text="Fraction of", size=colz_size)
        src.MakeCanvas.myText(x=0.86,y=0.029,color=ROOT.kBlack,text="Tower Modules", size=colz_size)
        self.c1.Print("%s/PMTscanResults.pdf" % (self.subdirs[0]), "pdf")
        self.c1.Print("%s/BadChannelTile.png" % (self.subdirs[0]), "png")

        #self.c1.Print("%s/PMTscanResults.ps" % (self.subdirs[0]))
        #self.c1.Write()

        ### --- histBadL1Calo ---
        self.c1.cd()
        self.histBadL1Calo.Divide(self.histAllL1Calo)

        #Readability
        self.histBadL1Calo.GetXaxis().SetNdivisions(8)
        self.histBadL1Calo.GetYaxis().SetNdivisions(16)
        self.grid.Draw()
        self.grid.cd()
        self.grid.SetGrid()
        self.grid.SetFillStyle(4000)

        self.histBadL1Calo.Draw("colz")
        self.histBadL1Calo.SetXTitle("iEta")
        self.histBadL1Calo.SetYTitle("Phi")
        self.histBadL1Calo.SetStats(0)
        self.c1.SetName("histBadL1Calo")
        src.MakeCanvas.myText(0.2,0.96,1,"Bad Channels in L1Calo and NOT in Tile (% per tower)", size=title_size)
        src.MakeCanvas.myText(x=0.86,y=0.05,color=ROOT.kBlack,text="Fraction of", size=colz_size)
        src.MakeCanvas.myText(x=0.86,y=0.029,color=ROOT.kBlack,text="Tower Modules", size=colz_size)
        self.c1.Print("%s/PMTscanResults.pdf" % (self.subdirs[0]), "pdf")
        self.c1.Print("%s/BadChannelL1Calo.png" % (self.subdirs[0]), "png")

        #self.c1.Print("%s/PMTscanResults.ps" % (self.subdirs[0]))
        #self.c1.Write()

        ### --- histAllTile ---
        self.c1.cd()

        #Readability
        self.histAllTile.GetXaxis().SetNdivisions(8)
        self.histAllTile.GetYaxis().SetNdivisions(16)
        self.grid.Draw()
        self.grid.cd()
        self.grid.SetGrid()
        self.grid.SetFillStyle(4000)

        self.histAllTile.Draw("colz")
        self.histAllTile.SetXTitle("iEta")
        self.histAllTile.SetYTitle("Phi")
        self.histAllTile.SetStats(0)
        self.c1.SetName("histAllTile")
        src.MakeCanvas.myText(0.2,0.96,1,"Tile All Channels", size=title_size)
        src.MakeCanvas.myText(x=0.86,y=0.05,color=ROOT.kBlack,text="Total PMTs", size=colz_size)
        src.MakeCanvas.myText(x=0.86,y=0.029,color=ROOT.kBlack,text="in Tower", size=colz_size)
        self.c1.Print("%s/PMTscanResults.pdf" % (self.subdirs[0]), "pdf")
        self.c1.Print("%s/TileAllChannels.png" % (self.subdirs[0]), "png")

        #self.c1.Print("%s/PMTscanResults.ps" % (self.subdirs[0]))
        #self.c1.Write()

        ### --- histAllL1Calo ---
        self.c1.cd()

        #Readability
        self.histAllL1Calo.GetXaxis().SetNdivisions(8)
        self.histAllL1Calo.GetYaxis().SetNdivisions(16)
        self.grid.Draw()
        self.grid.cd()
        self.grid.SetGrid()
        self.grid.SetFillStyle(4000)

        self.histAllL1Calo.Draw("colz")
        self.histAllL1Calo.SetXTitle("iEta")
        self.histAllL1Calo.SetYTitle("Phi")
        self.histAllL1Calo.SetStats(0)
        self.c1.SetName("histAllL1Calo")
        src.MakeCanvas.myText(0.2,0.96,1,"L1Calo All Channels", size=title_size)
        src.MakeCanvas.myText(x=0.86,y=0.05,color=ROOT.kBlack,text="Total PMTs", size=colz_size)
        src.MakeCanvas.myText(x=0.86,y=0.029,color=ROOT.kBlack,text="in Tower", size=colz_size)
        self.c1.Print("%s/PMTscanResults.pdf)" % (self.subdirs[0]), "pdf")
        self.c1.Print("%s/L1CaloAllChannels.png" % (self.subdirs[0]), "png")
        #self.c1.Print("%s/PMTscanResults.ps)" % (self.subdirs[0]))
        #self.c1.Write()

        #self.outfile.Close()

        #write out bad channels
        textout = open(self.subdirs[0]+"/output.txt",'w')
        print("", file=textout)
        print("Cut values for low gain: %f , zero-gain: %f " %(self.lowGainCutValue, self.zeroGainCutValue), file=textout)
        print("--------------------------------------------", file=textout)
        print("Tile Bad Channels:", file=textout)
        print("->  \t ieta, \t phi, \t PMT, \t Tile: (Tower)", file=textout)
        for ti in self.TileBad:
            partition = ""
            if ti[3]==1:
                partition = "LBA"
            if ti[3]==2:
                partition = "LBC"
            if ti[3]==3:
                partition = "EBA"
            if ti[3]==4:
                partition = "EBC"
            print("-> \t %i, \t %i, \t %i, \t %s%i ch %i (T%i)" %(ti[0], ti[1], ti[2], partition, ti[4], ti[5], ti[6]), file=textout)
        print("", file=textout)
        print("--------------------------------------------", file=textout)
        print("Tile Half-Gain Channels: ", file=textout)
        print("->  \t ieta, \t phi, \t PMT, \t Tile: (Tower)", file=textout)
        for ti in self.TileHalf:
            partition = ""
            if ti[3]==1:
                partition = "LBA"
            if ti[3]==2:
                partition = "LBC"
            if ti[3]==3:
                partition = "EBA"
            if ti[3]==4:
                partition = "EBC"
            print("-> \t %i, \t %i, \t %i, \t %s%i ch %i (T%i)" %(ti[0], ti[1], ti[2], partition, ti[4], ti[5], ti[6]), file=textout)
        print("", file=textout)
        print("--------------------------------------------", file=textout)
        print("L1Calo Bad Channels: ", file=textout)
        print("->  \t ieta, \t phi, \t PMT, \t Tile: (Tower)", file=textout)
        for ti in self.L1CaloBad:
            partition = ""
            if ti[3]==1:
                partition = "LBA"
            if ti[3]==2:
                partition = "LBC"
            if ti[3]==3:
                partition = "EBA"
            if ti[3]==4:
                partition = "EBC"
            print("-> \t %i, \t %i, \t %i, \t %s%i ch %i (T%i)" %(ti[0], ti[1], ti[2], partition, ti[4], ti[5], ti[6]), file=textout)
        print("", file=textout)
        print("--------------------------------------------", file=textout)
        print("L1Calo Half-Gain Channels: ", file=textout)
        print("->  \t ieta, \t phi, \t PMT, \t Tile: (Tower)", file=textout)
        for ti in self.L1CaloHalf:
            partition = ""
            if ti[3]==1:
                partition = "LBA"
            if ti[3]==2:
                partition = "LBC"
            if ti[3]==3:
                partition = "EBA"
            if ti[3]==4:
                partition = "EBC"
            print("-> \t %i, \t %i, \t %i, \t %s%i ch %i (T%i)" %(ti[0], ti[1], ti[2], partition, ti[4], ti[5], ti[6]), file=textout)
        print("", file=textout)
        print("--------------------------------------------", file=textout)
        print("Bad L1Calo Channels (good in Tile): ", file=textout)
        print("->  \t ieta, \t phi, \t PMT, \t Tile: (Tower)", file=textout)
        for ti in self.BadL1CaloGoodTile:
            partition = ""
            if ti[3]==1:
                partition = "LBA"
            if ti[3]==2:
                partition = "LBC"
            if ti[3]==3:
                partition = "EBA"
            if ti[3]==4:
                partition = "EBC"
            print("-> \t %i, \t %i, \t %i, \t %s%i ch %i (T%i)" %(ti[0], ti[1], ti[2], partition, ti[4], ti[5], ti[6]), file=textout)
        textout.close()
