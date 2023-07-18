#!/usr/bin/env python
# Author: Cora Fischer
#
# plot mbias current vs lumiblock
#

import os
os.chdir(os.getenv('TUCS','.'))
exec(open('src/load.py').read(), globals()) # don't remove this!

runs =[]

	
#runs.append(201269)
#runs.append(201289)
#runs.append(202660)
#runs.append(202789)
#runs.append(203027)
#runs.append(203258)
#runs.append(203336)
#runs.append(203353)
#runs.append(203719)
	
#runs.append(206955)
#runs.append(215456)
#runs.append(202668)
#runs.append(201257)
runs.append(298609)

#doSingleRun = False
#if len(runs) == 1: doSingleRun =True
run_type = "MBias" 
#selected_region = "EBC_m22_c16_highgain" #
selected_region = "LBA_m02_c15_highgain" #module number is not important here
Go([ 
    Use(run=runs, region=selected_region, runType=run_type),
    ReadMBias_2015(doSingleRun=False, doRatio=True, modnum = 1, refCell="D1"),
    CurrentRatioVsLB(doRatio = True),
    ])
