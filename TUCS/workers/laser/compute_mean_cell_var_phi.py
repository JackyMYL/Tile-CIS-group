############################################################
#
# compute_mean_cell_var_phi.py
#
############################################################
#
# Author: D. Boumediene, M. Marjanovic
# Compute deviations averaged in each Phi bins corresponding to module azimutal coverage
# Results are displayed seperately for LB (average over a long module)
# and EB (average over A and C sides)
# Average is done over eta bins either using a Gaussian fit (UseGaus=True)
# or simple average (default)
# Channels with DQ (masked, severe corruptions) flags, low amplitude, HV<5V are ignored
# outputs are saved in the hardcoded path results/
#############################################################

from src.GenericWorker import *
from src.laser.toolbox import *
from src.oscalls import *
from array import array

import os.path

if os.path.isfile('./root_macros/AtlasStyle.C'):
    ROOT.gROOT.LoadMacro("./root_macros/AtlasStyle.C")
else:
    ROOT.gROOT.LoadMacro("$TUCS/root_macros/AtlasStyle.C")



import src.MakeCanvas
import time
import math


class compute_mean_cell_var_phi(GenericWorker):
    "Produce summary plots"

    def ProcessStart(self):
        ROOT.SetAtlasStyle()
        print("Using run #", self.runNumber," for phi cell map. ")
        

    def __init__(self, limit=2, gain=0,runNumber=0, UseGaus=False):

        ROOT.gStyle.SetLineColor(0);
        self.limit = limit
        self.runNumber=runNumber
        graph_lim  = 5*self.limit
        graph_lim_calib_up = 0
        graph_lim_calib_down = 0

        self.UseGaus = False

        self.gain  = gain

        if self.gain == 0:
            self.gname = 'lg'
            graph_lim_calib_up = 1
            graph_lim_calib_down = -0.05
        if self.gain == 1:
            self.gname = 'hg'
            graph_lim_calib_up = 0.01
            graph_lim_calib_down = -0.002
        if self.gain == 2:
            self.gname = 'global'
            
        self.dir    = getPlotDirectory()
        self.PMTool = LaserTools()

        # Create the different canvas

        self.channel = src.MakeCanvas.MakeCanvas()
            
        self.channel.SetFrameFillColor(0)
        self.channel.SetFrameLineColor(0)
        self.channel.SetFillColor(0);
        self.channel.SetBorderMode(0);
        self.channel.SetLogy(0); 


        self.cnv = src.MakeCanvas.MakeCanvas()
        self.cnv.SetFillColor(0);
        self.cnv.SetBorderMode(0);
        self.cnv.SetLogy(0);             

        # Then create the different histograms

        self.chans = [] # histo of cells
        
        for i in range(64): #A Cells

            name_h = "cell_deviation_a_m%d" % (i)
            self.chans.append(ROOT.TH1F(name_h, '', 100, -12, +12))

        for i in range(64): #BC Cells

            name_h = "cell_deviation_BC_m%d" % (i)
            self.chans.append(ROOT.TH1F(name_h, '', 100, -12, +12))

        for i in range(64): #D Cells

            name_h = "cell_deviation_d_m%d" % (i)
            self.chans.append(ROOT.TH1F(name_h, '', 100, -12, +12))

        for i in range(64): #EA Cells

            name_h = "cell_deviation_ea_m%d" % (i)
            self.chans.append(ROOT.TH1F(name_h, '', 100, -12, +12))

        for i in range(64): #EB Cells + C10

            name_h = "cell_deviation_eb_m%d" % (i)
            self.chans.append(ROOT.TH1F(name_h, '', 100, -12, +12))

        for i in range(64): #ED Cells

            name_h = "cell_deviation_ed_m%d" % (i)
            self.chans.append(ROOT.TH1F(name_h, '', 100, -12, +12))

        for i in range(64): #gap E Cells

            name_h = "cell_deviation_egap1 %d" % (i)
            self.chans.append(ROOT.TH1F(name_h, '', 100, -40, +40))

        for i in range(64): #gap E Cells

            name_h = "cell_deviation_egap2 %d" % (i)
            self.chans.append(ROOT.TH1F(name_h, '', 100, -40, +40))
        for i in range(64): #gap E Cells

            name_h = "cell_deviation_egap3 %d" % (i)
            self.chans.append(ROOT.TH1F(name_h, '', 100, -40, +40))

        for i in range(64): #gap E Cells

            name_h = "cell_deviation_egap4 %d" % (i)
            self.chans.append(ROOT.TH1F(name_h, '', 100, -40, +40))

            
        self.fib = ROOT.TH1F('fiber variation'  , '', 100, -graph_lim, graph_lim)




    def ProcessStop(self):
        
        ############# LB
        rmax=1.0
        maxdriftlb=0.2 # will be used for automatic color scale
        maxdrifteb=0.2
        maxdriftecells=0.2


        self.pol_his = ROOT.TH2D("polarHist", "polarHist", 64, 0., 2.0*3.1415926, 3, 0.35, rmax); # the polar data. X maps to theta, Y maps to R
        self.his_A = ROOT.TH1D("HistA", "HistA", 64, 0., 2.0*3.1415926); # A cells LB
        self.his_B = ROOT.TH1D("HistB", "HistB", 64, 0., 2.0*3.1415926); # B cells LB
        self.his_D = ROOT.TH1D("HistD", "HistD", 64, 0., 2.0*3.1415926); # D cells LB

        self.his_EA = ROOT.TH1D("HistEA", "HistEA", 64, 0., 2.0*3.1415926); # A cells LB
        self.his_EB = ROOT.TH1D("HistEB", "HistEB", 64, 0., 2.0*3.1415926); # B cells LB
        self.his_ED = ROOT.TH1D("HistED", "HistED", 64, 0., 2.0*3.1415926); # D cells LB

        self.his_E1 = ROOT.TH1D("HistE1", "HistE1", 64, 0., 2.0*3.1415926); # E1 cells
        self.his_E2 = ROOT.TH1D("HistE2", "HistE2", 64, 0., 2.0*3.1415926); # E2 cells
        self.his_E3 = ROOT.TH1D("HistE3", "HistE3", 64, 0., 2.0*3.1415926); # E3 cells
        self.his_E4 = ROOT.TH1D("HistE4", "HistE4", 64, 0., 2.0*3.1415926); # E4 cells

        for b in range(self.pol_his.GetNbinsX()):
            theta = self.pol_his.GetXaxis().GetBinCenter(b)
            for c in range(self.pol_his.GetNbinsY()):
                r = self.pol_his.GetYaxis().GetBinCenter(c)
                    ## histo number
                h = b+(c*64)
                #print ' module #', b, 'layer ',c,' histo number ',h

                cvar=0.0
                ecvar=0.0
                if (self.chans[h].GetEntries() != 0 and self.chans[h].GetMean()!=0):
                    if (h < 64+64+64):
                        self.chans[h].Fit("gaus","Q","",-8.5,+2.5)
                    else:
                        self.chans[h].Fit("gaus","Q0","",-25.5,+25.5)

                    self.ch_fit= ROOT.TVirtualFitter.Fitter(self.chans[h])
            
                    if ((abs(self.ch_fit.GetParameter(1)-self.chans[h].GetMean())>0.4) or (self.UseGaus)):
                        cvar=self.chans[h].GetMean()
                    else:
                        cvar=self.ch_fit.GetParameter(1)
                    ecvar=self.ch_fit.GetParError(1)
                    if (ecvar>10 and self.chans[h].GetEntries()>0):
                        ecvar=self.chans[h].GetRMS()/sqrt(self.chans[h].GetEntries())

