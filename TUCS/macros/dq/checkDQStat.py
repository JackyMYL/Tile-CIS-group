#!/usr/bin/env python

import os
os.chdir(os.getenv('TUCS','.'))
exec(open('src/load.py').read(), globals()) # don't remove this!
import pymysql

def getRuns(min,max,byRun):
    db = pymysql.connect(host='pcata007.cern.ch', user='reader')
    cursor = db.cursor()
    if byRun:
        if max == -1:
            cursor.execute("""select run from tile.comminfo where run>%i and events > 4000 and type='Ped'""" % (min-1))
        else:
            cursor.execute("""select run from tile.comminfo where run>%i and run<%i and events > 4000 and type='Ped'""" % (min-1,max+1))
    else:
        if max == '-1':
            cursor.execute("""select run from tile.comminfo where date>"%s" and events > 4000 and type='Ped'""" % (min))
        else:
            cursor.execute("""select run from tile.comminfo where date>"%s" and date<"%s" and events > 4000 and type='Ped'""" % (min,max))
    runs = []
    for run in cursor.fetchall():
        runs.append(int(run))

    db.close()
    return runs

runList = [414261,417891,421547]

#theRegion= "LBA_m02_s"
theRegion = 'H1447'
#theRegion= ""

u=Use(run=runList,type='physical',region=theRegion,verbose=True,keepOnlyActive=False)

processList = [u,ReadChanStat(type='physical'),Print(type='physical')]

g = Go(processList)
