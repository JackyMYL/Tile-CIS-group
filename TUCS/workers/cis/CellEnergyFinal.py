# Author: Grey Wilburn <gwwilburn@gmail.com>
# Edited by: Andrew Mattillion <amattillion@gamil.com>

# This script makes the final Cell Energy plot containing all of 
# the distributions by reading the local root files that are made 
# by CellEnergy.py.

from src.ReadGenericCalibration import *
from src.oscalls import *
from src.region import *
from array import array
from src.MakeCanvas import *
from ROOT import TFile
import numpy

class CellEnergyFinal(ReadGenericCalibration):
    """Make final Cell Energy Deposition Public Plot using local root files produced by CellEnergy.py"""

    def __init__(self):
        ROOT.gStyle.SetOptStat(0)
        ROOT.gErrorIgnoreLevel = 1001
        
    def ProcessStart(self):
        pass

    def ProcessStop(self):
        #Change CellEnergyPlots and EtaEnergy Plots to True or False to choose what to plot
        CellEnergyPlots = True
        EtaEnergyPlots = False
        VertexPlots = False

        if CellEnergyPlots:
                ROOT.gStyle.SetOptStat(0)
                c1 = src.MakeCanvas.MakeCanvas()
                c1.cd()
                c1.SetLogy()

                #Open up root files, and extract histograms
                #13 TeV
                f13 = ROOT.TFile('CellEnergy/cell_energy_histo_13TeVvercut1andL1MBTS_unscaled.root')
                h13 =  ROOT.TH1D("h13", "", 100, -1.0, 5.0)
                h13 = f13.Get('cell_energy')
                h13.SetDirectory(0)

                #0.9 TeV
                f9 = ROOT.TFile("CellEnergy/cell_energy_histo_0.9TeV_unscaled.root")
                h9 = ROOT.TH1D("h9", "", 100, -1.0, 5.0)
                h9 = f9.Get('cell_energy')
                h9.SetDirectory(0)

                #13 TeV w/ random trigger
                fr = ROOT.TFile("CellEnergy/RTalladded.root")
                hr = ROOT.TH1D("hr", "", 100, -1.0, 5.0)
                hr = fr.Get('cell_energy')
                hr.SetDirectory(0)

                #13 TeV Monte Carlo
                fmc = ROOT.TFile("CellEnergy/cell_energy_histo_MCvercut1_unscaled.root")
                hmc = ROOT.TH1D("mc", "", 100, -1.0, 5.0)
                hmc = fmc.Get('cell_energy')
                hmc.SetDirectory(0)

                #Pedestal noise distribution
                fped = ROOT.TFile("CellEnergy/cell_energy_histo_ped100k_unscaled.root")
                hped = ROOT.TH1D("hped", "", 100, -1.0, 5.0)
                hped = fped.Get('cell_energy')
                hped.SetDirectory(0)

                # Set error bars. It is very important to do this BEFORE scaling        
                for i in range(0,102):
                    h13.SetBinError(i, sqrt(h13.GetBinContent(i)))
                    h9.SetBinError(i, sqrt(h9.GetBinContent(i)))

                #format axes
                hr.GetXaxis().SetTitle("Tile Cell Energy [GeV]")
                hr.GetYaxis().SetTitle("# of Cells / 0.06 GeV / Event")
                hr.GetYaxis().SetTitleOffset(1.4)
                hr.GetYaxis().SetNdivisions(10, 10, 10, ROOT.kTRUE)
                
                #Scale the histogram, i.e., normalize using the number of events analyzed
                #Scale factor  =  1/n_events
                h13.Scale(0.000013)
                h9.Scale(0.00000798)
                hr.Scale(0.00000215)
                hmc.Scale(0.000017)
                hped.Scale(0.000010)

                #Set y axis range limits to match first public plot
                #h9.SetMinimum(0.00001)
                #h9.SetMaximum(100000)
                #h13.SetMinimum(0.00001)
                #h13.SetMaximum(100000)
                #hmc.SetMinimum(0.00001)
                #hmc.SetMaximum(100000)
                hr.SetMinimum(0.00001)
                hr.SetMaximum(100000)
                
                #Format Draw Options
                hr.SetMarkerStyle(ROOT.kDot)
                hr.SetLineColor(ROOT.kBlue-10)
                hr.SetFillColor(ROOT.kBlue-10)
                #hr.SetFillStyle(1001)
                hr.SetFillStyle(4050)

                hmc.SetLineColor(ROOT.kRed)
                hmc.SetMarkerStyle(ROOT.kDot)

                h13.SetLineColor(ROOT.kBlue)
                h13.SetMarkerColor(ROOT.kBlue)
                h13.SetMarkerStyle(ROOT.kFullCircle)
                h9.SetLineColor(ROOT.kGreen-7)
                h9.SetMarkerColor(ROOT.kGreen-7)
                h9.SetMarkerStyle(ROOT.kFullSquare)

                hped.SetLineColor(ROOT.kBlack)
                hped.SetMarkerColor(ROOT.kBlack)
                hped.SetMarkerStyle(ROOT.kDot)

                #Draw histograms as points w/ error bars
                hr.SetStats(0)
                hr.Draw('histe')
                h9.Draw('e1same')
                h13.Draw('e1same')
                hmc.Draw('histsamee')
                hped.Draw('histsamee')
                
                RatioPanel = True
                if RatioPanel:
                    #Make a ratio panel showing Data/MC
                    
                    h9.GetXaxis().SetLabelSize(0)
                    h13.GetXaxis().SetLabelSize(0)
                    hmc.GetXaxis().SetLabelSize(0)
                    hr.GetXaxis().SetLabelSize(0)
                    ratio = h13.Clone("ratio")
                    ratio.SetDirectory(0)
                    ratio.Divide(hmc)
            
                    ratio.GetYaxis().SetTitle("Data / MC       ")
                    ratio.GetYaxis().SetTitleSize(0.025)
                    ratio.GetYaxis().SetTitleOffset(1.00)
                    ratio.GetYaxis().SetLabelSize(0.025)
                    ratio.GetXaxis().SetLabelSize(0.04)
                    ratio.SetXTitle(hmc.GetXaxis().GetTitle())
                    ratio.GetYaxis().SetDecimals(kTRUE)
                    ratio.GetYaxis().SetRangeUser(0,1.75)
        
                    c1.cd()
                    ratio2 = hped.Clone("ratio2")
                    ratio2.SetDirectory(0)
                    ratio2.Divide(h13)
                    
                    c1.SetBottomMargin(0.3)
                    p = ROOT.TPad("p_test", "", 0, 0, 1, 1, 0, 0, 0)
                    ROOT.SetOwnership(p, False)
                    p.SetTopMargin(0.7)
                    p.SetFillStyle(0)
                    p.Draw()
                    p.SetGridy(kTRUE)
                    p.cd()

                    ratio.Draw("e1p")
