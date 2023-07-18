from ROOT import *
from array import array
from datetime import datetime
from time import time
import os
import ctypes

gStyle.SetOptStat(0)
gStyle.SetFrameBorderMode(0);
gStyle.SetCanvasBorderMode(0);
gStyle.SetPadBorderMode(0);
gStyle.SetPadColor(0);
gStyle.SetCanvasColor(0);
gStyle.SetStatColor(0);
gStyle.SetFrameFillColor(10);
gStyle.SetTitleFillColor(10);
gStyle.SetFillColor(10);
gStyle.SetTextFont(42);
gStyle.SetTimeOffset(0)
#gStyle.SetTitleAlign(33)
gStyle.SetTitleX(.3)
def set_palette(ncontours=50):
    """Set a color palette from a given RGB list
    stops, red, green and blue should all be lists of the same length
    see set_decent_colors for an example"""
    stops = [0.00, 0.25, 0.75, 1.00]
    red   = [0.00, 1.00, 1.00, 1.00]
    green = [1.00, 1.00, 0.70, 0.00]
    blue  = [0.00, 0.00, 0.00, 0.00]
    s = array('d', stops)
    r = array('d', red)
    g = array('d', green)
    b = array('d', blue)
    npoints = len(s)
    TColor.CreateGradientColorTable(npoints, s, r, g, b, ncontours)
    gStyle.SetNumberContours(ncontours)


histdir = os.getenv('TUCSRESULTS','.')+'/output/'
plotdir = os.getenv('TUCSPLOTS','plots')+'/'

#files used in 2018
#histfiles=['.total','.pre2011','.2011-022013','.M5','.2015','.2016','.2017', '' ]
#files used in 2022
histfiles=['.total','.preRUN3', '' ]
cmd="hadd -f "
for f in histfiles:
   cmd += histdir + 'Tucs.HIST' + f + '.root '
os.system(cmd)
f = TFile(histdir+'Tucs.HIST' + histfiles[0] + '.root')
f2 = TFile(histdir+'Tucs.HIST' + histfiles[-1] + '.root')
set_palette()
c1 = TCanvas()
#c1.Divide(2,2)
#pp=1
#for cell in ['','A','BC','D']:
cell = ''
#c1.cd(pp)
#c1.GetPad(pp).SetGridx(1)
#c1.GetPad(pp).SetGridy(1)
#c1.GetPad(pp).SetTickx(1)
#c1.GetPad(pp).SetTicky(1)
c1.SetGridx(1)
c1.SetGridy(1)
c1.SetTickx(1)
c1.SetTicky(1)
h = f2.Get('h_etaphi'+cell+'_badCell')
#h = f2.Get('h_etaphi'+cell+'_maskedCell')
#h = f.Get('h_etaphi'+cell+'_badCell')
h2 = f.Get('h_timeline_masked')
h3 = f.Get('h_timeline_maskedCell')

######h2.SetPoint(h2.GetN()-1,1296647000,2.055)
h2.GetXaxis().SetNdivisions(8,False)
h2.GetXaxis().SetTimeDisplay(1)
h2.GetXaxis().SetTimeFormat("%b-%y")
#if pp==1:
#    h.Draw('lego2')
#else:
#    h.Draw('colz')
#    c1.GetPad(pp).SetFrameFillColor(kGreen)
h.SetMaximum(3)
h.Draw('colz')
c1.SetFrameFillColor(kGreen)
h.GetXaxis().SetTitleOffset(0.8)
h.GetYaxis().SetTitleOffset(0.8)

#this takes the date from the final point on the timeline plot and adds it to the title of the 2-d masking plot
#pointX=ctypes.c_double()
#pointY=ctypes.c_double()
h2.Sort()
x=ctypes.c_double()
y=ctypes.c_double()

xvalue=[]
for i in range (0, h2.GetN()):
    h2.GetPoint(i,x,y)
    xvalue.append(x.value)
    
h2.GetPoint(xvalue.index(max(xvalue)),x,y)
#masked_Ch = "%.3f" % y.value
masked_Ch = "%.2f" % y.value
   
#h2.GetPoint( h2.GetN()-1,pointX,pointY)

Udate=datetime.fromtimestamp(int(x.value))
date=TString()
date=Udate.strftime("%Y-%m-%d")
h.SetTitle( h.GetTitle() +" "+date )

