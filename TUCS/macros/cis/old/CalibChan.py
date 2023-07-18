#!/usr/bin/env python
# Author: Dave Hollander <daveh@uchicago.edu>
#
# November 17, 2009
#

"""
This macro plots the average calibration for a channel as a function of
channel number in a given module.  The user should use the same set of
runs as the calibration distribution macro to check for problems within
a module.

The user can change the calibration type, use 'calibration' to get the channel
calibration from the ntuple and use 'calibration_db' to get the database
calibration value.
"""

import os
os.chdir(os.getenv('TUCS','.'))
exec(open('src/load.py').read(), globals()) # don't remove this!

runs = '-28 days'

Go([
    Use(run=runs, runType='CIS', region=''),\
    ReadCIS(),\
    ReadDB(),\
    CISRecalibrateProcedure(all=True),\
    calibTrack(calibType = 'calibration'),\
    ])
