#!/usr/bin/env python

import os
os.chdir(os.getenv('TUCS','.'))
exec(open('src/load.py').read(), globals()) # don't remove this!

# Set this to some bi-gain CIS scan.  This does not work
# MonoCIS since there is currently no MonoCIS calibration
# to access if a run is good or not.

# Please select a run or collection of runs by uncommenting one
# of the three lines below
runs = 114371                # choose only run one
#runs = [104835,104934]      # or a list of runs
#runs = "-1 week"            # or you can also look at the last week of CIS runs

#
# Expert's only: you probably don't want to touch the code below here
#

u = Use(run=runs, runType='CIS')

readcal = ReadCalibFromCool(schema = 'OFL', folder = 'CALIB/CIS', tag = 'UPD4')

processors = [u, ReadChanStat(),             # Load the channel status information from COOL
              u, ReadCIS(),                  # Read in the CIS ntuples from AFS
              readcal,                       # Read in the CIS DB constants
              CISFlagProcedure(),            # Determine if an ADC channel is good for CIS
              DumpIsBadToFile("CIS"),        # Dump the CIS ADC channel status
              DumpIsBadToFile("ChanStat")]   # Dump the COOL ADC channel status

# Run the script...
Go(processors)


