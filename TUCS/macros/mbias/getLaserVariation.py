#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Author: Cora Fischer
#
# macro used by mbias to produce matching laser variations that we use later on
#

import os, sys
os.chdir(os.getenv('TUCS','.'))

#if os.environ.get('TUCS'):

exec(open('src/mbias/getDatesForCool.py').read(), globals())

exec(open('src/load.py').read(), globals()) # don't remove this!


# run this giving a region (--region cellname)
# it will read in laser information from txt file and just add everything to a TGraph and print it

runs =[]

selected_region = "EBC_m40_c12_highgain" #just any region



runs.append(276262) # doesn't mean anything here

#runs = '2012-04-01'
#runs2 = '2012-12-31' # for some reason no effect for us, we have a requirement on the runNumber in the worker to avoid crashes
run_type = "MBias" # don|t care, just for calling Use.py, the only input used will be from a txt file produced by different scripts

processors = []

processors.append(Use(run=runs, region=selected_region, runType=run_type))
#processors.append(ReadMBias_2015(doSingleRun=True, doRatio=False, checkCell=False))# dummy, not needed
processors.append(GetLaserVariations(cellname=region))



Go(processors)




