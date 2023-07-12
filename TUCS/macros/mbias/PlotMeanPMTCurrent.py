#!/usr/bin/env python
# Author: Cora Fischer
#
# A test for Mbias data integration
#

import os
os.chdir(os.getenv('TUCS','.'))
exec(open('src/load.py').read(), globals()) # don't remove this!

runs =[]

	
#runs.append(206955)
#runs.append(215456)
#runs.append(202668)
#runs.append(206848) no events??
#runs.append(200863)
#runs.append(201257)
runs.append(267152)
#runs.append(267638)
#runs.append(267639)
#runs.append(270448)
#runs.append(270588)
#uns.append(270953)
#runs.append(271048)
#runs.append(271298)
#runs.append(271421)
#runs.append(271516)
#uns.append(271595)
#uns.append(271744)
#runs.append(272531)
#doSingleRun = False
#if len(runs) == 1: doSingleRun =True
run_type = "MBias" 
#selected_region = "EBC_m22_c16_highgain" #
selected_region = "EBA_m64_c17_highgain" #doesn't matter what it is here

Go([
    Use(run=runs, region=selected_region, runType=run_type),
    ReadMBias(processingDir="/afs/cern.ch/user/t/tilecali/w0/ntuples/mbias/2015/first_data/",doSingleRun=True),
    MBiasPlotMeanPMTCurrent(lb=230),
    ])
