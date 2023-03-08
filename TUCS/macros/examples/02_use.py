#!/usr/bin/env python
# Author: Christopher Tunnell <tunnell@hep.uchicago.edu>
#
# Show how Use works with a single run
#

import os
os.chdir(os.getenv('TUCS','.'))
exec(open('src/load.py').read(), globals()) # don't remove this!

Go([
    Use(run=90555),     # Tell Use() to prepare TUCS to use run 90555
    Print(),            # Afterwards, dump the information from Use() for each detector region
    ]) 



