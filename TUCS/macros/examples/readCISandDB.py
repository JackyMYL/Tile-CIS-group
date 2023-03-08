#!/usr/bin/env python
# Author: Christopher Tunnell <tunnell@hep.uchicago.edu>
#
# This macro demonstrates how one can read from the DB.  This specific
# example involves reading in CIS events with ReadCISFile() and then
# reading from the database with ReadDB()
#

import os, sys
os.chdir(os.getenv('TUCS','.'))
exec(open('src/load.py').read(), globals()) # don't remove this!

# Use run 9055 and only look at LBA module 33 channel 26
u = Use(run=90555, region='LBA_m33_c26')

# Read in the CIS information from the CIS tool ntuples
x = ReadCIS()

# Look up the calibration values in Oracle
d = ReadCalibFromCool(schema = 'OFL', folder = 'CALIB/CIS', tag = 'UPD4')

workers = [u, x, d, Print()]

Go(workers)


