########################################################
#
# Author: Peter Camporeale
# Contact: peter.thomas.camporeale@cern.ch
# Date: 29.03.2023
#
# Description: Getluminosity data and show LVPS trips
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
import csv
import matplotlib.dates as mdates


### USER MAY EDIT ###
# Date and time
startdate_ = "2022.07.04 00:00:00.00"
enddate_ = "2022.11.28 12:00:00.00"
#####################

startdate = datetime.strptime(startdate_, "%Y.%m.%d %H:%M:%S.%f")
enddate = datetime.strptime(enddate_, "%Y.%m.%d %H:%M:%S.%f")



# Import files (should be downloaded ito the same directory as this script)
file_pattern_start = "CH"
file_pattern_end = "A"
path="./data/"
files = [path+f for f in listdir(path) if isfile(join(path, f)) and file_pattern_start in f]

#Make plot directory
plotpath = "plots"
if plotpath not in listdir("."):
    mkdir(plotpath)
plotpath = "./"+plotpath+"/"


# Datetime formatting

# Formatting data
def dateTime(date):
    return datetime.strptime(date, "%Y/%m/%d %H:%M")

# Global plot parameters

fig, ax = plt.subplots(figsize=(8,6))
colors = ["black","red", "orange","yellow","green","blue","purple","pink"]
ymax=0
ymin=100

# Plot continuously all channels
channel_patterns=[]
for f in files:
    channel_patterns.append(int(f.split("CH")[1][0]))
channel_patterns = list(set(channel_patterns))




for channel in channel_patterns:

    # Data
    time = [] #YYYY/MM/DD HH:MM
    temperature = [] # C
    humidity = [] # %
    dewpoint = [] # C
    heatindex = [] # C

    # Read files corresponding to same channel
    # Store all data from the same channel and plot before resetting
    for f in files:
        if file_pattern_start+str(channel) in f:
        

        
            with open(f, newline='') as csvfile:
                data = csv.reader(csvfile, delimiter=' ')
                for row in data:
                    if len(row)>1 and "-" not in row:
                        # Extract data
                        time_ = row[0]+" "+row[1].split(",")[0]
                        temperature_ = row[1].split(",")[1]

                        humidity_ = row[1].split(",")[2]
                        dewpoint_ = row[1].split(",")[3]
                        heatindex_ = row[1].split(",")[4]
                        
                        # Datetime format the time
                        time_ = dateTime(time_)

                        # Add to lists
                        if "-" not in temperature_ and "-" not in humidity_ and "-" not in dewpoint_ and "-" not in heatindex_:
                            time.append(time_)
                            temperature.append(float(temperature_))
                            humidity.append(float(humidity_))
                            dewpoint.append(float(dewpoint_))
                            heatindex.append(float(heatindex_))
            # Set min/max y axis
            if min(temperature) < ymin:
                ymin = np.floor(min(temperature))
            if max(temperature) > ymax:
                ymax = np.ceil(max(temperature))
    
    # Plot for each channel
    if channel==1:
        alpha=1
    else:
        alpha=0.3
    ax.plot(time, temperature,"-",drawstyle="steps-post", color=colors[int(channel)-1],label="Channel "+str(channel), alpha=alpha)
ax.xaxis.set_major_locator(mdates.MonthLocator())
ax.xaxis.set_minor_locator(mdates.DayLocator())
plt.xlabel("Date [YYYY-MM]")
#plt.ylabel("Temperature [$^{\\circ}C$]")
plt.suptitle("B175 Temperature")
plt.legend(loc="upper left")
plt.yticks(np.arange(ymin, ymax+1, 1.0))
plt.savefig("./plots/Temperature.png")
plt.close()

# Humidity plot

fig, ax = plt.subplots(figsize=(8,6))
colors = ["black","red", "orange","yellow","green","blue","purple","pink"]
ymax=0
ymin=100

for channel in channel_patterns:

    # Data
    time = [] #YYYY/MM/DD HH:MM
    temperature = [] # C
    humidity = [] # %
    dewpoint = [] # C
    heatindex = [] # C

    # Read files corresponding to same channel
    # Store all data from the same channel and plot before resetting
    for f in files:
        if file_pattern_start+str(channel) in f:
        

        
            with open(f, newline='') as csvfile:
                data = csv.reader(csvfile, delimiter=' ')
                for row in data:
                    if len(row)>1 and "-" not in row:
                        # Extract data
                        time_ = row[0]+" "+row[1].split(",")[0]
                        temperature_ = row[1].split(",")[1]

                        humidity_ = row[1].split(",")[2]
                        dewpoint_ = row[1].split(",")[3]
                        heatindex_ = row[1].split(",")[4]
                        
                        # Datetime format the time
                        time_ = dateTime(time_)

                        # Add to lists
                        if "-" not in temperature_ and "-" not in humidity_ and "-" not in dewpoint_ and "-" not in heatindex_:
                            time.append(time_)
                            temperature.append(float(temperature_))
                            humidity.append(float(humidity_))
                            dewpoint.append(float(dewpoint_))
                            heatindex.append(float(heatindex_))
            # Set min/max y axis
            if min(humidity) < ymin:
                ymin = np.floor(min(humidity))
            if max(humidity) > ymax:
                ymax = np.ceil(max(humidity))
    
    # Plot for each channel
    if channel==1:
        alpha=1
    else:
        alpha=0.3
    ax.plot(time, humidity,"-",drawstyle="steps-post", color=colors[int(channel)-1],label="Channel "+str(channel), alpha=alpha)
ax.xaxis.set_major_locator(mdates.MonthLocator())
ax.xaxis.set_minor_locator(mdates.DayLocator())
plt.xlabel("Date [YYYY-MM]")
plt.ylabel("Humidity [%]")
plt.suptitle("B175 Humidity")
plt.legend(loc="upper left")
plt.yticks(np.arange(ymin, ymax+1, 1.0))
plt.savefig("./plots/Humidity.png")
plt.show()
    

exit()
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


