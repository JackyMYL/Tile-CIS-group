#!/usr/bin/env python
# Author: Cora Fischer
#
# for each run, plot PMT current distribution
#

import os
os.chdir(os.getenv('TUCS','.'))
exec(open('src/load.py').read(), globals()) # don't remove this!

runs =[]

	
runs.append(295147)
#runs.append(215456)
#runs.append(202668)
#runs.append(206848) no events??
#runs.append(204265)
#doSingleRun = False
#if len(runs) == 1: doSingleRun =True
run_type = "MBias" 
#selected_region = "EBC_m22_c16_highgain" #
selected_region = "EBC_m22_c17_highgain" #doesn't matter what it is here
#module = 'A13'

#for i in range(len(runs)):

Go([
    Use(run=runs, region=selected_region, runType=run_type),
    ReadMBias(doSingleRun=True),
    MBiasPlotPMTCurrentRun(module= 'A13'),
   ])
