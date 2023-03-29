########################################################
#
# Author: Peter Camporeale
# Contact: peter.thomas.camporeale@cern.ch
# Date: 2.11.2022
#
# Description: Get luminosity and MB current data for 
#              processing
# Dependencies: NA 
#
########################################################

import os 
from datetime import date, timedelta
import datetime
import shutil



# Imports

from os import listdir, mkdir, remove, system
from os.path import isfile, join
from datetime import datetime, date, timedelta
import numpy as np
import matplotlib.pyplot as plt


### USER MAY EDIT ###
# Date and time
startdate_ = "2022.07.04 00:00:00.00"
enddate_ = "2022.11.28 12:00:00.00"
#####################

startdate = datetime.strptime(startdate_, "%Y.%m.%d %H:%M:%S.%f")
enddate = datetime.strptime(enddate_, "%Y.%m.%d %H:%M:%S.%f")



# Import files (should be downloaded ito the same directory as this script)
file_pattern = "LvpsThresMonitor_ATLTILLV0"
path="./"
files = [f for f in listdir(path) if isfile(join(path, f)) and file_pattern in f]


# Read the files to determine LVPS of interest
# Get LVPS list to input to getDataSafely method
LVPS_data = []
threshold_dict = {}

print("\nReading trip data files: ...")
for f in files:
    print(f)
    # Hard code values: EBA 00, LBA 01, LBC 02, EBC 03:
    if "00" in f: module="EBA"
    elif "01" in f: module="LBA"
    elif "02" in f: module="LBC"
    elif "03" in f: module="EBC"

    # List of LVPS
    LVPS_list = []
    
    file = open(f,"r")

    for line in file:
        # Do not read the lines with just single values
        # We want the lines that contain dates and thresholds
        if len(line.split(", ")) > 1:
            time = datetime.strptime(line.split(", ")[0], "%Y.%m.%d %H:%M:%S.%f")
            LVPS = str(line.split(", ")[1][5:])
            I_reading = float(line.split(", ")[2].split("= ")[1])
            I_threshold = float(line.split(", ")[3].split("= ")[1])
        
            if time >= startdate and time <= enddate:
                LVPS_list.append(LVPS)
                # Make a blank array if first instance of the module/partition
                if module+LVPS not in threshold_dict:
                    threshold_dict[module+LVPS] = []
                # Append to the array in other cases
                threshold_dict[module+LVPS].append([time,I_threshold])

    # Keep onlyunique values 
    LVPS_list = list(set(LVPS_list))
    for LVPS in LVPS_list:
        LVPS_data.append([module,LVPS])

# Retrieve data from online
# Setup folder to feed in data
datapath = "data"
if datapath not in listdir(path):
    mkdir(datapath)
datapath = "./"+datapath+"/"

# URL to retrieve data (do not touch)
url = 'http://atlas-ddv.cern.ch:8089/multidata/getDataSafely'

# Special function to split up time period to retrieve data
def perdelta(start, end, delta):
    curr = start
    while curr < end:
        yield curr, min(curr + delta, end)
        curr += delta

print("\nRetrieving data from DDV server: ...")

filenames=[]
counter=0
new_output_file = "Luminosity.txt"
start = datetime.strptime(startdate_.split(" ")[0], "%Y.%m.%d")
end = datetime.strptime(enddate_.split(" ")[0], "%Y.%m.%d")

# Check if file already exists; otherwise, go to the else statement 
if new_output_file in listdir(datapath):
    print(new_output_file+" already exists")
    new_output_file = datapath+"Luminosity.txt"
else:
    new_output_file=datapath+new_output_file
    for s, e in perdelta(date(2022, 7, 4), date(2022, 11, 28), timedelta(days=30)):
        counter+=1
        #Format retrieval parameters (temporary filename and LVPS for single digit)
        output_file=datapath+"Luminosity_"+str(counter)+".txt"

        cmd = 'wget --post-data "queryInfo=atlas_pvssDCS, comment_, LHC Luminosity InstantaneousLuminosity ATLAS, ' + s.strftime("%d-%m-%Y") + ' 13:55, ' + e.strftime("%d-%m-%Y") + ' 13:55, , , , , ,no, , +2!" ' + url 
        system(cmd)

        #Output file formatting
        if counter==1:
            output_file="getDataSafely"
        else:
            output_file="getDataSafely."+str(int(counter-1))
        filenames.append(output_file)

    with open(new_output_file, 'w') as outfile:
        for fname in filenames:
            with open(fname) as infile:
                for line in infile:
                    outfile.write(line+", ")
            remove(fname)



# Formatting data
def dateTime(date):
    return datetime.strptime(date, "%Y.%m.%d %H:%M:%S.%f")

def integratedLuminosity(enddate,L_inst):
    L_int=0
    enddate = dateTime(enddate)
    in_time_period = None
    for i,lumi in enumerate(L_inst):

        if t_real[i]>=startdate and t_real[i+1]<= enddate:
            delta = t_real[i+1]-t_real[i]
            delta_sec = delta.total_seconds()
            L_int+=delta_sec*lumi
        else:
            in_time_period = i
            break
    delta = enddate-t_real[in_time_period]
    delta_sec = delta.total_seconds()
    L_int+=delta_sec*lumi
    # print("L_int=%f"%L_int)
    return L_int

