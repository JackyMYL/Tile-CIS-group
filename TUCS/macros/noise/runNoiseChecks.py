#!/usr/bin/env python

#===========================================================
# This macro provides an interface for:
# + computing Tile Noise constants
# + checking their consistency with the DB
# + monitoring their consistency over multiple runs
# + updating the Tile/Calo noise DB
#===========================================================
import os
import os.path
import optparse
parser = optparse.OptionParser()
parser.add_option('-d','--useDigits',action="store_true",dest="doDigits",default=False)
parser.add_option('-r','--useRawCh', action="store_true",dest="doRawCh", default=False)
parser.add_option('-c','--useCells', action="store_true",dest="doCells", default=False)
parser.add_option('-w','--writeDB',  action="store_true",dest="writeDB", default=False)
parser.add_option('--IOVbeg',                            dest="IOVbeg",  default=-1)
parser.add_option('--IOVend',                            dest="IOVend",  default=-1)
parser.add_option('-p','--print',    action="store_true",dest="doPrint", default=False)
parser.add_option('-b','--batch',    action="store_true",dest="batch",   default=False)
parser.add_option('-T','--dbTag',                        dest="dbTag",   default="RUN2-UPD1-00")
parser.add_option('--dbTagAC',                           dest="dbTagAC",   default="")
parser.add_option('--patch',         action="store_true",dest="doPatch",   default=False)
parser.add_option('--runList',                           dest="runList",               help="comma-separated list")
parser.add_option('--minRun',                            dest="minRun")
parser.add_option('--maxRun',                            dest="maxRun",  default='-1')
parser.add_option('--minDate',                           dest="minDate",               help="Format=YYYY-MM-DD")
parser.add_option('--maxDate',                           dest="maxDate", default='-1', help="Format=YYYY-MM-DD")
parser.add_option('-R','--Region',                       dest="selected_region", default='')
parser.add_option('-D','--dbConnection',dest="DB",default='CONDBR2')
parser.add_option('-Q','--readDQ',  action="store_true", dest="doDQ",    default=False)
parser.add_option('-P','--PlotDetail',                   dest="thePlotDetail", default=2)
parser.add_option('--maskList',   dest="maskList",help="comma-separated list, precede cell hashes with H")
parser.add_option('-I','--inputDir',                     dest="inputDir",   default="/afs/cern.ch/user/t/tilecali/w0/ntuples/ped")
parser.add_option('-O','--useOracle',   action="store_true",dest="useOracle",default=False)

(options, args) = parser.parse_args()

os.chdir(os.getenv('TUCS','.'))
exec(open('src/load.py').read(), globals()) # don't remove this!
import _mysql
#print "MAX = ",MAXLBK
sys.argv = []

def getRuns(min,max,byRun):
    db = _mysql.connect(host='pcata007.cern.ch', user='reader')
    if byRun:
        if max == -1:
            db.query("""select run from tile.comminfo where run>%i and events > 4000 and type='Ped'""" % (min-1))
        else:
            db.query("""select run from tile.comminfo where run>%i and run<%i and events > 4000 and type='Ped'""" % (min-1,max+1))
    else:
        if max == '-1':
            db.query("""select run from tile.comminfo where date>"%s" and events > 4000 and type='Ped'""" % (min))
        else:
            db.query("""select run from tile.comminfo where date>"%s" and date<"%s" and events > 4000 and type='Ped'""" % (min,max))
    
    r = db.store_result()
    
    runs = []
    for run in r.fetch_row(maxrows=0):
        runs.append(run[0])

    db.close()
        
    return runs

if options.runList:
    runList = [ int(i) for i in options.runList.split(',')]
elif options.minRun:
    minRun = int(options.minRun)
    maxRun = int(options.maxRun)
    runList = getRuns(minRun,maxRun,True)
elif options.minDate:
    minDate = options.minDate
    maxDate = options.maxDate
    runList = getRuns(minDate,maxDate,False)
else:
    print "Please select either a minRun or minDate, or specify a run list."
    sys.exit(1)

doMask = False
if options.maskList:
    doMask = True
    maskList = [ r for r in options.maskList.split(',')]
writeDB  = options.writeDB

if options.IOVbeg != -1:
    IOVbeg = int(options.IOVbeg)
else:
    IOVbeg =  runList[0]
IOVend   = int(options.IOVend)
dbTag    = options.dbTag
if options.dbTagAC == "":
    dbTagAC = options.dbTag
else:
    dbTagAC = options.dbTagAC
doPrint  = options.doPrint
selected_region = options.selected_region
thePlotDetail = int(options.thePlotDetail)