latex =TLatex()
#latex.DrawLatex(0.65,3.6,'ATLAS Internal');
latex.DrawLatex(0.75,3.6,'ATLAS Preliminary');
latex.DrawLatex(0.75,3.3,'Tile Calorimeter');	#splitline uses too much whitespace
#latex.DrawLatex(0.6,3.3,'ATLAS Preliminary');
#latex.DrawLatex(0.6,3.3,'ATLAS Internal');
#pp+=1
c1.Update()
#c1.SaveAs(plotdir+"map2d.png")
#c1.SaveAs(plotdir+"map2d.eps")
#c1.SaveAs(plotdir+"map2d.C")
c1.SaveAs(plotdir+"maskedEtaPhi.png")
c1.SaveAs(plotdir+"maskedEtaPhi.eps")
c1.SaveAs(plotdir+"maskedEtaPhi.C")
c1.SaveAs(plotdir+"maskedEtaPhi.pdf")

ymax=5.5
c2 = TCanvas("c2","c2",900,500)
#leg2 = TLegend(0.75,0.85,0.98,0.98)
#leg2 = TLegend(0.14,0.55,0.37,0.9)
leg2 = TLegend(0.14,0.70,0.34,0.9)
leg2.SetBorderSize(1)
#actual time period
h3.Draw()
ymax=h3.GetYaxis().GetXmax()
maintBox = TBox(1229295600,-0.0,1243807200,ymax)
h2.Sort()
#h2.LabelsOption("u");
#h2.Draw('ap')
#stopping box at X=0 for presentation purposes
maintBox = TBox(h2.GetXaxis().GetBinLowEdge(1),-0.0,1243807200,ymax)
h2.SetTitle('Evolution of Masked Channels and Cells '+date)
h2.GetYaxis().SetRangeUser(-0.0,ymax)
h2.SetMarkerColor(kRed)
h2.GetXaxis().SetTitleOffset(0.8)
h2.GetYaxis().SetTitleOffset(0.8)
c2.SetGridx(1)
c2.SetGridy(1)
h3.SetTitle('Evolution of Masked Cells '+date)
h3.GetYaxis().SetRangeUser(-0.0,ymax)
h3.Set(h3.GetN()+1)
#h3.SetPoint(h3.GetN()-1,1296647000,1.542)
#h3.SetPoint(h3.GetN()-2,1298323416,1.389)
#if pp==1:
h3.Sort()
timevalue=[]
for i in range (0, h3.GetN()):
    h3.GetPoint(i,x,y)
    timevalue.append(x.value)

h3.GetXaxis().SetNdivisions(8,False)
h3.GetXaxis().SetTimeDisplay(1)
h3.GetXaxis().SetTimeFormat("%b-%y")
h3.GetPoint(timevalue.index(max(timevalue)),x,y)
time=x.value
masked_cell=y.value
#str_masked_cell= "%.3f" % masked_cell
str_masked_cell= "%.2f" % masked_cell

#leg2.AddEntry(h2,'Masked Channels '+masked_Ch+'%','p')

#h3.Draw('psame')
h3.Draw('ap')
h3.SetMarkerColor(kBlue)
h3.GetXaxis().SetTitleOffset(0.8)
h3.GetYaxis().SetTitleOffset(0.8)
#leg2.AddEntry(h3,'Masked Cells '+str_masked_cell+'%','p')
#leg2.SetBorderSize(0)
#leg2.SetFillStyle(0)
leg2.AddEntry(h3,'#splitline{Masked Cells}{'+str_masked_cell+'%}','p')
maintBox.Draw()
maintBox.SetFillStyle(3001)
maintBox.SetFillColor(kRed)
maintBox1 = TBox(1293087600,-0.0,1294963200,ymax)
maintBox1.SetFillStyle(3001)
maintBox1.SetFillColor(kRed)
maintBox1.Draw()
maintBox2 = TBox(1324543746,-0.0,1328172546,ymax)
maintBox2.SetFillStyle(3001)
maintBox2.SetFillColor(kRed)
maintBox2.Draw()
maintBox3 = TBox(1360882800,-0.0,1404165600,ymax)
maintBox3.SetFillStyle(3001)
maintBox3.SetFillColor(kRed)
maintBox3.Draw()
maintBox4 = TBox(1405375200,-0.0,1409868000,ymax)
maintBox4.SetFillStyle(3001)
maintBox4.SetFillColor(kRed)
maintBox4.Draw()
leg2.Draw()
leg2.AddEntry(maintBox,'Maintenance','f')
#ap2 = TPaveText(0.2,0.8,0.5,0.9,"NDC")
#ap2.AddText("Atlas Preliminary")
#ap2.SetBorderSize(0)
#ap2.SetFillColor(0)
#ap2.SetFillStyle(4000)
#ap2.Draw()
latex.SetNDC()
#latex.DrawLatex(0.65,0.92,'ATLAS Preliminary');
c2.Update()
#c2.SaveAs(plotdir+"timeline.png")
c2.SaveAs(plotdir+"timeline_2012.png")
c2.SaveAs(plotdir+"luca2010evolution.png")
c2.SaveAs(plotdir+"luca2010evolution.eps")
#c2.SaveAs(plotdir+"timeline.C")
#c2.SaveAs(plotdir+"timeline.eps")
c2.SaveAs(plotdir+"timeline_2012.eps")
print ("percentage of masked channels: "+masked_Ch)
print ("percentage of masked cells: "+str_masked_cell)

