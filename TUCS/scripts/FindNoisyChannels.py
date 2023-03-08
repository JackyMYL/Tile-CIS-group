#!/bin/env python
# ReadCalibFromCool.py
# Andrei Artamonov 2009-11-03
# Improved by Gabriele Bertoli 28-03-2013

import getopt,sys,os,string


def usage():
    print "Usage: ",sys.argv[0]," [OPTION] ... "
    print "Dumps the TileCal calibrations from various schemas / folders / tags"
    print ""
    print "-h, --help    shows this help"
    print "-f, --folder  specify status folder to use f.i. /TILE/OFL02/CALIB/EMS or /TILE/OFL02/CALIB/CIS/LIN "
    print "-t, --tag     specify tag to use, f.i. RUN2-HLT-UPD1-01 or UPD4"
    print "-T, --tresh   specify a treshold for noisy channels, default is 1.9"
    print "-G, --gain    specify channel gain, f.i. HG, LG or BOTH, default is BOTH"
    print "-r, --run     specify run  number, by default uses latest iov"
    print "-l, --lumi    specify lumi block number, default is 0"
    print "-n, --nval    specify number of values to output, default is all"
    print "-g, -a, --adc specify adc to print or number of adcs to print with - sign, default is -2"
    print "-s, --schema  specify schema to use, like 'COOLOFL_TILE/CONDBR2' or 'sqlite://;schema=tileSqlite.db;dbname=CONDBR2'"
    


letters = "hr:l:s:t:T:G:f:n:a:g:"
keywords = ["help","run=","lumi=","schema=","tag=","folder=","nval=","adc=","gain=","treshold=","changain="]

try:
    opts, extraparams = getopt.getopt(sys.argv[1:],letters,keywords)
except getopt.GetOptError, err:
    print str(err)
    usage()
    sys.exit(2)

# defaults 
run = 2147483647
lumi = 0
schema = 'COOLOFL_TILE/CONDBR2'
folderPath =  "/TILE/OFL02/CALIB/CIS/LIN"
tag = "UPD4"
nval = 0
nadc = -2
treshold = 1.9
changain = "BOTH"

for o, a in opts:
    if o in ("-f","--folder"):
        folderPath = a
    elif o in ("-t","--tag"):
        tag = a
    elif o in ("-s","--schema"):
        schema = a
    elif o in ("-n","--nval"):
        nval = int(a)
    elif o in ("-a","--adc","-g","--gain"):
        nadc = int(a)
    elif o in ("-r","--run"):
        run = int(a)
    elif o in ("-l","--lumi"):
        lumi = int(a)
    elif o in ("-T","--tresh"):
        treshold = float(a)
    elif o in ("-G","--gain"):
        changain = a
    elif o in ("-h","--help"):
        usage()
        sys.exit(2)
    else:
        assert False, "unhandeled option"


from TileCalibBlobPython import TileCalibTools
from TileCalibBlobObjs.Classes import *

from TileCalibBlobPython.TileCalibLogger import TileCalibLogger, getLogger
log = getLogger("FindNoisyChannels")
import logging
log.setLevel(logging.DEBUG)


#=== set database
db = TileCalibTools.openDbConn(schema,'READONLY')
folderTag = TileCalibTools.getFolderTag(db, folderPath, tag )
log.info("Initializing folder %s with tag %s" % (folderPath, folderTag))

#=== initialize blob reader
blobReader = TileCalibTools.TileBlobReader(db,folderPath, folderTag)
#blobReader.log().setLevel(logging.DEBUG)

#=== get drawer with status at given run
log.info("Initializing for run %d, lumiblock %d" % (run,lumi))
log.info("Comment: %s" % blobReader.getComment((run,lumi)))
log.info( "\n" )

if nadc<0:
    a1=0
    a2=-nadc
else:
    a1=nadc
    a2=nadc+1

#=== loop over all partitions,modules,channels
for ros in xrange(1,5):
    for mod in xrange(0, min(64,TileCalibUtils.getMaxDrawer(ros))):
        modName = TileCalibUtils.getDrawerString(ros,mod)
        flt = blobReader.getDrawer(ros, mod,(run,lumi))
        if nval<1:
            mval = flt.getObjSizeUint32()
        else:
            mval = nval
        for chn in xrange(TileCalibUtils.max_chan()):
            for adc in xrange(a1,a2):
                msg = "%s %2i %1i  " % ( modName, chn, adc )
                for val in xrange(0,mval):
                    msg += "  %f" % flt.getData(chn, adc, val)
                
                
                to_print = msg.split()

                if float(to_print[3]) > treshold:
                    if changain == "BOTH":
                        print msg
                    elif changain == "HG" and int(to_print[2]) == 1:
                        print msg
                    elif changain == "LG" and int(to_print[2]) == 0:
                        print msg

                

#=== close DB
db.closeDatabase()
