#!/usr/bin/env python
# Author: Jacky
#
# Developing

import os
os.chdir(os.getenv('TUCS','.'))
exec(open('src/load.py').read(), globals()) # don't remove this!

import numpy as np
import argparse
from datetime import date
#######

# This is calling ReadCalibFromCool.py from (), not the file in the worker!
os.system("ReadCalibFromCool.py --schema=\"sqlite://;schema=./results/tileSqlite.db;dbname=CONDBR2\" --folder=/TILE/OFL02/CALIB/CIS/LIN --tag=UPD1 > ./results/CIS_before_Recalib.txt")

today = date.today()
year = today.strftime('%Y')

folder_path = "./results/original_data/"

if (os.path.exists(folder_path)):
    os.system("rm -r "+ folder_path)

os.mkdir(folder_path)
os.rename("./results/tileSqlite.db", folder_path + "tileSqlite.db")
os.rename("./results/CIS_before_Recalib.txt", folder_path + "CIS_before_Recalib.txt")
os.rename("./results/CIS_DB_update.txt", folder_path + "CIS_DB_update.txt")
os.rename("./results/toRecalibrate.txt", folder_path + "toRecalibrate.txt")

#######

parser = argparse.ArgumentParser(description='Generate files for CIS constant recalibration')

parser.add_argument('--recal_file', default= folder_path + "toRecalibrate.txt", help=
'Txt file of channels to be recalibrated. Required! \n \
Format: PartitionModule    channel gain    value(optional)    date \n \
EX: LBA02	06	0	1.24	7/22 \n \
OR: LBA02	06	0	7/22 \n ')

parser.add_argument('--end_date', default=today.strftime('%Y-%m-%d'), help=
'End date for the plots to be generated. \n \
 Format: YYYY-MM-DD. Default is today\'s date. \n')

parser.add_argument('--output', help='Output folder for plots. Default=ExampleFolder', default='ExampleFolder')

parser.add_argument('--cistxt', help='MonthCIS.txt file (output of update command), \
	slightly more accurate than not including it. required \
	if separate_partitions is used.', default=None)

parser.add_argument('--cisupdate', action='store_true', help=
'Generate new constants using the CIS update command instead of StudyFlag.')

parser.add_argument('--result', help='if --cisupdate is used, \
	name of the txt file containing the new constants. \
	Default=toRecalibrate.txt (which will be in the results file)', default='toRecalibrate.txt')

parser.add_argument('--separate_partitions', action='store_true', help=
'Use if there are different valid runs for different partitions+gains.')

parser.add_argument('--valid_file', help=
'List of valid runs for each partition + gain. \n \
Only needed if separate_partitions is True. \
Format: LBA_lowgain  396441 397150 397165 397192 397291 ....')

parser.add_argument('--bashfile', help='Bash File to be created', default='./results/RecalCommands.sh')

parser.add_argument('--already_in_update', default='./results/in_update.txt', help='File to be created of channels in the update. Default=corr1.txt')

parser.add_argument('--add_to_update', default='./results/add_to_update.txt', help='File to be created of channels NOT in the update. Default=corr2.txt')

parser.add_argument('--ini_DB_update', default= folder_path + 'CIS_DB_update.txt', help='File listing which channels are in the update')



args = parser.parse_args()

if not os.path.exists(args.recal_file):
	print('Need to specify recalibration file!')
	exit()


def read_cistxt(fname):
	runs = []
	dates = []
	inBlock = False
	with open(args.cistxt) as f:
		for l in f.readlines():
			lst = l.split()
			if len(lst) > 1:
				if lst[0] == "Running" and lst[1] == "ReadCIS":
					# run list ends at: "Running ReadCIS - Read in CIS calibration factors and quality flags from CIS calibration ntuples"
					break
			if inBlock:
				try:
					run = lst[1]
					run = run.strip('[')
					run = run.strip(',')
					date = (lst[3]).strip('\'')
					runs.append(run)
					dates.append(date)
					print("Run: %s \t Date: %s"%(run, date))
				except:
					print("NOPE")
					pass
			if len(lst) > 1:
				if lst[0] == "Use:":
					# run list starts at: "Use: Using all the detector"
					inBlock = True
	return runs, dates



