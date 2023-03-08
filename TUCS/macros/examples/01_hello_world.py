#!/usr/bin/env python
# Author: Christopher Tunnell <tunnell@hep.uchicago.edu>
#
# This macro just prints "hello world"
#

import os
os.chdir(os.getenv('TUCS','.'))
exec(open('src/load.py').read(), globals()) # don't remove this!

Go([ 
    PrintHelloWorld(),    # Run the "hello world" worker at workers/Examples/PrintHellowWorld.py
    ])


