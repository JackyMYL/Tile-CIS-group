import os
os.chdir(os.getenv('TUCS','.'))
exec(open('src/load.py').read(),globals()) #don't remove

selected_region = ''
#runNumber = 
runNumber = 189493
myConn = 'CONDBR2' #data
#myConn = 'OFLP200' #MC
#myTag = 'PileUp-Dt75-OFC0-HVCorr'
#myTag = 'PileUp-Dt75-OFC0-HVCorr-02'
myTag = 'RUN2-UPD1-00' # often used for data

processlist = [
Use(run=runNumber,runType='Ped',type='physical',region=selected_region,verbose=True,keepOnlyActive=True),
ReadCellNoiseFile(),
#ReadCellNoiseDB(useSqlite=True,dbFile='../sqlfiles/caloSqlite_MC11b_iov4.db',folderStructure='Calo',folderTag=myTag,dbConn=myConn), #FolderStructure Calo not default,  uses old file structure of COOL
EtaDependence(parameter='cell',fromDB=False),
]

g = Go(processlist,withMBTS=True,withSpecialMods=True)
