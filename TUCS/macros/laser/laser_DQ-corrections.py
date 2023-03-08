#!/usr/bin/env python
# Atuh: Henric
# date: A sunny day
#
# Even though its not FORTRAN, its good to be able to print....
#        1         2         3         4         5         6         7         8
#2345678901234567890123456789012345678901234567890123456789012345678901234567890

import os, sys
print sys.argv
os.chdir(os.getenv('TUCS','.'))
exec(open('src/laser/laserGetOpt.py').read(), globals())
exec(open('src/load.py').read(), globals()) # don't remove this!

# Laser Argument class
localArgParser=laserArgs(verbose=True)
# Add local arguments that are specific to this macro
localArgParser.add_local_arg('--newArg', action='store_true',  default=False, arghelp='New argument \n')
# Get arguments from parser 
localArgs=localArgParser.args_from_parser()
newArg=localArgs.newArg

produce_wiki = False
processors = [ Use(runs, run2=enddate, filter=filt_pos, runType='Las', region=region, TWOInput=twoinput) ]

if os.path.exists('/data/ntuples/las'):
    b = ReadLaser(processingDir='/data/ntuples/las', diode_num_lg=0, diode_num_hg=0, verbose=True)
else:
    b = ReadLaser(diode_num_lg=0, diode_num_hg=0)

processors.append( b )


processors.append( CleanLaser() )

#
# Read the reference values from the CondDB
#
# useSqlite=True will read info from 'tileSqlite.db' file (useful for debugging)
# storeADCinfo=False is necessary here otherwise you might have memory problems
#



processors.append( ReadBchFromCool( schema = 'COOLOFL_TILE/CONDBR2',
                                    folder = '/TILE/OFL02/STATUS/ADC',
                                    tag = 'UPD4',
                                    Fast = True,
                                    storeADCinfo = True) )

dbconnectionstring = 'sqlite://;schema=/afs/cern.ch/user/t/tilelas/public/DBWithLaserConstants/tileSqlite.db.3.cste;dbname=CONDBR2'

dbconnectionstring = 'sqlite://;schema=/afs/cern.ch/user/t/tilelas/public/DBWithLaserConstants/tileSqlite.3months.05032012.db;dbname=CONDBR2'


sqlitefile = '/afs/cern.ch/user/t/tilelas/public/tileSqlite_Ces_Mar-2012_with_Las_Cst.db'
sqlitefile = '/afs/cern.ch/user/t/tilelas/public/tileSqlite.June.db'
dbconnectionstring ='sqlite://;schema=%s;dbname=CONDBR2' % sqlitefile

processors.append( ReadCalFromCool( schema = dbconnectionstring,
                                    folder = '/TILE/OFL02/CALIB/CES',
                                    runType = 'Las_REF',
                                    tag = 'RUN2-HLT-UPD1-01',
                                    verbose = True) )

processors.append( ReadCalFromCool( schema = dbconnectionstring,
                                    folder = '/TILE/OFL02/CALIB/LAS/LIN',
                                    runType = 'Las',
                                    tag = 'RUN2-HLT-UPD1-00',
                                    verbose = True) )


processors.append( getGlobalShiftsDirect(siglim=2.0, n_iter=3, verbose=True) )
processors.append( do_global_plot(doEps = True) )
processors.append( getFiberShiftsDirect(siglim=1.0, n_iter=3, verbose=True) )
processors.append( getPMTShiftsDirect() )

if region == None:
    region=''

for chan in xrange(48):
    processors.append(do_calib_plot(limit=.1, part=EBC, mod=01, chan=chan, doEps = True))

Go(processors)


doHVPlot=False

