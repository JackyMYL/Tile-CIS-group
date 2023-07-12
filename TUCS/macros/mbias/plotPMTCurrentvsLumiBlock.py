#!/usr/bin/env python
# Author: Cora Fischer
#
# A test for Mbias data integration
#

import os

exec(open('src/load.py').read(), globals()) # don't remove this!

runs =[]
#f = open('list.txt','r')
#for line in f:		#read run numbers from file
    #runs.append(int(line[:6]))	
	
#runs.append(206955)
#runs.append(215456)
#runs.append(202668)
runs.append(298609)

#runs.append(266904)
#runs.append(271595)

#doSingleRun = False
#if len(runs) == 1: doSingleRun =True
run_type = "MBias" 
selected_region = "LBA_m02_c14_highgain" #
#selected_region = "EBA_m01_c02_highgain" #
Go([ 
    Use(run=runs, region=selected_region, runType=run_type),
    ReadMBias_2015(doSingleRun=False),
    MBiasPlotPMTCurrentVsLB(),
    ])
