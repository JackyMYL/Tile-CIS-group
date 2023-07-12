#!/usr/bin/env python
# Author: Christopher Tunnell <tunnell@hep.uchicago.edu>
#
# Refit the CIS scans but introducing systematic errors
# in order to make the errors and chi2 more realistic
#
# March 05, 2009
#

import os
os.chdir(os.getenv('TUCS','.'))
exec(open('src/load.py').read(), globals()) # don't remove this!

selected_region = ''
u1 = Use(run='-1 month', useDateProg=True, runType='CIS', region=selected_region)

x1 = ReadCISFile(getScans=True)

c = CalibBadBit()

Go([u1, x1, CISSysRefit()])

