#!/usr/bin/env python
# 
# Sam Meehan
# Updated for Batch Generation by Joshua Montgomery
#
# NOTE THAT HV USES LAS SOURCE NTUPLES
#

import sys
import argparse

parser = argparse.ArgumentParser(description='This is used to batch generate the \
common NTuples as used for the Calibration WebApp (PCATA023.cern.ch/plotting). \
It can generate NTuples for CIS, Las, Ces, and High Voltage (from Las source NTuples). \
All NTuples are dropped into a "CommonNTuple" folder in your TUCS director.')
                    
parser.add_argument('--runtype', action='store', nargs=1, type=str, default='NOTYPE',
                    required=True, help='Give runtype corresponding to runnnumber \
                    entered above.  If these two arguments are incompatible, an error \
                    will be returned. The translator can handle the following runtypes \
                    at the moment: \
                    cesium       = \'cesium\' \
                    cis          = \'CIS\' \
                    laser        = \'Las\' \
                    highvoltage  = \'HV\'')

parser.add_argument('--output', action='store', nargs=1, type=str, default='./',
                    help='Name the output folder. This will be a subdirectory in \
                    your plotting directory (generally ~/Tucs/plots/) \
                    Single quotes are only necessary for folders with a space \
                    in them. EX: --output OutPutFolder or --output \'Output Folder\' ')

parser.add_argument('--debug', action='store_true', default=False,
                    help='This is a switch that will print debugging messages added\
                    into the coding')

parser.add_argument('--mdebug', action='store_true', default=False,
                    help='This is a switch allowing the user to get resource consumption\
                    information using tools in TUCS workers')
                    
parser.add_argument('--date', action='store', nargs=1, type=str, default='2012-01-01',
                    required=True, help='Select runs to use. Preferred formats: \
                    1) list of integers: [194834, 194733] \
                    2) starting date as a string (takes from there to present):\
                       \'YYYY-MM-DD\' \
                    3) runs X days, or X months in the past as string: \
                       \'-28 days\' or \'-2 months\' \
                    EX: --date 2011-10-01 or --date \'-28 days\' ')
                    
parser.add_argument('--enddate', action='store', nargs=1, type=str, default='',
                    help='Select the enddate for the runs you wish to use if you \
                    want to specify an interval in the past. Accepted format is \
                    \'YYYY-MM-DD\' EX: --enddate 2012-02-01')


args=parser.parse_args()
import os
os.chdir(os.getenv('TUCS','.'))
exec(open('src/load.py').read(), globals()) # don't remove this!
import src.oscalls

filt_pos      = ' '
debug         = args.debug
mdebug        = args.mdebug
date          = args.date[0]
runtype       = args.runtype[0]
csrundict     = {}

if isinstance(args.enddate, list):
    enddate   = args.enddate[0] 
else:
    enddate   = args.enddate
    
if enddate:
    twoinput  = True
else:
    twoinput  = False
                                                                                                                    
if not args.output:
    output = args.output[0]
else:
    output = args.output[0]
    
############### MAKE STORAGE DIRECTORIES ###########
## FOR USER-VERSION OF THIS PROGRAM. NOT CRON-JOB ##
startdir    = src.oscalls.getPlotDirectory()
editdir     = startdir.split('/')
plotindex   = editdir.index('plots')
newstartdir = editdir[:plotindex]
newdir = []
for entry in newstartdir:
    newdir.append(entry)
newdir.append('CommonNTuples')
print newdir
NTupleDir  = '/'.join(newdir)
print NTupleDir
NTupleDir = '{0}/{1}-to-{2}'.format(NTupleDir, date, enddate)
print NTupleDir
src.oscalls.createDir(NTupleDir)
#####################################################

print '============================'
print 'Arguments Provided:'
print 'mdebug    : ',mdebug
print 'debug     : ',debug
print 'output    : ',output
print 'run       : '
print 'runtype   : ',runtype
print 'startdate : ',date
print 'enddate   : ',enddate
print '============================\n\n'



