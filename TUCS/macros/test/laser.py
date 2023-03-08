#!/usr/bin/env python

import os
os.chdir(os.getenv('TUCS','.'))
exec(open('src/load.py').read(), globals()) # don't remove this!

u = Use(run=[91998, 92003])
x = ReadLaser()
p = Print()

processors = [u, x, p]

Go(processors)


