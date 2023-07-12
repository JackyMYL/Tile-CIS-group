#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Author: Cora Fischer
#
# A Mbias macro to produce plots: lumi coefficient vs module for given cell
#

import os, sys
os.chdir(os.getenv('TUCS','.'))

exec(open('src/mbias/getDatesForCool.py').read(), globals())

exec(open('src/load.py').read(), globals()) # don't remove this!


# the region is not given by the user, we use all the cells we have to produce the plot
# the command line reads: python macros/mbias/getCoeffficient.py --region=cellName

runs =[]

selected_region = "EBC_m40_c12_highgain" #just any region



runs.append(276262)

#runs = '2012-04-01'
#runs2 = '2012-12-31' # for some reason no effect for us, we have a requirement on the runNumber in the worker to avoid crashes
run_type = "MBias" 

#now we loop over all cells when calling the worker GetLumiCoefficient.py
processors = []

processors.append(Use(run=runs, region=selected_region, runType=run_type))
processors.append(ReadMBias_2015(processingDir="/afs/cern.ch/user/c/cfischer/TUCS_QT/Tucs/",doSingleRun=True, doRatio=False, checkCell=False))
processors.append(CurrentVsModule_2015(checkCell=region,LumiBegin=150,LumiRange=num))



Go(processors)




