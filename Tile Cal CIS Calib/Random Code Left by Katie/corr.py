import argparse
import os

#Katie Hughes, October 2021

parser = argparse.ArgumentParser('Generate files to be used in updating sqlite values, based on whether they are in the update.')

parser.add_argument('--directory', '-d', help='Directory where files are')

parser.add_argument('--recalibrated_name', default='toRecalibrate.txt', help=
'File containing channels to be recalibrated. \n \
Default = toRecalibrate.txt. \n \
Needs to follow this format: \n \
PartitionModule Channel Gain Value \n \
Ex: LBA02	06	1	75.97 \n \ ')

parser.add_argument('--update', default='corr1.txt', help='File to be created of channels in the update. Default=corr1.txt')

parser.add_argument('--not_update', default='corr2.txt', help='File to be created of channels NOT in the update. Default=corr2.txt')

parser.add_argument('--cis', default='cis.txt', help=
'File listing which channels are in the update. Get it by running: \n \
ReadCalibFromCool.py --schema=\"sqlite://;schema=tileSqlite.db;dbname=CONDBR2\" --folder=/TILE/OFL02/CALIB/CIS/LIN --tag=UPD1 | grep -v miss > cis.txt \n \
Default=cis.txt')

args = parser.parse_args()

if args.directory is not None: 
    try:
        os.chdir(args.directory)
    except: 
        print("Couldn't change to directory %s"%(args.directory))


# creating a list of the updated channels
updated_channels = []
with open(args.cis, 'r') as f:
	lines = f.readlines()
	for l in lines: 
		x = l.split()
		if len(x) == 4: 
			# Exclude the calibration from the old update and only leave the ID
			updated_channels.append(x[:3])

corr1 = open(args.update, 'w')
corr2 = open(args.not_update, 'w') 

in_update = 0
not_in_update = 0
with open(args.recalibrated_name, 'r') as f:
	lines = f.readlines()
	# check if line matches the ID from the update list
	for l in lines:
		x = l.split()
		if x[:3] in updated_channels:
			in_update += 1
			corr1.write(l)
		else: 
			not_in_update += 1
			corr2.write(l)

print(in_update, "recalibrated channels are in the update")
print(not_in_update, "recalibrated channels are NOT in the update")
print("\nTxt files", args.update, "and", args.not_update, "successfully written to!\n")
