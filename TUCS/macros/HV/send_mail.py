#!/usr/bin/env python
# Author: romano <sromanos@cern.ch>
#
# HV analysis
#

import os, sys
os.chdir(os.getenv('TUCS','.'))
exec(open('src/load.py').read(), globals()) # don't remove this!

processors = []

processors.append( send_mail() )

# Go!
Go(processors)

