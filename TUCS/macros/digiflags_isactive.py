#!/usr/bin/env python
# Author: Brian Martin <brian.thomas.martin@cern.ch>
#
# This macro demonstrates how Use() can check the digiflag
# fragments in the database to see if a module was included
# in a run.
#
# March 05, 2009
#

import os
os.chdir(os.getenv('TUCS','.'))
exec(open('src/load.py').read(), globals()) # don't remove this!

Go([Use(run=99027), Print()])




