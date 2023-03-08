#!/usr/bin/env python
# Author: Christopher Tunnell <tunnell@hep.uchicago.edu>
#
# Tune the fixed-charge RMS and chi2 quality flags
#
# March 05, 2009
#

import os
os.chdir(os.getenv('TUCS','.'))
exec(open('src/load.py').read(), globals()) # don't remove this!

runs = '-28 days' # Use the last month of runs
#runs = [102208, 102501, 102893, 103322, 103347, 103864, 104019, 104051, 104131]
#runs = [190748]

plot_bad = True ## Don't change this from True ...keeping it as a switch for now.

u = Use(run=runs, runType='CIS')
x = ReadCIS()
r = GetScans(all=True,getScansRMS=True)
t = TuneCuts(probbad=plot_bad)

Go([u,x,ReadDB(),CISFlagProcedure(),r,t,])

