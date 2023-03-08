#!/usr/bin/env python

import os
os.chdir(os.getenv('TUCS','.'))
exec(open('src/load.py').read(), globals()) # don't remove this!

selected_region = ''
runList = [MAXRUN]
Tag = 'COM-01'
acrTag = 'COM-02'
Conn = 'OFLP200'

u=Use(run=runList,type='readout',region=selected_region,verbose=True,keepOnlyActive=False)
processList = [u,ReadDigiNoiseDB(useSqlite=True,dbConn=Conn,folderTag=Tag,folderTagAC=acrTag),ReadACRNoiseFile(),WriteDigiNoiseDB(runType='Ped',offline_iov_beg=(0,0),offline_iov_end=(MAXRUN,MAXLBK),folderTag=Tag,folderTagAC=acrTag,dbConn=Conn)]

g = Go(processList,withMBTS=False,withSpecialMods=False)


