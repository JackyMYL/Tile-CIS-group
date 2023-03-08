'''
This macro creates a ROOT tree filled with values stored in a caloSqlite.
To specify: data or MC, runNumber, tag, read from caloSqlite or from root file.
'''

import os
os.chdir(os.getenv('TUCS','.'))
exec(open('src/load.py').read(),globals()) #don't remove

useData = True
useSqlite = True
selected_region = ''
runNumber =333602   #must be same run number as was used to produce the caloSqlite
myPedNr='38'

if useData==True:
    myConn = 'CONDBR2' #data
    myTag = 'RUN2-UPD4-19' #data (often)
if useData==False:
    myConn = 'OFLP200' #MC
    myTag = 'IOVDEP-02' #latest MC
#    myTag = 'PileUp-Dt75-OFC0-HVCorr-02' #latest MC
#    myTag = 'PileUp-Dt75-OFC0-HVCorr'

if useSqlite== True:
    processlist = [
    Use(run=runNumber,runType='Ped',type='physical',region=selected_region,verbose=True,keepOnlyActive=True),
#ReadCellNoiseFile(),
    ReadCellNoiseDB(useSqlite=True, sqlfn='tile_cell_noise_333602.sqlite',folderTag=myTag,dbConn=myConn), #FolderStructure Calo not default,  uses old file structure of COOL
    EtaDependence(parameter='cell',fromDB=True),
]

elif useSqlite ==False:
    Use(run=runNumber,runType='Ped',type='physical',region=selected_region,verbose=True,keepOnlyActive=True),
    ReadCellNoiseFile(),
    EtaDependence(parameter='cell',fromDB=useSqlite)
    
else:
    print "please specify if you plot values from Sqlite or from root file in useSqlite boolean"

g = Go(processlist,withMBTS=True,withSpecialMods=True)
