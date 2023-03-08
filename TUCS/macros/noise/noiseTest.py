#!/usr/bin/env python

import os
os.chdir(os.getenv('TUCS','.'))
exec(open('src/load.py').read(), globals()) # don't remove this!

#selected_region = 'EBA_m08'
selected_region = 'LBC_m27'
#runList = [116602]
#runList = [91569,91585,91841,92018,92417,92973,92974,92976,92977,93403,93413,93414,93885,94110,95385,96632,96635,96637,97077]
runList = [9]
#os.remove('noise.HIST.root')        
#u = Use(run=99027) # only EBA
u=Use(run=runList,type='readout',region=selected_region,verbose=True,keepOnlyActive=False,runType='Ped')
#processList = [u,ReadDigiNoiseFile(),ReadChanNoiseFile(),ReadDigiNoiseDB(),ReadChanNoiseDB(),CheckNoiseBounds()]
#processList = [u,ReadDigiNoiseDB(),Print()]
#processList = [u,ReadDigiNoiseDB(),ReadDigiNoiseFile(),NoiseStability(plotDetail=1),NoiseVsDB(),WriteNoiseDB(runNumber=runList[-1])]
#processList = [u,ReadDigiNoiseDB(),ReadDigiNoiseFile(),NoiseStability(plotDetail=1),NoiseVsDB()]

#processList = [u,ReadCellNoiseDB(),ReadCellNoiseFile(),NoiseStability(parameter='cell'),NoiseVsDB(parameter='cell'),WriteCellNoiseDB(offline_iov=(runList[0],0))]
#processList = [u,ReadCellNoiseDB(),Print(type='physical')]
#processList = [u,ReadCellNoiseFile(),Print(type='physical')]
processList = [u,ReadOnlineADCNoiseDB(useSqlite=True),Print()]

g = Go(processList)


