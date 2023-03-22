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
for module,LVPS in LVPS_data:

    # Check to see if file already exists
    # Skip if it is already in the data directory
    new_output_file = module+LVPS+"_5VMotherboardCurrent.txt"
    if new_output_file in listdir(datapath):
        print(new_output_file+" already exists")
        continue

    new_output_file = datapath+new_output_file
    filenames=[]
    counter=0
    start = datetime.strptime(startdate_.split(" ")[0], "%Y.%m.%d")
    end = datetime.strptime(enddate_.split(" ")[0], "%Y.%m.%d")

    for s, e in perdelta(date(2022, 7, 4), date(2022, 11, 28), timedelta(days=30)):
        counter+=1

        #Format retrieval parameters (temporary filename and LVPS for single digit)
        output_file=datapath+str(module)+str(LVPS)+"_"+str(counter)+".txt"
        if int(LVPS)<10: LVPS = str(LVPS)[-1]

        cmd = 'wget -O '+output_file+' --post-data "queryInfo=atlas_pvssTIL, comment_, TIL '+module+' LVPS '+LVPS+' MotherBoard 5V OUTPUT_I, ' + s.strftime("%d-%m-%Y") + ' 00:00, ' + e.strftime("%d-%m-%Y") + ' 00:00, , , , , ,no, , +1!" ' + url 
        system(cmd) 
        filenames.append(output_file)
    if int(LVPS)<10: LVPS = "0"+str(int(LVPS))
    else: LVPS=str(LVPS)

    
    with open(new_output_file, 'w') as outfile:
        for fname in filenames:
            with open(fname) as infile:
                for line in infile:
                    outfile.write(line+", ")
            remove(fname)

# Plotting
print("\nCreating plots ...")
# Retrieve data from online
# Setup folder to feed in data
plotpath = "plots"
if plotpath not in listdir(path):
    mkdir(plotpath)
plotpath = "./"+plotpath+"/"

files = [datapath+f for f in listdir(datapath)]


# Read preapared datafiles
for f in files:
    infile = open(f,"r")
    # Open files and format data for plotting
    for line in infile:
        data = line.split(", ")[1:]
        I,t =[],[]
        for i, entry in enumerate(data):
            if "LVPS" not in entry:
                current = entry.split(" ")[0]
                date_time = entry.split(" ")[1]+" "+entry.split(" ")[2]
                time = datetime.strptime(date_time, "%d-%m-%Y %H:%M:%S:%f")
                if i==0:
                    referencetime=datetime.strptime(date_time, "%d-%m-%Y %H:%M:%S:%f")
                delta = time-referencetime
                # t.append(delta.total_seconds())
                t.append(time)
                I.append(np.around(float(current),decimals=2))


        # Now make each plot
        title=f[7:12]
        partition=title[0:3]
        module=title[3::]
        print(title)
        plt.figure(figsize=(8,6))

        #Plot time v. current
        plt.plot(t,I, drawstyle="steps-post", color="black",label="Recorded Current")

        # Text annorations for plot
        line1 = "Total Trips: "
        line2 = "Date/Time of Trips:"

        #Organize and plot thresholds on top of this
        trip_time = []
        trip_threshold = []
        trip_counter = 0
        for time, threshold in threshold_dict[title]:
            trip_time.append(time)
            if trip_counter < 10:
                line2_time = datetime.strftime(time, "%d-%m-%Y %H:%M:%S:%f")[0:-10]
                line2+="\n"+line2_time
            trip_threshold.append(threshold)
            trip_counter+=1
        if trip_counter >= 10:
            line2 += "\n [...]"

        # Add start and end date to make continuous over plotting range
        trip_time.insert(0,startdate)
        trip_threshold.insert(0,trip_threshold[0])
        trip_time.append(enddate)
        trip_threshold.append(trip_threshold[-1])

        # Finalize text
        line1 = line1+str(int(trip_counter))
        text = line1+"\n"+line2
        plt.annotate(text,xy =(0.60,0.15) , xycoords="figure fraction")

        #Plot threshold
        plt.plot(trip_time, trip_threshold,"--",drawstyle="steps-post", color="red",label="Threshold")
        
        # Plot formatting
        plt.ylim([-1,15])
        plt.ylabel("Current [A]")
        plt.xlabel("Date During Run 3 [YYYY-MM]")
        plt.suptitle(" 5V Motherbard Current to 3-in-1 Card (%s LVPS)"%title)
        plt.legend(loc="upper right")
        #plt.tight_layout()
        plt.savefig(plotpath+title+"_LVPS_5VMotherboardCurrent.png")
        plt.close()