print 'Runs to analyze:'
print runList
if not options.batch:
    cont = raw_input('Run over these runs? (y/n)')
    if cont != 'y':
        sys.exit(0)

# Check for sqlite DB's make copies if needed
if not options.useOracle and (options.doDigits or options.doRawCh) and not os.path.exists('./tileSqlite.db'):
    if not options.batch:
        cont = raw_input('tileSqlite.db is missing. Would you like to make a copy from Oracle DB? (y/n)')
        if cont != 'y':
            sys.exit(0)
    cmd = 'macros/noise/copyDB.sh -T'
    if options.DB == 'OFLP200':
        cmd += ' -M'
    if options.doDigits:
        cmd += ' -D'
    if options.doRawCh:
        cmd += ' -H'
    os.system(cmd)
if not options.useOracle and options.doCells and not os.path.exists('./caloSqlite.db'):
    if not options.batch:
        cont = raw_input('caloSqlite.db is missing. Would you like to make a copy from Oracle DB? (y/n)')
        if cont != 'y':
            sys.exit(0)
    cmd = 'macros/noise/copyDB.sh -C -R '+str(IOVbeg)+' -G '+dbTag
    if options.DB == 'OFLP200':
        cmd += ' -M'
    os.system(cmd)


# convert runList from string to int
for r in xrange(len(runList)): runList[r] = int(runList[r])
runList.sort()

processList = []
if options.doDigits:
    doAutoCorr=True
    processList.append(Use(run=runList,runType='Ped',region=selected_region,verbose=True,keepOnlyActive=False))
    processList.append(ReadDigiNoiseDB(useSqlite=(not options.useOracle),folderTag=dbTag,dbConn=options.DB,load_autocr=doAutoCorr,folderTagAC=dbTagAC))
    processList.append(ReadDigiNoiseFile(processingDir=options.inputDir,load_autocr=doAutoCorr))
    if options.doDQ: processList.append(ReadChanStat(type='readout',runs=runList,runType='Ped'))
    processList.append(NoiseStability(plotDetail=thePlotDetail,load_autocr=doAutoCorr))
    processList.append(NoiseVsDB(load_autocr=doAutoCorr))
    if writeDB: 
        processList.append(WriteDigiNoiseDB(offline_iov_beg=(IOVbeg,0),offline_iov_end=(IOVend,MAXLBK),folderTag=dbTag,dbConn=options.DB,load_autocr=doAutoCorr,folderTagAC=dbTagAC))
    if doPrint:
        processList.append(Print(region=selected_region)) 
if options.doRawCh:
    processList.append(Use(run=runList,region=selected_region,verbose=True,keepOnlyActive=False))
    processList.append(ReadChanNoiseDB(useSqlite=(not options.useOracle),folderTag=dbTag,dbConn=options.DB))
    processList.append(ReadChanNoiseFile(processingDir=options.inputDir))
    if options.doDQ: processList.append(ReadChanStat(type='readout',runs=runList,runType='Ped'))
    processList.append(NoiseStability(parameter='chan'))
    processList.append(NoiseVsDB(parameter='chan'))
    if writeDB: 
        processList.append(WriteChanNoiseDB(offline_iov=(runList[0],0),folderTag=dbTag,dbConn=options.DB))
    if doPrint:
        processList.append(Print(region=selected_region)) 
if options.doCells:
    processList.append(Use(run=runList,runType='Ped',type='physical',region=selected_region,verbose=True,keepOnlyActive=False))
    #processList.append(ReadDigiNoiseFile(processingDir=options.inputDir,load_autocr=True))
    processList.append(ReadCellNoiseDB(useSqlite=(not options.useOracle),folderTag=dbTag,dbConn=options.DB))
    processList.append(ReadCellNoiseFile(processingDir=options.inputDir))
    if options.doDQ: processList.append(ReadChanStat(type='physical',runs=runList,runType='Ped'))
    #processList.append(NoiseStability(parameter='cell',plotDetail=thePlotDetail))
    processList.append(NoiseVsDB(parameter='cell'))
    if options.doPatch:
        processList.append(PatchBadValues(runType='PedUpdate',type='physical',standard_p='cellsigma1'))
    if doMask:
        processList.append(MaskComponent(parameter='cell',components=maskList))
    if writeDB: 
        processList.append(WriteCellNoiseDB(offline_iov_beg=(IOVbeg,0),offline_iov_end=(IOVend,MAXLBK),folderTag=dbTag,dbConn=options.DB))
    if doPrint:
        processList.append(Print(region=selected_region,type='physical')) 


if options.DB == 'OFLP200':
    MBTS=False
    Special=False
else:
    MBTS=True
    Special=True
       
g = Go(processList,withMBTS=MBTS,withSpecialMods=Special)