if doHVPlot:
    if region=='' or region.find('LBA')!=-1:
        print "We will do problematic HV plot for LBA"
        processors.append(do_calib_plot(limit=.1, part=LBA, mod=15, chan=16, doEps = True)) # HV pb
        processors.append(do_calib_plot(limit=.1, part=LBA, mod=17, chan=16, doEps = True)) # HV pb
        processors.append(do_calib_plot(limit=.1, part=LBA, mod=19, chan=02, doEps = True)) # HV pb
        processors.append(do_calib_plot(limit=.1, part=LBA, mod=21, chan=34, doEps = True)) # HV pb
        processors.append(do_calib_plot(limit=.1, part=LBA, mod=23, chan=3,  doEps = True)) # HV pb
        processors.append(do_calib_plot(limit=.1, part=LBA, mod=23, chan=42, doEps = True)) # HV pb
        processors.append(do_calib_plot(limit=.1, part=LBA, mod=33, chan=16, doEps = True)) # HV pb
        processors.append(do_calib_plot(limit=.1, part=LBA, mod=43, chan=01, doEps = True)) # HV pb
        processors.append(do_calib_plot(limit=.1, part=LBA, mod=47, chan=02, doEps = True)) # HV pb
        processors.append(do_calib_plot(limit=.1, part=LBA, mod=50, chan=23, doEps = True)) # HV pb
        processors.append(do_calib_plot(limit=.1, part=LBA, mod=51, chan= 9, doEps = True)) # HV pb, Sacha' list
        processors.append(do_calib_plot(limit=.1, part=LBA, mod=53, chan=16, doEps = True)) # HV pb
        processors.append(do_calib_plot(limit=.1, part=LBA, mod=59, chan=12, doEps = True)) # HV pb
        processors.append(do_calib_plot(limit=.1, part=LBA, mod=61, chan=13, doEps = True)) # HV pb

    if region=='' or region.find('LBC')!=-1:
        print "We will do problematic HV plot for LBC"
        processors.append(do_calib_plot(limit=.1, part=LBC, mod= 3, chan=41, doEps = True)) # HV pb
        processors.append(do_calib_plot(limit=.1, part=LBC, mod= 4, chan=20, doEps = True)) # HV pb, Tho's list
        processors.append(do_calib_plot(limit=.1, part=LBC, mod=23, chan=13, doEps = True)) # Henric adds,  HV pb
        processors.append(do_calib_plot(limit=.1, part=LBC, mod=27, chan=17, doEps = True)) # HV pb
        processors.append(do_calib_plot(limit=.1, part=LBC, mod=28, chan= 7, doEps = True)) # HV pb, Henric adds,
        processors.append(do_calib_plot(limit=.1, part=LBC, mod=42, chan=40, doEps = True)) # HV pb
        processors.append(do_calib_plot(limit=.1, part=LBC, mod=43, chan=36, doEps = True)) # HV pb
        processors.append(do_calib_plot(limit=.1, part=LBC, mod=44, chan=18, doEps = True)) # HV pb
        processors.append(do_calib_plot(limit=.1, part=LBC, mod=44, chan=38, doEps = True)) # HV pb
        processors.append(do_calib_plot(limit=.1, part=LBC, mod=45, chan=29, doEps = True)) # HV pb
        processors.append(do_calib_plot(limit=.1, part=LBC, mod=45, chan=47, doEps = True)) # Henric adds, HV pb
        processors.append(do_calib_plot(limit=.1, part=LBC, mod=46, chan=41, doEps = True)) # HV pb
        processors.append(do_calib_plot(limit=.1, part=LBC, mod=57, chan=13, doEps = True)) # HV pb
        processors.append(do_calib_plot(limit=.1, part=LBC, mod=58, chan=21, doEps = True)) # HV pb
        processors.append(do_calib_plot(limit=.1, part=LBC, mod=59, chan= 4, doEps = True)) # HV pb
        processors.append(do_calib_plot(limit=.1, part=LBC, mod=60, chan=16, doEps = True)) # HV pb
        processors.append(do_calib_plot(limit=.1, part=LBC, mod=62, chan=23, doEps = True)) # HV pb
        processors.append(do_calib_plot(limit=.1, part=LBC, mod=62, chan=39, doEps = True)) # HV pb

    if region=='' or region.find('EBA')!=-1:
        processors.append(do_calib_plot(limit=.1, part=EBA, mod= 7, chan=39, doEps = True)) # HV pb
        processors.append(do_calib_plot(limit=.1, part=EBA, mod=17, chan= 8, doEps = True)) # HV pb
        processors.append(do_calib_plot(limit=.1, part=EBA, mod=35, chan= 5, doEps = True)) # HV pb
        processors.append(do_calib_plot(limit=.1, part=EBA, mod=38, chan=10, doEps = True)) # HV pb
        processors.append(do_calib_plot(limit=.1, part=EBA, mod=40, chan=30, doEps = True)) # HV pb
        processors.append(do_calib_plot(limit=.1, part=EBA, mod=61, chan=11, doEps = True)) # HV pb

    if region=='' or region.find('EBC')!=-1:
        processors.append(do_calib_plot(limit=.1, part=EBC, mod=20, chan= 0, doEps = True)) # HV pb but MBTS
        processors.append(do_calib_plot(limit=.1, part=EBC, mod=30, chan=13, doEps = True)) # HV pb
        processors.append(do_calib_plot(limit=.1, part=EBC, mod=31, chan=36, doEps = True)) # HV pb
        processors.append(do_calib_plot(limit=.1, part=EBC, mod=36, chan= 5, doEps = True)) # HV pb
        processors.append(do_calib_plot(limit=.1, part=EBC, mod=40, chan=13, doEps = True)) # HV pb
        processors.append(do_calib_plot(limit=.1, part=EBC, mod=51, chan=13, doEps = True)) # HV pb
        processors.append(do_calib_plot(limit=.1, part=EBC, mod=51, chan=14, doEps = True)) # HV pb
        processors.append(do_calib_plot(limit=.1, part=EBC, mod=53, chan=21, doEps = True)) # HV pb
        processors.append(do_calib_plot(limit=.1, part=EBC, mod=56, chan=36, doEps = True)) # HV pb
        processors.append(do_calib_plot(limit=.1, part=EBC, mod=60, chan= 6, doEps = True)) # HV pb
        processors.append(do_calib_plot(limit=.1, part=EBC, mod=60, chan=10, doEps = True)) # Why marked?
        processors.append(do_calib_plot(limit=.1, part=EBC, mod=61, chan=17, doEps = True)) # HV pb
        processors.append(do_calib_plot(limit=.1, part=EBC, mod=61, chan=22, doEps = True)) # HV pb
        processors.append(do_calib_plot(limit=.1, part=EBC, mod=64, chan=32, doEps = True)) # Henric adds, HV pb


