#!/usr/bin/env python

import os
os.chdir(os.getenv('TUCS','.'))
exec(open('src/load.py').read(), globals()) # don't remove this!

u = UseRuns(90555)
x = ReadChanStat()
p = Print()

processors = [u, x, p]

Go(processors)


