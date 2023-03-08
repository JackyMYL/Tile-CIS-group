#!/usr/bin/env python
# Author: romano <sromanos@cern.ch>
#
# HV analysis
#

import os, sys
os.chdir(os.getenv('TUCS','.'))
exec(open('src/load.py').read(), globals()) # don't remove this!

# RegularJob mode to perform the daily HV analysis
# -m mode to perform the HV analysis between 2 dates

mode = sys.argv[1]
	
if mode=='RegularJob':		
	ini_Date = datetime.date.today() - datetime.timedelta(days=45) # ini_date (yesterday's date - 31 days)	
	fin_Date = datetime.date.today() - datetime.timedelta(days=1) # fin_date (yesterday's date) 
	
elif mode=='-m':		
	ini_y, ini_m, ini_d = int(sys.argv[2]), int(sys.argv[3]), int(sys.argv[4])
	fin_y, fin_m, fin_d = int(sys.argv[5]), int(sys.argv[6]), int(sys.argv[7])
	ini_Date = datetime.date(ini_y, ini_m, ini_d)
	fin_Date = datetime.date(fin_y, fin_m, fin_d)
	
else:
	print 'Bad arguments! Please insert: RegularJob or -m mode'	
	sys.exit()
	
print ini_Date
print fin_Date

processors = []

processors.append( dataTaker(ini_Date, fin_Date, mode) )

# Go!
Go(processors)