def integratedLuminosityStep(enddate,L_inst):
    
    L_int=0
    enddate = dateTime(enddate)
    in_time_period = None
    for i,lumi in enumerate(L_inst):

        if t_real[i]>=startdate and t_real[i+1]<= enddate:
            delta = t_real[i+1]-t_real[i]
            delta_sec = delta.total_seconds()
            L_int+=delta_sec*lumi
        else:
            in_time_period = i
            break
    delta = enddate-t_real[in_time_period]
    delta_sec = delta.total_seconds()
    L_int+=delta_sec*lumi
    # print("L_int=%f"%L_int)
    return L_int

# Read in luminosity data to create a fresh list each time
L_inst=[]
t_real=[]
t_sec=[]
with open(new_output_file,"r") as fileREAD:
    for line in fileREAD:
        data=line.split(", ")
        for i,entry in enumerate(data):
            #print(i,entry)
            if "Luminosity" not in entry and ''!=entry:
                L_inst.append(float(entry.split(" ")[0]))
                date_time = entry.split(" ")[1]+" "+entry.split(" ")[2]
                time = datetime.strptime(date_time, "%d-%m-%Y %H:%M:%S:%f")
                if i==1:
                    referencetime=datetime.strptime(date_time, "%d-%m-%Y %H:%M:%S:%f")
                delta = time-referencetime
                t_sec.append(delta.total_seconds())
                t_real.append(time)
        # print(data)
print(len(t_real))
print("\nReading trip data files: ...")


# Import files (should be downloaded ito the same directory as this script)
file_pattern = "LvpsThresMonitor_ATLTILLV0"
path="./"
files = [f for f in listdir(path) if isfile(join(path, f)) and file_pattern in f]
t_trip=[]
L_trip=[]
for f in files:
    print(f)
    # Hard code values: EBA 00, LBA 01, LBC 02, EBC 03:
    if "00" in f: module="EBA"
    elif "01" in f: module="LBA"
    elif "02" in f: module="LBC"
    elif "03" in f: module="EBC"

    # List of LVPS
    file = open(f,"r")

    for line in file:
        # Do not read the lines with just single values
        # We want the lines that contain dates and thresholds
        if len(line.split(", ")) > 1:
            time = line.split(", ")[0]
            LVPS = str(line.split(", ")[1][5:])
            I_reading = float(line.split(", ")[2].split("= ")[1])
            I_threshold = float(line.split(", ")[3].split("= ")[1])
            # Just need toimes of trips
        
            if dateTime(time) >= startdate and dateTime(time) <= enddate:
                
                t_trip.append((dateTime(time)-startdate).total_seconds())
                L_trip.append(integratedLuminosity(time,L_inst))
                # print(integratedLuminosity(time,L_inst))
            #     LVPS_list.append(LVPS)
            #     # Make a blank array if first instance of the module/partition
            #     if module+LVPS not in threshold_dict:
            #         threshold_dict[module+LVPS] = []
            #     # Append to the array in other cases
            #     threshold_dict[module+LVPS].append([time,I_threshold])

    # # Keep onlyunique values 
    # LVPS_list = list(set(LVPS_list))
    # for LVPS in LVPS_list:
    #     LVPS_data.append([module,LVPS])
L_trip.sort()
t_trip.sort()
print(L_trip)
N_trip = [i for i in range(len(L_trip))]

fig, ax = plt.subplots()
plt.rcParams['figure.figsize'] = [8,6]


# Twin the x-axis twice to make independent y-axes.
axes = [ax, ax.twinx()]

axes[0].plot(t_trip,N_trip, drawstyle="steps-post",label="Accumulated Trips", linestyle='-', color="black", marker="s")
axes[0].set_ylabel("Accumulated Trips", color="black")
axes[0].tick_params(axis='y', colors="black")

#Integrated luminosoty v. time 
L_plot=[]
L_int=0
for i in range(len(t_real)-1):
    delta=t_real[i+1]-t_real[i]
    dt=delta.total_seconds()
    L_int+=dt*L_inst[i]
    L_plot.append(L_int)
axes[1].plot(t_sec[0:-1],L_plot,color="blue")
axes[1].set_ylabel("Integrated Luminosity [$\\propto$b]", color="blue")
axes[1].tick_params(axis='y', colors="blue")

# Final plot frmatting
axes[0].set_xlabel("Time from Beginning of Run 3 [s]")
d = np.zeros(len(L_plot))
axes[1].fill_between(t_sec[0:-1],L_plot, where=L_plot>=d, interpolate=True, color='blue',alpha=0.2)




plt.grid()
# plt.xlim([0,5e10])
# plt.ylim([0,50])
plt.suptitle("LVPS Trips During Run 3 (4 July - 28 November, 2022)")
plt.tight_layout()
plt.savefig("./plots/Trips_Luminosity.png")
plt.show()