#                if (cvar == 0):
#                    cvar=1                    
                print(' -- Module ',h,' mean deviation = ',self.chans[h].GetMean(),'% Fitted mean ', self.ch_fit.GetParameter(1),' % (will use: ',cvar,') ',self.chans[h].GetEntries(),' entries..')
                if (cvar > 1 or cvar <-10):
                    print('WARNING WARNING, printed a control plot for module #', b, 'layer ',c,' histo number ',h)
                    self.c1 = src.MakeCanvas.MakeCanvas()
                    self.c1.SetFillColor(0)
                    self.c1.SetBorderMode(0)                    
                    self.c1.cd()
                    self.chans[h].Draw()
                    self.c1.Print("%s/%d.eps" % (self.dir,h))
                    self.c1.Delete()

                # some special cases may need to use the average if non-gaussian behavior
                if (b==60):
                    cvar=self.chans[59+(64*c)].GetMean()

                if (c==0):
                    self.his_A.SetBinContent(b+1,cvar)
                    self.his_A.SetBinError(b+1,ecvar)
                if (c==1):
                    self.his_B.SetBinContent(b+1,cvar)
                    self.his_B.SetBinError(b+1,ecvar)
                if (c==2):
                    self.his_D.SetBinContent(b+1,cvar)
                    self.his_D.SetBinError(b+1,ecvar)


                self.pol_his.SetBinContent(b+1, c+1, cvar)
                if (abs(cvar) > maxdriftlb):
                    maxdriftlb = abs(cvar)+0.1


        self.dummy_his = ROOT.TH2D("dummy", "histo title", 100, -rmax, rmax, 100, -rmax, rmax)


        ############# EB
        rmax=1.0

        self.pol_his_eb = ROOT.TH2D("polarHistEB", "polarHistEB", 64, 0., 2.0*3.1415926, 3, 0.35, rmax); # the polar data. X maps to theta, Y maps to R

        for b in range(self.pol_his_eb.GetNbinsX()):
            theta = self.pol_his_eb.GetXaxis().GetBinCenter(b)
            for c in range(self.pol_his_eb.GetNbinsY()):
                r = self.pol_his_eb.GetYaxis().GetBinCenter(c)
                    ## histo number
                h = b+(c*64)+(64+64+64)
                ## print ' module #', b, 'layer ',c,' histo number ',h

                cvar=0.0
                if (self.chans[h].GetEntries() != 0 and self.chans[h].GetMean()!=0):
                    if (h < 64):
                        self.chans[h].Fit("gaus","Q0","",-8.5,+8.5)
                    elif (h>64+64+64+64):
                        self.chans[h].Fit("gaus","Q0","",-25.5,+25.5)
                    else:
                        self.chans[h].Fit("gaus","Q0","",-8.5,+8.5)

                    self.ch_fit= ROOT.TVirtualFitter.Fitter(self.chans[h])
            
                    if (abs(self.ch_fit.GetParameter(1)-self.chans[h].GetMean())>0.4):
                        cvar=self.chans[h].GetMean()
                    else:
                        cvar=self.ch_fit.GetParameter(1)

                    ecvar=self.ch_fit.GetParError(1)
                    if (self.chans[h].GetEntries()>0):
                        ecvar=self.chans[h].GetRMS()/sqrt(self.chans[h].GetEntries())
                        cvar=self.chans[h].GetMean()
                    else:
                        cvar=0
                        ecvar=0

                if (c==0):
                    self.his_EA.SetBinContent(b+1,cvar)
                    self.his_EA.SetBinError(b+1,ecvar)
                if (c==1):
                    self.his_EB.SetBinContent(b+1,cvar)
                    self.his_EB.SetBinError(b+1,ecvar)
                if (c==2):
                    self.his_ED.SetBinContent(b+1,cvar)
                    self.his_ED.SetBinError(b+1,ecvar)
                

                if (cvar > 1 or cvar <-10):
                    print('WARNING WARNING, printed a control plot for module #', b, 'layer ',c,' histo number ',h)
                    self.c1 = src.MakeCanvas.MakeCanvas()
                    self.c1.SetFillColor(0)
                    self.c1.SetBorderMode(0)                    
                    self.c1.cd()
                    self.chans[h].Draw()
                    self.c1.Print("%s/%d.eps" % (self.dir,h))
                    self.c1.Delete()

                self.pol_his_eb.SetBinContent(b+1, c+1, cvar)
                if (abs(cvar) > maxdrifteb):
                    maxdrifteb = abs(cvar)+0.1
                #print ' self.pol_his_eb.SetBinContent(',b+1,', ',c,', ',cvar,')'

        ############# Ecells
        rmax=1.0

        self.pol_his_Ecells = ROOT.TH2D("polarHistEcells", "polarHistEcells", 64, 0., 2.0*3.1415926, 4, 0.35, rmax)

        for b in range(self.pol_his_Ecells.GetNbinsX()):
            theta = self.pol_his_Ecells.GetXaxis().GetBinCenter(b)
            for c in range(self.pol_his_Ecells.GetNbinsY()):
                r = self.pol_his_Ecells.GetYaxis().GetBinCenter(c)
                    ## histo number
                h = b+(c*64)+(64+64+64+64+64+64)
                ## print ' module #', b, 'layer ',c,' histo number ',h

                cvar=0.0

                if (self.chans[h].GetEntries() != 0 and self.chans[h].GetMean()!=0):

                #    ecvar=self.ch_fit.GetParError(1)
                    if (self.chans[h].GetEntries()>0):
                        ecvar=self.chans[h].GetRMS()/sqrt(self.chans[h].GetEntries())
                        cvar=self.chans[h].GetMean()
                        for i in range (self.chans[h].GetSize()):
                            if  self.chans[h].GetEntries() > 2. and (self.chans[h])[i] > 0.:
                                print('!!!!!!!!!!!!!!!!!!!', 'number of entries ', self.chans[h].GetEntries())
                                print('bin i ', i, (self.chans[h])[i], (self.chans[h]).GetXaxis().GetBinCenter(i))
                                print('Ecells -- Module ',h,' mean deviation = ',self.chans[h].GetMean(),'% Fitted mean ', self.ch_fit.GetParameter(1),' % (will use: ',cvar,') ',self.chans[h].GetEntries(),' entries..')

                else: # (self.chans[h].GetEntries() == 0):
                    cvar=-21.

                if (c==0):
                    self.his_E4.SetBinContent(b+1,cvar)
                    self.his_E4.SetBinError(b+1,ecvar)
                if (c==1):
                    self.his_E3.SetBinContent(b+1,cvar)
                    self.his_E3.SetBinError(b+1,ecvar)
                if (c==2):
                    self.his_E2.SetBinContent(b+1,cvar)
                    self.his_E2.SetBinError(b+1,ecvar)
                if (c==3):

                    self.his_E1.SetBinContent(b+1,cvar)
                    self.his_E1.SetBinError(b+1,ecvar)

                if (cvar > 1 or cvar <-10):
                    print('WARNING WARNING, printed a control plot for module #', b, 'layer ',c,' histo number ',h)
                    self.c1 = src.MakeCanvas.MakeCanvas()
                    self.c1.SetFillColor(0)
                    self.c1.SetBorderMode(0)                    
                    self.c1.cd()
                    self.chans[h].Draw()
                    self.c1.Print("%s/%d.eps" % (self.dir,h))
                    self.c1.Delete()

                self.pol_his_Ecells.SetBinContent(b+1, c+1, cvar)
                if (abs(cvar) > maxdriftecells):
                    maxdriftecells = abs(cvar)+0.1


        self.dummy_his = ROOT.TH2D("dummy", "histo title", 100, -rmax, rmax, 100, -rmax, rmax)


        self.canvPhi = ROOT.TCanvas("canvPhi","canvPhi",0,0,600,600)
        self.padPhi = self.canvPhi.cd()
        

        NRGBs = 5;
        NCont = 255;



        stops = [ 0.00, 0.25, 0.50, 0.75, 1.00 ]
        red   = [ 1.00, 1.00, 0.12, 0.00, 0.00 ]
        green = [ 0.00, 0.81, 1.00, 0.35, 0.00 ]
        blue  = [ 0.00, 0.00, 0.30, 0.65, 1.00 ]



        stopsArray = array('d', stops)
        redArray   = array('d', red)
        greenArray = array('d', green)
        blueArray  = array('d', blue)

        ROOT.TColor.CreateGradientColorTable(NRGBs, stopsArray, redArray, greenArray, blueArray, NCont)

        ROOT.gStyle.SetNumberContours(NCont)
        ROOT.gStyle.SetOptStat(0)
        ROOT.gStyle.SetOptTitle(0)

        ### DRAW LB

        self.channel.cd()

        self.dummy_his.GetZaxis().SetRangeUser(-1.0*maxdriftlb,maxdriftlb)

        #self.dummy_his.GetZaxis().SetTitleOffset(1.6)
        #self.dummy_his.SetZTitle("%")
        self.dummy_his.GetYaxis().SetLabelOffset(999);
        self.dummy_his.GetYaxis().SetLabelSize(0);
        self.dummy_his.GetXaxis().SetLabelOffset(999);
        self.dummy_his.GetXaxis().SetLabelSize(0);
        self.dummy_his.GetXaxis().SetAxisColor(0);
        self.dummy_his.GetYaxis().SetAxisColor(0);

        self.dummy_his.Draw("COL") ## draw the dummy histogram first

        print(" Range in LB: ",-1.0*maxdriftlb,'% to ',maxdriftlb)
        

        self.pol_his.GetZaxis().SetRangeUser(-1.0*maxdriftlb,maxdriftlb)