########################## DO WE NEED THIS? ####################################
# Check to ensure you are running on dedicated pcata023 machine
# machinename = os.uname()[1]
# print 'Your machine is ',machinename
# if machinename != 'pcata023':
#     print '------------------------------------------------------------------------'
#     print 'THIS PROGRAM MUST BE RUN ON pcata023. This is the dedicated TUCS machine. '
#     print 'If you do not have access, email samuel.meehan@cern.ch.'
#     print '<<<<<< Exiting >>>>>>'
#     print '------------------------------------------------------------------------'
#     sys.exit(0)

# make output directory if not already present
# CommonDir = '/tucs/CommonNTuples'
# cmd = 'mkdir '+CommonDir
# os.system(cmd)
# dirpath  = CommonDir+'/'+runtype
# os.system('mkdir -p '+dirpath)
################################################################################
#============================== SETUP COMMANDS ================================#


COOL_Cal_Las  = ReadCalibFromCool(schema='OFL',
                                   folder='CALIB/CES',
                                   runType='Las_REF',
                                   tag='UPD4', verbose=True)
                                   
COOL_Cal_Int  = ReadCalibFromCool(runType='integrator',
                                   schema='OFL',
                                   folder='INTEGRATOR',
                                   tag='UPD4')
                                   
COOL_Cal_Cs   = ReadCalibFromCool(runType='cesium',
                                   schema='OFL',
                                   folder='CALIB/CES',
                                   tag='UPD4')

COOL_Cal_CIS  = ReadCalibFromCool(runType='CIS',
                                   schema='OFL', 
                                   folder='CALIB/CIS',
                                   tag='UPD4')

COOL_Cal_ChannelProblems  = ReadBadChFromCool(schema='OFL',
                                            tag='UPD4',
                                            Fast=True,
                                            storeADCinfo=True)
                                   
Laser_Global_Shifts       = getGlobalShiftsDirect(siglim=2.0,n_iter=3,verbose=True)
Laser_Fibre_Shifts        = getFiberShiftsDirect(siglim=1.0, n_iter=3,verbose=True)

#====================== RUN COMMANDS DEPENDING ON SYSTEM ======================#

if runtype=='CIS':
    print 'TRANSLATING CIS .......'

    cispath  = NTupleDir+'/CIS'
    src.oscalls.createDir(cispath)
 
    MkFinalCsList = False
    MkInitialList = True
    InitialList   = []
    
    Go([Use_Common(run=date, run2=enddate, TWOInput=twoinput, runType='CIS', cscomment='', keepOnlyActive=True, region=''),
        Clear()],
        memdebug=mdebug)
        
    global run_list        
    for CISrun in InitialList:
        run_list.run_list = []
        filepath          = cispath+'/commonntuple_CIS_{0}.root'.format(CISrun)
        Go([Use(run=CISrun, runType='CIS'),
            ReadCIS(),
            CleanCIS(),
            NTuplerWorker( DebugFlag=debug , OutputPath=filepath, RunType=runtype ),
            Clear()],
            memdebug=mdebug)
        

if runtype=='Las':       
    print 'TRANSLATING Laser .......'
    
    laspath = NTupleDir+'/Las'
    src.oscalls.createDir(laspath)
    
    MkFinalCsList = False
    MkInitialList = True
    InitialList   = []
    
    Go([Use_Common(run=date, run2=enddate, TWOInput=twoinput, runType='Las', cscomment='',keepOnlyActive=True,region=''),
        Clear()],
        memdebug=mdebug)
    
    global run_list
    for laserrun in InitialList:
        run_list.run_list = []
        filepath          = laspath+'/commonntuple_laser_{0}.root'.format(laserrun)
        Go([Use(run=laserrun, filter=filt_pos, runType='Las', region=''),                                     
            ReadLaser(diode_num_lg=0, diode_num_hg=0, verbose=True),                                  
            CleanLaser(),                                
            COOL_Cal_Las,                                
            COOL_Cal_Int,
            COOL_Cal_ChannelProblems,
            Laser_Global_Shifts,                    
            Laser_Fibre_Shifts,                         
            getPMTShiftsDirect(),
            NTuplerWorker( DebugFlag=debug , OutputPath=filepath, RunType=runtype ),
            Clear()],
            memdebug=mdebug)
        
