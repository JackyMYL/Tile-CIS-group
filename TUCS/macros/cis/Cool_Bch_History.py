import os
os.chdir(os.getenv('TUCS','.'))
exec(open('src/load.py').read(), globals())
import argparse
import itertools
import datetime

parser = argparse.ArgumentParser(description=
'Plots the detector performance of the calibration systems after status updates in COOL \n.', 
formatter_class=argparse.RawTextHelpFormatter)

parser.add_argument('--date', action='store', nargs='+', type=str, default='2012-01-01',
                    required=True, help=
  'Select runs to use. If you want to use \n \
a list of run numbers instead, use --ldate. \n \
You have to select SOMETHING for --date, \n \
but it is irrelevant if --ldate is used \n \
(There is probably a better way about that) \n \
Preferred formats: \n \
1) starting date as a string (takes from there \n \
to present). EX: \'YYYY-MM-DD\' \n \
2) runs X days, or X months in the past as string: \n \
   \'-28 days\' or \'-2 months\' \n \
3) All of the runs between two dates. \n \
   This should use two arguments \n \
   each of this form: \'Month DD, YYYY\' \n \
EX: --date 2011-10-01 or --date \'-28 days\' \n \
    --date \'January 01, 2011\' \'February 11, 2011\' \n ')
    
parser.add_argument('--calflags', action='store', nargs=1, type=str, default='All',
                    required=True, help=
  'Select calibration flags you want to see  \n ')
    
parser.add_argument('--preprocessing', action='store_true', default=False,
                    help=
'Use this switch to create a list of channels that \n\
should be automatically recalibrated during a \n\
reprocessing based on the date entered. Must be \n\
used with the ldate option.\n ')

args=parser.parse_args()

if len(args.date) == 1:
    runs             = args.date[0]
elif len(args.date) == 2:
    runs             = (args.date[1], args.date[0])
else:
    print '\
    --DATE HAS TOO MANY ARGUMENTS \n \
    USING ONLY THE FIRST'
    runs             = args.date[0]

if args.calflags[0] == 'CIS':
    cflags = args.calflags
elif args.calflags[0] == 'Las':
    cflags = args.calflags
elif args.calflags[0] == 'Cs':
    cflags = args.calflags
else: 
    cflags = args.calflags
print "cflags=", cflags
     
Preprocessing        = args.preprocessing

u = Use(run=runs, runType='CIS', preprocessing=Preprocessing)
Go([
        u,\
        database_flag_hist(calflags=cflags[0])])