#                    ratio2.Draw("e1")
                    c1.cd() 
          
                #Add label
                l = ROOT.TLatex()
                l.SetNDC()
                l.SetTextFont(72)
                l.DrawLatex(0.55,0.867,"ATLAS Preliminary") 
                
                #Add Legend
                leg = ROOT.TLegend(0.55, 0.67, 0.87, 0.85)
                leg.SetBorderSize(0)
                leg.AddEntry(h9, "Data, #sqrt{s} = 0.9 TeV", "pe")
                leg.AddEntry(h13, "Data, #sqrt{s} = 13 TeV", "pe")
                leg.AddEntry(hr, "Random Trigger", "f")
                leg.AddEntry(hmc, "Minimum Bias MC, #sqrt{s} = 13 TeV", "l")
                leg.AddEntry(hped, "Pedestal Run", "pe")
                leg.Draw()
                        
                c1.SetLogy()
                c1.SetTickx(1)  
                c1.SetTicky(1)  
                c1.Print('cell_energy_9_13_randonewratio_mu.png')
                c1.Print('cell_energy_9_13_randonewratio_mu.pdf')
                print('Done with Cell Energy plot')
        
        if EtaEnergyPlots:                                
                ROOT.gStyle.SetOptStat(0)
                c2 = src.MakeCanvas.MakeCanvas()
                c2.cd()
                
                #Open up Eta Energy (EE) root files, and extract histograms
                #13 TeV
                f13EE = ROOT.TFile('CellEnergy/eta_energy_profile13TeVn.root')
                h13EE = ROOT.TProfile("h13EE", "", 34, -1.6, 1.6) 
                h13EE = f13EE.Get('eta_energy_profile')
                h13EE.SetDirectory(0)
                
                #Set Error bars        
                for i in range(0,36):
                    h13EE.SetBinError(i, sqrt(h13EE.GetBinContent(i)))
                
                #Format axes
                h13EE.GetXaxis().SetTitle("Tile cell #eta")
                h13EE.GetYaxis().SetTitle("Tile cell Energy [MeV]")
                h13EE.GetYaxis().SetLabelSize(0.04)
                h13EE.GetXaxis().SetLabelSize(0.04)
                h13EE.GetYaxis().SetTitleOffset(1.0)
                h13EE.SetMinimum(400)
                h13EE.SetMaximum(1500)

                #Scale Histogram
                #h13EE.Scale(0.000010)        
                
                #Drqw histogram with error bars
                h13EE.SetStats(0)
                h13EE.Draw('E1')

                #Add Legend
                leg = ROOT.TLegend(0.55, 0.67, 0.87, 0.85)
                leg.SetBorderSize(0)
                leg.AddEntry(h13EE, "Data, #sqrt{s} = 13 TeV", "pe")
                #leg.AddEntry(h13, "Minimum Bias MC, #sqrt{s} = 13 TeV", "pe")
                leg.Draw()
                
                #Add label
                label = ROOT.TLatex()
                label.SetNDC()
                label.SetTextFont(72)
                label.DrawLatex(0.55,0.867,"ATLAS Preliminary") 
                
                c2.SetTickx(1)  
                c2.SetTicky(1)  
                c2.Print('EE_13_mc.pdf')
                print('Done with EE plot')

        if VertexPlots:
                ROOT.gStyle.SetOptStat(0)
                c3 = src.MakeCanvas.MakeCanvas()
                c3.cd()
                c3.SetLogy()

                #Open up sumpt vertex root files and extract histograms
                #13 TeV Data
                f13ver = ROOT.TFile('CellEnergy/sumpt13TeVL1MBTS.root')
                h13ver =  ROOT.TH1D("h13ver", "", 150, 0, 150)
                h13ver = f13ver.Get('sumpt')
                h13ver.SetDirectory(0)

                #13 TeV MC
                fmcver = ROOT.TFile("CellEnergy/sumptMC.root")
                hmcver = ROOT.TH1D("hmcver", "", 150, 0, 150)
                hmcver = fmcver.Get('sumpt')
                hmcver.SetDirectory(0)

                # Set error bars. It is very important to do this BEFORE scaling        
                for i in range(0,152):
                    h13ver.SetBinError(i, sqrt(h13ver.GetBinContent(i)))
                    hmcver.SetBinError(i, sqrt(hmcver.GetBinContent(i)))

                #Scale the histogram, i.e., normalize using the number of events analyzed
                #Scale factor  =  1/n_events
                h13ver.Scale(0.000013)
                hmcver.Scale(0.0000167)

                hmcver.SetLineColor(ROOT.kRed)
                hmcver.SetMarkerColor(ROOT.kRed)
                hmcver.SetMarkerStyle(ROOT.kDot)

                h13ver.Draw('e1')
                hmcver.Draw('e1same')

                #Add a ratio panel
                h13ver.GetXaxis().SetLabelSize(0)        
                hmcver.GetXaxis().SetLabelSize(0) 
                ratio = h13ver.Clone("ratio")
                ratio.SetDirectory(0)
                ratio.Divide(hmcver)
            
                ratio.GetYaxis().SetTitle("13 TeV Data / MC")
                ratio.GetYaxis().SetTitleSize(0.025)
                ratio.GetYaxis().SetTitleOffset(2.25)
                ratio.GetYaxis().SetLabelSize(0.025)
                ratio.GetXaxis().SetLabelSize(0.04)
                ratio.SetXTitle(hmcver.GetXaxis().GetTitle())
                ratio.GetYaxis().SetDecimals(kTRUE)
                ratio.GetYaxis().SetRangeUser(0,3)
        
                c3.cd()         
                c3.SetBottomMargin(0.3)
                p = ROOT.TPad("p_test", "", 0, 0, 1, 1, 0, 0, 0)
                ROOT.SetOwnership(p, False)
                p.SetTopMargin(0.7)
                p.SetFillStyle(0)
                p.Draw()
                p.SetGridy(kTRUE)
                p.cd()

                ratio.Draw("e1p")
                c3.cd()

                leg = ROOT.TLegend(0.55, 0.67, 0.87, 0.85)
                leg.SetBorderSize(0)
                leg.AddEntry(h13ver, "Data, #sqrt{s} = 13 TeV", "pe")
                leg.AddEntry(hmcver, "Minimum Bias MC, #sqrt{s} = 13 TeV", "pe")
                leg.Draw()

                c3.Print('sumpt13_mc.png')
                print('Done with sumpt plot')

                #Open up ntracks vertex root files and extract histogrmas
                #13 TeV Data

                f13vernt = ROOT.TFile('CellEnergy/ntracks13TeVL1MBTS.root')
                h13vernt =  ROOT.TH1D("h13vernt", "", 150, 0, 150)
                h13vernt = f13vernt.Get('ntracks')
                h13vernt.SetDirectory(0)

                #13 TeV MC
                fmcvernt = ROOT.TFile("CellEnergy/ntracksMC.root")
                hmcvernt = ROOT.TH1D("hmcvernt", "", 150, 0, 150)
                hmcvernt = fmcvernt.Get('ntracks')
                hmcvernt.SetDirectory(0)

                # Set error bars. It is very important to do this BEFORE scaling        
                for i in range(0,152):
                    h13vernt.SetBinError(i, sqrt(h13vernt.GetBinContent(i)))
                    hmcvernt.SetBinError(i, sqrt(hmcvernt.GetBinContent(i)))

                #Scale the histogram, i.e., normalize using the number of events analyzed
                #Scale factor  =  1/n_events
                h13vernt.Scale(0.000013)
                hmcvernt.Scale(0.0000167)

                hmcvernt.SetLineColor(ROOT.kRed)
                hmcvernt.SetMarkerColor(ROOT.kRed)
                hmcvernt.SetMarkerStyle(ROOT.kDot)

                h13vernt.Draw('e1')
                hmcvernt.Draw('e1same')

                #Add a ratio panel
                h13vernt.GetXaxis().SetLabelSize(0)        
                hmcvernt.GetXaxis().SetLabelSize(0) 
                ratio = h13vernt.Clone("ratio")
                ratio.SetDirectory(0)
                ratio.Divide(hmcvernt)
            
                ratio.GetYaxis().SetTitle("13 TeV Data / MC")
                ratio.GetYaxis().SetTitleSize(0.025)
                ratio.GetYaxis().SetTitleOffset(2.25)
                ratio.GetYaxis().SetLabelSize(0.025)
                ratio.GetXaxis().SetLabelSize(0.04)
                ratio.SetXTitle(hmcvernt.GetXaxis().GetTitle())
                ratio.GetYaxis().SetDecimals(kTRUE)
                ratio.GetYaxis().SetRangeUser(0,3)
        
                c3.cd()         
                c3.SetBottomMargin(0.3)
                p = ROOT.TPad("p_test", "", 0, 0, 1, 1, 0, 0, 0)
                ROOT.SetOwnership(p, False)
                p.SetTopMargin(0.7)
                p.SetFillStyle(0)
                p.Draw()
                p.SetGridy(kTRUE)
                p.cd()

                ratio.Draw("e1p")
                c3.cd()


                leg = ROOT.TLegend(0.55, 0.67, 0.87, 0.85)
                leg.SetBorderSize(0)
                leg.AddEntry(h13vernt, "Data, #sqrt{s} = 13 TeV", "pe")
                leg.AddEntry(hmcvernt, "Minimum Bias MC, #sqrt{s} = 13 TeV", "pe")
                leg.Draw()

                c3.Print('ntracks13_mc.png')
                print('Done with ntracks plot')

    def ProcessRegion(self, region):
       pass

  
