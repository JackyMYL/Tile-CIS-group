# Author: Joshua Montgomery <joshua.montgomery@cern.ch>
# Sept. 23, 2011
# This is designed to compare two text files in archive format
# typically produced by the StudyFlag macro
# It outputs the common channels

import os
os.chdir(os.getenv('TUCS','.'))
exec(open('src/load.py').read(), globals())
from workers.cis.Comparefile import *

compinst = Comparefile()

compinst.ProcessStart()
compinst.ProcessStop()

print 'i have finished'
