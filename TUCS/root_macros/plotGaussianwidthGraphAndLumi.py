# Contact: ammara.ahmad@cern.ch
# This root macro plots Gaussian Width time evolution graphs for average cells & average layers and the delivered luminosity histogram
#
#   -- NAMING dictionary for laser evolution graphs --
# for layers -> gDirectory: AverageResponsePerLayer; 
# for cells -> gDirectory: CellsEvolution;          

#!/usr/bin/env python

import os
import sys
import subprocess
import ROOT 

year = '2017'
doCells = True
doLayers = False
def main():
    # X-axis range
   # X-axis range
    if year == '2015':
        ti=ROOT.TDatime("2015-07-17 01:01:00")## new for all cells
        tf=ROOT.TDatime("2015-11-03 01:01:00")
    if year == '2016':
        #ti=TDatime("2016-04-07 01:01:00")  ## for ref 01/04
        ti=ROOT.TDatime("2016-05-24 01:01:00")  ## for ref 24/05
        tf=ROOT.TDatime("2016-10-27 01:01:00")
    if year == '2017':
        ti=ROOT.TDatime("2017-03-07 01:01:00")
        tf=ROOT.TDatime("2017-11-26 01:01:00")
    if year == '2018':
        ti=ROOT.TDatime("2018-02-18 01:01:00")
        tf=ROOT.TDatime("2018-10-26 01:01:00")
    if year == '2019':
        ti=ROOT.TDatime("2018-10-25 01:01:00")
        tf=ROOT.TDatime("2020-09-20 01:01:00")
    if year == '2021':
        ti=ROOT.TDatime("2015-07-26 01:01:00")
        tf=ROOT.TDatime("2021-09-26 01:01:00")
    outDir="results/output"

    
    # Graphs file
    fileTag="try"
    graphFileDir="results/output"
    graphsFileName="{}/Tucs.HIST{}.root".format(graphFileDir,fileTag) 
    if doCells:
        gDir="CellsEvolution"
    if doLayers:
        gDir="AverageResponsePerLayer"  
    
    graphsFile=ROOT.TFile(graphsFileName,"read")

    # Histogram with Integrated Luminosity (must change X-axis: RunNumber->Date)
    drawLumi=True
    lumiFileName="data/deliveredLumiTime{}.root".format(year)
    lumiFile=ROOT.TFile(lumiFileName,"read")
    lumiGraph=lumiFile.Get("IntLuminosity")

        
    # Canvas and Pads
    canvas=ROOT.TCanvas()
    canvas.SetCanvasSize(1700, 1300) ## (width, height)
    ROOT.gStyle.SetPadRightMargin(0.15)
    canvas.SetFillColor(0)
    legend=ROOT.TLegend(0.5,0.70,0.7,0.88)
    legend.SetFillStyle(0)
    legend.SetBorderSize(0)
   
    padLumi=ROOT.TPad()
    padLumi.SetFillStyle(4000) #transparent pads
    padLumi.SetFrameFillStyle(4000)
    padGraph=ROOT.TPad()
    padGraph.SetFillStyle(4000) #transparent pads
    padGraph.SetFrameFillStyle(4000)
    if drawLumi: padLumi.Draw()
    padLumi.cd()
    ROOT.gStyle.SetOptStat(0)

    # Luminosity graph
    lumiAxis=ROOT.TH1F("","",100,ti.Convert(),tf.Convert())
    if year == '2015':
        lumiAxis.SetMaximum(5)
        ymax = 5.
    if year == '2016':
        lumiAxis.SetMaximum(45)
        ymax = 45.
    if year == '2017':
        lumiAxis.SetMaximum(55)
        ymax = 55.
    if year == '2018':
        lumiAxis.SetMaximum(70.)
        ymax = 70. 
    lumiAxis.SetYTitle("Integrated Delivered Luminosity [fb^{-1}]")
    lumiAxis.GetYaxis().SetAxisColor(14)
    lumiAxis.GetYaxis().SetLabelColor(14)
    lumiAxis.GetYaxis().SetTitleColor(14)
    lumiAxis.GetYaxis().SetTitleOffset(1.5)
    lumiAxis.GetXaxis().SetAxisColor(0)
    lumiAxis.GetXaxis().SetLabelSize(0)
    lumiAxis.GetXaxis().SetLabelColor(0)
    lumiAxis.GetXaxis().SetTickSize(0)
    lumiGraph.Sort()
    lumiGraph.SetFillColor(17)
    lumiGraph.SetLineColor(17)
    lumiGraph.SetMarkerColor(17)
    if drawLumi: lumiAxis.Draw("histY+")
    if drawLumi: lumiGraph.Draw("F same")
    padLumi.cd()
    YRightAxis = ROOT.TGaxis(tf.Convert(),0.,tf.Convert(),ymax,0,ymax,510,"+L")
    YRightAxis.SetLabelSize(0)
    YRightAxis.Draw()
    padLumi.Update()
    padLumi.Modified()

    # Time evolution graphs
    canvas.cd()
    padGraph.Draw()
    padGraph.cd()
    if doLayers:
        layers=["A","BC","D"]
        c=1
        for layer in sorted (list(set(layers))):
            tmpgraph=graphsFile.Get("{}/GaussianWidth_{}".format(gDir,layer))
            tmpgraph.SetMarkerColor(1+c)
            tmpgraph.SetLineColor(1+c)
            tmpgraph.SetMarkerStyle(19+c)
            tmpgraph.SetMarkerSize(1.4)
            legend.AddEntry(tmpgraph,"Layer {}".format(layer),"lp")
            if c==1:
                tmpgraph.Draw("aep")
                tmpgraph.GetXaxis().SetTimeFormat("#splitline{%d/%m}{%Y}%F1970-01-01 00:00:00s0")
                tmpgraph.GetXaxis().SetTimeDisplay(1)
                tmpgraph.GetXaxis().SetLimits(ti.Convert(),tf.Convert())
                tmpgraph.GetXaxis().SetLabelSize(0.03)
                tmpgraph.GetXaxis().SetLabelOffset(0.017)
                tmpgraph.GetXaxis().SetTitleOffset(1.25)
                tmpgraph.GetXaxis().SetTitle("Time [dd/mm and year]")
                tmpgraph.GetYaxis().SetTitle("PMT Drift Gaussian width [%]")
                tmpgraph.GetYaxis().SetRangeUser(0.,2.)
                tmpgraph.Draw("aep")
            else: tmpgraph.Draw("epsame")
            padGraph.Update()
            c+=1
        padGraph.Modified()
        canvas.cd()
       # if drawLumi: legend.AddEntry(lumiGraph,"Luminosity","f")
        legend.Draw()
        ATLAS_label()
    if doCells:
        cells=["A10",'E2']
        c=1
        for cell in cells:
            tmpgraph=graphsFile.Get("{}/GaussianWidth_{}".format(gDir,cell))
            tmpgraph.SetMarkerColor(1+c)
            tmpgraph.SetLineColor(1+c)
            tmpgraph.SetMarkerStyle(19+c)
            tmpgraph.SetMarkerSize(1.4)
            legend.AddEntry(tmpgraph,"Cell {}".format(cell),"p")
            if c==1:
                tmpgraph.Draw("ap")
                tmpgraph.GetXaxis().SetTimeFormat("#splitline{%d/%m}{%Y}%F1970-01-01 00:00:00s0")
                tmpgraph.GetXaxis().SetTimeDisplay(1)
                tmpgraph.GetXaxis().SetLimits(ti.Convert(),tf.Convert())
                tmpgraph.GetXaxis().SetLabelSize(0.03)
                tmpgraph.GetXaxis().SetLabelOffset(0.017)
                tmpgraph.GetXaxis().SetTitleOffset(1.25)
                tmpgraph.GetXaxis().SetTitle("Time [dd/mm and year]")
                tmpgraph.GetYaxis().SetTitle("PMT Drift Gaussian width [%]")
                tmpgraph.GetYaxis().SetRangeUser(0.,3.)
                tmpgraph.Draw("ap")
            else: tmpgraph.Draw("psame")
            padGraph.Update()
            c+=1
    padGraph.Modified()
    canvas.cd()
    if year == '2018':
        line1=ROOT.TLine(0.31,0.15,0.31,0.60)
        line1.SetLineWidth(2)
        line1.SetLineColor(1)
        line1.SetLineStyle(2)
        line1.Draw()
    if year == '2017':
        line1=ROOT.TLine(0.35,0.15,0.35,0.60)
        line1.SetLineWidth(2)
        line1.SetLineColor(1)
        line1.SetLineStyle(2)
        line1.Draw()
        if doCells:
            # if cells == ["E1","E2","E3","E4"]:
            if cell == "E3" or cell == 'E4':
                line3=ROOT.TLine(0.525,0.15,0.525,0.65) ### 26/07/2017
                line3.SetLineWidth(2)
                line3.SetLineColor(1)
                line3.SetLineStyle(3)
                line3.Draw()
                legend.AddEntry(line3,"HV change in E3, E4 cells","l") 
    if drawLumi: legend.AddEntry(lumiGraph,"Luminosity","f")
    legend.Draw()
    ATLAS_label()


    if doLayers:
        plotname="{}/{}_{}".format(outDir,gDir,fileTag)
    else:
        plotname="{}/{}_{}".format(outDir,gDir,fileTag)
    canvas.Print(plotname+".pdf")
    canvas.Print(plotname+".root")
    padGraph.Delete()
    padLumi.Delete()

    graphsFile.Close()
    lumiFile.Close()