#
# Go for it!!!
#




# Sacha & Tho channels:

if region=='' or region.find('LBA')!=-1:
    processors.append(do_calib_plot(limit=.1, part=LBA, mod= 4, chan=44, doEps = True)) #Emanuelle' list
    processors.append(do_calib_plot(limit=.1, part=LBA, mod= 6, chan=26, doEps = True)) #Sacha' list
    processors.append(do_calib_plot(limit=.1, part=LBA, mod=14, chan=36, doEps = True)) #Sacha' list
    processors.append(do_calib_plot(limit=.1, part=LBA, mod=14, chan=46, doEps = True)) #Sacha' list
    processors.append(do_calib_plot(limit=.1, part=LBA, mod=17, chan= 6, doEps = True)) #Sacha' list
#this one expose a bug in the ploting of deviation....range goes to +/- 100%
    processors.append(do_calib_plot(limit=.1, part=LBA, mod=23, chan=45, doEps = True)) # Clement's list
    processors.append(do_calib_plot(limit=.1, part=LBA, mod=29, chan= 2, doEps = True)) # Henric adds
    processors.append(do_calib_plot(limit=.1, part=LBA, mod=37, chan= 1, doEps = True)) #Tho's list
    processors.append(do_calib_plot(limit=.1, part=LBA, mod=44, chan=23, doEps = True)) #Tho's list
    processors.append(do_calib_plot(limit=.1, part=LBA, mod=48, chan=45, doEps = True)) # Henric adds
    processors.append(do_calib_plot(limit=.1, part=LBA, mod=50, chan=18, doEps = True)) #Sacha' list
    processors.append(do_calib_plot(limit=.1, part=LBA, mod=49, chan= 4, doEps = True)) # Emanuelle' list
    processors.append(do_calib_plot(limit=.1, part=LBA, mod=51, chan=12, doEps = True)) #
    processors.append(do_calib_plot(limit=.1, part=LBA, mod=59, chan=38, doEps = True)) #Tho's list
    processors.append(do_calib_plot(limit=.1, part=LBA, mod=61, chan=13, doEps = True)) #
    processors.append(do_calib_plot(limit=.1, part=LBA, mod=62, chan=18, doEps = True)) # Clement's list

    ## The masked channels unspecified
    processors.append(do_calib_plot(limit=.1, part=LBA, mod=29, chan= 1, doEps = True))
    processors.append(do_calib_plot(limit=.1, part=LBA, mod=51, chan= 9, doEps = True))

    ## The masked ADC unspecified
    processors.append(do_calib_plot(limit=.1, part=LBA, mod= 2, chan=33, doEps = True))
    processors.append(do_calib_plot(limit=.1, part=LBA, mod= 2, chan=35, doEps = True))
    processors.append(do_calib_plot(limit=.1, part=LBA, mod=13, chan=35, doEps = True))
    processors.append(do_calib_plot(limit=.1, part=LBA, mod=19, chan=23, doEps = True))
    processors.append(do_calib_plot(limit=.1, part=LBA, mod=37, chan=19, doEps = True))

    ## The masked wrong HV
    # processors.append(do_calib_plot(limit=.1, part=LBA, mod= 6, chan=26, doEps = True))
    processors.append(do_calib_plot(limit=.1, part=LBA, mod=18, chan=13, doEps = True))
    processors.append(do_calib_plot(limit=.1, part=LBA, mod=21, chan=19, doEps = True))
    #    processors.append(do_calib_plot(limit=.1, part=LBA, mod=59, chan=38, doEps = True))

    ## Adc dead
    #processors.append(do_calib_plot(limit=.1, part=LBA, mod=23, chan=45, doEps = True))
    #processors.append(do_calib_plot(limit=.1, part=LBA, mod=37, chan= 1, doEps = True))
    #processors.append(do_calib_plot(limit=.1, part=LBA, mod=62, chan=18, doEps = True))

    ## No PMT connected
    processors.append(do_calib_plot(limit=.1, part=LBA, mod=17, chan=14, doEps = True))
    processors.append(do_calib_plot(limit=.1, part=LBA, mod=17, chan=26, doEps = True))