#
D = {}
#F is only added to if separate_partitions is true, its keys are the list
#of runs and the value is the partition+gains for which it is valid for.
#So if multiple paritions use the same run list, it will run them together!
F = {}
if args.separate_partitions is True:
	if args.valid_file is not None:
		with open(args.valid_file) as f:
			for l in f.readlines():
				lst = l.split()
				partition = lst[0]
				runs = " ".join(lst[1:])
				if runs in F:
					F[runs].append(partition)
				else:
					F[runs] = []
					F[runs].append(partition)
	else:
		print("You must include valid_file if you are separating partitions!")
		exit()
	runs, dates = read_cistxt(args.cistxt)
	datenums = [int(i.replace('-','')) for i in dates]


if args.cistxt is not None:
	runs, dates = read_cistxt(args.cistxt)
	datenums = [int(i.replace('-','')) for i in dates]


def convertName(name):
	spl = name.split('_')
	#EBC_m03_c02_lowgain
	partition = spl[0]
	module = int(spl[1].strip('m'))
	channel = int(spl[2].strip('c'))
	if module < 10:
		module = '0'+str(module)
	else:
		module = str(module)
	if channel < 10:
		channel = ' '+str(channel)
	else:
		channel = str(channel)
	gain = spl[3]
	if gain == 'lowgain':
		gain = 0
	elif gain == 'highgain':
		gain = 1
	else:
		gain = -1
	return partition+module+' '+channel+' '+str(gain)




listdate = False
with open(args.recal_file) as f:
	lines = f.readlines()
	for l in lines:
		lst = l.split()
		partition = lst[0][:3]
		module = lst[0][3:]
		channel = lst[1]
		if len(channel) == 1:
			channel = '0'+channel
		gain = lst[2]
		if gain == '0':
			gain = '_lowgain'
		else:
			gain = '_highgain'
		if len(lst) == 5:
			date = lst[4]
		else:
			date = lst[3]
		dateID = date.split('/')
		month = dateID[0]
		day = dateID[1]
		if len(month)==1:
			month = '0'+month
		if len(day)==1:
			day = '0'+day
		date = year+'-'+month+'-'+day
		datenum = int(year+month+day)
		ID = partition+'_m'+module+'_c'+channel+gain
		print("Channel ID: %s \t Recal Date: %s"%(ID, date))
		if args.cistxt is not None:
			listdate = True
			mask = np.array(datenums)>datenum
			first_run = (np.array(runs)[mask])[0]
			runs_to_use = runs[runs.index(first_run):]
			ldate = ' '.join([str(x) for x in runs_to_use])
			if ldate in D:
				D[ldate].append(ID)
			else:
				D[ldate] = []
				D[ldate].append(ID)
		elif args.separate_partitions is False:
			if date in D:
				D[date].append(ID)
			else:
				D[date] = []
				D[date].append(ID)
		else:
			# I want to group by ones that have the same list of runs and date
			listdate = True
			for i in F.items():
				if partition+gain in i[1]:
					mask = np.array(datenums)>datenum
					first_run = (np.array(runs)[mask])[0]
					arr = np.array([int(x) for x in i[0].split()])
					run_range = list(arr[arr>=first_run])
					ldate = ' '.join([str(x) for x in run_range])
					if ldate in D:
						D[ldate].append(ID)
					else:
						D[ldate] = []
						D[ldate].append(ID)

f = open(args.bashfile, "w")
f.write('#!/usr/bin/env bash\n')

