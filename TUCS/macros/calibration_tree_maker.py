#!/usr/bin/env python
# Author: Marco van Woerden, December 2010 (mwoerden@gmail.com)
# This worker creates overview and time evolution plots for all three calibration types.

import os
os.chdir(os.getenv('TUCS','.'))
exec(open('src/load.py').read(), globals()) 							# DON'T REMOVE THIS
from src.oscalls import *
import ROOT
import numpy as m

runs  = '-9 month'									# RUN PERIOD, START
runs2 = '-5 month'									# RUN PERIOD, END

#regio = ['TILECAL_LBA_m09','TILECAL_LBA_m11','TILECAL_LBA_m12','TILECAL_LBA_m15','TILECAL_LBA_m19','TILECAL_LBA_m22','TILECAL_LBA_m30','TILECAL_LBA_m34','TILECAL_LBA_m47','TILECAL_LBA_m58','TILECAL_LBC_m07','TILECAL_LBC_m12','TILECAL_LBC_m22','TILECAL_LBC_m23','TILECAL_LBC_m33','TILECAL_LBC_m36','TILECAL_LBC_m40','TILECAL_LBC_m47','TILECAL_LBC_m29','TILECAL_LBC_m48','TILECAL_LBC_m52','TILECAL_EBA_m23','TILECAL_EBA_m50','TILECAL_EBC_m42','TILECAL_EBC_m43']

regio = ['TILECAL_EBC_m42','TILECAL_EBA_m12']
#rrr = ['TILECAL_EBC_m42']

f = ROOT.TFile(os.path.join(getPlotDirectory(),"calibration_tree.root"),"RECREATE")	# OPEN FILE
f.Close()

processors = []
cs1 = Use(run=[2384, 2385, 2386, 2387, 2388, 2389, 2390, 2391, 2392, 2393, 2394, 2395, 2396, 2399, 2484, 2485,  2486, 2487, 2488, 2489, 2490, 2491, 2492, 2493, 2494, 2495, 2496, 2497, 2498, 2499, 2500, 2501, 2742, 2743, 2744, 2745, 2746, 2747, 2748, 2749, 2750, 2751, 2752, 2753, 2754, 2755, 2756, 2896, 2897, 2898, 2899, 2900, 2901, 2902, 2903, 2904, 2905, 2907, 2908, 2909, 2910, 2910, 3063, 3064, 3065, 3066, 3067, 3068, 3069, 3070, 3071, 3072, 3073, 3074, 3075, 3076, 3077, 3162, 3163, 3164, 3165, 3166, 3167, 3168, 3169, 3170, 3171, 3172, 3173, 3174, 3175, 3176, 3177, 3178, 3179, 3180, 3181, 3182, 3183, 3184, 3185, 3186, 3187, 3188, 3189, 3190, 3191, 3192, 3193, 3194, 3195, 3196, 3197, 3198, 3199, 3200, 3201, 3202, 3203, 3204, 3205, 3206, 3207, 3208, 3209, 3210, 3211, 3212, 3213, 3214, 3215, 3216, 3217, 3218, 3219, 3220, 3221, 3222, 3223, 3224, 3225, 3226, 3227, 3228, 3229, 3230, 3231, 3232, 3233, 3234, 3235, 3236, 3237, 3238, 3239, 3240, 3241, 3242, 3243, 3244, 3245, 3246, 3247, 3248, 3249, 3250, 3251, 3252, 3253, 3254, 3255, 3256, 3257, 3258, 3259, 3260, 3261, 3262, 3263, 3264, 3265, 3266, 3267, 3268, 3269, 3270, 3271, 3272, 3273, 3274, 3275, 3276, 3277, 3278, 3279, 3280, 3281, 3282, 3283, 3284, 3285, 3286, 3287, 3288, 3289, 3290, 3291, 3292, 3293, 3294, 3295, 3296, 3297, 3298, 3299, 3300, 3301, 3302, 3303, 3304, 3305, 3306, 3307, 3308, 3309, 3310, 3311, 3312, 3313, 3314, 3315, 3316, 3317, 3318, 3319, 3320, 3321, 3322, 3323, 3324, 3325, 3326, 3327, 3328, 3329, 3330, 3331, 3332, 3333, 3334, 3335, 3336, 3337, 3338, 3339, 3340, 3341, 3342, 3343, 3344, 3345, 3346, 3347, 3348, 3349, 3350, 3351, 3352, 3353, 3354, 3355, 3356, 3357, 3604, 3605, 3606, 3607, 3608, 3609, 3610, 3611, 3612, 3613, 3614, 3615, 3616, 3617, 3618, 3619, 3620, 3621],runType='cesium',region=regio,cscomment='sol+tor',keepOnlyActive=True)
cs2 = ReadCsFile(processingDir="/data/cs",normalize=True)				# READ CESIUM ROOT FILES
cs3 = ReadCalibFromCool(runType = 'cesium', schema = 'OFL', folder = 'CALIB/CES', tag = 'UPD4')		# READ CESIUM DATABASE
processors.append(cs1)									# APPEND USE WORKER TO LIST
processors.append(cs2)									# APPEND READCSFILE WORKER TO LIST
processors.append(cs3)									# APPEND READDB WORKER TO LIST
las1 = Use(runs,run2=runs2,runType='Las',filter='6',region=regio,TWOInput=False)	# APPEND USE WORKER TO LIST
las2 = Use(runs,run2=runs2,runType='Las',filter='8',region=regio,TWOInput=False)	# APPEND USE WORKER TO LIST
las3 = ReadLaser()									# GRAB LASER DATA FROM DB
las4 = ReadCalibFromCool(runType = 'Las_REF', schema = 'OFL', folder = 'CALIB/CES', tag = 'UPD4')		# APPEND READDB WORKER TO LIST
las5 = getFiberShifts()									# GET FIBER SHIFTS
las6 = getPMTShiftsObsolete()									# GET PMT SHIFTS
processors.append(las1)									# APPEND USE WORKER TO LIST
processors.append(las2)									# APPEND USE WORKER TO LIST
processors.append(las3)									# APPEND READLASER WORKER TO LIST
processors.append(las4)									# APPEND READDB WORKER TO LIST
processors.append(las5)									# APPEND SHIFT CORRECTIONS
processors.append(las6)									# APPEND SHIFT CORRECTIONS
cis1 = Use(runs,run2=runs2,runType='CIS',region=regio,TWOInput=False)			# GRAB CIS RUNS 
cis2 = ReadCIS()									# GRAB CIS DATA FROM DATABASE
cis3 = ReadCalibFromCool(runType = 'CIS', schema = 'OFL', folder = 'CALIB/CIS', tag = 'UPD4') 									# ATLAS CONDDB
processors.append(cis1)									# APPEND USE WORKER TO LIST
processors.append(cis2)									# APPEND READCIS WORKER TO LIST
processors.append(cis3)									# APPEND READDB WORKER TO LIST
for rrr in regio:
    processors.append(saveonfile(region=rrr))
#for reg in rrr:									# LOOP OVER ALL REGIONS OF INTEREST
#    for c in range(0,48):								# LOOP OVER ALL CHANNELS
#        rg = reg + '_c%02i'%c								# SPECIFY REGION
        ### FINALLY PLOT IT ###
#        processors.append(saveonfile(region=rg))					# APPEND SAVEONFILE WORKER TO LIST
Go(processors)										# GO!
