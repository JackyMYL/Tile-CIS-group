#!/usr/bin/env python

import os
os.chdir(os.getenv('TUCS','.'))
exec(open('src/load.py').read(), globals()) # don't remove this!
#===========================================================
# This macro prints the noise constants in the DB for a given region
#===========================================================
import optparse
parser = optparse.OptionParser()
parser.add_option('-d','--useDigits',action="store_true",dest="doDigits",default=False)
parser.add_option('-r','--useRawCh', action="store_true",dest="doRawCh", default=False)
parser.add_option('-c','--useCells', action="store_true",dest="doCells", default=False)
parser.add_option('--run',   dest="run")
parser.add_option('-R','--Region',      dest="selected_region", default='')
parser.add_option('-O','--useOracle',   action="store_true",dest="useOracle",default=False)
parser.add_option('-D','--dbConnection',dest="DB",default='CONDBR2')
parser.add_option('-T','--dbTagSuffix', dest="dbTag",default='RUN2-UPD1-00')
parser.add_option('-I','--inputDB',     dest='dbFile',default='')
parser.add_option('--data',     dest='data',default='')
(options, args) = parser.parse_args()


u=Use(run=int(options.run),type='physical',region=options.selected_region,verbose=True,keepOnlyActive=False)
processList = [u]

if options.doDigits:
    if options.dbFile == '': options.dbFile = 'tileSqlite.db'
    processList += [ReadDigiNoiseDB(useSqlite=(not options.useOracle),dbConn=options.DB,load_autocr=False,folderTag=options.dbTag,folderTagAC=options.dbTag,dbFile=options.dbFile)]
    processList += [Print(type='readout',data=options.data)]
elif options.doRawCh:
    if options.dbFile == '': options.dbFile = 'tileSqlite.db'
    processList += [ReadChanNoiseDB(useSqlite=(not options.useOracle),dbConn=options.DB,folderTag=options.dbTag,dbFile=options.dbFile)]
    processList += [Print(type='readout',data=options.data)]
elif options.doCells:
    if options.dbFile == '': options.dbFile = 'caloSqlite.db'
    processList += [ReadCellNoiseDB(useSqlite=(not options.useOracle),dbConn=options.DB,folderTag=options.dbTag,dbFile=options.dbFile)]
    processList += [Print(type='physical',data=options.data)]

if options.DB == 'OFLP200':
    MBTS=False
    Special=False
else:
    MBTS=True
    Special=True
       
g = Go(processList,withMBTS=MBTS,withSpecialMods=Special)
