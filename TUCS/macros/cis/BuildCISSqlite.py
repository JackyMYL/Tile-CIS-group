############################################################################################
# Author : Jeff Shahinian                                                                  #
# Date   : November 12, 2013                                                               #
#                                                                                          #
#                                                                                          #
# Creates new sqlite files from local tileSqlite.db file for consolidated modules          #
# containing only the new CIS constants for that module.                                   #     
# Remember to update the tag if a new one has been created (would be nice to automate)     #
############################################################################################

import os, sys
os.chdir(os.getenv('TUCS','.'))
sys.path.insert(0, 'src')
from oscalls import *
import Get_Consolidation_Date
from TileCalibBlobObjs.Classes import *
import subprocess
import argparse
import datetime
import _mysql,MySQLdb


from TileCalibBlobPython import TileCalibTools
from TileCalibBlobObjs.Classes import *


parser = argparse.ArgumentParser(description=
'Builds sqlite files containing new CIS constants \n \
for consolidated modules',
formatter_class=argparse.RawTextHelpFormatter)

parser.add_argument('--cons_after', action='store', nargs=1, type=str, default=False,
                    required=False, help=
'This option will produce sqlite files for all modules that \n \
were consolidated after the date specified in the argument. \n \
A useful date to use would be the date of the last recalibration. \n \
This option is not required. \n \
Do not use this option if you want to make sqlite files \n \
for every consolidated module. \n \
Format should be \'YYYY-MM-DD\' \n \
EX: --cons_after \'2013-10-15\' \n ')

parser.add_argument('--cons_before', action='store', nargs=1, type=str, default=False,
                    required=False, help=
'This option will produce sqlite files for all modules that \n \
were consolidated before the date specified in the argument. \n \
This option is not required. \n \
Do not use this option if you want to make sqlite files \n \
for every consolidated module. \n \
Format should be \'YYYY-MM-DD\' \n \
EX: --cons_before \'2013-10-15\' \n ')

parser.add_argument('--cons_between', action='store', nargs=2, type=str, default=False,
                    required=False, help=
'This option will produce sqlite files for all modules that \n \
were consolidated berween the dates specified in the argument. \n \
This option is not required. \n \
Do not use this option if you want to make sqlite files \n \
for every consolidated module. \n \
Format should be \'YYYY-MM-DD\' \n \
EX: --cons_before \'2013-10-15\' \'2013-11-20\' \n ')
                    

args=parser.parse_args()

if args.cons_after:
    cons_date = datetime.datetime.strptime(str(args.cons_after)[2:-2], '%Y-%m-%d')
elif args.cons_before:
    cons_date = datetime.datetime.strptime(str(args.cons_before)[2:-2], '%Y-%m-%d')
elif args.cons_between:
    cons_date1 = datetime.datetime.strptime(str(args.cons_between[0]), '%Y-%m-%d')
    cons_date2 = datetime.datetime.strptime(str(args.cons_between[1]), '%Y-%m-%d')


# Connect to database
mysqldb = _mysql.connect(host='pcata007.cern.ch', user='reader')

# Build list of consolidated modules, sorted by consolidation date (starting with earliest)
# Also include the channel number to be used by oracle and the closest CIS run number since consolidation
partition = ['LBA','LBC','EBA','EBC']
cons_list = []
entry = []
#list = ''
for part in partition:
    if 'LBA' in part:
        part_num = 1
    if 'LBC' in part:
        part_num = 2
    if 'EBA' in part:
        part_num = 3
    if 'EBC' in part:
        part_num = 4
    for module in range(64):
        mod = part + "_m" + "%02d" % (module+1,)                                        # Format module name 
        cons_status = Get_Consolidation_Date.IsModCons(mod)                             # Check whether module has been consolidated
        if cons_status == True:                                                         # Only look at consolidated modules
            date = Get_Consolidation_Date.GetConsDate(mod)                              # Get consolidation date
            # Get the first CIS run number after consolidation:
            mysqldb.query("SELECT run FROM tile.comminfo WHERE date >'%d' AND type='CIS'" % (int(date.replace('-','')))) 
            run = mysqldb.store_result()                                                # Store the run number
            run = run.fetch_row()[0][0]                                                 # Format the result
            channel = TileCalibUtils.getDrawerIdx(part_num, module)                     # Get the oracle channel number for the module
            entry = {"module":mod, "date":date, "channel":channel, "run":run}           # Create a potential entry to the list
            if args.cons_after:                                                         # Was cons_after specified?
                if datetime.datetime.strptime(entry["date"], '%Y-%m-%d') > cons_date:   # Was module consolidated after cons_date?
                    cons_list.append(entry)                                             # If yes: include module
            elif args.cons_before:                                                      # Was cons_before specified?
                if datetime.datetime.strptime(entry["date"], '%Y-%m-%d') < cons_date:   # Was module consolidated before cons_date?     
                    cons_list.append(entry)                                             # If yes: include module
            elif args.cons_between:
                if datetime.datetime.strptime(entry["date"], '%Y-%m-%d') > cons_date1 and datetime.datetime.strptime(entry["date"], '%Y-%m-%d') < cons_date2:
                    cons_list.append(entry)
            else:
                cons_list.append(entry)

# Sort list by consolidation date (starting with earliest):
cons_list.sort(key=lambda x: datetime.datetime.strptime(x['date'], '%Y-%m-%d'))

print 'MAKING SQLITE FILES FOR THE FOLLOWING MODULES:'
for index in cons_list:
    print index



#process = subprocess.Popen("AtlCoolConsole.py 'sqlite://;schema=tileSqlite.db;dbname=CONDBR2'; listags /TILE/OFL02/CALIB/CIS/LIN", shell=True)
##process = subprocess.Popen("listags /TILE/OFL02/CALIB/CIS/LIN", shell=True, stdout=subprocess.PIPE)
#stdout, stderr = process.communicate()
#test = str(stdout)
#print 'TEST IS:', test


# Create sqlite file for each consolidated module, specifying the relevant run number:
for index in cons_list:
    process = subprocess.call("AtlCoolCopy.exe 'sqlite://;schema=tileSqlite.db;dbname=CONDBR2' 'sqlite://;schema=tileSqlite_%s_%s.db;dbname=CONDBR2' -create -folder /TILE/OFL02/CALIB/CIS/LIN -tag TileOfl02CalibCisLin-RUN2-UPD4-08 -ch %s -alliov -nrls %s 0" % (index["run"], index["module"], index["channel"], index["run"]), shell = True)