c3 = TCanvas("c3","c3",900,500)
leg3 = TLegend(0.1,0.10,0.5,0.3)
#leg3 = TLegend(0.5,0.10,0.95,0.3)
leg3.SetBorderSize(1)
c3.SetGridx(1)
c3.SetGridy(1)

h2.Draw();
h3.Draw();
#h2.GetXaxis().SetRangeUser(1265000000 , 1285759000.0)
#h3.GetXaxis().SetRangeUser(1265000000 ,  1285759000.0)
h2.GetXaxis().SetRangeUser(1265000000 , time+1000)
#h2.GetXaxis().SetRangeUser(1293840000 , time+1000)
h3.GetXaxis().SetRangeUser(1265000000 , time+1000)
#h3.GetXaxis().SetRangeUser(1293840000 , time+1000)
h2.GetYaxis().SetRangeUser(-0.1,6.5)
h3.GetYaxis().SetRangeUser(-0.1,6.5)
h3.SetMarkerColor(kBlue)
h3.GetXaxis().SetTitleOffset(0.8)
h3.GetYaxis().SetTitleOffset(0.8)
h2.SetMarkerColor(kRed)
h2.GetXaxis().SetTitleOffset(0.8)
h2.GetYaxis().SetTitleOffset(0.8)
h3.SetTitle('Evolution of Masked Channels and Cells:' +" "+date)
h3.Draw('ap')
#h2.GetXaxis().SetTimeFormat("%d\/%m");
h3.GetXaxis().SetTimeFormat("%y-%m-%d");
h2.Draw('psame')
leg3 = TLegend(0.63,0.58,0.87,0.87)
leg3.AddEntry(h2,'Masked Channels '+masked_Ch+'%','p')
leg3.AddEntry(h3,'Masked Cells '+str_masked_cell+'%','p')
leg3.SetBorderSize(0)
leg3.SetFillStyle(0)
leg3.Draw()
latex.SetNDC()
#latex.DrawLatex(0.65,0.92,'ATLAS Preliminary');
#c3.Update()
c3.SaveAs(plotdir+"timeline_2010.png")
c3.SaveAs(plotdir+"timeline_2010.eps")

