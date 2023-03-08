#!/bin/env python
# Author: nils.gollub@cern.ch

import sys, os
import time
import ROOT
import logging
from ROOT import TCanvas, TH1D, TGraph, TArrayD
from . import TileDCSDataGrabber
from src.oscalls import *


class TileDCSDataPlotter:

    #_______________________________________________________________________________________
    def __init__( self, argv, useCool, verbose, dbstring=None ):

        dbSource = "ORACLE"
        if useCool:
            dbSource = "COOL"
        logLvl = logging.WARNING
        if verbose:
            logLvl = logging.DEBUG
            
        self.dataGrabber = TileDCSDataGrabber.TileDCSDataGrabber(dbSource, logLvl, dbstring) 
        self.info = self.dataGrabber.info

        self.cmd     = argv[1]
        self.drawer  = argv[2]
        self.varExp  = argv[3]
        beg          = argv[4]
        end          = argv[5]
        self.iovBeg  = int(time.mktime(time.strptime(beg,"%Y-%m-%d %H:%M:%S")))
        self.iovEnd  = int(time.mktime(time.strptime(end,"%Y-%m-%d %H:%M:%S")))
        self.cutExp  = ""
        if len(argv) >6:
            self.cutExp = argv[6]
        beg = beg.replace(' ','_')
        end = end.replace(' ','_')
        self.outName   = self.drawer+"_"+self.varExp+"__"+beg+"__"+end
        self.outName   = self.outName.replace('/',':')    
        self.outName   = self.outName.replace('(','0')    
        self.outName   = self.outName.replace(')','0')    
        print("---> OUTNAME: " , self.outName)
        if len(argv) >7:
            self.outName = argv[7]

        timeBegInfo = time.localtime(self.iovBeg);
        timeEndInfo = time.localtime(self.iovEnd);
        self.rangeStr = "FROM: "+time.asctime(timeBegInfo)+"  UNTIL: "+time.asctime(timeEndInfo)


    #_______________________________________________________________________________________
    def parseVarExpression(self, varExpression):

        knownVars = self.info.get_all_variables()
        varDict = {}
        for var in knownVars:
            pos = varExpression.find(var)
            if pos>-1:
                if pos in varDict:
                    #=== other variable found at same place?
                    #=== -> choose the longer one
                    oldVar = varDict[pos]
                    if len(oldVar) > len(var):
                        var = oldVar
                varDict[pos] = var

        #=== check for overlap
        positions = sorted(varDict.keys())
        posLength = len(positions)
        if posLength > 1:
            iPos = 1
            while iPos < posLength:
                if positions[iPos] < positions[iPos-1]+len(varDict[positions[iPos-1]]):
                    varDict.pop(positions[iPos])
                    positions.pop(iPos)
                    posLength=len(positions)
                else:
                    iPos+=1
                    
        varList = list(varDict.values())
        if "ALL_LVPS_AI" in varExpression:
            varList.extend(list(self.info.vars_LVPS_AI.keys()))
        if "ALL_LVPS_STATES" in varExpression:
            varList.extend(list(self.info.vars_LVPS_STATES.keys()))
        if "ALL_HV" in varExpression:
            varList.extend(list(self.info.vars_HV.keys()))
        return list(set(varList))


    #_______________________________________________________________________________________
    def getTree(self):

        #=== parse for variables needed
        varList = self.parseVarExpression(self.varExp+self.cutExp)

        #=== get the variable
        t = self.dataGrabber.getDCSTree(self.iovBeg, self.iovEnd, self.drawer.split(","), varList)
        if t.GetEntries()==0:
            print("ERROR: No data in time intervall!")
            sys.exit(1)
        else:
            print("Found number of entries: ", t.GetEntries())

        #=== append drawer to all variables
        if self.cmd!="tree":
            for var in varList:
                self.varExp = self.varExp.replace(var,self.drawer+"."+var)
                self.cutExp = self.cutExp.replace(var,self.drawer+"."+var)
            print("self.varExp: ", self.varExp)
            print("self.cutExp: ", self.cutExp)

        return t


    #_______________________________________________________________________________________
    def getTimelinePlot(self):
        """
        Returns a TCanvas with the variable plotted vs time.

        """

        ROOT.gStyle.SetOptStat(0)
        t = self.getTree()

        if t.GetEntries()==1:
            print("ERROR: Only one data point, need at least 2")
            print("---> Try increasing the time span")
            sys.exit(1)

        #=== extract the values
        t.Draw(self.varExp+":EvTime",self.cutExp,"goff");
        n = t.GetSelectedRows()
        print("n=",n)
        x = t.GetV2()
        y = t.GetV1()

        #=== fix for **** root time convention and add end time
        offset = 788918400 # = 1.1.1995(UTC), the root offset
        xarr = TArrayD(n+1)
        for i in range(n):
            xarr[i] = x[i]-offset
        xarr[n] = self.iovEnd-offset

        #=== create and fill histogram with values
        title = self.rangeStr+";;"+self.varExp
        h = TH1D("hDCS",title,n,xarr.GetArray())
        for i in range(n):
            center = h.GetBinCenter(i+1)
            h.Fill(center,y[i])

        #=== set time display
        sec_min = 60
        sec_hrs = sec_min*60
        sec_day = sec_hrs*24
        sec_mon = sec_day*30
        timeDiff = self.iovEnd-self.iovBeg
        h.GetXaxis().SetTimeFormat("%S")
        h.SetXTitle("time [seconds]")
        if timeDiff > 2*sec_mon:
            h.GetXaxis().SetTimeFormat("%m")
            h.SetXTitle("time [month]")
        elif timeDiff > 2*sec_day:
            h.GetXaxis().SetTimeFormat("%d(%H)")
            h.SetXTitle("time [day(hour)]")
        elif timeDiff > 2*sec_hrs:
            h.GetXaxis().SetTimeFormat("%H:%M")
            h.SetXTitle("time [hour:min]")
        elif   timeDiff > 2*sec_min:
            h.GetXaxis().SetTimeFormat("%M")
            h.SetXTitle("time [min]")
        h.GetXaxis().SetTimeDisplay(1)
        h.SetLineColor(2)
        return h


    #_______________________________________________________________________________________
    def getDistributionPlot(self):
        """
        Returns a TCanvas with the variable distribution plotted (using weights)

        """

        t = self.getTree()
        cut = "weight"
        if self.cutExp!="":
            cut = "weight*("+self.cutExp+")"
        t.Draw(self.varExp,cut,"goff");
        h = ROOT.gDirectory.Get("htemp")
        h.SetXTitle(self.varExp.split(":")[0])
        h.SetTitle(self.rangeStr)
        h.SetName("TileDCSDataPlotter")
        h.SetLineColor(2)
        h.SetMarkerColor(2)
        return h


