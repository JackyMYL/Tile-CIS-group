#!/usr/bin/env python

import os
os.chdir(os.getenv('TUCS','.'))
exec(open('src/load.py').read(), globals()) # don't remove this!

u1 = Use(run='-1 month', useDateProg=True, runType='CIS')
x1 = ReadCISFile(getScans=False, cut=3, processingDir='/tmp/ctunnell/recis', badCut=27)

processors = [u1, x1, IsEntireModuleBad()]

Go(processors)