h2.Draw();
h3.Draw();
#h2.GetXaxis().SetRangeUser(1265000000 , 1285759000.0)
#h3.GetXaxis().SetRangeUser(1265000000 ,  1285759000.0)
h2.GetXaxis().SetRangeUser(1293840000, time+1000)
h3.GetXaxis().SetRangeUser(1293840000, time+1000)
h2.GetYaxis().SetRangeUser(-0.1,6.5)
h3.GetYaxis().SetRangeUser(-0.1,6.5)
h3.SetMarkerColor(kBlue)
h3.GetXaxis().SetTitleOffset(0.8)
h3.GetYaxis().SetTitleOffset(0.8)
h2.SetMarkerColor(kRed)
h2.GetXaxis().SetTitleOffset(0.8)
h2.GetYaxis().SetTitleOffset(0.8)
h3.SetTitle('Evolution of Masked Channels and Cells:' +" "+date)
h3.Draw('ap')
ymax=6.5;
maintBox1 = TBox(1293087600,-0.1,1294963200,ymax)
maintBox1.SetFillStyle(3004)
maintBox1.SetFillColor(kRed)
maintBox1.Draw()
#maintBox2 = TBox(1324543746,-0.1,1328172546,ymax)
maintBox2 = TBox(1323318673,-0.1,1325232436,ymax)
maintBox2.SetFillStyle(3004)
maintBox2.SetFillColor(kRed)
maintBox2.Draw()
maintBox3 = TBox(1360882800,-0.1,1403647200,ymax)
maintBox3.SetFillStyle(3004)
maintBox3.SetFillColor(kRed)
maintBox3.Draw()
maintBox4 = TBox(1405807200,-0.1,1409522400,ymax)
maintBox4.SetFillStyle(3004)
maintBox4.SetFillColor(kRed)
maintBox4.Draw()
h3.Draw('p')
#h3.GetXaxis().SetRangeUser(1293840000, 1416870000)
#h2.GetXaxis().SetTimeFormat("%d\/%m");
#h3.GetXaxis().SetTimeFormat("%d\/%m");
h3.GetXaxis().SetTimeFormat("%b-%y");
h3.GetYaxis().SetTitle("[%]");
h2.Draw('psame')
#leg3 = TLegend(0.5,0.65,0.87,0.85)
leg3 = TLegend(0.63,0.58,0.87,0.87)
#leg3.SetTextFont(42);
leg3.SetTextSize(0.04);
leg3.AddEntry(h2,'#splitline{Masked Channels}{('+masked_Ch+'%)}','p')
leg3.AddEntry(h3,'#splitline{Masked Cells}{('+str_masked_cell+'%)}','p')
leg3.AddEntry(maintBox1,'Maintenance','f')
#leg3.SetBorderSize(0)
#leg3.SetFillStyle(0)
leg3.Draw()
latex.SetNDC()
#latex.DrawLatex(0.65,0.96,'ATLAS Preliminary');
#latex.DrawLatex(0.65,0.92,'Tile Calorimeter'); # splitlie uses too much whitespace
#latex.DrawLatex(0.65,0.92,'ATLAS Preliminary');
#latex.DrawLatex(0.65,0.92,'ATLAS Internal');
#latex.DrawLatex(0.82,0.21,'M6');
#latex.DrawLatex(0.86,0.26,'M7');
#latex.DrawLatex(0.90,0.30,'M8');
#c3.Update()
c3.SaveAs(plotdir+"timeline_2015.png")
c3.SaveAs(plotdir+"timeline_2015.eps")
c3.SaveAs(plotdir+"timeline_2015.C")
c3.SaveAs(plotdir+"timeline_2015.root")
c3.SaveAs(plotdir+"timeline_2015.pdf")

