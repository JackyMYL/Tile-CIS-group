#!/usr/bin/env python
# Author: Christopher Tunnell <tunnell@hep.uchicago.edu>
#
# Dump all of the bad CIS scans for some run
#
# March 05, 2009
#

import os
os.chdir(os.getenv('TUCS','.'))
exec(open('src/load.py').read(), globals()) # don't remove this!

u = Use(run=90555)
p = Print()

processors = [u, ReadChanStat(), RemoveGoodEvents(), p,\
              u, ReadCISFile(getScans=True, cut=3),\
              ShowCISScans()]

Go(processors)