if region=='' or region.find('LBC')!=-1:
    processors.append(do_calib_plot(limit=.1, part=LBC, mod= 3, chan=44, doEps = True)) #Tho's list
    processors.append(do_calib_plot(limit=.1, part=LBC, mod= 4, chan=20, doEps = True))
    processors.append(do_calib_plot(limit=.1, part=LBC, mod= 9, chan=40, doEps = True))
    processors.append(do_calib_plot(limit=.1, part=LBC, mod=11, chan=28, doEps = True))
    processors.append(do_calib_plot(limit=.1, part=LBC, mod=14, chan= 1, doEps = True))
    processors.append(do_calib_plot(limit=.1, part=LBC, mod=18, chan=13, doEps = True)) #Tho's list
#processors.append(do_calib_plot(limit=.1, part=LBC, mod=28, chan= 4, doEps = True)) #Sacha' list
    processors.append(do_calib_plot(limit=.1, part=LBC, mod=28, chan= 7, doEps = True)) #Sacha' list
    processors.append(do_calib_plot(limit=.1, part=LBC, mod=28, chan=35, doEps = True)) #Sacha' list
    processors.append(do_calib_plot(limit=.1, part=LBC, mod=38, chan=21, doEps = True)) #
    processors.append(do_calib_plot(limit=.1, part=LBC, mod=38, chan=25, doEps = True)) #
    processors.append(do_calib_plot(limit=.1, part=LBC, mod=44, chan=23, doEps = True)) #
    processors.append(do_calib_plot(limit=.1, part=LBC, mod=44, chan=36, doEps = True)) #
    processors.append(do_calib_plot(limit=.1, part=LBC, mod=45, chan=47, doEps = True)) #
    processors.append(do_calib_plot(limit=.1, part=LBC, mod=46, chan=37, doEps = True))              # Tomas list
    processors.append(do_calib_plot(limit=.1, part=LBC, mod=49, chan=27, doEps = True)) #Tho's list
