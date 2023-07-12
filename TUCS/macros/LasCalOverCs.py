#!/usr/bin/env python
# Atuh: Henric
# date: a Wednesday afternoon in Sept 2012
#
# Even though its not FORTRAN, its good to be able to print....
#        1         2         3         4         5         6         7         8 
#2345678901234567890123456789012345678901234567890123456789012345678901234567890

import _mysql
import os
os.chdir(os.getenv('TUCS','.'))
exec(open('src/load.py').read(), globals()) # don't remove this!

processors = []

#db = _mysql.connect(host='pcata007.cern.ch', user='reader')
#query = "select run  from tile.runDescr where (time>'2015-08-26' and time<'2015-08-27') or (time>'2015-07-16' and time<'2015-07-18')"
#db.query(query)
#r2 = db.store_result()	

#runs=[]
#for run in r2.fetch_row(maxrows=0):
#    if int(run[0]) not in runs:
#        runs.append(int(run[0]))
#db.close()
#print runs

#run_1 = 272491
#run_2 = 277319
run_1 = 295931
run_2 = 299887
run_2 = 299635
runs2=[run_1,run_2]


#processors.append( Use(run=sorted(runs), runType='cesium', cscomment='sol+tor',
#processors.append( Use(run='2015-07-15', run2='2015-08-30',runType='cesium', cscomment='sol+tor',
#                       keepOnlyActive=True) )

#runs=[9758,9759,9760,9761,9762,9763,9764,9765,9766,9767,9768,9769,9808,9809,9810,9811,9812,9813,9814,9815,9816]

processors.append( Use(run='2016-04-14', run2='2016-06-10',runType='cesium',
                       keepOnlyActive=True, TWOInput=True) )


#processors.append( Use(run='2015-08-25', run2='2015-08-28', runType='Las',
#                       filter='6', TWOInput=True) )
#processors.append( Use(run='2015-07-15', run2='2015-07-19', runType='Las',
#                       filter='6', TWOInput=True) )
processors.append( Use(runs2, runType='Las',
                       filter='6', TWOInput=True) )
#processors.append( Use(run='2012-08-14', runType='Las',
#                       filter='6' ) )

processors.append( ReadCsFile(processingDir="/afs/cern.ch/user/t/tilecali/w0/ntuples/cs",normalize=True) )
processors.append( ReadLaser(diode_num_lg=12, diode_num_hg=13, verbose=False) )
processors.append( CleanLaser() )
schema='sqlite://;schema=tileSqlite_272166.db;dbname=CONDBR2'
schema='sqlite://;schema=tileSqlite-2015.db;dbname=CONDBR2'
schema='sqlite://;schema=tileSqlite.db;dbname=CONDBR2'

processors.append( ReadCalFromCool(folder='/TILE/OFL02/CALIB/CES',
                                   runType = 'Las_REF',
                                   schema=schema,
                                   tag = 'RUN2-HLT-UPD1-01', verbose=True) )#schema='sqlite://;schema=tileSqlite.db;dbname=CONDBR2',

#processors.append( ReadCalFromCool(runType='integrator',
#                                   schema='COOLOFL_TILE/CONDBR2',
#                                   folder='/TILE/OFL02/INTEGRATOR',
#                                   tag='UPD4') )

processors.append( ReadCalFromCool(runType='cesium',
                                   schema='COOLOFL_TILE/CONDBR2',
                                   folder='/TILE/OFL02/CALIB/CES',
                                   tag='UPD4') )

#processors.append( getGlobalShiftsDirect(siglim=2.0,n_iter=3,verbose=True) )
#processors.append( getFiberShiftsDirect(siglim=1.0, n_iter=3,verbose=False) )
#processors.append( getPMTShift() )


processors.append(getFiberShifts(SkipEmergency=True,verbose=False,n_sig=3, n_iter=5))

# And finally the globally corrected PMT shifts  
processors.append( getPMTShiftsObsolete(Threshold_LB=0.,Threshold_EB=0.) ) 

# Red cell variations
processors.append(compute_mean_cell_var(gain=0,runNumber=run_2)) ##needed to rescale EB

# Rescale EB factors considering the correction computed by compute_mean_cell_var
processors.append( scaleEB() ) 

processors.append( LasOverCs())


Go(processors)

