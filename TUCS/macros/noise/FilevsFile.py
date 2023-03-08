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
parser.add_option('--Dirs',              dest="dirList",help="comma-separated pair of directories to use")
(options, args) = parser.parse_args()

runList = [int(options.run)]
dirList = [ dir for dir in options.dirList.split(',')]
print dirList
processList = []
theType=''
thePar=''
if options.doDigits:
    theType='readout'
    thePar = 'digi'
    processList.append( Use(run=runList,type=theType,region=options.selected_region,verbose=True,keepOnlyActive=False) )
    processList.append( ReadDigiNoiseFile(load_autocr=True,processingDir=dirList[0]) )
    processList.append( ReadDigiNoiseFile(load_autocr=True,processingDir=dirList[1]) )
elif options.doRawCh:
    theType='readout'
    thePar = 'chan'
    processList.append( Use(run=runList,type=theType,region=options.selected_region,verbose=True,keepOnlyActive=False) )
    processList.append( ReadChanNoiseFile(processingDir=dirList[0]) )
    processList.append( ReadChanNoiseFile(processingDir=dirList[1]) )
elif options.doCells:
    theType='physical'
    thePar = 'cell'
    processList.append( Use(run=runList,type=theType,region=options.selected_region,verbose=True,keepOnlyActive=False) )
    processList.append( ReadCellNoiseFile(processingDir=dirList[0]) )
    processList.append( ReadCellNoiseFile(processingDir=dirList[1]) )
        
    
processList.append(CompareConstants(type=theType))    
    
g = Go(processList)

