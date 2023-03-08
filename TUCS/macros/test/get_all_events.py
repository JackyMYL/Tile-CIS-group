#!/usr/bin/env python

import os
os.chdir(os.getenv('TUCS','.'))
exec(open('src/load.py').read(), globals()) # don't remove this!

u = Use(90555)

processors = [u, GetAllEvents()]

Go(processors)


