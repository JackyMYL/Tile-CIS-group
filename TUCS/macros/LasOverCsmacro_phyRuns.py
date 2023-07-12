#!/usr/bin/env python
# Author: Henric <henric.wilkens@cern.ch>
# date: a Wednesday afternoon in Sept 2012
# modifications: 
#		Feb, 2014 Silvestre M. Romano <sromanos@cern.ch>
# This macro was modified to make the las/Cs comparison for the laser events in the empty bunch crossing

import os
os.chdir(os.getenv('TUCS','.'))
exec(open('src/load.py').read(), globals()) # don't remove this!
import _mysql
import getopt,sys

#Example for execution of this macro, where: 
#iniLas and finLas are the initial and final laser run numbers
#iniCs and finCs are the Cs scan initial and final dates
#python macros/LasOverCsmacro_phyRuns.py --iniLas=207982 --finLas=208484 --iniCs='2012-08-04' --finCs='2012-08-15'

# read arguments
las_opt = [sys.argv[1],sys.argv[2]]
cs_opt = [sys.argv[3],sys.argv[4]]

las_runs = []
cs_dates = []

for i in range(2):
	las_runs.append(las_opt[i].split('=')[1])
	#print las_runs[i]
	
	cs_dates.append(cs_opt[i].split('=')[1])
	#print cs_dates[i]


runs = [int(las_runs[0]),int(las_runs[1])]
name_runs = las_runs[0]+'_'+las_runs[1]

processors = []

processors.append( Use(run=cs_dates[0], run2=cs_dates[1], TWOInput=True, runType='cesium', cscomment='sol+tor') ) 

processors.append( Use(run=runs, runType='Las', filter='2' ) )

processors.append( ReadCsFile(processingDir="/afs/cern.ch/user/t/tilecali/w0/ntuples/cs",normalize=True,skipITC=True) )
processors.append( ReadLaser_phyRuns(diode_num_lg=0, diode_num_hg=0, verbose=False) )

processors.append( CleanLaser() )

processors.append( ReadBadChFromCool( schema='OFL', tag='UPD4', Fast=True, storeADCinfo=True ) )

processors.append( ReadCalibFromCool(runType='Las_REF', schema='OFL', folder='CALIB/CES',  tag = 'UPD4') )#schema='sqlite://;schema=tileSqlite.db;dbname=CONDBR2',
processors.append( ReadCalibFromCool(runType='cesium' , schema='OFL', folder='CALIB/CES',  tag = 'UPD4') )

processors.append( getFiberShifts(verbose=False) )
processors.append( getPMTShiftsObsolete(Threshold_LB=0.0,Threshold_EB=0.0) )

processors.append( LasOverCs_phyRuns(name=name_runs, verbose=False) )

Go(processors)
