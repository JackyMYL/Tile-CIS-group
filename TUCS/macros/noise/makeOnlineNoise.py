#!/usr/bin/env python

import os
os.chdir(os.getenv('TUCS','.'))
exec(open('src/load.py').read(), globals()) # don't remove this!

filename = '/afs/cern.ch/user/t/tilecali/w0/ntuples/ped/RawCh_NoiseCalib_1_264026_Ped.root'
pedNr = 264026

#selected_region = 'EBA_m08'
#selected_region = 'EBC_m27_c14'
selected_region = ''
runList = [MAXRUN]
processList = [
    Use(run=pedNr,runType='Ped',type='physical',region=selected_region,verbose=True,keepOnlyActive=False),
    #Use(run=runList,type='physical',region=selected_region,verbose=True,keepOnlyActive=False,runType='Ped'),
    ReadOnlineADCNoiseDB(useSqlite=True),
    #ReadDigiNoiseDB(useSqlite=False,load_autocr=False,folderTag='RUN2-HLT-UPD1-01'),
    #ReadCellNoiseDB(useSqlite=False,folderTag='RUN2-UPD1-00'),
    ReadCellNoiseFile(processingDir = filename, pedNr=pedNr, doOnlineOnly=True), 
    #MakeOnlineADCNoise(),
    WriteOnlineADCNoiseDB()
               ]

# MC
#g = Go(processList,withMBTS=False,withSpecialMods=False)

# Data
g = Go(processList,withMBTS=True,withSpecialMods=True, RUN2=True)