#        self.pol_his.GetZaxis().SetRangeUser(-1.0*maxdrifteb,maxdrifteb)
        self.pol_his.GetYaxis().SetLabelOffset(999);
        self.pol_his.GetYaxis().SetLabelSize(0);
        self.pol_his.GetZaxis().SetTitleOffset(0.6)
        self.pol_his.SetZTitle("PMT gain variation [%]")
        self.pol_his.Draw("COL POLZ SAME") ##  now draw the data histogram. If it has "SAME" it will use the first histogram ranges
        
        ROOT.gPad.Update()
        self.tpad = self.channel.GetPad(0)
#        tpad.SetLeftMargin(0.5)
        self.tpad.SetLeftMargin(0.15)
        self.tpad.SetRightMargin(0.15)
        self.tpad.SetBottomMargin(0.05)
        self.tpad.SetTopMargin(0.05)

        palette = self.pol_his.FindObject("palette")
        palette.SetX1NDC(0.86)
        palette.SetX2NDC(0.91)
        palette.SetY1NDC(0.05)
        palette.SetY2NDC(0.95)

        gPad.Modified()
        gPad.Update()
       
        l = ROOT.TLatex()
        l.SetNDC()
        l.SetTextFont(66)
#        l.DrawLatex(0.19,0.16,"LASER LB")
        
        l2 = ROOT.TLatex()
        l2.SetNDC()
