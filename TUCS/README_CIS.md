# CIS Calibration Instructions

This guide describes in a step-by-step fashion the basic and most important commands for the monthly CIS Updates and running the plotting scripts. Of course, many channels require fuller investigation. For a full description of all CIS tools and parameters, see the Twiki pages: ```https://twiki.cern.ch/twiki/bin/viewauth/Atlas/TileCisCalibration``` 

## Preliminaries

First, log into *lxplus* and setup the *Athena* environment. Perferably use the most up-to-date version of Athena, accessed by only typing (```asetup```). Then, you should enter the main Tucs directory to run the scripts.

```
ssh -XY USER@lxplus.cern.ch
asetup Athena [VERSION]
cd Tucs
```

Clean the ```Tucs/results``` directory before running any calibration scripts because the ```tileSqlite.db``` file may not be newly created or it may be overwritten in an undesirable way.

```
rm -r results/*
```

## Recalibration Macro

Usually, CIS constants are updated once per month. Ideally, one should use all runs in the month since the last run used to recalibrate in the previous month (simply, you want to include as many calibration points as possible for better statistics). One should try to use as many runs as possible, but one may ise the ```--ldate``` option to specify and exclude certainr runs if necessary. Additionally, as CIS experts one should track exactly *when* problems start occurring in each channel and investigate *why* they occur. Various options allow the user to specify the threshold for recalibration and the minimum run window, among various other options. It is also helpful to use the ```&tee``` command to save the terminal output.

```
macros/cis/CIS_DB_Update.py --date 'May 1,2023' 'June 1, 2023'--ldate 451195 451772 454106 |&tee results/MONTH-CIS-Notes.txt
```

## Output: Files and Plots

After running the macro, there are now some output files to inspect:
* **MONTH-CIS-Notes.txt**:  the CIS_DB_Update.py output log file
* **tileSqlite.db** : this file contains each channel and its newly calculated CIS constant, located in ~/Tucs/results
* **CIS_DB_Update.txt**: lists the channels in the update, as well as some statistics from the update. Also in ~/Tucs/results
* **NoCIS**: list of channels with no CIS response
* **Tucs/plots**: plots for all problemaic channels and those included in the update after running the macro; it also stores plots from other macros

## Recalibrating Channels


## Flag Updates

## Summary Plots

After verifying the calibration runs and the behaviour of each channel, it is often useful to provide various summary plots that track the performance of CIS for all channels. There are copious plotting tools in the online Twiki documentation, but here are some useful examples. Like always, you can use the options in the macro to speficy runs or other parameters. 

```
macros/cis/Public_Super_Macro.py --gcals --date '05/01/22' '06/01/22' --datelabel 'May 1 - June 1, 2022' --mean --lowmem --rmsplots --flagplots
macros/cis/Public_Super_Macro.py --history -0.5 0.5 --date 'May 1, 2023' 'June 1, 2023' --ndate 'May 1, 2022' 'June 1, 2022' --datelabel 'May 2022 v 2023'
```

## Pushing Constants/Flags to the COOL Database
Currently, no special UPD1/UPD4 tagging is required, so you can upload the ```tileSqlitedb``` files as they are. The recalibration scripts orgaize the two files into two different folders along with intermediary log files.

Log into ```https://atlas-tile-calib.cern.ch ``` and . Post to elog and exit. After submitting the changes, make sure to exit the session so other users can access. One may have to wait for other users to finish their session before uploading constants to the database. 

* **ConstantUD/tileSqlite.db**: Upload to ```CISLIN_ALL``` folder in COOL website
* **FlagUD/tileSqlite.db**: Upload to  ```ADC_UPD4_UPD1``` folder in COOL website





