#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Author: Cora Fischer
#
# A Mbias macro to produce plots: irradiation effect vs integrated charge
#

import os, sys
os.chdir(os.getenv('TUCS','.'))

#if os.environ.get('TUCS'):

exec(open('src/mbias/getDatesForCool.py').read(), globals())

exec(open('src/load.py').read(), globals()) # don't remove this!


# this script calls GetIntegrateCharge_2016_EB which reads txt files of mbias and laser variations, subtracts the laser from the mbias variation (->irradiation effect) 
# the time information is matche with the integrated lumi -> we calculate the charge using the lumi coeff of run 298633
# run simply with: macros/mbias/getIntegratedCharge2016.py

runs =[]

selected_region = "EBC_m40_c12_highgain" #just any region



runs.append(298633)

#runs = '2012-04-01'
#runs2 = '2012-12-31' # for some reason no effect for us, we have a requirement on the runNumber in the worker to avoid crashes
run_type = "MBias" 

#now we loop over all cells when calling the worker GetLumiCoefficient.py
processors = []

processors.append(Use(run=runs, region=selected_region, runType=run_type))
processors.append(ReadMBias_2015(doSingleRun=True, doRatio=False, checkCell=False))
processors.append(GetIntegratedCharge_2016_EB(LumiBegin=200,LumiRange=30))



Go(processors)




