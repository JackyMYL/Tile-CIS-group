exec(open('src/load.py').read(), globals()) # don't remove this!
import getopt,sys
exec(open('src/laser/laserGetOpt.py').read(), globals()) 

# Laser Argument class
localArgParser=laserArgs(verbose=True)

RUNNUM = 314244 #05/12/2016
#RUNNUM = 300521 #30/05/2016
RUNNUM = 300371 #28/05/2016

RUNNUM = 314244
RUNNUM = 314478

RUNNUM = 311556 #27/10/2016

# Add local arguments that are specific to this macro
localArgParser.add_local_arg('--RUNNUM', action='store',  default=RUNNUM, arghelp='Run number \n')
# Get arguments from parser 
localArgs=localArgParser.args_from_parser()
RUNNUM=localArgs.RUNNUM

runs = [RUNNUM]

#runs = [280440]

a = Use(runs,runType='Las',filter='6')
b = ReadLaser(diode_num_lg=12, diode_num_hg=13)
c = CleanLaser()
p = Print(verbose=True)
#schema='sqlite://;schema=tileSqlite.db;dbname=CONDBR2'
schema='COOLOFL_TILE/CONDBR2'
#d = ReadCalibFromCool(runType = 'Las_REF', folder='/TILE/OFL02/CALIB/CES',  tag = 'RUN2-HLT-UPD1-01', schema = schema)
d = ReadCalFromCool(runType = 'Las_REF', folder='/TILE/OFL02/CALIB/CES',  tag = 'RUN2-HLT-UPD1-01', schema = schema)

#a  = Use(runs,getLast=True,runType='Las',filter='6') # Low gain
#b  = Use(runs,getLast=True,runType='Las',filter='8') # High gain
#ab = Use(runs,runType='Las') # If you gave the run number yourself
#c = ReadLaser(diode_num=0)
#e = ReadBchFromCool( schema='COOLONL_TILE/COMP200',
#                                    folder='/TILE/OFL01/STATUS/ADC',
#                                    tag='HLT-UPD1-00',
#                                    Fast=True,
#                                    storeADCinfo=True )
#d = ReadCalFromCool(runType = 'Las_REF', folder='/TILE/OFL02/CALIB/CES', tag = 'HLT-UPD1-01')




# Compute the fiber partitions variations, (stored in event.data['fiber_var'])

f = getFiberShifts(verbose=True)

# And finally the globally corrected PMT shifts 

g = getPMTShiftsObsolete()
#g1 = getGlobalShiftsDirect(siglim=3.,n_iter=2,verbose=True)
###else:
#g2 = getFiberShiftsDirect(siglim=2.,verbose=True)

#g = getPMTShiftsDirect()

# computing mean cell variation

EBScale=0
j = compute_mean_cell_var(gain=0)
m = compute_mean_cell_var_phi(gain=0)

k = scaleEB()

# Use a predefined list of runs
##processors = [a,b,c,d,g1,g2,g,j]

## processors = [a,b,c,d,f,g,j,k,j]
processors = [a,b,c,d,f,g,j,k,m,j]

Go(processors)


# rename outputs and image creation

db = _mysql.connect(host='pcata007.cern.ch', user='reader')
query = """select date from tile.comminfo where run=%s  LIMIT 0, 1""" % (RUNNUM)


db.query(query)
print " SQL query is ",query

res = db.store_result()

pouet = []
pouet = res.fetch_row(maxrows=0)

date = pouet[0][0]

import subprocess

command = "cp results/data_cells_var_lg.txt cells/data_cells_var_lg_%s.txt" % (RUNNUM)
p = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, shell=True)
outputlines = p.stdout.readlines()
p.wait()

command = "echo \"run %s %s\" >> results/data_cells_var_lg.txt" % (RUNNUM,date)
#print command
p = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, shell=True)
outputlines = p.stdout.readlines()
p.wait()

command = "cp results/data_cells_var_lg.txt gains.txt"
p = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, shell=True)
outputlines = p.stdout.readlines()
p.wait()
command = "./scripts/make_tile_figure.sh"
p = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, shell=True)
outputlines = p.stdout.readlines()
p.wait()
print outputlines
command = "mv test.eps cells/cells_var_lg_%s.eps" % (RUNNUM)
p = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, shell=True)
outputlines = p.stdout.readlines()
p.wait()
command = "cp test.png cells/cells_var_lg_%s.png" % (RUNNUM)
p = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, shell=True)
outputlines = p.stdout.readlines()
p.wait()
command = "mv test.png plots/latest/cells_var_lg_%s.png" % (RUNNUM)
p = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, shell=True)
outputlines = p.stdout.readlines()
p.wait()

