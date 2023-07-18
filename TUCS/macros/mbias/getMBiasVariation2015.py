#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Author: Cora Fischer
#
# A Mbias macro to produce plots: lumi coefficient vs eta for A,BC,D and E cells
#

import os, sys
os.chdir(os.getenv('TUCS','.'))

#if os.environ.get('TUCS'):

exec(open('src/mbias/getDatesForCool.py').read(), globals())

exec(open('src/load.py').read(), globals()) # don't remove this!


# run this giving a region (--region cellname)
# it will read in Mbias information from txt file and just add everything to a TGraph and print it

runs =[]

selected_region = "EBA_m01_c01_highgain" #just any region

region='A13'

runs.append(276262) # doesn't mean anything here
runs.append(298633)
runs.append(302872)
#runs = '2012-04-01'
#runs2 = '2012-12-31' # for some reason no effect for us, we have a requirement on the runNumber in the worker to avoid crashes
run_type = "MBias" 

processors = []

processors.append(Use(run=runs, region=selected_region, runType=run_type))
#processors.append(ReadMBias_2015(doSingleRun=True, doRatio=False, checkCell=False))# dummy, not needed
processors.append(GetMBiasVariations_2015(cellname=region))



Go(processors)




