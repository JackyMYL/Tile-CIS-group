#!/usr/bin/env python

from ROOT import *
import sys
import math
import ROOT

class MyFunctionObject:
    """ A test function for fitting """

    def __init__(self):
        self.LumiYear = "2018"
        self.lumiFileName = "data/deliveredLumiTime{}.root".format(self.LumiYear)
       # self.lumiFileName = "LumiGraph.root"
        self.lumiFile=TFile(self.lumiFileName,"read")
       # self.lumiGraph=self.lumiFile.Get("Graph")
        self.lumiGraph=self.lumiFile.Get("Luminosity")
        self.t0 = self.lumiGraph.GetX()
        self.lumi = self.lumiGraph.GetY()
        print self.t0

    def __call__(self,x,p):
        y = p[0]+p[1]*x[0]/(86400.*365.25)
        for i in range(len(self.lumi)):
            if (self.t0[i]<x[0]):
               # y = y-p[2]*self.lumi[i]*TMath.Exp(-(x[0]-self.t0[i])/(86400.*p[3])) 
                try:
                    l = pow(self.lumi[i],abs(p[3]))
                except:
                    print "pow exception for run %d, lumi %f, power %f" % (i, self.lumi[i], abs(p[3]))
                    l=0
                y = y-p[2]*l*TMath.Exp(-(x[0]-self.t0[i])/(86400.*p[4]))-p[5]*l*TMath.Exp(-(x[0]-self.t0[i])/(86400.*p[6]))
               # y = y-p[2]*self.lumi[i]*TMath.Exp(-(x[0]-self.t0[i])/(86400.*p[3]))-p[4]*self.lumi[i]*TMath.Exp(-(x[0]-self.t0[i])/(86400.*p[5]))
      #  print len(self.lumi)
        return y

fobj = MyFunctionObject()
fit = ROOT.TF1("fit", fobj, 0., 2e9, 7)
fit.SetParNames("par0","slope","drift1","pow1","par_time1","drift2","par_time2",)
#fit.SetParNames("par0","slope","drift1","par_time1")
fit.SetParameters(1.,0.2,0.0005,1.,20.,0.0004,40.)
#fit.SetParameters(1.,0.2,0.0005,20.)
fit.SetParLimits(0,-10,10)
fit.SetParLimits(1,0,0.7)
fit.SetParLimits(2,0,10)
fit.SetParLimits(3,0,2)
fit.SetParLimits(4,1,90)
fit.SetParLimits(5,0,10)
fit.SetParLimits(6,1,90)

LumiYear = "2018"
GraphFileTag = "LumiFitFunction{}".format(LumiYear)
GraphFileName = "results/output/Tucs.HIST{}.root".format(GraphFileTag)
GraphFile=TFile(GraphFileName,"read")
gDir = "CellsEvolution"
ti=TDatime("2018-04-17 01:01:00")
tf=TDatime("2018-10-30  01:01:00")
outDir="results/output/LumiFitting"
canvas=TCanvas()
gStyle.SetPadRightMargin(0.15)
canvas.SetFillColor(0)
legend=TLegend(0.5,0.70,0.7,0.88)
legend.SetFillStyle(0)
legend.SetBorderSize(0)
canvas.cd()
if gDir == "CellsEvolution":
   # cells =['A1','A2','A3','A4','A5','A6','A7','A8','A9','A10'] #LB
    cells =['A9','A10'] #LB
elif gDir == "AEBCellsEvolution":
    # cells = ['A12','A13','A14','A15','A16'] #EB
    cells = ['A14','A16'] #EB
elif gDir == "ECellsEvolution":
    cells = ['E1','E2']
elif gDir == "DLBCellsEvolution":
    # cells = ['D0','D1','D2','D3'] #LB
    cells = ['D0','D1','D3'] #LB
elif gDir == "DEBCellsEvolution":
    cells = ['D4','D6'] #EB
elif gDir == "BCLBCellsEvolution":
    # cells = ['BC1','BC2','BC3','BC4','BC5','BC6','BC7','BC8','B9']  #LB
    cells = ['BC2','BC8','B9']  #LB
elif gDir == "BCEBCellsEvolution":  
    #  cells = ['B11','B12','B13','B14','B15','C10'] #EB 
    cells = ['B11','B14','C10'] #EB 
else:
    pass

c=1
for cell in cells:
    print "Lumi Fitting for cell", cell
    tmpgraph = GraphFile.Get("{}/Combined_{}".format(gDir,cell))
    tmpgraph.SetMarkerColor(1+c)
    tmpgraph.SetMarkerSize(0.9)
    legend.AddEntry(tmpgraph,"cell {}".format(cell),"P")
    ROOT.gStyle.SetOptStat(1111)
    ROOT.gStyle.SetOptFit(1)
    if LumiYear == "2015":
        tmpgraph.Fit(fit,"","",1433322000,1446507600)## 03/06/15 - 02/11/15 
    elif LumiYear == "2016":
        tmpgraph.Fit(fit,"V","",1461366000,1477585800)## 22/04/16 - 27/10/16 
    elif LumiYear == "2017":
        tmpgraph.Fit(fit,"V","",1494871200,1511661600)## 15/05/17 - 26/11/2017
    elif LumiYear == "2018":
        tmpgraph.Fit(fit,"V","",1523966400,1540501200)## 17/04/18 - 25/10/18 
    tmpgraph.GetFunction("fit").SetLineColor(1+c)
    if c ==1:
        tmpgraph.Draw("aep")
        tmpgraph.GetXaxis().SetTimeFormat("#splitline{%d/%m}{%Y}%F1970-01-01 00:00:00s0")
        tmpgraph.GetXaxis().SetTimeDisplay(1)
        tmpgraph.GetXaxis().SetLimits(ti.Convert(),tf.Convert())
        tmpgraph.GetXaxis().SetLabelSize(0.03)
        tmpgraph.GetXaxis().SetLabelOffset(0.025)
        tmpgraph.GetXaxis().SetTitleOffset(1.5)
        tmpgraph.GetXaxis().SetTitle("Time [dd/mm and year]")
        tmpgraph.GetYaxis().SetTitle("Average Response Deviation [%]")
        tmpgraph.GetYaxis().SetRangeUser(-6,3)
        tmpgraph.Draw("aep")
    else: 
        tmpgraph.Draw("epsame")
    canvas.Update()
    c+=1
legend.Draw()
canvas.Modified()
canvas.cd()
plotname="{}/LumiSlope_doubleExpo_doublePowerFit{}_{}".format(outDir,gDir,GraphFileTag)
canvas.SetGridx()
canvas.SetGridy()
canvas.Print(plotname+".pdf")
canvas.Print(plotname+".root")
