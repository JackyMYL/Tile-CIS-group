#!/usr/bin/env python
# author: Bernardo Sotto-Maior Peralva <bernardo@cern.ch>
# date: July 30, 2010
# Major update on December 20, 2013 by Jeff Shahinian <jeffrey.david.shahinian@cern.ch>
# Macro to run trigger channel analysis and update the trigger bits in TileCal database.

"Trigger macro"

import os
import argparse
os.chdir(os.getenv('TUCS','.'))
exec(open('src/load.py').read(), globals()) # don't remove this!

parser = argparse.ArgumentParser(description=
'Run trigger channel analysis and update the trigger bits',
formatter_class=argparse.RawTextHelpFormatter)

parser.add_argument('--date', action='store',nargs='+', type=str, default='',
                    help=
'Select runs to use. If you want to use \n\
a list of run numbers instead, use --ldate. \n\
Preferred formats: \n\
1) starting date as a string (takes from there \n\
to present). EX: \'YYYY-MM-DD\' \n\
2) runs X days, or X months in the past as string: \n\
   \'-28 days\' or \'-2 months\' \n\
3) All of the runs between two dates. \n\
   This should use two arguments \n\
   each of this form: \'Month DD, YYYY\' \n\
EX: --date 2011-10-01 or --date \'-28 days\' \n\
    --date \'January 01, 2011\' \'February 11, 2011\' \n ')

parser.add_argument('--ldate', action='store', nargs='+', type=int, default=0,
                    help=
'Allows you to select runs to use \n\
by their actual run number. \n\
Run numbers should be separated by whitespace \n\
EX: --ldate 222876 223076 224185 \n ')

parser.add_argument('--plot_runs', action='store_true', default=False,
                    help=
'Use this switch to produce history plots as a function of run number. \n\
Default is to produce plots as a function of time. \n ')

parser.add_argument('--update', action='store_true', default=False,
                    help=
'Use this switch when you want to update the database. If used, \n\
CopyLocalChanStat.py will be called to make a copy of the \n\
current database in the form of an sqlite file, as well as \n\
WriteChanStat.py, which will create a new sqlite file \n\
containing updates to be put in the database. \n ')

args=parser.parse_args()


if args.date:
    if len(args.date) == 1:
        runList = args.date[0]
    elif len(args.date) == 2:
        runList = (args.date[1], args.date[0])
    else:
        print('\
        --DATE HAS TOO MANY ARGUMENTS \n\
USING ONLY THE FIRST')
        runList = args.date[0]
        
if args.ldate:
    runList = args.ldate
    print(runList)

if args.date and args.ldate:
    print('WARNING: BOTH RUNDATE AND RUNLIST SPECIFIED \n\
USING DATE 12-01-01')
    runList = '12-01-01'
if not args.date and not args.ldate:
    print('WARNING: NEITHER RUNDATE NOR RUNLIST SPECIFIED \n\
USING DATE 12-01-01')
    runList = '12-01-01'

## Variable plotTime=False for history plots in terms of runNumber, True in terms of month/year
if args.plot_runs == True:
    plotTime = False
else:
    plotTime = True


#u=Use(run=runList,type='physical',region=selected_region,verbose=True,keepOnlyActive=False)

#********************** General Setup - For History Plot and DB update *****************************
u=Use(run=runList,runType='L1Calo')

if args.update == True:
    processList = [u, HistoryTrigger(Run_List=runList, plotTime=plotTime),
                     #ReadBadChFromCool(schema='ONL',
                      #               tag='',
                       #              Fast=True,
                        #             storeADCinfo=False),
		     ReadBchFromCool(schema='COOLONL_TILE/CONDBR2',
				     folder='/TILE/ONL01/STATUS/ADC',
				     tag='',
				     Fast=True,
				     storeADCinfo=False),
                     CopyLocalChanStat(runType='L1Calo'),
                     WriteChanStat(runType='L1Calo'),
                   ]
else:
     processList = [u, HistoryTrigger(Run_List=runList, plotTime=plotTime),
                     #ReadBadChFromCool(schema='ONL',
                      #               tag='',
                       #              Fast=True,
                        #             storeADCinfo=False),
		     ReadBchFromCool(schema='COOLONL_TILE/CONDBR2',
                                     folder='/TILE/ONL01/STATUS/ADC',
                                     tag='',
                                     Fast=True,
                                     storeADCinfo=False),
                   ]
#***************************************************************************************************


g = Go(processList)