#processors.append(do_calib_plot(limit=.1, part=LBC, mod=51, chan=25, doEps = True)) #Sacha' list
    processors.append(do_calib_plot(limit=.1, part=LBC, mod=55, chan= 2, doEps = True)) #Tho's list
    processors.append(do_calib_plot(limit=.1, part=LBC, mod=55, chan= 3, doEps = True)) # Henric adds
    processors.append(do_calib_plot(limit=.1, part=LBC, mod=59, chan=33, doEps = True)) #Tho's list
    processors.append(do_calib_plot(limit=.1, part=LBC, mod=62, chan=32, doEps = True))              # Tomas list
    processors.append(do_calib_plot(limit=.1, part=LBC, mod=63, chan=41, doEps = True)) #Tho's list
    processors.append(do_calib_plot(limit=.1, part=LBC, mod=60, chan=34, doEps = True)) #Sacha' list
    ## The masked channels unspecified
    processors.append(do_calib_plot(limit=.1, part=LBC, mod= 2, chan=38, doEps = True))
    processors.append(do_calib_plot(limit=.1, part=LBC, mod=21, chan=47, doEps = True))
    processors.append(do_calib_plot(limit=.1, part=LBC, mod=26, chan=34, doEps = True)) # Henric adds
    #    processors.append(do_calib_plot(limit=.1, part=LBC, mod=31, chan=23, doEps = True)) # 2012 Reapirs?
    processors.append(do_calib_plot(limit=.1, part=LBC, mod=36, chan=24, doEps = True))

    ## The masked ADCs unspecified
    processors.append(do_calib_plot(limit=.1, part=LBC, mod=37, chan=32, doEps = True)) # 2012 Reapirs?

    ## The masked wrong HV
    processors.append(do_calib_plot(limit=.1, part=LBC, mod=16, chan=26, doEps = True))
    processors.append(do_calib_plot(limit=.1, part=LBC, mod=29, chan=26, doEps = True)) #Tho's list
    processors.append(do_calib_plot(limit=.1, part=LBC, mod=61, chan=13, doEps = True))

    ## Adc dead
    #Unmasked processors.append(do_calib_plot(limit=.1, part=LBC, mod=26, chan=23, doEps = True))


if region == '' or region.find('EBA')!=-1:
    #processors.append(do_calib_plot(limit=.1, part=EBA, mod= 3, chan= 0, doEps = True)) # 7th Sept. MBTS
    processors.append(do_calib_plot(limit=.1, part=EBA, mod= 3, chan= 1, doEps = True)) # 7th Sept.
    processors.append(do_calib_plot(limit=.1, part=EBA, mod= 3, chan= 2, doEps = True)) # 7th Sept.
    processors.append(do_calib_plot(limit=.1, part=EBA, mod= 3, chan= 3, doEps = True)) # 7th Sept.
    processors.append(do_calib_plot(limit=.1, part=EBA, mod= 3, chan= 4, doEps = True)) # 7th Sept.
    processors.append(do_calib_plot(limit=.1, part=EBA, mod= 3, chan= 5, doEps = True)) # 7th Sept.
#    processors.append(do_calib_plot(limit=.1, part=EBA, mod= 4, chan= 0, doEps = True)) # Emmanuelle' list
    processors.append(do_calib_plot(limit=.1, part=EBA, mod= 7, chan=10, doEps = True)) # Henric adds, Emmanuelle' list