def ATLAS_label(label="Preliminary"):
    l = ROOT.TLatex()
    l.SetNDC()
    l.SetTextFont(42)
    l.SetTextColor(1)
    l.SetTextSize(0.04)
    l.DrawLatex(.17, .85, "#bf{#it{ATLAS}} "+label)        
    l.DrawLatex(.17, .80, "Tile Calorimeter")
    if year == '2015':
        l.DrawLatex(.17, .75, "2015 Data #scale[0.9]{#sqrt{s} = 13 TeV}")
    if year == '2016':
        l.DrawLatex(.17, .75, "2016 Data #scale[0.9]{#sqrt{s} = 13 TeV}")
       # l.SetTextSize(0.034)
       # l.DrawLatex(.16, .62, "Start of pp collisions")
    if year == '2017':
        l.DrawLatex(.17, .75, "2017 Data #scale[0.9]{#sqrt{s} = 13 TeV}")
        l.SetTextSize(0.034)
        l.DrawLatex(.16, .62, "Start of pp collisions")
    if year == '2018':
        l.DrawLatex(.17, .75, "2018 Data #scale[0.9]{#sqrt{s} = 13 TeV}")
        l.SetTextSize(0.034)
        l.DrawLatex(.16, .62, "Start of pp collisions")
    l.SetTextSize(0.04)
    l.SetTextFont(62)
   # l.DrawLatex(.23, .74, label2)

main()