h2.Draw();
h3.Draw();
#h2.GetXaxis().SetRangeUser(1265000000 , 1285759000.0)
#h3.GetXaxis().SetRangeUser(1265000000 ,  1285759000.0)
h2.GetXaxis().SetRangeUser(1293840000, time+1000)  # it changed for Tomas Run1 mainatance, actual value for public plot for twiki 1293840000
h3.GetXaxis().SetRangeUser(1293840000, time+1000)
h2.GetYaxis().SetRangeUser(-0.1,6.5)
h3.GetYaxis().SetRangeUser(-0.1,6.5)
h3.SetMarkerColor(kBlue)
h3.GetXaxis().SetTitleOffset(1.0)
h3.GetYaxis().SetTitleOffset(0.8)
h2.SetMarkerColor(kRed)
h2.GetXaxis().SetTitleOffset(0.8)
h2.GetYaxis().SetTitleOffset(0.8)
h3.SetTitle('Evolution of Masked Channels and Cells:' +" "+date)
h3.Draw('ap')
ymax=6.5;
maintBox1 = TBox(1293087600,-0.1,1294963200,ymax)
maintBox1.SetFillStyle(3004)
maintBox1.SetFillColor(kRed)
maintBox1.Draw()
#maintBox2 = TBox(1324543746,-0.1,1328172546,ymax)
maintBox2 = TBox(1323318673,-0.1,1325232436,ymax)
maintBox2.SetFillStyle(3004)
maintBox2.SetFillColor(kRed)
maintBox2.Draw()
maintBox3 = TBox(1360882800,-0.1,1403647200,ymax)
maintBox3.SetFillStyle(3004)
maintBox3.SetFillColor(kRed)
maintBox3.Draw()
maintBox4 = TBox(1405807200,-0.1,1409522400,ymax)
maintBox4.SetFillStyle(3004)
maintBox4.SetFillColor(kRed)
maintBox4.Draw()
#maintBox5 = TBox(1450656000,-0.1,1451865600,ymax)
#maintBox5 = TBox(1450656000,-0.1,1461283200,ymax) # First collision run of 2016
maintBox5 = TBox(1450656000,-0.1,1454976000,ymax) # First cosmic run of 2016
maintBox5.SetFillStyle(3004)
maintBox5.SetFillColor(kRed)
maintBox5.Draw()
maintBox6 = TBox(1481955682,-0.1,1489645282,ymax) # First cosmic run of 2016
maintBox6.SetFillStyle(3004)
maintBox6.SetFillColor(kRed)
maintBox6.Draw()
maintBox7 = TBox(1512774000,-0.1,1518476400,ymax) # First cosmic run of 2016
maintBox7.SetFillStyle(3004)
maintBox7.SetFillColor(kRed)
maintBox7.Draw()
h3.Draw('p')
#h3.GetXaxis().SetRangeUser(1293840000, 1416870000)
#h2.GetXaxis().SetTimeFormat("%d\/%m");
#h3.GetXaxis().SetTimeFormat("%d\/%m");
h3.GetXaxis().SetTimeFormat("%b-%y");
h3.GetXaxis().SetTitle("month-year");
h3.GetYaxis().SetTitle("Evolution of Masked Channels and Cells [%]");
h2.Draw('psame')
#leg3 = TLegend(0.5,0.65,0.87,0.85)
leg3 = TLegend(0.63,0.58,0.87,0.87)
#leg3.SetTextFont(42);
leg3.SetTextSize(0.03); # was (0.04) in Run2
leg3.AddEntry(h2,'#splitline{Masked Channels}{('+masked_Ch+'%)}','p')
leg3.AddEntry(h3,'#splitline{Masked Cells}{('+str_masked_cell+'%)}','p')
leg3.AddEntry(maintBox1,'Maintenance','f')
#leg3.SetBorderSize(0)
#leg3.SetFillStyle(0)
leg3.Draw()
latex.SetNDC()
#latex.DrawLatex(0.65,0.96,'ATLAS Internal');
latex.DrawLatex(0.65,0.96,'ATLAS Preliminary');
latex.DrawLatex(0.65,0.92,'Tile Calorimeter'); # splitlie uses too much whitespace
#c3.Update()
c3.SaveAs(plotdir+"timeline_2018.png")
c3.SaveAs(plotdir+"timeline_2018.eps")
c3.SaveAs(plotdir+"timeline_2018.C")
c3.SaveAs(plotdir+"timeline_2018.root")
c3.SaveAs(plotdir+"timeline_2018.pdf")
h2.Draw();
h3.Draw();
#h2.GetXaxis().SetRangeUser(1293840000, time+1000)
h3.GetXaxis().SetRangeUser(1293840000, time+1000)
#h2.GetYaxis().SetRangeUser(-0.1,5.5)
h3.GetYaxis().SetRangeUser(-0.1,5.5)
h3.SetMarkerColor(kBlue)
h3.GetXaxis().SetTitleOffset(0.8)
h3.GetYaxis().SetTitleOffset(0.8)
#h2.SetMarkerColor(kRed)
#h2.GetXaxis().SetTitleOffset(0.8)
#h2.GetYaxis().SetTitleOffset(0.8)
h3.SetTitle('Evolution of Masked Cells: '+" "+date )
h3.Draw('ap')
#h2.GetXaxis().SetTimeFormat("%d\/%m");
#h3.GetXaxis().SetTimeFormat("%d\/%m");
h3.GetXaxis().SetTimeFormat("%y-%m-%d");
h3.GetYaxis().SetTitle("[%]");
#h2.Draw('psame')
leg3 = TLegend(0.1,0.70,0.5,0.9)
#leg3.AddEntry(h2,'Masked Channels '+masked_Ch+'%','p')
leg3.AddEntry(h3,'Masked Cells '+str_masked_cell+'%','p')
leg3.SetBorderSize(0)
leg3.SetFillStyle(0)
leg3.Draw()
latex.SetNDC()
#latex.DrawLatex(0.65,0.92,'ATLAS Preliminary');
#c3.Update()
c3.SaveAs(plotdir+"timeline.png")
c3.SaveAs(plotdir+"timeline.eps")
###c3.SaveAs(plotdir+"timeline.C") # hack by Tomas
#raw_input()


