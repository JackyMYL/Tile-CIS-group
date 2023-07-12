#!/usr/bin/env python
# Author: Cora Fischer
#
# for each run, plot PMT current ratio of A13/D5 distribution, fit with gaussian, plot as function of time
#

import os
os.chdir(os.getenv('TUCS','.'))
exec(open('src/load.py').read(), globals()) # don't remove this!
exec(open('src/mbias/getDatesForCool.py').read(), globals())


runs =[]
 	
#runs.append(208485)
#runs.append(206955)
#runs.append(215456)
#runs.append(213796)

#runs.append(200863)
#runs.append(202668)
#runs.append(202712)
#runs.append(203027)
#runs.append(204071)
#runs.append(204265)
#runs.append(207582)
#runs.append(208982)
#runs.append(209787)
#runs.append(210308)
#runs.append(213250)
#runs.append(213951)
#runs.append(214176)
#runs.append(214721)
#runs.append(214758)

#62 out of 64 modules have good entries EBA
#runs.append(213796)
#runs.append(203779)
#runs.append(202798)
#runs.append(206971)
#runs.append(203353)
#runs.append(202660)
#runs.append(207982)
#runs.append(206962)
#runs.append(200863)#c

#63 out of 64 modules have good entries EBC
runs.append(207490)
runs.append(209899)
runs.append(203027)#c
runs.append(210302)
runs.append(209787)#c
runs.append(212172)
runs.append(202668)#c
runs.append(204955)
runs.append(203277)
runs.append(209995)
runs.append(214777)
runs.append(207306)
runs.append(206248)
runs.append(203636)
runs.append(212144)
runs.append(209183)
runs.append(202798)#b
runs.append(214390)
runs.append(212967)
runs.append(215473)
runs.append(200863)#c#b
runs.append(202660)#b
runs.append(213900)
runs.append(203258)
runs.append(207696)
runs.append(206253)

#runs.append(215473)
##runs.append(206848)# no events??
#runs.append(204265)
#doSingleRun = False
#if len(runs) == 1: doSingleRun =True
# runs = '2012-04-01' 
run_type = "MBias" 
#selected_region = "EBC_m22_c16_highgain" #
selected_region = "EBA_m01_c12_highgain" #doesn't matter what it is here
detectorRegion = region# "A13" # if you want to use the same as selected_region, leave this variable to None, but better use this option, otherwise it only takes one PMT channel
referenceCell = "D5"
side = None #you can also specify if you want only A or C-side analysed, if you leave it empty, it will average over both sides


#for i in range(len(runs)):

Go([
    Use(run=runs, region=selected_region, runType=run_type),
    ReadMBias(doSingleRun=False, doRatio = True, modnum=64, detector_region=detectorRegion, detector_side=side, refCell=referenceCell),
    PlotRatioPMTsVsTime(modnum=64, detector_region=detectorRegion),
   ])
