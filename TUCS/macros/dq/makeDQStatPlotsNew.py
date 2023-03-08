#!/usr/bin/env python

import os
os.chdir(os.getenv('TUCS','.'))
exec(open('src/load.py').read(), globals()) # don't remove this!

#runs = [206356]
runs = '-1week'
#runs = '-3month'
#runs = '2012-07-01'

processList = [ Use(run=runs,runType='CIS',type='physical',verbose=True,keepOnlyActive=False),
                ReadChanStat(type='physical',schema='COOLOFL_TILE/CONDBR2',folder='/TILE/OFL02/STATUS/ADC'),
                MakeDQPlots(type='physical',runForDetail=-1)]

g = Go(processList)

