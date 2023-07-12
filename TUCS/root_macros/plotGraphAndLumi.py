# Contact: rute.pedro@cern.ch
# This root macro plots time evolution graphs and the delivered luminosity histogram
#
#   -- NAMING dictionary for laser evolution graphs --
# gDirectory: AverageResponsePerLayer; TGraph: LBCombined_A
# gDirectory: CellsEvolution;          TGraph: Combined_A14

#!/usr/bin/env python

import os
import sys
import subprocess
from ROOT import *

def main():

    # X-axis range
    ti=TDatime("2018-04-01 01:01:00")
    tf=TDatime("2018-11-01 01:01:00")    
    outDir="output"

    # Graphs file
    fileTag=".DQplotsDefaultSmooth"
    graphFileDir="output"
    graphsFileName="{}/Tucs.HIST{}.root".format(graphFileDir,fileTag)
    gDir="AverageResponsePerLayer"
    graphsFile=TFile(graphsFileName,"read")

    # Histogram with Integrated Luminosity
    drawLumi=True
    lumiFileName="data/deliveredLumiTime2018.root"
    lumiFile=TFile(lumiFileName,"read")
    lumiGraph=lumiFile.Get("IntLuminosity")

    # Canvas and Pads
    canvas=TCanvas()
    gStyle.SetPadRightMargin(0.15)
    canvas.SetFillColor(0)
    legend=TLegend(0.5,0.70,0.7,0.88)
    legend.SetFillStyle(0)
    legend.SetBorderSize(0)
    padLumi=TPad()
    padLumi.SetFillStyle(4000) #transparent pads
    padLumi.SetFrameFillStyle(4000)
    padGraph=TPad()
    padGraph.SetFillStyle(4000) #transparent pads
    padGraph.SetFrameFillStyle(4000)
    if drawLumi: padLumi.Draw()
    padLumi.cd()
    gStyle.SetOptStat(0)

    # Luminosity graph
    lumiAxis=TH1F("","",100,ti.Convert(),tf.Convert())
    lumiAxis.SetMaximum(80000)
    lumiAxis.SetYTitle("Integrated Delivered Luminosity [pb^{-1}]")
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
    padLumi.Update()
    padLumi.Modified()

    # Time evolution graphs
    canvas.cd()
    padGraph.Draw()
    padGraph.cd()
    layers=["A","BC","D"]
    part="EB"

    if part=="LB": label="Long Barrel"
    elif part=="EB": label="Extended Barrel"
    
    c=1
    for layer in layers:
        if part=="EB" and layer=="BC": layer="B"
        tmpgraph=graphsFile.Get("{}/{}Combined_{}".format(gDir,part,layer))
        tmpgraph.SetMarkerColor(1+c)
        tmpgraph.SetMarkerSize(1.)
        legend.AddEntry(tmpgraph,"Layer {}".format(layer),"ep")
        if c==1:
            tmpgraph.Draw("aep")
            tmpgraph.GetXaxis().SetTimeFormat("#splitline{%d/%m}{%Y}%F1970-01-01 00:00:00s0")
            tmpgraph.GetXaxis().SetTimeDisplay(1)
            tmpgraph.GetXaxis().SetLimits(ti.Convert(),tf.Convert())
            tmpgraph.GetXaxis().SetLabelSize(0.03)
            tmpgraph.GetXaxis().SetLabelOffset(0.025)
            tmpgraph.GetXaxis().SetTitleOffset(1.5)
            tmpgraph.GetXaxis().SetTitle("Time [dd/mm and year]")
            tmpgraph.GetYaxis().SetTitle("Average Response Deviation [%]")
            tmpgraph.GetYaxis().SetRangeUser(-5,3)
            tmpgraph.Draw("aep")
        else: tmpgraph.Draw("epsame")
        padGraph.Update()
        c+=1
    padGraph.Modified()
    canvas.cd()
    if drawLumi: legend.AddEntry(lumiGraph,"Luminosity","f")
    legend.Draw()
    ATLAS_label(label2=label)


    plotname="{}/{}_{}_{}".format(outDir,gDir,part,fileTag)
    canvas.Print(plotname+".pdf")
    padGraph.Delete()
    padLumi.Delete()

    graphsFile.Close()
    lumiFile.Close()

def ATLAS_label(label="Internal",label2=""):
    l = TLatex()
    l.SetNDC()
    l.SetTextFont(42)
    l.SetTextColor(1)
    l.SetTextSize(0.05)
    l.DrawLatex(.19, .84, "#bf{#it{ATLAS}} "+label)        
    l.DrawLatex(.21, .79, "Tile Calorimeter")
    l.SetTextSize(0.04)
    l.SetTextFont(62)
    l.DrawLatex(.23, .74, label2)

main()
