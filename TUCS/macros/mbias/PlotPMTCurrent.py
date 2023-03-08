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
#runs.append(266904)
#runs.append(266919)
#runs.append(267152)
#runs.append(267638)
#runs.append(267639)
#runs.append(267167)
runs.append(338468)
#runs = '2012-04-01'
#doSingleRun = False
#if len(runs) == 1: doSingleRun =True
run_type = "MBias" 
#selected_region = "EBC_m22_c16_highgain" #
selected_region = "EBC_m13_c"#c02_highgain" #

for i in range(1,41):
    selected_region = "EBA_m13_c"
    if i<10:
        selected_region+="0"
    selected_region+=str(i)
    for j in ["_lowgain","_highgain"]:
        sregion=selected_region+j
        print "\n---- Doing selected_region: ",sregion,"\n"
        Go([ 
                Use(run=runs, region=sregion, runType=run_type),
                ReadMBias(processingDir="/afs/cern.ch/user/t/tilecali/w0/ntuples/mbias/2015/first_data/",doSingleRun=False),
                MBiasPlotPMTCurrent(),
                ])
        
