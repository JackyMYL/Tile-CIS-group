#!/usr/bin/env python

import os
os.chdir(os.getenv('TUCS','.'))
exec(open('src/load.py').read(), globals()) # don't remove this!

# Author: Mikhail Makouski
# June 2009
# Look through some cesium runs and write constants to COOL

#x1 = ReadCsFile(processingDir="/afs/cern.ch/user/t/tilecali/w0/ntuples/cs")

# good runs taken in June 2009, no B field
#u1 = Use(run=[1292,1295,1296,1299,1307,1309,1310,1300,1306,1308],runType='cesium',region='',cscomment='',keepOnlyActive=True)
u1 = Use(run='2015-03-11',runType='cesium',region='',cscomment='sol+tor',keepOnlyActive=True)
#u1 = Use(run=123000,runType='cesium',region='EBC_m18',cscomment='',keepOnlyActive=False)

# region must be something like 'EBA_m18' or 'LBA' or 'LBC_m10_c11' 
# Use it for CsQC, but use '' (all) for writing the DB in the end.    

# good runs taken in June 2009, B field 'sol+tor'
#u1 = Use(run=[1311,1316,1319,1312,1314,1317,1313,1315,1318],runType='cesium',region='',cscomment='sol+tor',keepOnlyActive=True)

#x1 = ReadCsFile(processingDir="/data/cs",normalize=True)
x1 = ReadCsFile(processingDir="/afs/cern.ch/user/t/tilecali/w0/ntuples/cs",normalize=True)
# reading integrators's gains
#r1 = ReadDB(useSqlite=True,runType='integrator',tag='RUN2-HLT-UPD1-00',version=2)
#r1 = ReadDB(runType='integrator',tag='RUN2-HLT-UPD1-00',version=2)

r1 = ReadCalFromCool(runType='integrator',schema='COOLOFL_TILE/CONDBR2',folder='/TILE/OFL02/INTEGRATOR',tag='RUN2-HLT-UPD1-00')
#r1 = ReadCalibFromCool(runType='integrator',schema='sqlite://;schema=tileSqlite.db;dbname=CONDBR2',folder='/TILE/OFL02/INTEGRATOR',tag='UPD4')


# reading cesium data from files
#r2 = ReadDB(useSqlite=True,runType='cesium',tag='RUN2-HLT-UPD1-01',version=2)

if (os.environ.get('TUCS')!=None):
    schema = 'sqlite://;schema='+getResultDirectory()+'tileSqlite.db;dbname=CONDBR2'
else:
    schema = 'sqlite://;schema=tileSqlite.db;dbname=CONDBR2'

schema='COOLOFL_TILE/CONDBR2'
r2 = ReadCalFromCool(runType='cesium', schema = schema, folder='/TILE/OFL02/CALIB/CES',tag='UPD4')
#r2 = ReadCalibFromCool(runType='cesium',folder='CALIB/CES',tag='UPD4', schema = 'OFL)

# check data and print messages
qc = CsQC()

# write to sqlite file.
# ALL channels will be written!!! 
# You can't update only one partition. You must supply data for all partitions
# Whatever is missing will be overwritten by default values
#w1 = WriteDB(runType='cesium',offline_tag='RUN2-HLT-UPD1-01',version=2)

p1 = Print()


# Execution sequence. Modify it to change behaviour 
#processors = [ u1, p1,  x1, r1, r2, qc, w1]
processors = [ u1, x1, r1, r2, qc]
Go(processors)


