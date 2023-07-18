#!/usr/bin/env python

import os
os.chdir(os.getenv('TUCS','.'))
exec(open('src/load.py').read(), globals()) # don't remove this!

selected_region = ''
#RUN = 146076
RUN = 149235
DB = 'OFLP200'

u=Use(run=[RUN],type='physical',region=selected_region,verbose=True,keepOnlyActive=False)

processList = [u,ReadDigiNoiseDB(load_autocr=True,dbConn=DB,folderTag='COM-00',folderTagAC='COM-00'),NoiseStability(plotDetail=0,load_autocr=True),NoiseVsDB(load_autocr=True),WriteDigiNoiseDB(runType='PedUpdate',folderTag='COM-00',folderTagAC='COM-00',offline_iov_beg=(0,0),dbConn=DB)]


g = Go(processList)