#        l2.DrawLatex(0.19,0.16,"Laser LB")
#        l2.DrawLatex(0.045,0.90,"#bf{#it{ATLAS}} Internal")
        l2.DrawLatex(0.045,0.90,"#bf{#it{ATLAS}} Preliminary")
        l2.DrawLatex(0.045,0.85,"Tile calorimeter")
        l2.SetTextSize(0.04)
        l2.DrawLatex(0.045,0.80,"Long Barrel")
        l2.DrawLatex(0.045,0.15,"Run 311556")
        l2.DrawLatex(0.045,0.10,"2016-10-27 08:30:41")

        self.arrowX = ROOT.TArrow(0.,0.,0.25,0.,0.01)
        self.arrowX.SetLineWidth(2)
        self.arrowX.SetLineColor(kBlack)
        #self.arrowX.SetTitle("x")
        self.arrowX.Draw()

        self.arrowY = ROOT.TArrow(0.,0.,0.,0.25,0.01)
        self.arrowY.SetLineWidth(2)
        self.arrowY.SetLineColor(kBlack)
        #self.arrowY.SetTitle("y")
        self.arrowY.Draw()

        l2.SetTextSize(0.030)
        l2.DrawLatex(0.575,0.47,"x")
        l2.DrawLatex(0.48,0.59,"y")



        self.ellipse1 = ROOT.TEllipse(-1.12, -.65, 1.25, 1.25, 82, 98)
        self.ellipse1.SetLineColor(kBlack)
        self.ellipse1.SetLineWidth(2)
        self.ellipse1.SetNoEdges(kTRUE)
        self.ellipse1.Draw()

        self.ellipse2 = ROOT.TEllipse(-1.12, -.65, 0.945, 0.945, 82, 98)
        self.ellipse2.SetLineColor(kBlack)
        self.ellipse2.SetLineWidth(2)
        self.ellipse2.SetNoEdges(kTRUE)
        self.ellipse2.Draw("same")

        self.ellipse3 = ROOT.TEllipse(-1.12, -.65, .638, .638, 82, 98)
        self.ellipse3.SetLineColor(kBlack)
        self.ellipse3.SetLineWidth(2)
        self.ellipse3.SetNoEdges(kTRUE)
        self.ellipse3.Draw("same")

        self.ellipse4 = ROOT.TEllipse(-1.12, -.65, .33, .33, 82, 98)
        self.ellipse4.SetLineColor(kBlack)
        self.ellipse4.SetLineWidth(2)
        self.ellipse4.SetNoEdges(kTRUE)
        self.ellipse4.Draw("same")

        self.lineE1 = ROOT.TLine(-1.165, -.32, -1.295, .585)
        self.lineE1.SetLineColor(kBlack)
        self.lineE1.SetLineWidth(2)
        self.lineE1.Draw()
        
        self.lineE2 = ROOT.TLine(-1.075, -.32, -.945, .585)
        self.lineE2.SetLineColor(kBlack)
        self.lineE2.SetLineWidth(2)
        self.lineE2.Draw()

        l2.SetTextSize(0.04)
        l2.DrawLatex(0.098,0.42,"A")
        l2.DrawLatex(0.088,0.55,"BC")
        l2.DrawLatex(0.098,0.68,"D")

        self.channel.Modified()                  
        self.channel.Print("results/tile_laser_lb_map_phi_public.png")
        self.channel.Print("results/tile_laser_lb_map_phi_public.C")
        self.channel.Print("results/tile_laser_lb_map_phi_public.eps")
        self.channel.Print("results/tile_laser_lb_map_phi_public.root")

        ### DRAW EB

        self.channel.cd()

        self.dummy_his.GetZaxis().SetRangeUser(-1.0*maxdrifteb,maxdrifteb)
        self.dummy_his.GetYaxis().SetLabelOffset(999);
        self.dummy_his.GetYaxis().SetLabelSize(0);
        self.dummy_his.GetXaxis().SetLabelOffset(999);
        self.dummy_his.GetXaxis().SetLabelSize(0);
        self.dummy_his.GetXaxis().SetAxisColor(0);
        self.dummy_his.GetYaxis().SetAxisColor(0);

        self.dummy_his.Draw("COL") ## draw the dummy histogram first

        self.pol_his_eb.GetZaxis().SetRangeUser(-1.0*maxdrifteb,maxdrifteb)
        self.pol_his_eb.GetYaxis().SetLabelOffset(999);
        self.pol_his_eb.GetYaxis().SetLabelSize(0);
        self.pol_his_eb.GetZaxis().SetTitleOffset(0.6)
        self.pol_his_eb.SetZTitle("PMT gain variation [%]")
        self.pol_his_eb.Draw("COL POLZ SAME") ##  now draw the data histogram. If it has "SAME" it will use the first histogram ranges        
        ROOT.gPad.Update()
        self.tpad = self.channel.GetPad(0)
