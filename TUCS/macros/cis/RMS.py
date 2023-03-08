#!/usr/bin/env python

# Author:  Andrew Hard           <ahard@uchicago.edu>
# January 18, 2011
#
# Updated : Joshua Montgomery
# Date    : June 14, 2012
# """
# This macro is used for obtaining RMS data for CIS scans. 
# The output is a plot of RMS value (for the fitted amplitudes of repeated 
# injections) as a function of the injected charge. 
# There is also an option to draw the fitted amplitude distributions associated 
# with each DAC Injection (and where the RMS values are derived from),
# though this slows down the program. 
# """

import argparse
import os.path
import itertools


parser = argparse.ArgumentParser(description=
'Plots the RMS distributions for the ADC channel \n \
and runs specificied by the user. These include \n \
the histograms of each DAC Injection as well as \n \
a plot of the RMS as a function of DAC injection. \n \
This is a great tool to investigate whether noise \n \
is due to reference voltages (or scales with injection). \n \
or is present in the pedestal to begin with. \n', 
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


parser.add_argument('--ldate', action='store', nargs='+', type=int, default=0,
                    help=
'Allows you to select runs to use \n \
by their actual run number. \n \
Run numbers should be separated by whitespace \n \
EX: --ldate 183009 183166 183367 \n ')


parser.add_argument('--region', action='store', nargs='*', type=str, default='',
                    required=True, help=
'Select ONE region (PMT --> so it can look at both high \n \
and low gains simulatneously, but only from one PMT at \n \
a time. \n \
Acceptable formatting is channels as they appear \n \
in the region.GetHash() format separated by spaces. \n \
EX: --region EBC_m02_c00 . \n')
                    
parser.add_argument('--output', action='store', nargs=1, type=str, required=True,
                    help=
'Name the output folder. It is a good idea to \n \
include the approximate date of the runs you \n \
are looking at. This will be a subdirectory \n \
in your plotting directory (generally ~/Tucs/plots/). \n \
Single quotes are only necessary for folders \n \
with a space in them. \n \
EX: --output OutPutFolder or --output \'Output Folder\' \n ')

parser.add_argument('--distplot', action='store_true', default=True,
                    help=
'This is a switch that defaults to on, and \n \
prints out histograms of each DAC-level injection. \n \
If turned off, only the distributions of RMS by DAC \n \
will be printed. \n ')
                    

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
if args.ldate:
    runs = args.ldate

selected_region      = args.region
Titling_Folder       = args.output[0]
dis_plots            = args.distplot


import os
os.chdir(os.getenv('TUCS','.'))
exec(open('src/load.py').read(), globals()) # don't remove this!


# EXPERTS ONLY BELOW

readbchfromcool = ReadBadChFromCool(schema='OFL', tag='UPD4', Fast=True)
readcalfromcool = ReadCalibFromCool(schema='OFL', runType='CIS', folder='CALIB/CIS', tag='UPD4')
u = Use(run=runs, runType='CIS', region=selected_region)


Go([\
    u,\
    ReadCIS(),\
    CleanCIS(),\
    readbchfromcool,\
    readcalfromcool,\
    CISFlagProcedure_modified(),\
    CISRecalibrateProcedure(),\
    GetRMSData(region=selected_region, draw_distribution_plots=dis_plots, folder_name=Titling_Folder ),\
    ])
