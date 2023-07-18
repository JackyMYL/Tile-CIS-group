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

# CIS Constant Reprocessing Procedure

This document describes the procedure for reprocessing the CIS constants after the data-taking period. The calibration coordinators will ask CIS experts to reprocess CIS constants at the end of data-taking to verify their previous updates and account for any changes in CIS constant values throughout the data-taking period. Tile will provide a full menu of database conditions to ATLAS to process run data.

## Run Verfication

Quality of runs should be verified just as they are in the monthly update. One should check Amplitude-Charge ratio and timing. If this has been properly done in the monthly updates, one can just take previously verified runs (i.e. not every run in the data-taking period, but only ``valid" ones).

Problems with individual runs may only become evident in the channel plots. There are usually two reasons for jumps in the CIS constant: (1) the run was faulty atually due to incorrect charge missed int he previous step but in one specific channel or (2) the jump is real and should be cross-checked with the laser system. In the latter case the IOV should be tuned accordingly


## Parameter Choice 

Since we ideally are updating all channels with the CIS Update macro, the CIS techs should tune the following paramaters. Try running the update macro with different combinations of parameters to find the best combination. The goal is to minimize the number of manual changes to just a handful of channels, otherwise it would be too tedious to update!

* **updateThreshold**: Use the ```--updateThreshold``` flag in the CIS update macro to specify at what level of variation the macro should start calculating a new CIS constant. Standard error is 0.5%, which is the default setting. In the past, we have foudn for some slowly drifting channels, it was better to set the threshold slightly lower to get a better match. It's not worth being too pedantic to below 0.2%. Start with 0.5% and see if it needs to be lowered later.
* **runWindow**: Use the ```--runWindow``` flag in the CIS update macro to specify howmany runs should be used at minimum before recalculating the CIS constant. For example, there may be three runs for which the calibration constant jumps to a different value for some electronics reason. In that case, setting the IOV (interval-of-validity) to 3 runs would capture that variation automatically. Start with 10, 7, and 4, and see if adjustments need tobe made. Generally, a higher number of runs in the minimumrun window is favored for better statistics.
* **multipleiov**: USe the Boolean ``--multipleiov`` flag to specify that you would like to use multiple IOVs


## Reference Runs

One should choose about one month's worth of runs *before* data taking to act as reference runs. The goal is to give a baseline value for every TileCal channel which may change during data-taking. For example, in 2022 data-taking, use the validated runs from March as the baseline. Make sure topick dates outside of the maintenance period where conditions may be changing, as well. Use the ```--recalALLL``` option to ensure that all channels are recalibrated.

```
cd Tucs
macros/cis/CIS_DB_Update.py --date 'REFERENCE_START' 'REFERENCE_END' --ldate XXXXXX YYYYYY ZZZZZZ --updateThreshold 0.0 --recalALL
mv results/tileSqlite.db results/tileSqlite_first_IOV.db
```

The final command changes the name of the reference Sqlite file. In the reprocessing step, it is used as a reference to see if the channel needs to be changed from this reference value. Either the IOV will be extended through data-taking (no change) or the constant will be changed in the next step as conditions evolve (change needed)

## Calibration Value in Data-Taking Period

Commands should look like the following, and one should analyze and compare the outputs for different combinations of parameters.

```
cd Tucs
macros/cis/CIS_DB_Update.py --date 'STARTDATE' 'ENDDATE' --ldate XXXXXX YYYYYY ZZZZZZ --runWindow 7 --updateThreshold 0.5
```

## Reprocessing the Calibration Runs
Now that a baseline value has been set, you can proceed with tuning the parameters in the macro to update 
necessary channels -- the ones that have deviated from their baseline value. In the CIS_DB_Update.py macro, one 
should change the ```readcalibfromcool``` line to (should be checked with database experts as tagging may 
change):

```
readcalfromcool = 
ReadCalibFromCool(schema='sqlite://;schema=tileSqlite_first_IOV.db;dbname=CONDBR2', 
runType='CIS', folder='CALIB/CIS', tag='RUN2-HLT-UPD1-00', data = 'DATA')
```

## Dealing with Memory Issues
It is likely that TUCS will use too much memory and be killed by the computing system because it is reading 
many large datafiles from calibration runs. There are two methods to circumvent this: (1) split the update into 
intervals of a few months or groups of a fixed number of runs and updating the sqlite baseline file each 
iteration or (2) do reprocessing by partition (EBA, EBC, LBA, LBC) and carefully merge all of the Sqlite files 
at the end.

### Option 1: Smaller Run Intervals

Use the same Sqlite file as input and output, so start by copying the baseline values to the master Sqlite 
file. In each step, the master file one appends the next chunk of the update.

```
cp tileSqlite_first_IOV.db tileSqlite.db
macros/cis/CIS_DB_Update.py --date 'DAY_0' 'DAY_60' --ldate XXXXXX YYYYYY ZZZZZZ --multipleiov --runWindow 4 
--updateThreshold 0.5
```

Remember to change the line in the ReadCalibFromCool worker call in the macro so thet tileSqlite becomes the 
input and output file that we constantly append.

```
readcalfromcool =
ReadCalibFromCool(schema='sqlite://;schema=tileSqlite.db;dbname=CONDBR2',
runType='CIS', folder='CALIB/CIS', tag='RUN2-HLT-UPD1-00', data = 'DATA')
```

If the update malfunctions somehow, start again from the beginning by copying the baseline values to the 
desired input/output file and batching the update into regular intervals again. Two months should be small 
enough in terms of memory demands, but it could be that one requires smaller intervals.

### Option 2: Processing by Detector Region and Merging

Another option to save memory is to process the full data-taking period but use smaller detector regions (EBA, 
EBC, LBA, LBC). Keep the ReadCalibFromCool schema as originally stated with the tileSqlite_first_IOV.db file as 
the schema parameter. Then, rename each output file for each detector region so that they are not overwritten. 
Finally, merge the detector region files as follows. The process is a little complicated because the database 
file needs to be in date-order, so some command line commands weave them together.

In general, for every comments line, one must write:
```
WriteCalibToCool.py 
--schema='sqlite://;schema=tileSqlite_final.db;dbname=CONDBR2' 
--folder=/TILE/OFL02/CALIB/CIS/LIN --tag=RUN2-HLT-UPD1-00 --run=XXX 
--lumi=YYY --comment="ZZZ"
```

First, dump the file comments, then sort and merge them.
```
eadCalibFromCool.py 
--schema='sqlite://;schema=tileSqlite_LBA.db;dbname=CONDBR2' 
--folder=/TILE/OFL02/CALIB/CIS/LIN --tag=RUN2-HLT-UPD1-00 --begin=0 -C 
2>comments
ReadCalibFromCool.py 
--schema='sqlite://;schema=tileSqlite_LBC.db;dbname=CONDBR2' 
--folder=/TILE/OFL02/CALIB/CIS/LIN --tag=RUN2-HLT-UPD1-00 --begin=0 -C 
2>>comments
ReadCalibFromCool.py 
--schema='sqlite://;schema=tileSqlite_EBA.db;dbname=CONDBR2' 
--folder=/TILE/OFL02/CALIB/CIS/LIN --tag=RUN2-HLT-UPD1-00 --begin=0 -C 
2>>comments
ReadCalibFromCool.py 
--schema='sqlite://;schema=tileSqlite_EBC.db;dbname=CONDBR2' 
--folder=/TILE/OFL02/CALIB/CIS/LIN --tag=RUN2-HLT-UPD1-00 --begin=0 -C 
2>>comments
grep "(.*,.*)" comments | sort -u | sed -e "s|).*):|)|g" -e "s|^.*INFO 
*||g"  > comments.sorted
```

Check that there are no duplicated run numbers in comments.sorted, and merge them in a single line if needed. 
Then convert comments.sorted into a shell script and execute it.

```
sed -e "s|(|WriteCalibToCool.py 
--schema='sqlite://;schema=tileSqlite_final.db;dbname=CONDBR2' 
--folder=/TILE/OFL02/CALIB/CIS/LIN --tag=RUN2-HLT-UPD1-00 --run=|1" -e 
"s|,| --lumi=|1" -e 's|) | --comment="|1' -e 's|$|"|1' comments.sorted > 
comments.sh
sh comments.sh
```

Finally, merge the results:

```
AtlCoolCopy 'sqlite://;schema=tileSqlite_first_IOV.db;dbname=CONDBR2' 
'sqlite://;schema=tileSqlite_final.db;dbname=CONDBR2' -ch 1000 -create
AtlCoolCopy 'sqlite://;schema=tileSqlite_LBC.db;dbname=CONDBR2' 
'sqlite://;schema=tileSqlite_final.db;dbname=CONDBR2' -ch1 84 -ch2 147
AtlCoolCopy 'sqlite://;schema=tileSqlite_LBA.db;dbname=CONDBR2' 
'sqlite://;schema=tileSqlite_final.db;dbname=CONDBR2' -ch1 20 -ch2 83
AtlCoolCopy 'sqlite://;schema=tileSqlite_EBA.db;dbname=CONDBR2' 
'sqlite://;schema=tileSqlite_final.db;dbname=CONDBR2' -ch1 148 -ch2 211
AtlCoolCopy 'sqlite://;schema=tileSqlite_EBC.db;dbname=CONDBR2' 
'sqlite://;schema=tileSqlite_final.db;dbname=CONDBR2' -ch1 212 -ch2 275
```