#        tpad.SetLeftMargin(0.5)
        self.tpad.SetLeftMargin(0.15)
        self.tpad.SetRightMargin(0.15)
        self.tpad.SetBottomMargin(0.05)
        self.tpad.SetTopMargin(0.05)

        palette = self.pol_his.FindObject("palette")
        palette.SetX1NDC(0.86)
        palette.SetX2NDC(0.91)
        palette.SetY1NDC(0.05)
        palette.SetY2NDC(0.95)

        gPad.Modified()
        gPad.Update()

        l = ROOT.TLatex()
        l.SetNDC()
        l.SetTextFont(66)
#        l.DrawLatex(0.19,0.16,"LASER LB")
        
        l2 = ROOT.TLatex()
        l2.SetNDC()
#        l2.DrawLatex(0.19,0.16,"Laser LB")
#        l2.DrawLatex(0.045,0.90,"#bf{#it{ATLAS}} Internal")
        l2.DrawLatex(0.045,0.90,"#bf{#it{ATLAS}} Preliminary")
        l2.DrawLatex(0.045,0.85,"Tile calorimeter")
        l2.SetTextSize(0.04)
        l2.DrawLatex(0.045,0.80,"Extended Barrel")
        l2.DrawLatex(0.045,0.15,"Run 311556")
        l2.DrawLatex(0.045,0.10,"2016-10-27 08:30:41")

        l2.SetTextSize(0.030)
        l2.DrawLatex(0.575,0.47,"x")
        l2.DrawLatex(0.48,0.59,"y")

        self.arrowX = ROOT.TArrow(0.,0.,0.25,0.,0.01)
        self.arrowX.SetLineWidth(2)
        self.arrowX.SetLineColor(kBlack)
        #self.arrowX.SetTitle("x")
        self.arrowX.Draw()

        self.arrowY = ROOT.TArrow(0.,0.,0.,0.25,0.01)
        self.arrowY.SetLineWidth(2)
        self.arrowY.SetLineColor(kBlack)
        #self.arrowY.SetTitle("y")
        self.arrowY.Draw()


        self.ellipse1 = ROOT.TEllipse(-1.12, -.65, 1.25, 1.25, 82, 98)
        self.ellipse1.SetLineColor(kBlack)
        self.ellipse1.SetLineWidth(2)
        self.ellipse1.SetNoEdges(kTRUE)
        self.ellipse1.Draw()

        self.ellipse2 = ROOT.TEllipse(-1.12, -.65, 0.945, 0.945, 82, 98)
        self.ellipse2.SetLineColor(kBlack)
        self.ellipse2.SetLineWidth(2)
        self.ellipse2.SetNoEdges(kTRUE)
        self.ellipse2.Draw("same")

        self.ellipse3 = ROOT.TEllipse(-1.12, -.65, .638, .638, 82, 98)
        self.ellipse3.SetLineColor(kBlack)
        self.ellipse3.SetLineWidth(2)
        self.ellipse3.SetNoEdges(kTRUE)
        self.ellipse3.Draw("same")

        self.ellipse4 = ROOT.TEllipse(-1.12, -.65, .33, .33, 82, 98)
        self.ellipse4.SetLineColor(kBlack)
        self.ellipse4.SetLineWidth(2)
        self.ellipse4.SetNoEdges(kTRUE)
        self.ellipse4.Draw("same")

        self.lineE1 = ROOT.TLine(-1.165, -.32, -1.295, .585)
        self.lineE1.SetLineColor(kBlack)
        self.lineE1.SetLineWidth(2)
        self.lineE1.Draw()
        
        self.lineE2 = ROOT.TLine(-1.075, -.32, -.945, .585)
        self.lineE2.SetLineColor(kBlack)
        self.lineE2.SetLineWidth(2)
        self.lineE2.Draw()

        l2.SetTextSize(0.04)
        l2.DrawLatex(0.098,0.42,"A")
        l2.DrawLatex(0.088,0.55,"BC")
        l2.DrawLatex(0.098,0.68,"D")

        self.channel.Modified()                  
        self.channel.Print("results/tile_laser_eb_map_phi_public.png")
        self.channel.Print("results/tile_laser_eb_map_phi_public.eps")
        self.channel.Print("results/tile_laser_eb_map_phi_public.C")
        self.channel.Print("results/tile_laser_eb_map_phi_public.root")
        self.channel.Delete()

        ### DRAW Ecells

        self.channel.cd()

#        self.dummy_his.GetZaxis().SetRangeUser(-1.0*maxdriftecells,maxdriftecells)
        self.dummy_his.GetZaxis().SetRangeUser(-1.0*19.9,19.9)
        self.dummy_his.GetYaxis().SetLabelOffset(999);
        self.dummy_his.GetYaxis().SetLabelSize(0);
        self.dummy_his.GetXaxis().SetLabelOffset(999);
        self.dummy_his.GetXaxis().SetLabelSize(0);
        self.dummy_his.GetXaxis().SetAxisColor(0);
        self.dummy_his.GetYaxis().SetAxisColor(0);

        self.dummy_his.Draw("COL") ## draw the dummy histogram first

#        self.pol_his_Ecells.GetZaxis().SetRangeUser(-1.0*maxdriftecells,maxdriftecells)
        self.pol_his_Ecells.GetZaxis().SetRangeUser(-1.0*19.9,19.9)
        self.pol_his_Ecells.GetYaxis().SetLabelOffset(999);
        self.pol_his_Ecells.GetYaxis().SetLabelSize(0);
        self.pol_his_Ecells.GetZaxis().SetTitleOffset(0.8)
        self.pol_his_Ecells.SetZTitle("PMT gain variation [%]")
        self.pol_his_Ecells.Draw("COL POLZ SAME") ##  now draw the data histogram. If it has "SAME" it will use the first histogram ranges        
        ROOT.gPad.Update()
        self.tpad = self.channel.GetPad(0)
