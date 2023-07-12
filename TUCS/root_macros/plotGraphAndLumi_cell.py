# Contact: Ammara(ammara.ahmad@cern.ch)
#Author : RUTE PEDRO(rute.pedro@cern.ch)
# This root macro plots time evolution graphs and the delivered luminosity histogram
#
#   -

#!/usr/bin/env python

import os
import sys
import subprocess
from ROOT import *

year = '2017'

def main():
    if year == '2015':
    # X-axis range
        ti=TDatime("2015-07-18 01:01:00")
        tf=TDatime("2015-11-03 01:01:00")
    if year == '2016':
        ti=TDatime("2016-05-24 01:01:00")
        tf=TDatime("2016-10-27 01:01:00")
    if year == '2017':
        ti=TDatime("2017-03-07 01:01:00")
        tf=TDatime("2017-11-26 01:01:00")
    if year == '2018':
        ti=TDatime("2018-02-18 01:01:00")
        tf=TDatime("2018-10-26 01:01:00")
  
    outDir="results/output/LumiPlots"

    # Graphs file

    if year == '2015':
        fileTag="LasPublicPlotsNewRef2015"  #2015 pUBLIC PLOTS
    if year == '2016':
        fileTag="LasPublicPlotsNewRef2016"  #2016 pUBLIC PLOTS
    if year == '2017':
        fileTag="LasPublicPlotsNewRef2017"  #2017 pUBLIC PLOTS
    if year == '2018':
        fileTag="LasPublicPlotsNewRef2018"  #2018 pUBLIC PLOTS

    graphFileDir="results/output"
    graphsFileName="{}/Tucs.HIST{}.root".format(graphFileDir,fileTag)
    gDir="BCEBCellsEvolution"
    graphsFile=TFile(graphsFileName,"read")

    # Histogram with Integrated Luminosity (must change X-axis: RunNumber->Date)
    drawLumi=True
    if year == '2015':
        lumiFileName="data/deliveredLumiTime2015.root"
    if year == '2016':
        lumiFileName="data/deliveredLumiTime2016.root"
    if year == '2017':
        lumiFileName="data/deliveredLumiTime2017.root"
    if year == '2018':
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
    lumiAxis.GetYaxis().SetAxisColor(kBlack)
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
    lumiGraph.SetMarkerSize(0.)
    if drawLumi: lumiAxis.Draw("histY+")
    if drawLumi: lumiGraph.Draw("F same")
    padLumi.cd()
    YRightAxis = TGaxis(tf.Convert(),0.,tf.Convert(),ymax,0,ymax,510,"+L")
    YRightAxis.SetLabelSize(0)
    YRightAxis.Draw()
    padLumi.Update()
    padLumi.Modified()

    # Time evolution graphs
    canvas.cd()
    padGraph.Draw()
    padGraph.cd()
  
    if gDir == "CellsEvolution":
        # cells =['A1','A2','A3','A4','A5','A6','A7','A8','A9','A10'] #LB
        cells =['A9','A10','A12','A13'] 
    elif gDir == "AEBCellsEvolution":
        # cells = ['A12','A13','A14','A15','A16'] #EB
        cells = ['A12','A14','A16'] #EB
    elif gDir == "ECellsEvolution":
        cells = ['E1','E2','E3','E4']
    elif gDir == "DLBCellsEvolution":
        cells = ['D0','D1','D2','D3'] #LB
    elif gDir == "DEBCellsEvolution":
        cells = ['D4','D5','D6'] #EB
    elif gDir == "BCLBCellsEvolution":
       # cells = ['BC1','BC2','BC3','BC4','BC5','BC6','BC7','BC8','B9']  #LB
        cells = ['BC2','BC8','B9']  #LB
    elif gDir == "BCEBCellsEvolution":  
       # cells = ['B11','B12','B13','B14','B15','C10'] #EB 
        cells = ['B11','B14','C10'] #EB 
    else:
        pass
    c=1
    color = [kRed, kBlue, kGreen, kMagenta]
    color = 0
    for cell in cells:
        tmpgraph=graphsFile.Get("{}/Combined_{}".format(gDir,cell))
        tmpgraph.SetMarkerStyle(19+c)
        tmpgraph.SetMarkerColor(2+color)
       # tmpgraph.SetLineColor(1+c)
        tmpgraph.SetMarkerSize(1.2)
        legend.AddEntry(tmpgraph,"Cell {}".format(cell),"p")
        if c==1:
            tmpgraph.Draw("aep")
            tmpgraph.GetXaxis().SetTimeFormat("#splitline{%d/%m}{%Y}%F1970-01-01 00:00:00s0")
            tmpgraph.GetXaxis().SetTimeDisplay(1)
            tmpgraph.GetXaxis().SetLimits(ti.Convert(),tf.Convert())
            tmpgraph.GetXaxis().SetLabelSize(0.03)
            tmpgraph.GetXaxis().SetLabelOffset(0.017)
            tmpgraph.GetXaxis().SetTitleOffset(1.25)
            tmpgraph.GetXaxis().SetTitle("Time [dd/mm and year]")
            tmpgraph.GetYaxis().SetTitle("Average Laser Drift [%]")
            tmpgraph.GetYaxis().SetRangeUser(-5.5,4.)
            tmpgraph.Draw("aep")
        else: tmpgraph.Draw("epsame")
        padGraph.Update()
        c+=1
        color +=1
    padGraph.Modified()
    canvas.cd()
    if drawLumi: legend.AddEntry(lumiGraph,"Luminosity","f")
    legend.Draw()
    ATLAS_label()


    plotname="{}/{}_{}".format(outDir,gDir,fileTag)
   # padGraph.SetGridx()
   # padGraph.SetGridy()
    canvas.Print(plotname+".pdf")
    canvas.Print(plotname+".root")
    padGraph.Delete()
    padLumi.Delete()

    graphsFile.Close()
    lumiFile.Close()

def ATLAS_label(label="Internal"):
    l = TLatex()
    l.SetNDC()
    l.SetTextFont(42)
    l.SetTextColor(1)
    l.SetTextSize(0.04)
    l.DrawLatex(.17, .85, "#bf{#it{ATLAS}} "+label)        
    l.DrawLatex(.17, .80, "Tile Calorimeter")
    l.DrawLatex(.17, .75, "2017 Data #scale[0.9]{#sqrt{s} = 13 TeV}")
    if year == '2017' or year == '2018':
        l.DrawLatex(.17, .50, "Start of pp collisions")
    l.SetTextSize(0.04)
    l.SetTextFont(62)
  #  l.DrawLatex(.23, .74, label2)

main()
