import numpy as np
import argparse

parser = argparse.ArgumentParser(description='Return High Deviation Channels')
parser.add_argument('--file', '-f', default='./results/CIS_DB_update.txt', help=
'CIS Update .txt file ')

args = parser.parse_args()

count = 0

threshold = 0.05

with open(args.file) as f:
	for l in f.readlines():
		if 'TILECAL' in l:
			spl = l.split()
			module = spl[0]
			old = float(spl[1])
			new = float(spl[2])
			percent = float(spl[3])
			if np.abs(percent) > threshold:
				print('%s \t %.2f \t %.2f \t %.2f%% '%((module.strip('TILECAL')).strip('_'), old, new, percent*100))
				count += 1

print(f'{count} channels greater than {threshold*100}% change')
