
import os
os.chdir(os.getenv('TUCS','.'))
exec(open('src/load.py').read(), globals()) # don't remove this!

#x1 = ReadCsFile(processingDir="/afs/cern.ch/user/t/tilecali/w0/ntuples/cs")

# good runs taken in June 2009, no B field
#u1 = Use(run=[1292,1295,1296,1299,1307,1309,1310,1300,1306,1308],runType='cesium',region='',cscomment='',keepOnlyActive=True)
#u1 = Use(run=[1292,1295,1296,1299,1307,1309,1310,1300,1306,1308],runType='cesium',region='EBA_m15',cscomment='',keepOnlyActive=True)
#u1 = Use(run=123000,runType='cesium',region='EBC_m18',cscomment='',keepOnlyActive=False)

# good runs taken in June 2009, B field 'sol+tor'
#u1 = Use(run=[1311,1316,1319,1312,1314,1317,1313,1315,1318],runType='cesium',region='',cscomment='sol+tor',keepOnlyActive=True)

# good runs taken in October 2009 with B field
#u1 = Use(run=[1796,1797,1798,1799,1800,1801,1802,1803,1804,1805,1806,1807,1808,1809,1810],runType='cesium',region='',cscomment='sol+tor',keepOnlyActive=True,verbose=1)

# good runs taken in November 2009 with B field
#u1 = Use(run=[1976,1977,1978,1979,1980,1981,1982,1983,1984,1985,1986,1987,1988,1989,1990,1991],runType='cesium',region='',cscomment='sol+tor',keepOnlyActive=True,verbose=1)

# good runs taken in February 2010 with B field
#u1 = Use(run=[2384,2385,2386,2388,2388,2389,2390,2391,2392,2393,2394,2395,2396,2397,2399],runType='cesium',region='',cscomment='sol+tor',keepOnlyActive=True,verbose=1)
#two runs with higher speed in barrel
#00:11 Scan G2->G3, run 2398, base freq 25, 40 cm/s
#03:34 Scan G1->G3, run 2400, high speed (40 cm/s)

# good runs taken in March 2010 with B field
#u1 = Use(run=[2484,2485,2486,2487,2488,2489,2490,2491,2492,2493,2494,2495,2496,2497,2498,2499,2500,2501],runType='cesium',region='',cscomment='sol+tor',keepOnlyActive=True,verbose=1)

# good runs taken in May 2010 with B field
#u1 = Use(run=[2742,2743,2744,2745,2746,2747,2748,2749,2750,2751,2752,2753,2754,2755,2756],runType='cesium',region='',cscomment='sol+tor',keepOnlyActive=True,verbose=1)

# good runs taken in June 2010 with B field
#u1 = Use(run=[2896,2897,2898,2899,2900,2901,2902,2903,2904,2905,2906,2907,2908,2909,2910],runType='cesium',region='',cscomment='sol+tor',keepOnlyActive=True,verbose=1)

# good runs taken in Aug 2010 with B field
#u1 = Use(run=[3063,3064,3065,3066,3067,3068,3069,3070,3071,3072,3073,3074,3075,3076,3077],runType='cesium',region='',cscomment='sol+tor',keepOnlyActive=True,verbose=1)

# good runs taken in Sep 2010 with B field
#u1 = Use(run=[3162,3163,3164,3165,3166,3167,3168,3169,3170,3171,3172,3173,3174,3175,3176],runType='cesium',region='',cscomment='sol+tor',keepOnlyActive=True,verbose=1)

# good runs taken in Oct 2010 with B field
#u1 = Use(run=[3283,3284,3285,3286,3287,3288,3289,3290,3291,3292,3293,3294,3295,3296,3297],runType='cesium',region='',cscomment='sol+tor',keepOnlyActive=True,verbose=1)

# good runs taken in Nov 2010 with B field
#u1 = Use(run=[3358,3359,3360,3361,3362,3363,3364,3365,3366,3367,3368,3369,3370,3371,3372],runType='cesium',region='',cscomment='sol+tor',keepOnlyActive=True,verbose=1)

# good runs taken in Dec 2010 with B field
#u1 = Use(run=[3459,3460,3461,3462,3463,3464,3465,3466,3467,3468,3469,3470,3471,3472,3473],runType='cesium',region='',cscomment='sol+tor',keepOnlyActive=True,verbose=1)

# good runs taken in Feb 2011 with B field
#u1 = Use(run=[3766,3767,3768,3769,3770,3771,3772,3773,3774,3775,3776,3777,3778,3779,3780],runType='cesium',region='',cscomment='sol+tor',keepOnlyActive=True,verbose=1)

import sys
print sys.argv

qcThre=0.04
gapThre=0.05
zeroHV=False

# good runs taken on 18-Feb-2011 with B field
if sys.argv[1] == '18-Feb-2011':
    u1 = Use(run=[3766,3767,3768,3769,3770,3771,3772,3773,3774,3775,3776,3777,3778,3779,3780
                  ],runType='cesium',region='',cscomment='sol+tor',keepOnlyActive=True,
             updateC10=True,updateSpecial=True,specialFile='./specialcells_gap_2011-02-18.txt',verbose=1 )
    iofval=176153
    iov=176153
    qcThre=0.03

