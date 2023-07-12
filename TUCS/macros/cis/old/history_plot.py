#!/usr/bin/env python
# Author: Christopher Tunnell <tunnell@hep.uchicago.edu>
#
# Make a TH1F of the time deviations
#
# March 05, 2009
#

import os
os.chdir(os.getenv('TUCS','.'))
exec(open('src/load.py').read(), globals()) # don't remove this!

selected_region = ''
u1 = Use(run='-1 month', useDateProg=True, runType='CIS', region=selected_region)

x1 = ReadCISFile()

c = CalibBadBit()

Go([u1, x1, ReadDB(), c, IsDefaultCalib(), HistoryPlot()])