if runtype=='HV':       
    print 'TRANSLATING HighVoltage .......'

    hvpath = NTupleDir+'/HV'
    src.oscalls.createDir(hvpath)
    MkFinalCsList = False
    MkInitialList = True
    InitialList   = []
    
    Go([Use_Common(run=date, run2=enddate, TWOInput=twoinput, runType='Las', cscomment='',keepOnlyActive=True,region=''),
        Clear()],
        memdebug=mdebug)
    global run_list
    for hvrun in InitialList:
        run_list.run_list = [] 
        filepath = hvpath+'/commonntuple_HV_{0}.root'.format(hvrun)
        Go([Use(run=hvrun, filter=filt_pos, runType='Las', region=''),                                     
            ReadLaser(diode_num=0, verbose=True),
            CleanLaser(),
            COOL_Cal_Las,
            COOL_Cal_Int,
            COOL_Cal_ChannelProblems,
            Laser_Global_Shifts,
            Laser_Fibre_Shifts,
            getPMTShiftsDirect(),
            NTuplerWorker( DebugFlag=debug , OutputPath=filepath, RunType=runtype ),
            Clear()],
            memdebug=mdebug)
        
                          

if runtype=='cesium':

    cspath = NTupleDir+'/cesium'
    src.oscalls.createDir(cspath)
    MkFinalCsList = False
    MkInitialList = True
    InitialList   = []
    Go([Use_Common(run=date, run2=enddate, TWOInput=twoinput, runType='cesium', cscomment='',keepOnlyActive=True,region=''),
        Clear()],
        memdebug=mdebug)
    MkFinalCsList = True
    MkInitialList = False
    golist        = []
    print 'In header InitialCsList', InitialList
    for givenrun in InitialList:
        golist.append(Use_Common(run=givenrun, runType='cesium', cscomment='',keepOnlyActive=True,region=''))
        golist.append(Clear())
    print 'TRANSLATING cesium .......'
    Go(golist,
        memdebug=mdebug)                             

    MkFinalCsList = False
    MkInitialList = False
    
    for globalcskey in csrundict.keys():
            global run_list
            run_list      = RunList()
            filepath      = cspath+'/commonntuple_cesium_AtlRun_{0}.root'.format(globalcskey)
            csrunninglist = csrundict[globalcskey]
            print 'useing go list', csrunninglist
            Go([Use_Common(run=csrunninglist, runType='cesium', cscomment='',keepOnlyActive=True,region=''),                                      
                ReadCsFile(normalize=True, verbose=False),   
                COOL_Cal_Int,                                
                COOL_Cal_Cs,                                 
                COOL_Cal_ChannelProblems, 
                NTuplerWorker( DebugFlag=debug , OutputPath=filepath, RunType=runtype ),
                Clear()],                    
                memdebug=mdebug)  

print csrundict
print 'FINISHING TRANSLATION OF NTUPLE',runtype




