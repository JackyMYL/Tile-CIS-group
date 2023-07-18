#!/usr/bin/env python

import os, sys
os.chdir(os.getenv('TUCS','.'))
exec(open('src/load.py').read(), globals()) # don't remove this!
#===========================================================
# This macro compares two DBs and prints out differeing values
#===========================================================
import optparse
parser = optparse.OptionParser()
parser.add_option('-d','--useDigits',action="store_true",dest="doDigits",default=False)
parser.add_option('-r','--useRawCh', action="store_true",dest="doRawCh", default=False)
parser.add_option('-c','--useCells', action="store_true",dest="doCells", default=False)
parser.add_option('--run',                          dest="run",     default=1)
parser.add_option('-R','--Region',      dest="selected_region", default='')
#parser.add_option('-O','--useOracle',   action="store_true",dest="useOracle",default=False)
parser.add_option('-D','--dbConnection',dest="DB",default='CONDBR2')
parser.add_option('-T','--dbTagList', dest="tagList",default='RUN2-UPD1-00,RUN2-sUPD1-00')
parser.add_option('--DBs',              dest="dbList",help="comma-separated pair of databases to open")
(options, args) = parser.parse_args()

runList = [int(options.run)]
dbList = [ db for db in options.dbList.split(',')]
tagList = [ tag for tag in options.tagList.split(',')]

processList = []
theType=''
thePar=''
if options.doDigits:
    theType='readout'
    thePar = 'digi'
    processList.append( Use(runType='Ped',run=runList,type=theType,region=options.selected_region,verbose=True,keepOnlyActive=False) )
    for i in [0,1]:
        if dbList[i] == 'ORACLE':
            processList.append( ReadDigiNoiseDB(useSqlite=False,dbConn=options.DB,load_autocr=False,folderTag=tagList[i],folderTagAC=tagList[i]) )
        else:
            processList.append( ReadDigiNoiseDB(useSqlite=True,dbConn=options.DB,dbFile=dbList[i],load_autocr=False,folderTag=tagList[i],folderTagAC=tagList[i]) )
elif options.doRawCh:

    theType='readout'
    thePar = 'chan'
    processList.append( Use(run=runList,type=theType,region=options.selected_region,verbose=True,keepOnlyActive=False) )
    for i in [0,1]:
        if dbList[i] == 'ORACLE':
            processList.append( ReadDigiNoiseDB(useSqlite=False,dbConn=options.DB,folderTag=tagList[i]) )
        else:
            processList.append( ReadDigiNoiseDB(useSqlite=True,dbConn=options.DB,dbFile=dbList[i],folderTag=tagList[i]) )
elif options.doCells:
    theType='physical'
    thePar = 'cell'
    processList.append( Use(runType='Ped',run=runList,type=theType,region=options.selected_region,verbose=True,keepOnlyActive=False) )
    for i in [0,1]:
        if dbList[i] == 'ORACLE':
            processList.append( ReadCellNoiseDB(useSqlite=False,dbConn=options.DB,folderTag=tagList[i]) )
        else:
            processList.append( ReadCellNoiseDB(useSqlite=True,dbConn=options.DB,dbFile=dbList[i],folderTag=tagList[i]) )
        
    
processList.append(CompareConstants(type=theType))    
    
g = Go(processList)