#        tpad.SetLeftMargin(0.5)
        self.tpad.SetLeftMargin(0.15)
        self.tpad.SetRightMargin(0.15)
        self.tpad.SetBottomMargin(0.05)
        self.tpad.SetTopMargin(0.05)

        palette = self.pol_his_Ecells.FindObject("palette")
        palette.SetX1NDC(0.86)
        palette.SetX2NDC(0.91)
        palette.SetY1NDC(0.05)
        palette.SetY2NDC(0.95)

        gPad.Modified()
        gPad.Update()

        l = ROOT.TLatex()
        l.SetNDC()
        l.SetTextFont(66)
#        l.DrawLatex(0.19,0.16,"LASER LB")
        
        l2 = ROOT.TLatex()
        l2.SetNDC()
#        l2.DrawLatex(0.045,0.90,"#bf{#it{ATLAS}} Internal")
        l2.DrawLatex(0.045,0.90,"#bf{#it{ATLAS}} Preliminary")
        l2.DrawLatex(0.045,0.85,"Tile calorimeter")
        l2.SetTextSize(0.04)
        l2.DrawLatex(0.045,0.80,"E cells")
        l2.DrawLatex(0.045,0.15,"Run 311556")
        l2.DrawLatex(0.045,0.10,"2016-10-27 08:30:41")

        l2.SetTextSize(0.030)
        l2.DrawLatex(0.575,0.47,"x")
        l2.DrawLatex(0.48,0.59,"y")

        self.arrowX = ROOT.TArrow(0.,0.,0.25,0.,0.01)
        self.arrowX.SetLineWidth(2)
        self.arrowX.SetLineColor(kBlack)
        #self.arrowX.SetTitle("x")
        self.arrowX.Draw()

        self.arrowY = ROOT.TArrow(0.,0.,0.,0.25,0.01)
        self.arrowY.SetLineWidth(2)
        self.arrowY.SetLineColor(kBlack)
        #self.arrowY.SetTitle("y")
        self.arrowY.Draw()

        self.ellipse1 = ROOT.TEllipse(-1.12, -.65, 1.25, 1.25, 82, 98)
        self.ellipse1.SetLineColor(kBlack)
        self.ellipse1.SetLineWidth(2)
        self.ellipse1.SetNoEdges(kTRUE)
        self.ellipse1.Draw()

        self.ellipse2 = ROOT.TEllipse(-1.12, -.65, 1.02, 1.02, 82, 98)
        self.ellipse2.SetLineColor(kBlack)
        self.ellipse2.SetLineWidth(2)
        self.ellipse2.SetNoEdges(kTRUE)
        self.ellipse2.Draw("same")

        self.ellipse3 = ROOT.TEllipse(-1.12, -.65, .79, .79, 82, 98)
        self.ellipse3.SetLineColor(kBlack)
        self.ellipse3.SetLineWidth(2)
        self.ellipse3.SetNoEdges(kTRUE)
        self.ellipse3.Draw("same")

        self.ellipse4 = ROOT.TEllipse(-1.12, -.65, .56, .56, 82, 98)
        self.ellipse4.SetLineColor(kBlack)
        self.ellipse4.SetLineWidth(2)
        self.ellipse4.SetNoEdges(kTRUE)
        self.ellipse4.Draw("same")

        self.ellipse5 = ROOT.TEllipse(-1.12, -.65, .33, .33, 82, 98)
        self.ellipse5.SetLineColor(kBlack)
        self.ellipse5.SetLineWidth(2)
        self.ellipse5.SetNoEdges(kTRUE)
        self.ellipse5.Draw("same")

        self.lineE1 = ROOT.TLine(-1.165, -.32, -1.295, .585)
        self.lineE1.SetLineColor(kBlack)
        self.lineE1.SetLineWidth(2)
        self.lineE1.Draw()
        
        self.lineE2 = ROOT.TLine(-1.075, -.32, -.945, .585)
        self.lineE2.SetLineColor(kBlack)
        self.lineE2.SetLineWidth(2)
        self.lineE2.Draw()

        l2.SetTextSize(0.04)
        l2.DrawLatex(0.092,0.41,"E4")
        l2.DrawLatex(0.092,0.50,"E3")
        l2.DrawLatex(0.092,0.60,"E2")
        l2.DrawLatex(0.092,0.70,"E1")

        self.channel.Modified()                  
        self.channel.Print("results/tile_laser_Ecells_map_phi_public.png")
        self.channel.Print("results/tile_laser_Ecells_map_phi_public.eps")
        self.channel.Print("results/tile_laser_Ecells_map_phi_public.C")
        self.channel.Print("results/tile_laser_Ecells_map_phi_public.root")
        self.channel.Delete()

        self.cnv.cd()

        self.his_A.GetYaxis().SetRangeUser(-8.0,8.0)
        self.his_A.Fit("pol0")
        self.his_A.Draw("EP")
               
        l = ROOT.TLatex()
        l.SetNDC()
        l.SetTextFont(66)
#        l.DrawLatex(0.19,0.16,"LASER LB")
        
        l2 = ROOT.TLatex()
        l2.SetNDC()
        l2.DrawLatex(0.19,0.2,"Laser A cells (LB)")
        
        self.cnv.Modified()                  
        self.cnv.Print("results/tile_laser_lb_phi_A_public.png")
        self.cnv.Print("results/tile_laser_lb_phi_A_public.C")
        self.cnv.Print("results/tile_laser_lb_phi_A_public.eps")
        self.cnv.Print("results/tile_laser_lb_phi_A_public.root")

        self.cnv.cd()

        self.his_B.GetYaxis().SetRangeUser(-8.0,8.0)
        self.his_B.Fit("pol0")
        self.his_B.Draw("EP")
               
        l = ROOT.TLatex()
        l.SetNDC()
        l.SetTextFont(66)