################################################################################
### FOR FUTURE REFERENCE: COMPLETE CS RUN DICTIONARY 2009-01-01 -> 2012-06-10 ##
################################################################################
#
# 2009-01-01 --> 2012-01-01:
# {'159951': [2993, 2994, 2995, 2996, 2997, 2998, 2999, 3000, 3001, 3002, 3003, 3004, 3005, 3006, 3007], '185188': [4395, 4386, 4383, 4387, 4391, 4396, 4397, 4384, 4388, 4390, 4392, 4394, 4393, 4385, 4389], '171618': [3613, 3611, 3610, 3612, 3614, 3615], '125798': [1468, 1462, 1469, 1463, 1464, 1467, 1470, 1465, 1466], '179734': [4064, 4061, 4069, 4070, 4067, 4059, 4071, 4058, 4057, 4068, 4062, 4063, 4056, 4066, 4073, 4060, 4072, 4065], '166571': [3286, 3285, 3287, 3297, 3295, 3294, 3296, 3288, 3290, 3283, 3284, 3291, 3293, 3289, 3292], '121112': [1311, 1312, 1313, 1314, 1315, 1316, 1317, 1318, 1319], '146832': [2385, 2392, 2389, 2386, 2400, 2395, 2388, 2384, 2397, 2396, 2393, 2390, 2387, 2394, 2399, 2391, 2398], '113689': [1278, 1277, 1276, 1275, 1274, 1273, 1272], '100920': [209, 210, 211, 214, 212, 213], '193211': [4883, 4878, 4881, 4886, 4879, 4887, 4877, 4888, 4889, 4885, 4880, 4884, 4875, 4876, 4882], '171843': [3619, 3620, 3621], '192234': [4827, 4829, 4828, 4826, 4820, 4831, 4834, 4830, 4825, 4823, 4821, 4833, 4822, 4832, 4824], '160710': [3063, 3064, 3065, 3066, 3067, 3068, 3069, 3070, 3071, 3072, 3073, 3074, 3075, 3076, 3077], '175258': [3740, 3738, 3742, 3729, 3737, 3735, 3734, 3732, 3739, 3741, 3743, 3736, 3730, 3731, 3733], '118679': [1291, 1292, 1293, 1294, 1295, 1296], '189490': [4667, 4663, 4662, 4672, 4674, 4675, 4666, 4669, 4673, 4671, 4676, 4670, 4668, 4664, 4665], '183981': [4309, 4312, 4310, 4315, 4320, 4319, 4308, 4317, 4311, 4322, 4321, 4316, 4314, 4313, 4318], '171448': [3607, 3604, 3608, 3606, 3605, 3609], '156346': [2800, 2807, 2808, 2812, 2809, 2802, 2811, 2805, 2799, 2810, 2798, 2801, 2803, 2806, 2804], '160079': [3028, 3029, 3030, 3031, 3032, 3033, 3034, 3035, 3036, 3037, 3038, 3039, 3040, 3041, 3042], '146019': [2373, 2380, 2381, 2379, 2382, 2368, 2370, 2369, 2377, 2378, 2375, 2374, 2371, 2372, 2367, 2376], '193774': [4975, 4983, 4976, 4977, 4981, 4982, 4984, 4972, 4986, 4978, 4985, 4973, 4974, 4980, 4979], '120062': [1297, 1298, 1299, 1300, 1301, 1302, 1303, 1304, 1305, 1306, 1307, 1308, 1309, 1310], '175660': [3766, 3771, 3777, 3776, 3769, 3774, 3772, 3768, 3773, 3770, 3779, 3780, 3775, 3767, 3778], '115404': [1290, 1289, 1288, 1287, 1286, 1285], '183669': [4304, 4305, 4296, 4301, 4306, 4302, 4298, 4303, 4307, 4300, 4299, 4293, 4297, 4294, 4295], '187254': [4510, 4514, 4515, 4517, 4522, 4509, 4523, 4521, 4512, 4520, 4511, 4519, 4518, 4513, 4516], '138086': [1954, 1952, 1946, 1948, 1955, 1947, 1949, 1951, 1943, 1944, 1950, 1945, 1953], '190354': [4724, 4714, 4722, 4715, 4726, 4719, 4720, 4725, 4718, 4716, 4721, 4727, 4717, 4713, 4723], '188607': [4595, 4585, 4589, 4599, 4591, 4586, 4598, 4593, 4592, 4594, 4597, 4596, 4587, 4588, 4590], '170413': [3473, 3464, 3472, 3466, 3465, 3471, 3469, 3461, 3468, 3460, 3463, 3470, 3462, 3459, 3467], '185895': [4424, 4418, 4431, 4420, 4423, 4425, 4427, 4430, 4428, 4419, 4426, 4429, 4421, 4432, 4422], '186691': [4481, 4474, 4477, 4479, 4484, 4483, 4485, 4487, 4473, 4482, 4480, 4478, 4476, 4475, 4486], '168263': [3359, 3363, 3372, 3368, 3367, 3366, 3370, 3358, 3361, 3371, 3365, 3369, 3362, 3364, 3360], '171667': [3616, 3617, 3618], '164075': [3162, 3163, 3164, 3165, 3166, 3167, 3168, 3169, 3170, 3171, 3172, 3173, 3174, 3175, 3176], '136259': [1808, 1806, 1797, 1802, 1798, 1803, 1809, 1805, 1800, 1801, 1799, 1796, 1810, 1804, 1807], '143985': [2287, 2298, 2302, 2289, 2281, 2283, 2297, 2284, 2280, 2288, 2285, 2296, 2275, 2293, 2300, 2301, 2286, 2290, 2291, 2277, 2279, 2295, 2294, 2303, 2276, 2282, 2274, 2292, 2278, 2299], '150421': [2487, 2495, 2492, 2501, 2488, 2500, 2491, 2499, 2496, 2493, 2489, 2486, 2484, 2494, 2490, 2485, 2498, 2497], '194622': [5022, 5015, 5016, 5018, 5008, 5013, 5021, 5009, 5019, 5014, 5010, 5012, 5011, 5017, 5020], '130396': [1598, 1604, 1597, 1603, 1600, 1601, 1602, 1605, 1599], '114614': [1279, 1280, 1281, 1282, 1283, 1284], '155485': [2750, 2745, 2744, 2756, 2748, 2743, 2753, 2754, 2742, 2755, 2746, 2751, 2747, 2752, 2749], '132616': [1676, 1669, 1677, 1670, 1674, 1673, 1678, 1672, 1671, 1675], '153898': [2669, 2664, 2670, 2663, 2676, 2674, 2666, 2675, 2673, 2665, 2667, 2671, 2668, 2672, 2662], '158275': [2905, 2904, 2907, 2903, 2906, 2896, 2902, 2899, 2898, 2901, 2897, 2908, 2900, 2909, 2910], '170760': [3537, 3538, 3526, 3524, 3536, 3525, 3529, 3535, 3528, 3530, 3531, 3527, 3532, 3534, 3533], '100374': [197, 198, 199, 200, 201, 202, 203, 204, 205, 207, 206, 208], '128652': [1562, 1557, 1558, 1561, 1563, 1560, 1559, 1564, 1565], '139182': [1991, 1990, 1986, 1979, 1982, 1976, 1989, 1987, 1980, 1985, 1977, 1984, 1983, 1981, 1988, 1978], '134203': [1710, 1719, 1717, 1721, 1709, 1716, 1715, 1722, 1720, 1712, 1711, 1723, 1713, 1714], '146020': [2383], '181981': [4158, 4166, 4156, 4157, 4167, 4164, 4165, 4162, 4154, 4155, 4159, 4163, 4168, 4161, 4160]}
#
# 2012-01-01 --> 2012-06-10:
# {'195992': [5204, 5200, 5193, 5201, 5195, 5196, 5198, 5205, 5202, 5203, 5206, 5197, 5194, 5199], '198373': [5272, 5276, 5281, 5277, 5273, 5269, 5267, 5275, 5279, 5270, 5271, 5278, 5274, 5268, 5280], '195234': [5136, 5135, 5144, 5140, 5138, 5145, 5149, 5139, 5141, 5148, 5137, 5146, 5142, 5143, 5147], '202466': [5488, 5481, 5484, 5479, 5486, 5492, 5478, 5482, 5487, 5491, 5489, 5490, 5480, 5485, 5483], '195536': [5152, 5151], '194805': [5091, 5083, 5090, 5087, 5093, 5094, 5089, 5088, 5086, 5092, 5084, 5085], '195427': [5150], '199600': [5346, 5342, 5345, 5354, 5356, 5350, 5343, 5344, 5349, 5351, 5352, 5347, 5348, 5355, 5353]}
#
################################################################################
#
########################################## INCOMPLETE RUN SETS ###################################################                           
# runnumber     = [5150] #### TEST OF RUN NUMBER CONTINUITY, Jan 25, 2012 ---> inner run of 195427 (LB)          #                           
# runnumber     = [5151, 5152] #### TEST OF RUN NUMBER CONTINUITY, Jan 26, 2012 ---> inner run of 195536 (LB)    #                           
##################################################################################################################                           

