#!/usr/bin/env python
# Author:   Christopher Tunnell   <tunnell@hep.uchicago.edu>
# Updated (November 18, 2010): Andrew Hard <ahard@uchicago.edu>
#
# Major Changes: Joshua Montgomery <Joshua.J.Montgomery@gmail.com>
# February 22, 2012

import argparse
import os.path
import itertools
parser = argparse.ArgumentParser(description=
'This macro is used for investigating problems \n \
with CIS. Plots can be created that summarize \n \
channel and detector status. These include: \n \
CIS event plots (showing the ADC counts for \n \
each of the 7 samples); distributions of \n \
fitted amplitudes for injected charges; \n \
CIS scans; a map of the channels that are \n \
not sending CIS data. See the twiki for more \n \
information and for example plots and how to \n \
produce them',
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
EX: --listdate 183009 183166 183367 \n ')


parser.add_argument('--region', action='store', nargs='*', type=str, default='',
                    required=False, help=
'Select the regions you wish to examine. \n \
Acceptable formatting is channels as they appear \n \
in the region.GetHash() format separated by spaces. \n \
Entire modules or barrels can be specified by \n \
leaving out the channel information or module and \n \
channel information respectively.\n \n \
EX: --region LBA_m22 EBC_m02_c00 EBA \n \
would produce plots for every channel in LBA22, \n \
every channel in the EBA partition, \n \
and EBC02 channel 00.\n ')

parser.add_argument('--usescans', action='store_true', default=False,
                    help=
'This is a switch that turns on functionality \n \
which looks at individual CIS scans for selected \n \
runs. be mindful that this will load in CIS \n \
scans for each channel for each run. \n \
This can be slow if you selected the whole \n \
detector and many runs.\n ')

parser.add_argument('--amplitude', action='store_true', default=False,
                    help=
'This is a switch that when selected \n \
will produce fitted amplitude distributions. \n \
of the CIS events being looked at. \n \
See the twiki for example plots. \n \
Be sure to specify the desired phase \n \
and DAC values! \n ')

parser.add_argument('--pevent', action='store_true', default=False,
                    help=
'This is a switch that when selected \n \
will produce plots of the actual CIS events.\n \
The plot produced will show the average of 4 \n \
identical events (one DAC value, one phase value) \n \
If --expert is selected, you can also look at an \n \
individual injection. \n \
Event-level data can be found with TimingFlag.py \n \n')

parser.add_argument('--injection', action='store', nargs=3, type=int,
                    default= [0,10,512], help=
'Use this flag to specify the Phase and DAC values \n \
of the injections you are interested in plotting. \n \
There are 3 required integer arguments (in order): \n \
1) Phase \n \
2) DAC (highgain) \n \
3) DAC (lowgain) \n \
Phase should be an integer of steps of 1.7ns. \n \
DACHI should on the order of 10 \n \
DACLO should be on the order of 512 \n \
See twiki for more specific information \n \
regarding DAC injection steps. \n \
Default is 0 10 512. \n \n')

parser.add_argument('--all', action='store_true', default=False,
                    help=
'This is a switch that when selected \n \
will produce plots for ALL of the selected \n \
regions. By default only scans for regions failing \n \
the 6 implemented and standard quality flags \n \
(Digital Errors, Chi2, Large RMS, Max Point, \n \
Likely Calibration, and DB Deviation) are produced. \n ')

parser.add_argument('--more', action='store_true', default=False,
                    help=
'This is a switch related to the --all option. \n \
If selected it extends the filter to include \n \
channels failing Edge Sample, Next To Edge Sample, \n \
and No Response quality flags. \n \
Defaults to False. \n ')

parser.add_argument('--WholeDetector', action='store_true', default=False,
                    help=
'This is a switch that allows for the production \n \
of plots concerning the whole detector rather \n \
than individual channels. The workers PlotNoCIS,\n \
PlotProblemModChannel, and CISRecalibrateProcedure \n \
are called. Defaults to False. \n ')


parser.add_argument('--expert', action='store', nargs=1, type=int, default=[0],
                    help=
'Using this flag you can specify the individual \n \
injection to be plotted by --pevent. \n \
Typically it will display the average of \n \
the four identical injections for the specified \n \
DAC and Phase values. It is this average that is \n \
used to compute the amplitude in CIS, but you \n \
specify injection by event number instead of you wish. \n ')

parser.add_argument('--verbose', action='store_true', default=False,
                    help=
'This is a switch that adds additional dignostic information \n \
to the CIS scan plots (ADC counts vs. injected charge). \n \
Only use this switch if also using the --usescans switch. \n \
Default value is false. Additional information includes: \n \
DB Variation (in percent) and the flag status (pass or fail) for \n \
Fail Max. Point, Next To Edge Sample, Large Injection RMS, Fail Likely Calib., \n \
No Response, Outlier, Low Chi2, Edge Sample, DB Deviatiion, \n \
Default Calibration, and Digital Errors. \n ')

args=parser.parse_args()

if len(args.date) == 1:
    runs      = args.date[0]
elif len(args.date) == 2:
    runs      = (args.date[1], args.date[0])
else:
    print('\
--DATE HAS TOO MANY ARGUMENTS \n \
USING ONLY THE FIRST')
    runs             = args.date[0]
wholedet      = args.WholeDetector
selected_region = args.region
useScans        = args.usescans
print_amplitude = args.amplitude
print_event     = args.pevent
single_event    = args.expert[0]
phase           = args.injection[0]
dachi           = args.injection[1]
daclo           = args.injection[2]
showAll         = args.all
moreInfo        = args.more
verbose         = args.verbose

if showAll and moreInfo:
    raise Exception(' \n \
ERROR: --ALL AND --MORE DO DIFFERENT THINGS. \n \
PLEASE CHOOSE ONE OR THE OTHER \n.')

if args.ldate:
    runs  = args.ldate

import os
os.chdir(os.getenv('TUCS','.'))
exec(open('src/load.py').read(), globals()) # don't remove this!

"""
step 5
dump debug information.  This will print all information in TUCS to the screen (stdout) and will 
save the detector tree, if you want to reload all information in Tucs with the LoadTree() worker
"""

debug = False

# EXPERTS ONLY BELOW

if print_amplitude or print_event:
    useSamples = True
else:
    useSamples = False

#badmodule = BadModule(datenum = 2, start_date = args.date[0], end_date = args.date[1])
u = Use(run=runs, runType='CIS', region=selected_region)

if useSamples:
    gs = GetSamples(all=showAll, region=selected_region, 
                    print_amplitude=print_amplitude, 
                    print_event=print_event, single_event=single_event)
else:
    gs = None

if useScans:
    gs2 = GetScans(all=showAll)
    scs = ShowCISScans(all=showAll)
else:
    gs2 = None
    scs = None

if debug:
    pr = Print()
    s = SaveTree()
else:
    pr = None
    s = None

p = PlotModuleChannel(runType1='CIS', parameter1='goodRegion', text1='Low-gain', invert1=True,
                      runType2='CIS', parameter2='goodRegion', text2='High-gain', invert2=True)

p2 = PlotProblemModChan(runType='CIS', parameter = 'CIS_problems', parameter2 = 'CIS_problems')

cisrecalpro = CISRecalibrateProcedure(all=False, MReg=False, Defaults=False, Deviations=False, Investigate=True)

readbchfromcool = ReadBadChFromCool(schema='OFL', tag='UPD4', Fast=True, storeADCinfo=True)
readcalfromcool = ReadCalibFromCool(schema='OFL', runType='CIS', folder='CALIB/CIS', tag='UPD4', data = 'DATA')

if len(args.date) == 1:
    badmodule = BadModule(datenum = 1, start_date = args.date[0])
else:
    badmodule = BadModule(datenum = 2, start_date = args.date[0], end_date = args.date[1])

if moreInfo:
    moreinfo = MoreInfo()
else:
    moreinfo = None

if wholedet:
   Go([\
      u,\
      ReadCIS(),\
      CleanCIS(),\
      readbchfromcool,\
      readcalfromcool,\
      CISFlagProcedure_modified(),\
      cisrecalpro,\
      moreinfo,\
      PlotNoCIS(),\
      p,\
      p2,\
      badmodule,\
      ])
else:
   Go([\
      u,\
      ReadCIS(),\
      CleanCIS(),\
      readbchfromcool,\
      readcalfromcool,\
      CISFlagProcedure_modified(),\
      moreinfo,\
      gs,\
      gs2,\
      scs,\
      ShowResiduals(),\
      IsEntireModuleBad(),\
      IsEntirePartitionBad(),\
      pr,\
      s,\
      ])