#        l.DrawLatex(0.19,0.16,"LASER LB")
        
        l2 = ROOT.TLatex()
        l2.SetNDC()
        l2.DrawLatex(0.19,0.2,"Laser B cells (LB)")
        
        self.cnv.Modified()                  
        self.cnv.Print("results/tile_laser_lb_phi_B_public.png")
        self.cnv.Print("results/tile_laser_lb_phi_B_public.C")
        self.cnv.Print("results/tile_laser_lb_phi_B_public.eps")
        self.cnv.Print("results/tile_laser_lb_phi_B_public.root")

        self.cnv.cd()

        self.his_D.GetYaxis().SetRangeUser(-8.0,8.0)
        self.his_D.Fit("pol0")
        self.his_D.Draw("EP")
               
        l = ROOT.TLatex()
        l.SetNDC()
        l.SetTextFont(66)
#        l.DrawLatex(0.19,0.16,"LASER LB")
        
        l2 = ROOT.TLatex()
        l2.SetNDC()
        l2.DrawLatex(0.19,0.2,"Laser D cells (LB)")
        
        self.cnv.Modified()                  
        self.cnv.Print("results/tile_laser_lb_phi_D_public.png")
        self.cnv.Print("results/tile_laser_lb_phi_D_public.C")
        self.cnv.Print("results/tile_laser_lb_phi_D_public.eps")
        self.cnv.Print("results/tile_laser_lb_phi_D_public.root")

        self.cnv.cd()

        self.his_EA.GetYaxis().SetRangeUser(-8.0,8.0)
        self.his_EA.Fit("pol0")
        self.his_EA.Draw("EP")
               
        l = ROOT.TLatex()
        l.SetNDC()
        l.SetTextFont(66)
#        l.DrawLatex(0.19,0.16,"LASER LB")
        
        l2 = ROOT.TLatex()
        l2.SetNDC()
        l2.DrawLatex(0.19,0.2,"Laser A cells (EB)")
        
        self.cnv.Modified()                  
        self.cnv.Print("results/tile_laser_eb_phi_A_public.png")
        self.cnv.Print("results/tile_laser_eb_phi_A_public.C")
        self.cnv.Print("results/tile_laser_eb_phi_A_public.eps")
        self.cnv.Print("results/tile_laser_eb_phi_A_public.root")


        self.cnv.cd()

        self.his_EB.GetYaxis().SetRangeUser(-8.0,8.0)
        self.his_EB.Fit("pol0")
        self.his_EB.Draw("EP")
               
        l = ROOT.TLatex()
        l.SetNDC()
        l.SetTextFont(66)
#        l.DrawLatex(0.19,0.16,"LASER LB")
        
        l2 = ROOT.TLatex()
        l2.SetNDC()
        l2.DrawLatex(0.19,0.2,"Laser B cells (EB)")
        
        self.cnv.Modified()                  
        self.cnv.Print("results/tile_laser_eb_phi_B_public.png")
        self.cnv.Print("results/tile_laser_eb_phi_B_public.C")
        self.cnv.Print("results/tile_laser_eb_phi_B_public.eps")
        self.cnv.Print("results/tile_laser_eb_phi_B_public.root")

        self.cnv.cd()

        self.his_ED.GetYaxis().SetRangeUser(-8.0,8.0)
        self.his_ED.Fit("pol0")
        self.his_ED.Draw("EP")
               
        l = ROOT.TLatex()
        l.SetNDC()
        l.SetTextFont(66)
#        l.DrawLatex(0.19,0.16,"LASER LB")
        
        l2 = ROOT.TLatex()
        l2.SetNDC()
        l2.DrawLatex(0.19,0.2,"Laser D cells (EB)")
        
        self.cnv.Modified()                  
        self.cnv.Print("results/tile_laser_eb_phi_D_public.png")
        self.cnv.Print("results/tile_laser_eb_phi_D_public.C")
        self.cnv.Print("results/tile_laser_eb_phi_D_public.eps")
        self.cnv.Print("results/tile_laser_eb_phi_D_public.root")

        self.his_E1.GetYaxis().SetRangeUser(-15.0,15.0)
        self.his_E1.Fit("pol0")
        self.his_E1.Draw("EP")
               
        l = ROOT.TLatex()
        l.SetNDC()
        l.SetTextFont(66)
#        l.DrawLatex(0.19,0.16,"LASER LB")
        
        l2 = ROOT.TLatex()
        l2.SetNDC()
        l2.DrawLatex(0.19,0.2,"Laser E1 cells")
        
        self.cnv.Modified()                  
        self.cnv.Print("results/tile_laser_E1_phi_public.png")
        self.cnv.Print("results/tile_laser_E1_phi_public.C")
        self.cnv.Print("results/tile_laser_E1_phi_public.eps")
        self.cnv.Print("results/tile_laser_E1_phi_public.root")

        self.his_E2.GetYaxis().SetRangeUser(-15.0,15.0)
        self.his_E2.Fit("pol0")
        self.his_E2.Draw("EP")
               
        l = ROOT.TLatex()
        l.SetNDC()
        l.SetTextFont(66)
#        l.DrawLatex(0.19,0.16,"LASER LB")
        
        l2 = ROOT.TLatex()
        l2.SetNDC()
        l2.DrawLatex(0.19,0.2,"Laser E2 cells")
        
        self.cnv.Modified()                  
        self.cnv.Print("results/tile_laser_E2_phi_public.png")
        self.cnv.Print("results/tile_laser_E2_phi_public.C")
        self.cnv.Print("results/tile_laser_E2_phi_public.eps")
        self.cnv.Print("results/tile_laser_E2_phi_public.root")

        self.his_E3.GetYaxis().SetRangeUser(-15.0,15.0)
        self.his_E3.Fit("pol0")
        self.his_E3.Draw("EP")
               
        l = ROOT.TLatex()
        l.SetNDC()
        l.SetTextFont(66)