#================================================================================================


#==== interactive use
callName = os.path.basename(sys.argv[0])
if callName=="TileDCSDataPlotter.py":

    #=== check if we are in batch mode
    batch = False
    if "-b" in sys.argv:
        batch=True
        sys.argv.remove("-b")


    #=== check if we are in Oracle mode
    useCool = False
    if "--cool" in sys.argv:
        useCool=True
        sys.argv.remove("--cool")


    #=== check if we are in verbose mode
    verbose = False
    if "-v" in sys.argv:
        verbose=True
        sys.argv.remove("-v")

    #=== catch invalid commands
    cmd = sys.argv[1]
    if not(cmd=="plot" or cmd=="dist" or cmd=="tree"):
        print(""" Please use one of the following commands: plot, dist, tree !""")
        sys.exit(1)

    #=== command is recognized, we go on....
    ROOT.gROOT.SetBatch()
    dp = TileDCSDataPlotter(sys.argv, useCool, verbose)

    #=== no graphics if only get tree
    if cmd == "tree":
        t = dp.getTree()
        f = ROOT.TFile(os.path.join(getPlotDirectory(),dp.outName+".root"), "recreate")
        t.Write()
        f.Close()

    else:
        #=== graphics output below -> configure style and canvas
        ROOT.gROOT.SetStyle("Plain")
        ROOT.gROOT.ForceStyle()
        can = TCanvas("c_TileDCSDataPlotter","c_TileDCSDataPlotter")
    
        #=== simple timeline plot
        if cmd =="plot":
            h = dp.getTimelinePlot()
            can.SetGridx()
            can.SetGridy()
            h.Draw()

        #=== distribution plot (using weights)
        elif cmd =="dist":
            h = dp.getDistributionPlot()
            dim = dp.varExp.count(':')
            if dim==0:
                h.Draw()
            elif dim==1:
                h.Draw("box")
            else:
                h.Draw()
        
        #=== save output in eps and png
        can.Print(os.path.join(getPlotDirectory(),dp.outName+".eps"))
        can.Print(os.path.join(getPlotDirectory(),dp.outName+".png"))
    
        #=== display plot 
        if not batch:
            os.system("display "+os.path.join(getPlotDirectory(),dp.outName+".png"))
