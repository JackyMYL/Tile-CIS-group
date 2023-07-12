#!/usr/bin/env python
import pymysql
import argparse
import datetime as dt
import os

os.chdir(os.getenv('TUCS','.'))
exec(open('src/load.py').read(), globals()) # don't remove this!

parser = argparse.ArgumentParser()

parser.add_argument('first_date', help='First date for the plot. '
                                      'Make sure the format is: YYYY-MM-DD')
parser.add_argument('last_date', help='Last date until which 3 day intervals will be made. '
                                      'Make sure the format is: YYYY-MM-DD')
parser.add_argument('use_sqlite', action='store', nargs='*', type=str, default='',
                    help='Put YES or TRUE here if you want to use sqlite instead of Oracle (much faster!)')

args = parser.parse_args()


first_date = dt.datetime.strptime(args.first_date, '%Y-%m-%d').date()
last_date = dt.datetime.strptime(args.last_date, '%Y-%m-%d').date()
if args.use_sqlite != '':
    schema='sqlite://;schema=/afs/cern.ch/user/t/tilebeam/scratch0/Commissioning/DQLeaderArea/tileSqlite_BCH.db;dbname=CONDBR2'
else:
    schema='COOLOFL_TILE/CONDBR2'


def getRuns(min,max,byRun,runtype='Las'):
    db = pymysql.connect(host='pcata007.cern.ch', user='reader')
    cursor = db.cursor()
    if byRun:
        if max == -1:
            cursor.execute("""select run from tile.comminfo where run>%i and events > 4000 and type='%s'""" % (min-1),runtype)
        else:
            cursor.execute("""select run from tile.comminfo where run>%i and run<%i and events > 4000 and type='%s'""" % (min-1,max+1,runtype))
    else:
        if max == '-1':
            cursor.execute("""select run from tile.comminfo where date>"%s" and events > 4000 and type='%s'""" % (min,runtype))
        else:
            cursor.execute("""select run from tile.comminfo where date>"%s" and date<"%s" and events > 4000 and type='%s'""" % (min,max,runtype))
    
    runs = []
    for run in cursor.fetchall():
        runs.append(int(run[0]))

    db.close()

    return runs


dateList = []
i_date = 0

while True:
    current_date = first_date + dt.timedelta(3 * i_date)

    if current_date <= last_date:
        dateList.append(current_date.strftime('%Y-%m-%d'))
    else:
        break

    i_date += 1


runList = []
oldDate = dateList[0]

for d in dateList[1:]:

    if not getRuns(oldDate, d, False):
        continue

    runList.append(getRuns(oldDate, d, False)[0])
    oldDate = d


#theRegion= "H1447"
theRegion= ""

print(runList)
print(runList[-1])

#u=Use(run='-3month',runType='Las')
processList = [ Use(run=runList,type='physical',region=theRegion,verbose=True,keepOnlyActive=False),
                ReadChanStat(type='physical',schema=schema,folder='/TILE/OFL02/STATUS/ADC'),
                MakeDQPlots(type='physical',runForDetail=runList[-1])]

g = Go(processList)

# before running this macro with sqlite file as input, please do the following:
#
# cd /afs/cern.ch/user/t/tilebeam/scratch0/Commissioning/DQLeaderArea/
# rm -f tileSqlite_BCH.db
# AtlCoolCopy "oracle://ATLAS_COOLPROD;schema=ATLAS_COOLOFL_TILE;dbname=CONDBR2" "sqlite://;schema=tileSqlite_BCH.db;dbname=CONDBR2" -f /TILE/OFL02/STATUS/ADC -create -t `CheckTagAssociation.py --folder=/TILE/OFL02/STATUS/ADC | awk 'END{print $NF}'`