print()
for key in D:
	if args.cisupdate:
		l1  = 'macros/cis/CIS_DB_Update.py '
		lf = ''
	else:
		l1 = 'macros/cis/StudyFlag.py '
		lf = '--output '+args.output+' --qflag \'all\' --timestab --printopt \'Print_All\''
	IDs = D[key]
	if listdate is False:
		date = key
		print("DATE:", date, end='\n\n')
		print(l1, end='')
		f.write(l1)
		l2 = '--date \''+date+'\' \''+args.end_date+'\' '
		print(l2, end='')
		f.write(l2)
		l3 = '--region '
		print(l3, end='')
		f.write(l3)
		for i in IDs:
			li = '\''+i+'\' '
			print(li, end='')
			f.write(li)
		print(lf)
		f.write(lf)
		print('\n')
		f.write('\n')
	else:
		print("Starting from RUN # %s \n\n" % key[:6])
		print(l1, end='')
		f.write(l1)
		l2 = '--date \'28 days\' '
		print(l2, end='')
		f.write(l2)
		l3 = '--region '
		print(l3, end='')
		f.write(l3)
		for i in IDs:
			li = '\''+i+'\' '
			print(li, end='')
			f.write(li)
		lr = '--ldate '+key+' '
		print(lr, end='')
		f.write(lr)
		print(lf)
		f.write(lf)
		print('\n')
		f.write('\n')
	if args.cisupdate:
		f.write('cd results\n')
		f.write('ReadCalibFromCool.py --schema="sqlite://;schema=tileSqlite.db;dbname=CONDBR2" --folder=/TILE/OFL02/CALIB/CIS/LIN --tag=UPD1 | grep -v miss > Recal.txt\n')
		for i in IDs:
			f.write('grep \''+convertName(i)+'\' Recal.txt >> '+args.result+'\n')
		f.write('rm tileSqlite.db CIS_DB_update.txt Recal.txt\n')
		f.write('cd ..\n')

f.close()
# Making the bashfile able to be run
os.chmod(args.bashfile, 0o755)

print("about to run recal commands")
os.system("bash results/RecalCommands.sh")
print("finished running recal commands")


##########################################################################################################


# creating a list of the updated channels
updated_channels = []
with open(args.ini_DB_update, 'r') as f:
	for l in f.readlines():
		if ("run" in l):
			runNum = l.split()[1]
		if ("TILECAL" in l):
			x = l.split()
			ID = (x[0])[8:]
			updated_channels.append(ID)

print()


def fix_length(str):
	if len(str) == 1:
		return '0'+str
	else:
		return str

corr1 = open(args.already_in_update, 'w')
corr2 = open(args.add_to_update, 'w')
in_update = 0
not_in_update = 0
with open("./results/"+args.result, 'r') as f:
	lines = f.readlines()
	# check if line matches the ID from the update list
	for l in lines:
		x = l.split()
		partition = fix_length(x[0][:3])
		module = fix_length(x[0][3:])
		channel = fix_length(x[1])
		ch_ID = partition+'_m'+module+'_c'+channel
		if x[2] == '1':
			ch_ID += "_highgain"
		else:
			ch_ID += "_lowgain"
		print('%s:' % ch_ID, end=' ')
		if ch_ID in updated_channels:
			print('in the update')
			in_update += 1
			corr1.write(l)
		else:
			print('NOT in the update')
			not_in_update += 1
			corr2.write(l)

corr1.close()
corr2.close()
print()

print(in_update, "recalibrated channels are in the update")
print(not_in_update, "recalibrated channels are NOT in the update")
print("\nTxt files", args.already_in_update, "and", args.add_to_update, "successfully written to!\n")

############################################################

os.system("cp ./results/original_data/tileSqlite.db ./results/tileSqlite.db")
#UDB short for Update Data Base

UDB_for_already_in = "WriteCalibToCool.py --schema=\"sqlite://;schema=./results/tileSqlite.db;dbname=CONDBR2\" --txtfile=./results/in_update.txt --folder=/TILE/OFL02/CALIB/CIS/LIN --tag=UPD1 --run="+runNum
UDB_for_not_in = "WriteCalibToCool.py --inschema=COOLOFL_TILE/CONDBR2 --outschema=\"sqlite://;schema=./results/tileSqlite.db;dbname=CONDBR2\" --update --txtfile=./results/add_to_update.txt --folder=/TILE/OFL02/CALIB/CIS/LIN --tag=UPD1 --run="+runNum
os.system(UDB_for_already_in)
os.system(UDB_for_not_in)

os.system("ReadCalibFromCool.py --schema=\"sqlite://;schema=./results/tileSqlite.db;dbname=CONDBR2\" --folder=/TILE/OFL02/CALIB/CIS/LIN --tag=UPD1 > ./results/CIS_after_Recalib.txt")

os.system("diff ./results/CIS_after_Recalib.txt ./results/original_data/CIS_before_Recalib.txt > ./results/Difference_in_DB.txt")
#############################################################

#os.system("~solodkov/scripts/calib_to_oracle CALIB/CIS/LIN ./results/tileSqlite.db")


#Go([ 
    #readcalfromcool,
#    ])


