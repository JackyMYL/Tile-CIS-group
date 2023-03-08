#!/usr/bin/env python

# Contact: rute.pedro@cern.ch
# This root macro makes the delivered luminosity vs time graph

from ROOT import *
import sys

if len(sys.argv)>1:
    filename = sys.argv[1]
else:
    print "Provide input file name"
    exit()

fileLumi = TFile(filename+".root","RECREATE")

grLumi=TGraph(filename+".txt")
grLumi.Sort()
grLumi.SetName("Luminosity")

grIntLumi=TGraph()
grIntLumi.SetName("IntLuminosity")
grIntLumi.Set(0)

intLumi=0.
d=Double(0.)
p=1
for p in range(grLumi.GetN()):
    l = Double(0.)
    grLumi.GetPoint(p,d,l)
    intLumi+=l    
    grIntLumi.SetPoint(p,d,intLumi/1000.)
    #print "Setting point {} date {} lumi {} intlumi {}".format(p,d,l,intLumi)

grIntLumi.SetPoint(p+1,d+1,0)

grLumi.GetXaxis().SetTitle("Date")
grLumi.GetYaxis().SetTitle("Luminosity [pb^{-1}]")
grIntLumi.GetXaxis().SetTitle("Date")
grIntLumi.GetYaxis().SetTitle("Integrated Delivered Luminosity [fb^{-1}]")
print "Total Delivered Luminosity from {} {:.1f} [fb^{{-1}}]".format(filename,intLumi/1000.)
grIntLumi.SetTitle("Total Delivered Luminosity {:.1f} [fb^{{-1}}]".format(intLumi/1000.))

fileLumi.cd()
grLumi.Write()
grIntLumi.Write()

fileLumi.Close()

