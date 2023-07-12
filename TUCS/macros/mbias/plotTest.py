#!/usr/bin/env python
# Author: Cora Fischer
#
# A test for Mbias data integration
#

import os
os.chdir(os.getenv('TUCS','.'))
exec(open('src/load.py').read(), globals()) # don't remove this!

runs =[]

	
#runs.append(207865)
#runs.append(215456)
#runs.append(204265)
#runs.append(202668)
runs.append(266904)
#doSingleRun = False
#if len(runs) == 1: doSingleRun =True
run_type = "MBias" 
selected_region = "EBC_m22_c16_highgain" #not important at the moment
Go([ 
    Use(run=runs, region=selected_region, runType=run_type),
    ReadMBias(processingDir="/afs/cern.ch/user/t/tilecali/w0/ntuples/mbias/2015/first_data/", doSingleRun=True),
    TestMBiasPlot(),
    ])