# good runs taken on 14-Apr-2011 with B field
if sys.argv[1] == '14-Apr-2011':
    u1 = Use(run=[4056,4057,4058,4059,4060,4061,4062,4063,4064,4065,4066,4067,4068,4069,4070,4071,4072,4073
                  ],runType='cesium',region='',cscomment='sol+tor',keepOnlyActive=True,
             updateC10=True,updateSpecial=True,specialFile='./specialcells_gap_2011-04-14.txt',verbose=1 )
    iov=179600
    qcThre=0.03
    gapThre=0.06

# good runs taken on 12-May-2011 with B field
if sys.argv[1] == '12-May-2011':
    u1 = Use(run=[4154,4155,4156,4157,4158,4159,4160,4161,4162,4163,4164,4165,4166,4167,4168
                  ],runType='cesium',region='',cscomment='sol+tor',keepOnlyActive=True,
             updateC10=True,updateSpecial=True,specialFile='./specialcells_gap_2011-05-12.txt',verbose=1 )
    iov=181900

# good runs taken on 18-Jun-2011 with B field
if sys.argv[1] == '18-Jun-2011':
    u1 = Use(run=[4293,4294,4295,4296,4297,4298,4299,4300,4301,4302,4303,4304,4305,4306,4307
                  ],runType='cesium',region='',cscomment='sol+tor',keepOnlyActive=True,
             updateC10=True,updateSpecial=True,specialFile='./specialcells_gap_2011-06-18.txt',verbose=1 )
    iov=183515

# good runs taken on 23-Jun-2011 with B field
if sys.argv[1] == '23-Jun-2011':
    u1 = Use(run=[4308,4309,4310,4311,4312,4313,4314,4315,4316,4317,4318,4319,4320,4321,4322
                  ],runType='cesium',region='',cscomment='sol+tor',keepOnlyActive=True,
             updateC10=True,updateSpecial=True,specialFile='./specialcells_gap_2011-06-23.txt',verbose=1 )
    iov=183960

# good runs taken on 09-Jul-2011 with B field
if sys.argv[1] == '09-Jul-2011':
    u1 = Use(run=[4383,4384,4385,4386,4387,4388,4389,4390,4391,4392,4393,4394,4395,4396,4397
                  ],runType='cesium',region='',cscomment='sol+tor',keepOnlyActive=True,
             updateC10=True,updateSpecial=True,specialFile='./specialcells_gap_2011-07-09.txt',verbose=1 )
    iov=185100

# good runs taken on 19-Jul-2011 with B field
if sys.argv[1] == '19-Jul-2011':
    u1 = Use(run=[4418,4419,4420,4421,4422,4423,4424,4425,4426,4427,4428,4429,4430,4431,4432
                  ],runType='cesium',region='',cscomment='sol+tor',keepOnlyActive=True,
             updateC10=True,updateSpecial=True,specialFile='./specialcells_gap_2011-07-19.txt',verbose=1 )
    iov=185890

# good runs taken on 01-Aug-2011 with B field
if sys.argv[1] == '01-Aug-2011':
    u1 = Use(run=[4473,4474,4475,4476,4477,4478,4479,4480,4481,4482,4483,4484,4485,4486,4487
                  ],runType='cesium',region='',cscomment='sol+tor',keepOnlyActive=True,
             updateC10=True,updateSpecial=True,specialFile='./specialcells_gap_2011-08-01.txt',verbose=1 )
    iov=186600

# good runs taken on 11-Aug-2011 with B field
if sys.argv[1] == '11-Aug-2011':
##    u1 = Use(run=[4509,4510,4511,4512,4513,4514,4515,4516,4517,4518,4519,4520,4521,4522,4523
##                  ],runType='cesium',region='',cscomment='sol+tor',keepOnlyActive=True,
##             updateC10=True,updateSpecial=True,specialFile='./specialcells_gap_2011-08-11.txt',verbose=1 )
    u1 = Use(run=[4509,4510,4511,4512,4513,4516,4519,4520,4521
                  ],runType='cesium',region='',cscomment='sol+tor',keepOnlyActive=True,
             updateC10=True,updateSpecial=True,specialFile='./specialcells_gap_2011-08-11.txt',verbose=1 )    
    iov=187050
    iofval=(187050,0)

# good runs taken on 17-Sep-2011 with B field
if sys.argv[1] == '17-Sep-2011':
    u1 = Use(run=[4662,4663,4664,4665,4666,4667,4668,4669,4670,4671,4672,4673,4674,4675,4676
                  ],runType='cesium',region='',cscomment='sol+tor',keepOnlyActive=True,
             updateC10=True,updateSpecial=True,specialFile='./specialcells_gap_2011-09-17.txt',verbose=1 )
    iov=188900