#        l.DrawLatex(0.19,0.16,"LASER LB")
        
        l2 = ROOT.TLatex()
        l2.SetNDC()
        l2.DrawLatex(0.19,0.2,"Laser E3 cells")
        
        self.cnv.Modified()                  
        self.cnv.Print("results/tile_laser_E3_phi_public.png")
        self.cnv.Print("results/tile_laser_E3_phi_public.C")
        self.cnv.Print("results/tile_laser_E3_phi_public.eps")
        self.cnv.Print("results/tile_laser_E3_phi_public.root")

        self.his_E4.GetYaxis().SetRangeUser(-15.0,15.0)
        self.his_E4.Fit("pol0")
        self.his_E4.Draw("EP")
               
        l = ROOT.TLatex()
        l.SetNDC()
        l.SetTextFont(66)
#        l.DrawLatex(0.19,0.16,"LASER LB")
        
        l2 = ROOT.TLatex()
        l2.SetNDC()
        l2.DrawLatex(0.19,0.2,"Laser E4 cells")
        
        self.cnv.Modified()                  
        self.cnv.Print("results/tile_laser_E4_phi_public.png")
        self.cnv.Print("results/tile_laser_E4_phi_public.C")
        self.cnv.Print("results/tile_laser_E4_phi_public.eps")
        self.cnv.Print("results/tile_laser_E4_phi_public.root")



    # Here we fill the histograms and the bad channel list
    def ProcessRegion(self, region):
                          
#        if 'TILECAL' == region.GetHash() or true:

        fib_list = set()

        first = True

        first_LG = True
        first_HG = True
            
        bad_fib_list    = []
        bad_las_list    = []
        bad_las_event   = []
        no_las_list     = []
        no_las_event    = []
        bad_las_list_K  = []
        bad_las_event_K = []
        no_las_list_K   = []
        no_las_event_K  = []
            
        for event in region.GetEvents():


            if ((self.runNumber!=event.run.runNumber) and (self.runNumber>0)):
                continue

            if 'is_OK' in event.data:

                [p, i, j, w] = self.PMTool.GetNumber(event.data['region'])

                MBTSi = [39, 40, 41, 42, 55, 56, 57, 58]
                MBTSo = [8, 24, 43, 54]
                if (p == 3 or p == 4) and j == 4 and i in MBTSi:
                    print('MBTSinner ', i, j)
                    #continue

                if  (p == 3 or p == 4) and j == 12 and i in MBTSo:
                    print('MBTSouter ', i, j)
                    #continue

                if w!=self.gain and self.gain!=2:
                    continue

                if first and self.gain!=2:
                    self.runno = event.run.runNumber


                    first=False
                elif self.gain==2:
                    if first_LG and w==0:
                        first_LG        = False
                        self.ref_LG_evt = event
                    if first_HG and w==1:
                        first_HG        = False
                        self.ref_HG_evt = event 


                if 'deviation' not in event.data: # No data
                    [p, i, j, w] = self.PMTool.GetNumber(event.data['region'])
                    index        = self.PMTool.get_index(p-1, i-1, j, w)


                    no_las_list.append(index)
                    no_las_event.append(event)     

                else:
                    pmt    = self.PMTool.get_PMT_index(p-1,i-1,j)                          
                    indice = self.PMTool.get_fiber_index(p-1,i-1,pmt)

                    if not event.data['status']:   # Don't put event on summary plot if on BC list
                            # Following selection remove the events with low LASER light (fiber problem)


                        if (event.data['calibration']>0.0001 and event.run.data['wheelpos']==8)\
                                or (event.data['calibration']>0.0001 and event.run.data['wheelpos']==6):

                            Celln = self.PMTool.get_stable_cells(p-1,pmt) # Get cell name needs pmt number starting from 1
                            Celli = self.PMTool.get_cell_index(p-1,i,pmt)

                                ## corrected map
                            layer =  region.GetLayerName()                       #Use of functions to get name of layer and region for 

                            cell  =  region.GetCellName()
                            module=i-1
                            ebindex=64+64+64 #EB starts after A BC D of LB
                            eindex=64+64+64 #E cell start after LB and EB
                            Celli=-1 ## histogram number

                            if (layer=="A"):
                                Celli=module
                                if int(cell[1:]) > 10: #in EB
                                    Celli += ebindex
                            elif (layer=="B"):
                                Celli=module+64
                                if int(cell[1:]) > 9: #in EB
                                    Celli += ebindex
                            elif (layer=="C"):
                                Celli=module+64
                                if int(cell[1:]) > 9: #in EB
                                    Celli += ebindex
                            elif (layer=="BC"):
                                Celli=module+64
                            elif (layer=="D"):
                                Celli=module+64+64
                                if int(cell[1:]) > 3: #in EB
                                    Celli += ebindex
                            elif (layer=='E4'):
                                Celli=module+ebindex+eindex

                            elif (layer=='E3'):
                                Celli=module+64+ebindex+eindex

                            elif (layer=='E2'):
                                Celli=module+64+64+ebindex+eindex

                            elif (layer=='E1'):
                                Celli=module+64+64+64+ebindex+eindex

                            elif (layer=="MBTS"):
                                Celli=-1

                            else:
                                print("ERROR, unknown cell ",layer)

                            ######## Status checks
                            ######## channels not calibrated not displayed
                            DQstatus_list = ['No HV','ADC masked (unspecified)','ADC dead','Severe data corruption','Severe stuck bit','Very large LF noise','Channel masked (unspecified)']
                            if 'problems' in event.data:
                                if (problem in DQstatus_list):
                                    continue                                        

                            if (event.data['status']&0x10 or event.data['status']&0x4):
                                continue

                            if (event.data['HV']<5):
                                continue

                            #if (module == 60 and p == 1): ### special case !! LBA61
                            #    print 'skiping ',event.data['region']
                            #    continue

                            if (Celli>=0):
#                                print 'filling ',Celli
#                                print 'deviation'
                                self.chans[Celli].Fill(event.data['deviation'])

