#!/usr/bin/env python

import os
os.chdir(os.getenv('TUCS','.'))
exec(open('src/load.py').read(), globals()) # don't remove this!

u = Use(run=90555, region='EBC_m64_c39')
p1 = Print()
p1.SetVerbose(True)

processors = [u, p1]

Go(processors)


