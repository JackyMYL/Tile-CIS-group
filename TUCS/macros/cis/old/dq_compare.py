#!/usr/bin/env python
# Author: Christopher Tunnell <tunnell@hep.uchicago.edu>
#
# Compare the CIS uncalibratable channels to a list of bad
# channels that DQ provides.
#
# March 04, 2009
#

import os
os.chdir(os.getenv('TUCS','.'))
exec(open('src/load.py').read(), globals()) # don't remove this!

sregion = ''  # Only look at a certain region?
u1 = Use(run=[100489,100699,100814,101152,101441,102009], runType='CIS', region=sregion)

x1 = ReadCISFile()

Go([u1, x1, ReadDB(), CalibBadBit(), RemoveSpecial(), Print(), CompareCIStoDQ()])


