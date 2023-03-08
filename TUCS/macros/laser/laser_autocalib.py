#!/usr/bin/env python
#
# Input :     One run number and option for plots from getLaserFlags worker: 
# Example:    python macros/laser/laser_autocalib_combined.py --first=269755 --doPlots will create the plots 
# Example:    python macros/laser/laser_autocalib_combined.py --first=269755 --IgnoreStatus will not use channels status for creating list
#                                                                     without any specification of the --doPlots option the plots will not be created
#
# This script provides for a given laser run a number of categories for the channels to decide whether they need and they can be calibrated

import os,sys
os.chdir(os.getenv('TUCS','.'))
exec(open('src/load.py').read(), globals()) # don't remove this!
exec(open('src/laser/laserGetOpt.py').read(), globals()) 

if not os.path.exists('results/output/'):
    os.makedirs('results/output/') 

# Laser Argument class
localArgParser=laserArgs(verbose=True)

# Add local arguments (specific to this macro)
localArgParser.add_local_arg('--first',             action='store',       default=270000, required=True, arghelp='Run of start of IOV \n')
localArgParser.add_local_arg('--IgnoreStatus',      action='store_false', default=True,  arghelp='For testing status of channels when sorting channels list \n')
localArgParser.add_local_arg('--doPlots',           action='store_true',  default=False, arghelp='For doing additional plots \n')
localArgParser.add_local_arg('--average',           action='store_true',  default=False, arghelp='Average laser constant in IOV \n')
localArgParser.add_local_arg('--append',            action='store_true',  default=False, arghelp='Append current constants to existing sqlite file \n')
localArgParser.add_local_arg('--correctHV',         action='store_true',  default=False, arghelp='Correct drifts for HV change \n')
localArgParser.add_local_arg('--ignoreWriteLaserSqlite', action='store_true',  default=False,  arghelp='For not writing the new laser constants in a new tileSqlite file \n')
localArgParser.add_local_arg('--ReadlocalTilesqlite', action='store_true',  default=False,  arghelp='Read the reference value from a local tileSqlite \n')

# Get arguments from parser 
localArgs=localArgParser.args_from_parser()
Doplots=localArgs.doPlots
run_f=int(localArgs.first)
Status=localArgs.IgnoreStatus
average=localArgs.average
append=localArgs.append
correctHV=localArgs.correctHV
ignoreWriteLaserSqlite=localArgs.ignoreWriteLaserSqlite
ReadlocalTilesqlite=localArgs.ReadlocalTilesqlite

print("Arguments --date {} --first {} --IgnoreStatus {} --doPlots {} --average {} --append {} --correctHV {} --outputTag {} --ignoreWriteLaserSqlite --ReadlocalTilesqlite".format(date,run_f,Status,Doplots,average,append,correctHV,outputTag,ignoreWriteLaserSqlite,ReadlocalTilesqlite))

# Get date of input run
command = "mysql -h pcata007.cern.ch -u reader -NB -e \"select date from tile.comminfo where run='"
command = command + str(run_f)
command = command + "' and comments IS NULL and lasreqamp='15000' and lasfilter='8' and events>'9000' and events<'231000' ORDER BY date DESC LIMIT 0, 1\" " # | sed ':start /^.*$/N; t start' | tr '\n' '\t'`"

r = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, shell=True)
lines = r.stdout.readlines()                                                                                                               
enddate = lines[0].split(b' ')[0].decode("utf-8")
if date == None: 
    date = enddate


processors = []

# Definition of all the runs that will be used
if average:
    processors.append( Use(run=date, run2=enddate, runType='Las', TWOInput= True, filter=8, amp='15000') )  # 2018 reference is 2018-03-01 (Cs scan 2018-02-17)
else:
    processors.append( Use(run=[run_f],runType='Las',TWOInput= True, amp='15000') )

# Read Information from the laser
processors.append( ReadLaser(diode_num_lg=12, diode_num_hg=13, doPisa=True ) )
processors.append( CleanLaser() )

# Read bad channels from COOL database
processors.append( ReadBchFromCool( schema='COOLOFL_TILE/CONDBR2',
                                    folder='/TILE/OFL02/STATUS/ADC',
                                    tag='UPD4', 
                                    Fast=True,
                                    storeADCinfo=True ) )


# Read the reference values from the Conditions DB
## Default schema and tag
if ReadlocalTilesqlite:
    schema='sqlite://;schema=data/laser/tileSqlite_files/tileSqlite_LasRef_2018_singleIOV.db;dbname=CONDBR2' #example on how to read the reference value from the DB
    tag='TileOfl02CalibCes-RUN2-UPD4-20'
else:
    schema='COOLOFL_TILE/CONDBR2' #by default the reference values are taken from the DB
    tag='TileOfl02CalibCes-RUN2-UPD4-24'

d = ReadCalFromCool(schema=schema,folder='/TILE/OFL02/CALIB/CES',runType = 'Las_REF',tag=tag,verbose=True)
processors.append(d)

# Different workers that store the infos for the HV to be compared with the laser
#processors.append( Listmaker(fin_Date,fin_Date,'-m') )
#processors.append( dataMerger(fin_Date,fin_Date,'-m') )
#processors.append( HV_value())


# Workers that perform the laser data analysis
if doDirect:
    # Global correction
    processors.append( getGlobalShiftsDirect(siglim=2.0, n_iter=3, verbose=True) )
    # Fibre correction
    processors.append( getFiberShiftsDirect(siglim=1.5, n_iter=3, verbose=True) )
    # And finally the corrected PMT shifts, (stored in event.data['deviation'])
    processors.append( getPMTShiftsDirect(usePisa=False) )
    processors.append( compute_EBScale() )
    processors.append( scaleEB() ) 
