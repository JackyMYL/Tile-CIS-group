#!/usr/bin/env python

import os
os.chdir(os.getenv('TUCS','.'))
exec(open('src/load.py').read(), globals()) # don't remove this!

selected_region = ''
#runList = [MAXRUN]
runList = 178715
#Tag = 'MC10-2g-900ns'
#Tag = 'MC10-N5_dT900'
#Tag = 'MC10-N5_dT25'
#Tag = 'MC10-N5_dT25_1034'
#Tag = 'mu10-dt50-00'
#Tag = 'PileUp-Dt75-OFC0'
#Tag = 'Pileup-Dt75-OFC0-2'
#Tag = 'REPP-06'
Tag = 'RUN2-UPD1-00'
#Conn = 'OFLP200'
Conn = 'CONDBR2'


u=Use(run=runList,runType='Ped',type='physical',region=selected_region,verbose=True,keepOnlyActive=False)
processList = [u,ReadCellNoiseDB(useSqlite=True,dbConn=Conn,folderTag='RUN2-UPD1-00'),ReadPileupNoiseFile(),WriteCellNoiseDB(runType='Ped',offline_iov_beg=(0,0),offline_iov_end=(MAXRUN,MAXLBK),folderTag=Tag,dbConn=Conn)]

# MC
#g = Go(processList,withMBTS=False,withSpecialMods=False)

# Data
g = Go(processList,withMBTS=True,withSpecialMods=True)


