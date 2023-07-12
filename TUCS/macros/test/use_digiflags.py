#!/usr/bin/env python

import os
os.chdir(os.getenv('TUCS','.'))
exec(open('src/load.py').read(), globals()) # don't remove this!

dict = {'LBA': 72652, 'LBC': 73305, 'EBA': 72653, 'EBC': 72661}
for k, v in dict.iteritems():
    print k, v
    u1 = Use(run=v, region='')
    x1 = ReadCISFile(getScans=False, cut=3)

    processors = [u1, x1, Print(),]

    Go(processors)