#processors.append(do_calib_plot(limit=.1, part=EBA, mod=12, chan=30, doEps = True)) #Sacha' list
    processors.append(do_calib_plot(limit=.1, part=EBA, mod=14, chan= 1, doEps = True)) # Henric adds Nov 08
    processors.append(do_calib_plot(limit=.1, part=EBA, mod=19, chan= 0, doEps = True)) # Henric adds
    processors.append(do_calib_plot(limit=.1, part=EBA, mod=21, chan=36, doEps = True)) #Tho's list
    processors.append(do_calib_plot(limit=.1, part=EBA, mod=25, chan=15, doEps = True)) #Sacha' list
    processors.append(do_calib_plot(limit=.1, part=EBA, mod=43, chan= 5, doEps = True)) # Clement's list
    processors.append(do_calib_plot(limit=.1, part=EBA, mod=43, chan=38, doEps = True)) # Emmanuelle's list
    processors.append(do_calib_plot(limit=.1, part=EBA, mod=51, chan= 7, doEps = True)) # Emmanuelle's list
#processors.append(do_calib_plot(limit=.1, part=EBA, mod=55, chan=36, doEps = True)) #Tho's list
    processors.append(do_calib_plot(limit=.1, part=EBA, mod=57, chan=22, doEps = True)) # Henric new

    ## The masked channels unspecified
    #processors.append(do_calib_plot(limit=.1, part=EBA, mod=39, chan= 4, doEps = True)) # half C10
    #processors.append(do_calib_plot(limit=.1, part=EBA, mod=40, chan= 4, doEps = True)) # half C10
    #processors.append(do_calib_plot(limit=.1, part=EBA, mod=41, chan= 4, doEps = True)) # half C10
    processors.append(do_calib_plot(limit=.1, part=EBA, mod=41, chan=13, doEps = True))
    #processors.append(do_calib_plot(limit=.1, part=EBA, mod=42, chan= 4, doEps = True)) # half C10

    #processors.append(do_calib_plot(limit=.1, part=EBA, mod=55, chan= 4, doEps = True)) # half C10
    #processors.append(do_calib_plot(limit=.1, part=EBA, mod=56, chan= 4, doEps = True)) # half C10
    processors.append(do_calib_plot(limit=.1, part=EBA, mod=56, chan=36, doEps = True))
    processors.append(do_calib_plot(limit=.1, part=EBA, mod=56, chan=37, doEps = True))
    processors.append(do_calib_plot(limit=.1, part=EBA, mod=56, chan=38, doEps = True))
    #processors.append(do_calib_plot(limit=.1, part=EBA, mod=57, chan= 4, doEps = True)) # half C10
    #processors.append(do_calib_plot(limit=.1, part=EBA, mod=58, chan= 4, doEps = True)) # half C10

    ## The masked ADCs unspecified
    processors.append(do_calib_plot(limit=.1, part=EBA, mod= 6, chan=40, doEps = True))
    processors.append(do_calib_plot(limit=.1, part=EBA, mod=16, chan= 2, doEps = True))
    processors.append(do_calib_plot(limit=.1, part=EBA, mod=18, chan=21, doEps = True))
    processors.append(do_calib_plot(limit=.1, part=EBA, mod=61, chan=16, doEps = True))
    ## The wrong HV

    ## Adc dead
    processors.append(do_calib_plot(limit=.1, part=EBA, mod=29, chan=23, doEps = True))
    processors.append(do_calib_plot(limit=.1, part=EBA, mod=43, chan= 5, doEps = True))

    ## No PMT connected
    processors.append(do_calib_plot(limit=.1, part=EBA, mod=24, chan=16, doEps = True))
    processors.append(do_calib_plot(limit=.1, part=EBA, mod=48, chan=13, doEps = True))



if region=='' or region.find('EBC')!=-1:
    processors.append(do_calib_plot(limit=.1, part=EBC, mod= 5, chan= 4, doEps = True)) #Sacha' list
    processors.append(do_calib_plot(limit=.1, part=EBC, mod=13, chan=37, doEps = True)) # Henric adds Nov 8
