#!/usr/bin/env python

import os, sys
os.chdir(os.getenv('TUCS','.'))
exec(open('src/load.py').read(), globals()) # don't remove this!
#===========================================================
# This macro creates root file with DB constants stored in a tree (dbTree)
#===========================================================
import optparse
parser = optparse.OptionParser()
parser.add_option('-d','--useDigits',action="store_true",dest="doDigits",default=False)
parser.add_option('-r','--useRawCh', action="store_true",dest="doRawCh", default=False)
parser.add_option('-c','--useCells', action="store_true",dest="doCells", default=False)
parser.add_option('-o','--useOnlineADC', action="store_true",dest="doOnlineADC", default=False)
parser.add_option('--runList',   dest="runList")
parser.add_option('-R','--Region',      dest="selected_region", default='')
parser.add_option('-O','--useOracle',   action="store_true",dest="useOracle",default=False)
parser.add_option('-D','--dbConnection',dest="DB",default='CONDBR2')
parser.add_option('-T','--dbTagSuffix', dest="dbTag",default='RUN2-UPD1-00')
parser.add_option('-I','--inputDB',     dest='dbFile',default='')
parser.add_option('-A','--autocorr',    action="store_true",dest='doAC',default=False)
(options, args) = parser.parse_args()

runList = [ int(i) for i in options.runList.split(',')]
selected_region = options.selected_region
dbTag   = options.dbTag
    

u=Use(runType='Ped',run=runList,type='physical',region=selected_region,verbose=True,keepOnlyActive=False)
processList = [u]
theType=''
thePar=''
if options.doDigits:
    if options.dbFile == '': options.dbFile = 'tileSqlite.db'
    processList += [ReadDigiNoiseDB(useSqlite=(not options.useOracle),dbConn=options.DB,load_autocr=options.doAC,folderTag=dbTag,folderTagAC=dbTag,dbFile=options.dbFile)]
    theType='readout'
    thePar = 'digi'
elif options.doRawCh:
    if options.dbFile == '': options.dbFile = 'tileSqlite.db'
    processList += [ReadChanNoiseDB(useSqlite=(not options.useOracle),dbConn=options.DB,folderTag=dbTag,dbFile=options.dbFile)]
    theType='readout'
    thePar = 'chan'
elif options.doCells:
    if options.dbFile == '': options.dbFile = 'caloSqlite.db'
    processList += [ReadCellNoiseDB(useSqlite=(not options.useOracle),dbConn=options.DB,folderTag=dbTag,dbFile=options.dbFile)]
    theType='physical'
    thePar = 'cell'
if options.doOnlineADC:
    if options.dbFile == '': options.dbFile = 'tileSqlite.db'
    processList += [ReadOnlineADCNoiseDB(useSqlite=(not options.useOracle),dbConn=options.DB,dbFile=options.dbFile)]
    theType='readout'
    thePar = 'onlineADC'
    
for runno in runList:
    processList.append(DumpDBtoFile(parameter=thePar,type=theType,runNumber=runno,load_autocr=options.doAC))

if options.DB == 'OFLP200':
    MBTS=False
    Special=False
else:
    MBTS=True
    Special=True
       
    
g = Go(processList,withMBTS=MBTS,withSpecialMods=Special)

if len(runList)>1:
    import os
    cmd = 'hadd -f noise.NTUP.root '
    for run in runList:
        fileStr = 'noiseXXX.NTUP.root '
        cmd += fileStr.replace('XXX',str(run))
    os.system(cmd)
