#!/bin/bash
echo "CurrentDir",`pwd`
echo "==========  Running Make_Common_NTuple_CRON.sh at `date` =========="


# For email notification
export NOTIFYEMAIL_1="smeehan12@gmail.com"
export NOTIFYEMAIL_2="cjmeyer@hep.uchicago.edu"
export SUBJECT="Cron job run to produce ntuples"
export MESSAGE="CronNotification.txt"



# Get dates for starting and stopping executing of NTupler
export ENDYEAR=`date "+%Y"`
export ENDMONTH=`date "+%m"`
export ENDDAY=`date "+%d"`

export STARTYEAR=`date "+%Y"`
export STARTMONTH_TEMP=`date "+%m"`
export STARTMONTH=`expr "$STARTMONTH_TEMP" - 1`
if [ $STARTMONTH_TEMP -eq 01 ]
then
    echo 'KEEPING MONTH'
    export STARTMONTH=$STARTMONTH_TEMP
else
    echo 'CHANGING MONTH'
    export STARTMONTH=`expr "$STARTMONTH_TEMP" - 1`
fi
export STARTDAY=`date "+%d"`

export STARTDATE=$STARTYEAR-$STARTMONTH-$STARTDAY
export ENDDATE=$ENDYEAR-$ENDMONTH-$ENDDAY

echo "Processing Start Date: ",$STARTDATE
echo "Processing Stop Date: ",$ENDDATE
cd /tucs/TileCalibAlgsTrunk/share/Tucs
echo "Running in: "`pwd`

echo "Starting ntuple production for: "$STARTDATE" to "$ENDDATE > $MESSAGE 2>&1
echo "Start Time: "`date`"\n" >> $MESSAGE 2>&1
echo "Running in: "`pwd`"\n" >> $MESSAGE 2>&1

# Setup Athena to 17.3.0,builds
echo "Setting up Athena" >> $MESSAGE
export AtlasSetup=/afs/cern.ch/atlas/software/dist/AtlasSetup
source $AtlasSetup/scripts/asetup.sh 17.3.0,builds
echo "Athena done setting up" >> $MESSAGE
echo `whoami` >> $MESSAGE
ls /afs/cern.ch/user/a/atlcond/utils/python >> $MESSAGE 2>&1
export PYTHONPATH="/afs/cern.ch/user/a/atlcond/utils/python:$PYTHONPATH"
echo $PYTHONPATH >> $MESSAGE 2>&1

# Loop over calibration systems for production of ntuples
# (1) Produce ntuples
# (2) Copy from temp area to permanent area
CALIBRATION_SYSTEMS="CIS Las cesium HV"

/bin/mail -s "$SUBJECT" "$NOTIFYEMAIL_1" < $MESSAGE 2>&1
#/bin/mail -s "$SUBJECT" "$NOTIFYEMAIL_2" < $MESSAGE 2>&1

for CAL in ${CALIBRATION_SYSTEMS}
do
    echo "--------------------------\n" >> $MESSAGE
    echo "Processing: "${CAL}"\n" >> $MESSAGE
    echo "Start Time: "`date`"\n" >> $MESSAGE
    COMMAND="python macros/Make_Common_NTuple.py  --date `expr "${STARTDATE}"` --enddate `expr "${ENDDATE}"` --runtype `expr "${CAL}"` --debug "
    echo $COMMAND
    echo $COMMAND"\n" >> $MESSAGE 2>&1
    `${COMMAND}` 
    COPYCOMMAND="cp /tucs/TileCalibAlgsTrunk/share/Tucs/CommonNTuples/`expr "${STARTDATE}"`-to-`expr "${ENDDATE}"`/`expr "${CAL}"`/* /tucs/CommonNTuples/${CAL}/."
    echo ${COPYCOMMAND}
    echo $COPYCOMMAND"\n" >> $MESSAGE 2>&1
    `${COPYCOMMAND}` 
    echo "Stop Time: "`date`"\n" >> $MESSAGE 2>&1
    
    /bin/mail -s "$SUBJECT" "$NOTIFYEMAIL_1" < $MESSAGE 2>&1
#    /bin/mail -s "$SUBJECT" "$NOTIFYEMAIL_2" < $MESSAGE 2>&1
    
done

echo "FINISHED PRODUCING COMMON NTUPLES\n" >> $MESSAGE 2>&1
echo "Stop Time: "`date`"\n" >> $MESSAGE 2>&1
echo "New ntuples stored in /tucs/CommonNTuples" >> $MESSAGE 2>&1


/bin/mail -s "$SUBJECT" "$NOTIFYEMAIL_1" < $MESSAGE 2>&1
#/bin/mail -s "$SUBJECT" "$NOTIFYEMAIL_2" < $MESSAGE 2>&1
rm CronNotification.txt
