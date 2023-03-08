#!/usr/bin/env python
# Author: Christopher Tunnell <tunnell@hep.uchicago.edu>
#
# This example shows you how to read in some CIS events
#

import os
os.chdir(os.getenv('TUCS','.'))
exec(open('src/load.py').read(), globals()) # don't remove this!

runs = "-2 week"
run_type = "CIS"
selected_region = "EBC_m62_c37_highgain"

Go([ 
    Use(run=runs, region=selected_region, runType = run_type),
    ReadCIS(),  # To previous examples, add ReadCIS(), which reads CIS ntuples from AFS
    Print(),
    ])



