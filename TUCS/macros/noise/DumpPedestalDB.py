#!/usr/bin/env python

# TUCS common
import os, re
os.chdir(os.getenv('TUCS','.'))
exec(open('src/load.py').read(), globals()) # don't remove this!

import _NoiseCommon
from datetime import datetime, timedelta

# handle arguments
argparser = _NoiseCommon.common_noise_arguments('Print pedestal data from DB')

argparser.add_argument('--first_run', required=True, type=int, help='First run number', dest='first_run')
argparser.add_argument('--last_run', required=True, type=int, help='Last run number', dest='last_run')
argparser.add_argument('--regions', required=False, default=None, type=str, help='Regions', dest='regions')
argparser.add_argument('--print_stat', required=False, action='store_true', help='Print statistics', dest='print_stat')
argparser.add_argument('--ped_thresholds', nargs='+', type=float, default=[0.5, 1, 3, 10, 50, 100], required=False, help='Pedestal thresholds', dest='ped_thresholds')
argparser.add_argument('--exclude_regions', required=False, default=None, type=str, help='Regions to exclude', dest='exclude_regions')
argparser.add_argument('--supress_number_of_changed', required=False, default=30, type=int, help='Do not list all channels if the number of changed is above this threshold', dest='supress_number_of_changed')
argparser.add_argument('--check_bad', required=False, action='store_true', help='Check bad channels', dest='check_bad')
argparser.add_argument('--ped_low', required=False, type=float, default=5.0, help='Pedestal low thresholds', dest='ped_low')
argparser.add_argument('--print_details', required=False, action='store_true', help='Print details for ADC pedesta changes, using the warn_threshold', dest='print_details')
argparser.add_argument('--warn_threshold', required=False, type=float, default=0.8, help='Pedestal difference warning threshold', dest='warn_threshold')

args = argparser.parse_args()

# Used when printing details
grl = sorted([308979, 308982, 309010, 309039, 309074, 309165, 309166, 309375, 309390, 309440, 309516, 309640, 309674, 309759, 310015, 310210, 310247, 310249, 310341, 310370, 310405, 310468, 310473, 310574, 310634, 310691, 310738, 310781,310809, 310863, 310872, 310969, 311071, 311170, 311244, 311287, 311321, 311365, 311402, 311473, 311481, 308084, 308047, 307935, 307861, 307732, 307716, 307710, 307656, 307619, 307601, 307569, 307539, 307514, 307454, 307394, 307358, 307354, 307306, 307259, 307195, 307126, 306451, 306448, 306442, 306419, 306384, 306310, 306278, 306269, 305920, 305811, 305777, 305735, 305727, 305723, 305674, 305671, 305618, 305571, 305543, 305380, 304494, 304431, 304409, 304337, 304308, 304243, 304211, 304198, 304178, 304128, 304008, 304006, 303943, 303892, 303846, 303832, 303638, 303560, 303499, 303421, 303338, 303304, 303291, 303266, 303264, 303208, 303201, 303079, 303007, 302956, 302925, 302919, 302872, 302831, 302737, 302393, 302391, 302380, 302347, 302300, 302269, 302265, 302137, 302053, 301973, 301932, 301918, 301912, 300908, 300863, 300800, 300784, 300687, 300655, 300600, 300571, 300540, 300487, 300418, 300415, 300345, 300279, 299584, 299243, 299184, 299147, 299144, 299055, 298967, 298862, 298773, 298771, 298690, 298687, 298633, 298609, 298595, 297730])

low_stat_ped_runs = sorted(_NoiseCommon.get_runs_between(args.first_run, args.last_run, 1000,50000))

if args.regions:
    args.regions = args.regions.split(',')
else:
    args.regions = None

if args.exclude_regions:
    args.exclude_regions = args.exclude_regions.split(',')
else:
    args.exclude_regions = None

output = _NoiseCommon.NoiseOutput('', '', '')

processList = [UseDB(output=output, first_run=args.first_run, last_run=args.last_run, use_sqlite=args.dbUseSqlite, db_conn=args.dbConn, db_file=args.dbSqliteFile, db_folder_tag=args.dbFolderTag, run_type='Ped', verbose=args.verbose, regions=args.regions, exclude_regions=args.exclude_regions, ped_low=args.ped_low)]

if args.check_bad:
    output.print_log("Check bad channels. Use bad channel schema %s with tag %s." % (args.badChannelSchema, args.badChannelTag))
    processList.append(ReadBadChFromCool(schema=args.badChannelSchema, tag=args.badChannelTag, Fast=False, storeADCinfo=True))

if args.print_stat:
    processList.append(PedestalDBStatistics(output=output, pedestal_thresholds=args.ped_thresholds, supress_number_of_changed=args.supress_number_of_changed, check_bad=args.check_bad, verbose=args.verbose, print_details=args.print_details, phys_runs=grl, low_stat_runs=low_stat_ped_runs, warn_threshold=args.warn_threshold))

g = Go(processList, withMBTS=args.withMBTS, withSpecialMods=args.withSpecialMods, RUN2=args.RUN2)
