#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Author: Cora Fischer
#
# A Mbias macro to produce current over inst. lumi plots
#

import os, sys
import numpy as np
os.chdir(os.getenv('TUCS','.'))

exec(open('src/mbias/getDatesForCool.py').read(), globals())

exec(open('src/load.py').read(), globals()) # don't remove this!

# if you want the current for a specific cell averaged over A and C side and all modules, specify --region="Cellname" in command line, if you want the current of a special pmt, then give region as usual in
# format part_mXX_cXX, if you do not specify anything, the default selected_region EBC_m40_c12_highgain will be analysed (no particular reason for that), so please specify a region!
# you can specify the number of consecutive entries to average over by --num=X, or if you choose 1 it will not average
# the command line reads: python macros/mbias/plotPMTCurrentVsInstLumi.py --region="XXX" --num=X
# runs are fixed for the moment....

#if region.startswith("EB") or region.startswith("LB"): # if partition is given but nothing else
#   if 'm' not in region or 'c' not in region:
#        print "you have to specify a module and channel if you don't give a cell name!"
#        sys.exit(2)

runs = []

selected_region = region
Cell = None
print region 
#distinguish different kind of inputs: specific pmts (Part_mXX_cXX) and cells
#if "m" in region:
#   selected_region=region
#else:
#   Cell = region 
#print Cell


# runs.append(298633)
# runs.append(299584)
# runs.append(302872)
# runs.append(303846)
# runs.append(310634)

#runs,Nlumiblocks = np.loadtxt("MinBias_goodruns.txt",unpack=True,dtype=int)

#print "Cell = ",Cell
#print "selected_region = ",region	


run_type = "MBias"

run = sys.argv[1]


print "\nReading run %s\n"%run

Go([ 
      Use(run=[int(run)], region=selected_region, runType=run_type),
      ReadMBias_2015(doSingleRun=True, doRatio=False, checkCell=Cell),
      PlotPMTCurrentVsInstLumi_2015perCell(checkCell=Cell, num_average=1),
      ])

# for n,run in enumerate(runs):
# 	if run > 308084: continue
# 	if Nlumiblocks[n]<100: continue
# 	print "\nReading run %s\n"%run
# 	Go([
# 		Use(run=[run], region=selected_region, runType=run_type),
#       	ReadMBias_2015(doSingleRun=True, doRatio=False, checkCell=Cell),
#       	PlotPMTCurrentVsInstLumi_2015perCell(checkCell=Cell, num_average=1),
#       	])