# good runs taken on 04-Oct-2011 with B field
if sys.argv[1] == '04-Oct-2011':
    u1 = Use(run=[4713,4714,4715,4716,4717,4718,4719,4720,4721,4722,4723,4724,4725,4726,4727
                  ],runType='cesium',region='',cscomment='sol+tor',keepOnlyActive=True,
             updateC10=True,updateSpecial=True,specialFile='./specialcells_gap_2011-10-04.txt',verbose=1 )
    iov=190350

# good runs taken on 31-Oct-2011 with B field
if sys.argv[1] == '31-Oct-2011':
    u1 = Use(run=[4820,4821,4822,4823,4824,4825,4826,4827,4828,4829,4830,4831,4832,4833,4834
                  ],runType='cesium',region='',cscomment='sol+tor',keepOnlyActive=True,
             updateC10=True,updateSpecial=True,specialFile='./specialcells_gap_2011-10-31.txt',verbose=1 )
    iov=192125

# good runs taken on 11-Nov-2011 with B field
if sys.argv[1] == '11-Nov-2011':
    u1 = Use(run=[4875,4876,4877,4878,4879,4880,4881,4882,4883,4884,4885,4886,4887,4888,4889
                  ],runType='cesium',region='',cscomment='sol+tor',keepOnlyActive=True,
             updateC10=True,updateSpecial=True,specialFile='./specialcells_gap_2011-11-11.txt',verbose=1 )
    iov=193200

# good runs taken on 25-Nov-2011 with B field
if sys.argv[1] == '25-Nov-2011':
    u1 = Use(run=[4972,4973,4974,4975,4976,4977,4978,4979,4980,4981,4982,4983,4984,4985,4986
                  ],runType='cesium',region='',cscomment='sol+tor',keepOnlyActive=True,
             updateC10=True,updateSpecial=True,specialFile='./specialcells_gap_2011-11-25.txt',verbose=1 )
    iov=193774

# good runs taken on 07-Dec-2011 without B field (after the end of collisions)
if sys.argv[1] == '07-Dec-2011':
    u1 = Use(run=[5008,5009,5010,5011,5012,5013,5014,5016,5015,5017,5018,5019,5020,5021,5022
                  ],runType='cesium',region='',cscomment='ANY',keepOnlyActive=True,
             updateC10=True,updateSpecial=True,specialFile='./specialcells_gap_2011-12-07.txt',verbose=1 )
    iov=194410

x1 = ReadCsFile(processingDir="/afs/cern.ch/user/t/tilecali/w0/ntuples/cs",normalize=True)

u = Use(run=223125,runType='Las')
rbch = ReadProblemChFromCool(schema="sqlite://;schema=tileSqlite.bch.db;dbname=CONDBR2",folder="/TILE/OFL02/STATUS/ADC",tag="RUN2-UPD4-08", storeADCinfo=True)

# reading integrators's gains
##r1 = ReadDB(useSqlite=True,runType='integrator',runNumber=iov,tag='RUN2-HLT-UPD1-00',version=1,sqlfile='tileSqlite_integrator_2011.db')s
r1 = ReadCalibFromCool(runType='integrator',schema='sqlite://;schema=tileSqlite_integrator_2011.db;dbname=CONDBR2',folder='/TILE/OFL02/INTEGRATOR',tag='RUN2-HLT-UPD1-00',runNumber=iov)
#r1 = ReadCalibFromCool(runType='integrator',schema='OFL',folder='INTEGRATOR',tag='RUN2-HLT-UPD1-00',runNumber=iov)

# reading cesium data from files
##r2 = ReadDB(useSqlite=True,runType='cesium',runNumber=iov,tag='RUN2-HLT-UPD1-01',version=2)
r2 = ReadCalibFromCool(runType='cesium',schema='sqlite://;schema=tileSqlite.db;dbname=CONDBR2',folder='/TILE/OFL02/CALIB/CES',tag='RUN2-HLT-UPD1-01',runNumber=iov)
#r2 = ReadCalibFromCool(runType='cesium',schema='OFL',folder='CALIB/CES',tag='UPD1',runNumber=iov)

# check data and print messages
#from src.cesium.chanlists import rerunchan
#qc = CsQC(qcthreshold=0.05,updthreshold=0.015,rerunlist=rerunchan)
qc = CsQC(qcthreshold=qcThre,gapthreshold=gapThre,updthreshold=0.00000000001,rerunlist=False)

# write to sqlite file.
# ALL channels will be writtens
##w1 = WriteDB(useSqliteRef=True,runType='cesium',runNumber=iov,offline_tag='RUN2-HLT-UPD1-01',version=2,allowZeroHV=zeroHV)

w1 = WriteDBNew(input_schema = 'sqlite://;schema=tileSqlite.db;dbname=CONDBR2',
                output_schema = 'sqlite://;schema=tileSqlite.db;dbname=CONDBR2',
                folder='/TILE/OFL02/CALIB/CES',
                tag='RUN2-HLT-UPD1-01',
                iov=iofval)
p1 = Print()

# Execution sequence. Modify it to change behaviour
##processors = [ u1, x1, r1, r2, qc, p1, w1]
processors = [ u1, rbch, x1, r1, r2, qc, p1, w1]

Go(processors)
