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

db = _mysql.connect(host='pcata007.cern.ch', user='reader')
query = "select run  from tile.runDescr where (time>'2012-07-09' and time<'2012-07-10') or (time>'2012-08-14' and time<'2012-08-15')"
db.query(query)
r2 = db.store_result()	

runs=[]
for run in r2.fetch_row(maxrows=0):
    if int(run[0]) not in runs:
        runs.append(int(run[0]))
db.close()
print runs


#processors.append( Use(run='2012-07-09', run2='2012-08-14',runType='cesium', cscomment='',
#                       keepOnlyActive=True, TWOInput=True) )
processors.append( Use(run=sorted(runs), runType='cesium', cscomment='',
                       keepOnlyActive=True) )

processors.append( Use(run='2012-07-09', run2='2012-07-10', runType='Las',
                       filter='6', TWOInput=True) )
processors.append( Use(run='2012-08-14', run2='2012-08-16', runType='Las',
                       filter='6', TWOInput=True) )
#processors.append( Use(run='2012-08-14', runType='Las',
#                       filter='6' ) )

processors.append( ReadCsFile(processingDir="/afs/cern.ch/user/t/tilecali/w0/ntuples/cs",normalize=True) )
processors.append( ReadLaser(diode_num_lg=0, diode_num_hg=0, verbose=False) )
processors.append( CleanLaser() )

processors.append( ReadCalFromCool(folder='/TILE/OFL02/CALIB/CES',
                                   runType = 'Las_REF',
                                   tag = 'RUN2-HLT-UPD1-01', verbose=True) )#schema='sqlite://;schema=tileSqlite.db;dbname=CONDBR2',

#processors.append( ReadCalFromCool(runType='integrator',
#                                   schema='COOLOFL_TILE/CONDBR2',
#                                   folder='/TILE/OFL02/INTEGRATOR',
#                                   tag='UPD4') )

processors.append( ReadCalFromCool(runType='cesium',
                                   schema='COOLOFL_TILE/CONDBR2',
                                   folder='/TILE/OFL02/CALIB/CES',
                                   tag='UPD4') )

processors.append( getGlobalShiftsDirect(siglim=2.0,n_iter=3,verbose=True) )
processors.append( getFiberShiftsDirect(siglim=1.0, n_iter=3,verbose=False) )
processors.append( getPMTShiftsDirect() )

processors.append( LasOverCs())


Go(processors)