else:
    # Global correction
    processors.append( getGlobalShiftsCombined(siglim=2.0, n_iter=3, verbose=True) )
    # Fill PMTs beta value here in case you want to correct for HV change 
    processors.append( FillBetaHVNom() )    
    # Fibre correction
    processors.append( getFiberShiftsCombined(siglim=2.0, n_iter=3, verbose=False) )
    # And finally the corrected PMT shifts, (stored in event.data['deviation'])
    processors.append( getPMTShiftsDirect(usePisa=False, correctHV=correctHV) )

if average:
    processors.append( DoAverageValues(key='deviation', verbose=False, removeOutliers=False) )
    processors.append( DoAverageValues(key='f_laser', verbose=False, removeOutliers=False) )
    processors.append( DoAverageValues(key='HV', verbose=False, removeOutliers=False))


fileTag = outputTag
if str(run_f) not in outputTag:
    fileTag = str(run_f)+"_"+outputTag
    
if not ignoreWriteLaserSqlite:
    # Write output sqlite file with laser constants
    if not os.path.isfile("results/tileSqlite.db"):
        input_schema  = None
    else:
        input_schema  = 'sqlite://;schema=results/tileSqlite.db;dbname=CONDBR2'

    if append:
        output_schema = 'sqlite://;schema=results/tileSqlite-allIOVs.db;dbname=CONDBR2'
    else:
        output_schema = 'sqlite://;schema=results/tileSqlite-{}.db;dbname=CONDBR2'.format(fileTag)
    processors.append( WriteDBNew(input_schema=input_schema,
                                  output_schema = output_schema,
                                  folder = '/TILE/OFL02/CALIB/LAS/LIN',
                                  tag = 'TileOfl02CalibLasLin-RUN2-HLT-UPD1-00',
                                  iov = (run_f, 0),
                                  runNumber=run_f,
                                  writeHV=True,##for HG
                                  useHighGain=True,
                                  average_const=average))##for HG #default is 'RUN2-HLT-UPD1-00', 'RUN2-UPD4-02'

# Make txt file with average cell constant variation
splitSides = True
processors.append(compute_mean_cell_var_combined(gain=1,runNumber=run_f,ComputeEBScale=False,verbose=False,average=average))
if splitSides:
    processors.append(compute_mean_cell_var_combined(gain=1,runNumber=run_f,ComputeEBScale=False,verbose=False,average=average,side='A'))
    processors.append(compute_mean_cell_var_combined(gain=1,runNumber=run_f,ComputeEBScale=False,verbose=False,average=average,side='C'))

if Doplots:
    # Plot global correction
    processors.append( do_global_plot(doEps = plotEps) )
    # Plot fibre correction
    processors.append( do_fiber_plot(doEps = plotEps) )

    processors.append( do_module_channel_plot(key="f_laser") )
    
#Launch processors
Go(processors)
if append:
    exit()

# Make Tile Map with average cell constant variation (run_f - run_ref) 
print("Producing TileCal map for run ",run_f," in ",getResultDirectory())

command = ""
if average:
    # Initial and end date on the tile laser map
    command = "echo \" {} to {}.\" >> {}/data_cells_var_hg.txt".format(date,enddate,getResultDirectory())
else:
    # Run number and date on the tile laser map
    command = "echo \"run {}, {}.\" >> {}/data_cells_var_hg.txt".format(fileTag,enddate,getResultDirectory())

p = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, shell=True)
outputlines = p.stdout.readlines()
p.wait()

command = "./scripts/make_tile_figure.sh {} data_cells_var_hg.txt".format(getResultDirectory())
p = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, shell=True)
outputlines = p.stdout.readlines()
p.wait()
print(outputlines)
subprocess.Popen("convert {}/tile_laser_map.eps results/tile_laser_map{}.pdf".format(getResultDirectory(),fileTag), stdout=subprocess.PIPE, stderr=subprocess.STDOUT, shell=True).wait()
subprocess.Popen("mv {}/tile_laser_map.eps results/tile_laser_map{}.eps".format(getResultDirectory(),fileTag), stdout=subprocess.PIPE, stderr=subprocess.STDOUT, shell=True).wait()


if splitSides:
    for side in ['A','C']:

        if average:
            command = "echo \" {} to {}.\" >> {}/data_cells_var_hg{}side.txt".format(date,enddate,getResultDirectory(),side)
        else:
            command = "echo \"run {}, {}.\" >> {}/data_cells_var_hg{}side.txt".format(run_f,enddate,getResultDirectory(),side)
        p = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, shell=True)
        outputlines = p.stdout.readlines()
        p.wait()

        command = "./scripts/make_tile_figure.sh {} data_cells_var_hg{}side.txt".format(getResultDirectory(),side)
        p = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, shell=True)
        outputlines = p.stdout.readlines()
        p.wait()
        subprocess.Popen("convert {}/tile_laser_map_{}side.eps results/tile_laser_map{}_{}side.pdf".format(getResultDirectory(),side,fileTag,side), stdout=subprocess.PIPE, stderr=subprocess.STDOUT, shell=True).wait()
        subprocess.Popen("mv {}/tile_laser_map_{}side.eps results/tile_laser_map{}_{}side.eps".format(getResultDirectory(),side,fileTag,side), stdout=subprocess.PIPE, stderr=subprocess.STDOUT, shell=True).wait()
