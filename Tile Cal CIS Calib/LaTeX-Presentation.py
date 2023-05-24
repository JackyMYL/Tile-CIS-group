#####################################################
#
# Author:  Peter Camporeale
# Contact: peter.thomas.camporeale@cern.ch
#
# Description: Generate LaTeX slides for CIS
#               update presentation after running
#               Tucs/macros/cis/CIS_DB_Update.py
#               Tucs/macros/cis/Public_Super_Macro.py
#
#####################################################


# Imports
import numpy as np
import datetime
import calendar
import string

file = open("LaTeXPresentation.txt","w")
datafile = open("CIS_DB_update.txt","r")
echofile = open("AprilCISNotes.txt","r")
echofile_1 = open("CISApril_Preliminary.txt","r")
history = open("History.txt","r")



with file as f:


    # Process runs and dates
    with echofile as e:
        filestring_spaces = ""
        filestring_commas = ""
        useflag=False
        for line in e:
            if "_CIS.0.root" in line:
                filestring_spaces+= line.split("_")[1]+" "
                filestring_commas+= line.split("_")[1]+", "
            if "Use: Using all the detector" in line:
                useflag=True
            elif "ReadCIS" in line:
                useflag=False
            if "run" and "CIS" in line and useflag:
                month=line.split(",")[2].split(" ")[1].split("-")[1]
                year=line.split(",")[2].split(" ")[1].split("-")[0][1:]
                print(year)
                datetime_object = datetime.datetime.strptime(month, "%m")
                month_name = datetime_object.strftime("%B")
                lastday = str(calendar.monthrange(int(year), int(month))[1])


                print(month_name)
                print(lastday)
        filestring_commas=filestring_commas[0:-2]

    with echofile_1 as e:
        filestring_spaces_1 = ""
        filestring_commas_1 = ""
        for line in e:
            if "_CIS.0.root" in line:
                filestring_spaces_1+= line.split("_")[1]+" "
                filestring_commas_1+= line.split("_")[1]+", "
        filestring_commas_1=filestring_commas_1[0:-2]
        print(filestring_commas_1)
        print(filestring_spaces_1)


    ### Write presentation
    # Write 5% deviation channels
    f.write("\\begin{frame}{Channels with $>5\%$ Change}\n")
    f.write("\scriptsize\n")
    f.write("       \\begin{table}[]\n")
    f.write("       \centering\n")
    f.write("        \\begin{tabular}{|c|c|c|c|c|}\n")
    f.write("        \hline\n")
    f.write("         Channel & Old DB Value & New DB Value & Change & Status \\\ \n")
    f.write("        \hline \hline\n")
    with datafile as d:
        for line in d:
            if "TILECAL" in line:
                print(line)
                module,old,new,pct = line.split(" \t ")
                tilecal,part,mod,chan,gain = module.split("_")
                old=float(old)
                new=float(new)
                pct=pct[0:-2]
                if abs(float(pct))>=0.05:
                    f.write("       "+part+" "+mod+" "+chan+" "+gain+" & "+str(np.round(a=old,decimals=2))+" & "+str(np.round(a=new,decimals=2))+" & "+str(np.round(a=float(pct)*100,decimals=1))+" & \\\\\n")
    f.write("        \hline\n")
    f.write("        \end{tabular}\n")
    f.write("        \label{tab:LargeDeviationTable}\n")
    f.write("    \end{table}\n")
    f.write("\end{frame}\n\n\n")

    # Write Summary
    f.write("\\begin{frame}{Summary}\n")
    f.write("\\begin{multicols}{2}\n")
    f.write("\\begin{table}[]\n")
    f.write("\scriptsize\n")
    f.write("    \\begin{tabular}{|c|c|}\n")
    
    f.write("    \hline\n")

    datafile = open("CIS_DB_Update.txt","r")
    with datafile as d:
        for line in d:
            if "updated" in line:
                f.write("       \\text{Channels in Update} & "+str(line.split("\t")[0][-3:])+"\\\\\n")
            if "good" in line:
                f.write("       Good ($>$1 Successful Calibration) &"+str(line.split("\t")[1][-3:-1])+"\\\\\n")
            if "Masked" in line:
                f.write("       Masked & "+line[-3:-1]+"\\\\\n")
                masked=line[-3:-1]
            if "Affected" in line:
                f.write("       Affected & "+line[-3:-1]+"\\\\\n")
                affected=line[-3:-1]
            if ">5 percent change" in line:
                f.write("       $>$5\% Change & "+line[-3:-1]+"\\\\\n")
                largedev = line[-3:]
    f.write("    \hline\n")
    f.write("    \end{tabular}\n")
    f.write("    \caption{Summary of channels included in the update. Runs are taken from the period 1 "+month_name+" "+year+" - "+lastday+" "+month_name+" "+year+". There are "+largedev+" channels with greater than $0.5\%$ change, the usual update threshold we use.}\n")
    f.write("\end{table}\n")
    f.write("\\begin{figure}\n")
    f.write("    \includegraphics[scale=0.2]{images/hist.png}\n")
    f.write("    \caption{Distribution of CIS constants for the entire detector. The histogram omits channels for which change is less than 0.5\% since the last update.}\n")
    f.write("    \label{fig:HistogramSummary}\n")
    f.write("\end{figure}\n")
    f.write("\end{multicols}\n")
    f.write("\end{frame}\n\n\n")


    # Affected/Masked Channel List
    f.write("\\begin{frame}{Masked/Affected Channel List}\n")
    f.write("\\begin{multicols}{2}\n")
    f.write("\scriptsize\n")
    f.write("\\textbf{Masked ("+masked+")}\\\\\n")
    
    datafile = open("CIS_DB_Update.txt","r")
    with datafile as d:
        masked_flag=False
        affected_flag=False
        for line in d:
            if "Masked" in line:
                masked_flag=True
            elif "Affected" in line:
                masked_flag=False
                affected_flag=True
                f.write("\\textbf{Affeted ("+affected+")}\\\\\n")
            if masked_flag or affected_flag:
                if ":" not in line:
                    name=line.split()[0]+" "+line.split()[1]+" "+line.split()[2]
                    f.write(name+"\\\\\n")

    f.write("\end{multicols}\n")
    f.write("\end{frame}\n\n\n")


    
    f.write("\\begin{frame}{Run Selection}\n")
    f.write("\\begin{table}[]\n")
    f.write("    \centering\n")
    f.write("    \\begin{tabular}{|c||c|}\n")
    f.write("    \hline\n")
    #Default is full month range
    f.write("       Date Range  &  1 "+month_name+" "+year+" - "+lastday+" "+month_name+" "+year+"\\\\\n")
    f.write("    \hline\n")
    # Keep 6 to a line
    includedtemp = filestring_spaces.split(" ")
    included=""
    for k,run in enumerate(includedtemp):
        if k%6==0 and k!=0:
            included+="\\\\&"
        included+=run+" "
        if k==0:
            firstrun=run
        else:
            lastrun=run
        
    f.write("       Runs Included  & \\text{"+filestring_spaces+"}\\\\\n")
    #List excluded runs
    full_list = filestring_spaces_1.split(" ")
    excluded=""
    alphabet = list(string.ascii_lowercase)
    counter=0
    for run in full_list:
        if counter%6==0 and counter!=0: # Keep 6 runs to a line
            excluded+="\\\\&"
        if run not in filestring_spaces:
            excluded+=run+"$^"+alphabet[counter]+"$ "
            counter+=1
    f.write("    \hline\n")
    f.write("       Runs Excluded & "+excluded+"\\\\\n")
    f.write("    \hline\n")
    f.write("    \end{tabular}\n")
    f.write("    \label{tab:RunSelection}\n")
    f.write("\end{table}\n")
    f.write("\\begin{itemize}\n")
    f.write("    \item DESCRIBE REASONING HERE\n")
    f.write("\end{itemize}\n")
    f.write("\end{frame}\n\n\n")

    #History



    f.write("\\begin{frame}{Detector History}\n")
    f.write("\\begin{multicols}{2}\n")
    f.write("    \\begin{figure}\n")
    f.write("        \centering\n")
    f.write("        \includegraphics[width=0.6\\textwidth]{images/public_plots/history.png}\n")
    f.write("        \caption{Change in CIS constants by channel from beginning to end of "+month_name+" "+year+"}\n")
    f.write("        \label{fig:History}\n")
    f.write("    \end{figure}\n")
    f.write("    \\begin{itemize}\n")
    f.write("        \item Here, we list the channels that underwent a drift of greater than $3\%$ between runs "+firstrun+" and "+lastrun+". These correspond the overflow bins in the histogram. \n")
    f.write("        \\begin{itemize}\n")
    with history as h:
        for line in h:
            if "High CIS deviation" in line:
                highdev = line.split("TILECAL_")[1]
                part,mod,chan,gain=highdev.split("_")
                gain,pctdev=gain.split(": ")
                f.write("            \item {} {} {} {} ({}\%)\n".format(part,mod,chan,gain,np.round(float(pctdev),decimals=1)))
    f.write("        \end{itemize}\n")
    f.write("        \item These channels in the overflow bins all need to be recalibrated. See a later slide with an extensive list of channels to recalibrate.\n")
    f.write("    \end{itemize}\n")
    f.write("\end{multicols}\n")
    f.write("\end{frame}\n\n\n")

op