#processors.append(do_calib_plot(limit=.1, part=EBC, mod=18, chan=15, doEps = True)) #Sacha' list
    processors.append(do_calib_plot(limit=.1, part=EBC, mod=24, chan= 1, doEps = True)) # Henric adds
    processors.append(do_calib_plot(limit=.1, part=EBC, mod=36, chan= 6, doEps = True))              # Tomas list
    processors.append(do_calib_plot(limit=.1, part=EBC, mod=43, chan= 4, doEps = True)) #Tho's list
    processors.append(do_calib_plot(limit=.1, part=EBC, mod=46, chan=23, doEps = True))              # Tomas list
    processors.append(do_calib_plot(limit=.1, part=EBC, mod=53, chan=39, doEps = True)) #Tho's list
    processors.append(do_calib_plot(limit=.1, part=EBC, mod=53, chan=38, doEps = True)) #Tho's list
    processors.append(do_calib_plot(limit=.1, part=EBC, mod=53, chan=41, doEps = True)) #Tho's list


#    processors.append(do_calib_plot(limit=.1, part=EBC, mod=57, chan=21, doEps = True)) # Henric adds
#    processors.append(do_calib_plot(limit=.1, part=EBC, mod=57, chan=22, doEps = True)) #Tho's list
    processors.append(do_calib_plot(limit=.1, part=EBC, mod=63, chan= 7, doEps = True)) # Henric adds
    processors.append(do_calib_plot(limit=.1, part=EBC, mod=63, chan=13, doEps = True)) # Henric adds
    processors.append(do_calib_plot(limit=.1, part=EBC, mod=63, chan=15, doEps = True)) #Tho's list
    processors.append(do_calib_plot(limit=.1, part=EBC, mod=63, chan= 1, doEps = True))
#    processors.append(do_calib_plot(limit=.1, part=EBC, mod=63, chan= 3, doEps = True))
#    processors.append(do_calib_plot(limit=.1, part=EBC, mod=63, chan= 5, doEps = True))
    processors.append(do_calib_plot(limit=.1, part=EBC, mod=63, chan= 7, doEps = True))
    processors.append(do_calib_plot(limit=.1, part=EBC, mod=63, chan= 9, doEps = True))
    processors.append(do_calib_plot(limit=.1, part=EBC, mod=63, chan=11, doEps = True))
    processors.append(do_calib_plot(limit=.1, part=EBC, mod=63, chan=13, doEps = True))

    ## The masked channels unspecified
    processors.append(do_calib_plot(limit=.1, part=EBC, mod= 4, chan= 1, doEps = True))
    processors.append(do_calib_plot(limit=.1, part=EBC, mod= 5, chan= 4, doEps = True))
    processors.append(do_calib_plot(limit=.1, part=EBC, mod=35, chan= 0, doEps = True))
    #processors.append(do_calib_plot(limit=.1, part=EBC, mod=39, chan= 4, doEps = True)) # half C10
    #processors.append(do_calib_plot(limit=.1, part=EBC, mod=40, chan= 4, doEps = True)) # half C10
    #processors.append(do_calib_plot(limit=.1, part=EBC, mod=41, chan= 4, doEps = True)) # half C10
    #processors.append(do_calib_plot(limit=.1, part=EBC, mod=42, chan= 4, doEps = True)) # half C10
    processors.append(do_calib_plot(limit=.1, part=EBC, mod=54, chan= 1, doEps = True))
    #processors.append(do_calib_plot(limit=.1, part=EBC, mod=55, chan= 4, doEps = True)) # half C10
    #processors.append(do_calib_plot(limit=.1, part=EBC, mod=56, chan= 4, doEps = True)) # half C10
    #processors.append(do_calib_plot(limit=.1, part=EBC, mod=57, chan= 4, doEps = True)) # half C10
    processors.append(do_calib_plot(limit=.1, part=EBC, mod=58, chan= 3, doEps = True)) # Low Cesium
    #processors.append(do_calib_plot(limit=.1, part=EBC, mod=58, chan= 4, doEps = True)) # half C10
    processors.append(do_calib_plot(limit=.1, part=EBC, mod=61, chan= 1, doEps = True))

    ## The masked ADCs unspecified
    processors.append(do_calib_plot(limit=.1, part=EBC, mod=64, chan=31, doEps = True))
    ## The masked wrong HV

    ## Adc dead
    #






