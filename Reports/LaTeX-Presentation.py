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
echofile = open("JuneNotes.txt","r")
echofile_1 = open("JuneNotes_1.txt","r")
history = open("History.txt","r")

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



# Write file
with file as f:



    # [0] HEADER/SETTINGS
    f.write("\documentclass[11pt]{beamer}\n")
    f.write("\\usetheme{Madrid}\n")
    f.write("\\usepackage{xcolor}\n")
    f.write("\\usepackage[utf8]{inputenc}\n")
    f.write("\\usepackage{hyperref}\n")
    f.write("\\usepackage{amsmath}\n")
    f.write("\\usepackage{amsmath}\n")
    f.write("\\usepackage{caption}\n")
    f.write("\\usepackage{subcaption}\n")
    f.write("\\usepackage{multicol}\n")
    f.write("\DeclareMathOperator {\\argmin}{argmin}\n")
    f.write("\hypersetup{\n")
    f.write("    colorlinks=true,\n")
    f.write("    urlcolor=magenta,\n")
    f.write("    linkcolor=white\n")
    f.write("    }\n")
    f.write("\\newcommand{\yes}{\\textcolor{green}{Yes }}\n")
    f.write("\\newcommand{\\no}{\\textcolor{red}{No }}\n")
    f.write("\\newcommand{\badcis}{\\textcolor{red}{Bad CIS }}\n")
    f.write("\\newcommand{\\nocis}{\\textcolor{orange}{No CIS }}\n")
    f.write("\\newcommand{\goodcis}{\\textcolor{green}{Good CIS }}\n")
    f.write("\\newcommand{\intervention}{\\textcolor{blue}{YETS Intervention}}\n")
    f.write("\\newcommand{\half}{\\textcolor{pink}{Moved to Half Gain}}\n")
    f.write("\\author{Peter Camporeale, Jacky Li}\n")
    f.write("\\title{Charge Injection System (CIS) Update}\n")
    f.write("\\newcommand{\email}{peter.thomas.camporeale@cern.ch}\n")
    f.write("\\setbeamertemplate{navigation symbols}{} \n")
    f.write("\logo{} \n")
    f.write("\institute[]{UNIVERSITY OF CHICAGO}  \n")
    f.write(" \n")
    f.write("\\bibliographystyle{apalike} \n")
    f.write(" \n")
    f.write("\\begin{document}\n")

    # [1] Title Slide
    f.write("\\begin{frame}\n")
    f.write("\\titlepage \n")
    f.write("\\begin{center} \n")
    f.write("\\includegraphics[scale=0.2]{images/title/ATLAS Experiment Logo.png}\n")
    f.write("\hspace{1cm}\n")
    f.write("\includegraphics[scale=0.1]{images/title/UChicago Logo.png}\n")
    f.write("\end{center}\n")
    f.write("\end{frame}\n")
    f.write("\n")


    # [2] Introduction Slide
    f.write("\\begin{frame}{Introduction}\n")
    f.write("    \\begin{itemize}\n")
    f.write("        \item\n")
    f.write("    \end{itemize}\n")
    f.write("\end{frame}\n")
    f.write("\n")



    # [3] Introduction Slide
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
    f.write("\n")



    # [4] Run Selection
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
    print(filestring_spaces)
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
    f.write("\n")


    # Print list of excluded and included runs
    print("Included: %s"%filestring_spaces)
    print(filestring_commas)
    print("Excluded: %s"%excluded)

    # [5] Run Selection Example Plots (add more if necessary)
    f.write("\\begin{frame}{Run Selection: Run XXXXXX AmpQ Ratio (X)}\n")
    f.write("\\begin{figure}\n")
    f.write("    \centering\n")
    f.write("    \includegraphics[width=\textwidth]{images/CIS_charge_run_.png}\n")
    f.write("    \label{fig:AmpQ}\n")
    f.write("\end{figure}\n")
    f.write("\end{frame}\n")
    f.write("\n")

    # [6] CIS Constant Distributions
    f.write("\\begin{frame}{CIS Constant Distributions}\n")
    f.write("    \\begin{multicols}{2}\n")
    f.write("        \\begin{figure}\n")
    f.write("            \centering\\n")
    f.write("            \includegraphics[width=0.5\\textwidth]{images/public_plots/calib_dist_hvalhi.png}\n")
    f.write("            \caption{Distribution of Mean HG CIS constants for calibration runs in "+month_name+" "+year+"}\n")
    f.write("            \label{fig:HGDistribution}\n")
    f.write("        \end{figure}\n")
    f.write("        \\begin{figure}\n")
    f.write("            \centering\n")
    f.write("            \includegraphics[width=0.5\\textwidth]{images/public_plots/calib_dist_hvallo.png}\n")
    f.write("            \caption{Distribution of Mean LG CIS constants for calibration runs in "+month_name+" "+year+"}\n")
    f.write("            \label{fig:HGAverage}\n")
    f.write("        \end{figure}\n")
    f.write("    \end{multicols}\n")
    f.write("\end{frame}\n")
    f.write("\n")

    # [7] Monthly Stability
    f.write("\\begin{frame}{Monthly Stability}\n")
    f.write("        \\begin{multicols}{2}\n")
    f.write("        \\begin{figure}\n")
    f.write("            \centering\n")
    f.write("            \includegraphics[width=0.\5\textwidth]{images/public_plots/HighgainDetAvg.png}\n")
    f.write("            \caption{"+month_name+" stability of CIS constant in TileCal compared to a single channel (HG)}\n")
    f.write("            \label{fig:HGDistribution}\n")
    f.write("        \end{figure}\n")
    f.write("        \\begin{figure}\n")
    f.write("            \centering\n")
    f.write("            \includegraphics[width=0.5\\textwidth]{images/public_plots/LowgainDetAvg.png}\n")
    f.write("            \caption{"+month_name+" stability of CIS constant in TileCal compared to a single channel (LG)}\n")
    f.write("            \label{fig:LGAverage}\n")
    f.write("        \end{figure}\n")
    f.write("    \end{multicols}\n")
    f.write("\end{frame}\n")
    f.write("\n")

    # [8] Detector History
    
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

    # [9] RMS Distributions
    f.write("\\begin{frame}{RMS Distributions}\n")
    f.write("    \\begin{figure}\n")
    f.write("        \centering\n")
    f.write("        \includegraphics[width=0.7\textwidth]{images/public_plots/time_spread_rms.png}\n")
    f.write("        \caption{RMS/Mean distribution of CIS constant. This month there is a lot of overflow  (cut off) because of modules being off and this affecting the calculation of RMS and Mean}\n")
    f.write("        \label{fig:RMS}\n")
    f.write("    \end{figure}\n")
    f.write("\end{frame}\n")
    f.write("\n")

    # [10] TUCS Quality Flags 
    f.write("\\begin{frame}{TUCS Quality Flags}\n")
    f.write("    \\begin{figure}\n")
    f.write("        \centering\n")
    f.write("        \includegraphics[width=0.7\\textwidth]{images/public_plots/TUCS_Flag_History.png}\n")
    f.write("        \caption{TUCS quality flags for all runs included in CIS constant update this month}\n")
    f.write("        \label{fig:QualityFlags}\n")
    f.write("    \end{figure}\n")
    f.write("\end{frame}\n")
    f.write("\n")

    # [11] Channels to Recalibrate
    f.write("\\begin{frame}{Channels to Recalibrate}\n")
    f.write("    \\begin{table}[]\n")
    f.write("        \centering\n")
    f.write("        \\begin{tabular}{|c|c|c|c|c|}\n")
    f.write("        \hline\n")
    f.write("         Module & Channel & Gain & Recalibrate From Date \\\\n")
    f.write("       \hline \hline\n")
    f.write("\n")
    f.write("        \hline\n")
    f.write("        \end{tabular}\n")
    f.write("        \label{tab:RecalibrationTable}\n")
    f.write("    \end{table}\n")
    f.write("\end{frame}\n")
    f.write("\n")

    # [12] Channels to Recalibrate Example Plots
    f.write("\\begin{frame}{Channels to Recalibrate}\n")
    f.write("    \\begin{multicols}{2}\n")
    f.write("        \\begin{figure}\n")
    f.write("            \centering\n")
    f.write("            \includegraphics[width=0.5\\textwidth]{images/recalibrate/CISUpdate_TILECAL_EBA_m05_c10_lowgain.png}\n")
    f.write("            \caption{Recalibrate from DATE}\n")
    f.write("            \label{fig:Recalibrate1}\n")
    f.write("        \end{figure}\n")
    f.write("        \\begin{figure}\n")
    f.write("            \centering\n")
    f.write("\            \includegraphics[width=0.5\\textwidth]{images/recalibrate/CISUpdate_TILECAL_EBA_m09_c16_lowgain.png}n")
    f.write("            \caption{Recalibrate from DATE}\n")
    f.write("            \label{fig:Recalibrate2}\n")    
    f.write("        \end{figure}\n")
    f.write("    \end{multicols}\n")
    f.write("\end{frame}\n")
    f.write("\n")

    # [13] Flag Changes
    f.write("\\begin{frame}{Flag Changes}\n")
    f.write("    \\begin{table}[]\n")
    f.write("        \centering\n")
    f.write("        \\begin{tabular}{|c|c|c|c|c|}\n")
    f.write("        \hline\n")
    f.write("         Module & Channel & Gain  & Change Flag To \\\\n")
    f.write("        \hline \hline\n")
    f.write("\n")
    f.write("        \hline\n")
    f.write("        \end{tabular}\n")
    f.write("        \label{tab:FlagChangesTable}\n")
    f.write("    \end{table}\n")
    f.write("\end{frame}\n")
    f.write("\n")

    # [14] Flag Changes Example Plots
    f.write("\\begin{frame}{Flag Changes: To Good CIS}\n")
    f.write("    \\begin{multicols}{2}\n")
    f.write("        \\begin{figure}\n")
    f.write("            \centering\n")
    f.write("            \includegraphics[width=0.5\\textwidth]{images/flag/CISUpdate_TILECAL_EBA_m05_c10_lowgain.png}\n")
    f.write("            \caption{Good CIS in X}\n")
    f.write("            \label{fig:FlagGood1}\n")
    f.write("        \end{figure}\n")
    f.write("        \\begin{figure}\n")
    f.write("            \centering\n")
    f.write("            \includegraphics[width=0.5\\textwidth]{images/flag/CISUpdate_TILECAL_EBA_m09_c16_lowgain.png}\n")
    f.write("            \caption{Good CIS in X}\n")
    f.write("            \label{fig:FlagGood2}\n")
    f.write("        \end{figure}\n")
    f.write("    \end{multicols}\n")
    f.write("\end{frame}\n")
    f.write("\n")

    # [15] Channels with >5% Change
    f.write("\\begin{frame}{Channels with $>5\%$ Change}\n")
    f.write("\scriptsize\n")
    f.write("       \\begin{table}[]\n")
    f.write("       \centering\n")
    f.write("        \\begin{tabular}{|c|c|c|c|c|}\n")
    f.write("        \hline\n")
    f.write("         Channel & Old DB Value & New DB Value & Change & Status \\\ \n")
    f.write("        \hline \hline\n")
    datafile = open("CIS_DB_update.txt","r")
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

    
    # Affected/Masked Channel List
    f.write("\\begin{frame}{Masked/Affected Channel List}\n")
    f.write("\\begin{multicols}{2}\n")
    f.write("\scriptsize\n")
    f.write("\\textbf{Masked ("+masked+")}\\\\\n")

    datafile = open("CIS_DB_update.txt","r")
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



