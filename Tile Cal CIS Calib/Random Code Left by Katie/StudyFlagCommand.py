import os
import numpy as np

#Katie Hughes, 2021

## CHANGE THESE AS NEEDED!
year = '2021'
end_date = '2021-08-23'

#file containing channels to be recalibrated
#format: PartitionModule    channel gain    value(optional)    date
# ex: LBA02	06	0	1.24	7/22
# or: LBA02	06	0	7/22
recalibrated_file = 'text.txt'

#name of the bash script that will be created
bashfile = 'bash.sh'

#where the plots will be placed
output_folder = 'ExampleFolder'

#If there are specific run numbers for each partition set this to True
separate_partitions = True

#The next two files are only relevant if separate_partitions is True

#file containing list of valid runs for each partition+gain combo
#format: LBA_lowgain  396441 397150 397165 397192 397291 ....
valid_file = 'valid_runs.txt'

#file containing list of run numbers and dates that you get from
#running the cis update script or studyflag
#format: run  [397291, 'CIS', '2021-07-13 15:24:33,2021-07-13 15:26:57']
run_file = 'run_numbers.txt'

#
D = {}
#F is only added to if separate_partitions is true, its keys are the list
#of runs and the value is the partition+gains for which it is valid for.
#So if multiple paritions use the same run list, it will run them together!
F = {}
if separate_partitions is True:
    with open(valid_file) as f:
        for l in f.readlines():
            lst = l.split()
            partition = lst[0]
            runs = " ".join(lst[1:])
            if runs in F:
                F[runs].append(partition)
            else:
                F[runs] = []
                F[runs].append(partition)
    runs = []
    dates = []
    with open(run_file) as f:
        for l in f.readlines():
            l = l.strip('run ')
            lst = l.split(', ')
            run = lst[0].strip('[')
            date = (lst[2].split())[0].strip('\'')
            runs.append(int(run))
            dates.append(date)
    datenums = [int(i.replace('-','')) for i in dates]

with open(recalibrated_file) as f:
    lines = f.readlines()
    for l in lines:
        #print('')
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
        #print(date)
        #print(datenum)
        ID = partition+'_m'+module+'_c'+channel+gain
        #print(ID)
        if separate_partitions is False:
            if date in D:
                D[date].append(ID)
            else:
                D[date] = []
                D[date].append(ID)
        else:
            # I want to group by ones that have the same list of runs and date
            for i in F.items():
                if partition+gain in i[1]:
                    #print("in", i[0],i[1])
                    #appropriate index
                    mask = np.array(datenums)>datenum
                    first_run = (np.array(runs)[mask])[0]
                    #print("first valid run:", first_run)
                    arr = np.array([int(x) for x in i[0].split()])
                    run_range = list(arr[arr>=first_run])
                    #print(run_range)
                    # find the run after
                    ldate = ' '.join([str(x) for x in run_range])
                    #print("ldate:", ldate)
                    #print(date_run)
                    if ldate in D:
                        D[ldate].append(ID)
                    else:
                        D[ldate] = []
                        D[ldate].append(ID)

f = open(bashfile, "w")
f.write('#!/usr/bin/env bash\n')

print()
for key in D:
    l1 = 'macros/cis/StudyFlag.py '
    lf = '--output '+output_folder+' --qflag \'all\' --timestab --printopt \'Print_All\''
    if separate_partitions is False:
        date = key
        print("DATE:", date, end='\n\n')
        print(l1, end='')
        f.write(l1)
        l2 = '--date \''+date+'\' \''+end_date+'\' '
        print(l2, end='')
        f.write(l2)
        l3 = '--region '
        print(l3, end='')
        f.write(l3)
        IDs = D[key]
        for i in IDs:
            li = '\''+i+'\' '
            print(li, end='')
            f.write(li)
        print(lf)
        f.write(lf)
        print('\n')
        f.write('\n')
    else:
        print(l1, end='')
        f.write(l1)
        l2 = '--date \'28 days\' '
        print(l2, end='')
        f.write(l2)
        l3 = '--region '
        print(l3, end='')
        f.write(l3)
        IDs = D[key]
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



os.chmod(bashfile, 0o777)
#macros/cis/StudyFlag.py --date '2021-08-06' '2021-08-23' --region 'EBC_m38_c05_highgain'  --output ExampleFolder --qflag 'all' --timestab --printopt 'Print_All'
