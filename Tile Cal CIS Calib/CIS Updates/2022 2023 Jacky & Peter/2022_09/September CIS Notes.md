# September CIS Notes

**Initial Command**: macros/cis/CIS_DB_Update.py --date 'August 9, 2022' 'September 5, 2022'|&tee August_SeptemberCIS.txt

**Initial Runs**: 430900, 431285, 431304, 431313, 431374, 431570, 431591, 431991, 432218, 432548, 432824, 433072, 433116
run  [430900, 'CIS', '2022-08-11 08:44:42,2022-08-11 08:45:44']

run  [431285, 'CIS', '2022-08-15 16:39:06,2022-08-15 16:40:28']

run  [431304, 'CIS', '2022-08-15 17:14:33,2022-08-15 17:15:36']

run  [431313, 'CIS', '2022-08-15 17:23:31,2022-08-15 17:24:52']

run  [431374, 'CIS', '2022-08-16 10:16:46,2022-08-16 10:18:13']

run  [431570, 'CIS', '2022-08-18 08:57:49,2022-08-18 08:59:27']

run  [431591, 'CIS', '2022-08-18 09:36:03,2022-08-18 09:37:30']

run  [431991, 'CIS', '2022-08-22 15:45:49,2022-08-22 15:47:20']

run  [432218, 'CIS', '2022-08-23 14:56:12,2022-08-23 14:57:31']

run  [432548, 'CIS', '2022-08-25 11:18:52,2022-08-25 11:20:15']

run  [432824, 'CIS', '2022-08-29 08:44:49,2022-08-29 08:46:26']

run  [433072, 'CIS', '2022-09-01 10:07:49,2022-09-01 10:09:24']

run  [433116, 'CIS', '2022-09-01 12:31:04,2022-09-01 12:32:42']



**AmpQ and Timing Plots:** CIS run 431591 is bad for low gain (there are some outliers). 

**Channel Plots:** Recurring issue in runs 433072, 433116 where the calibration constants are significantly lower for the last runs in the month, where otherwsie very stable. There was probably something wrong with the calibration. CHECK ELISA MESSAGES!

**Problems from Scripts:** 
Problem with mean_trunc in SetLowCISThreshold.py (TILECAL_LBA_m14_c37_highgain)
Problem with mean_trunc in SetLowCISThreshold.py (TILECAL_LBA_m14_c39_lowgain)
Module LBC_m49 has ymax = 0 (TILECAL_LBC_m49_c27_lowgain)
Calibration values:[0.0] (not filtered out by the script, even though it should be) This seems to be a known issue fro DQ [cite]
LBC_m52 legend covers last two datapoints and getting rid of the legend does not work. Here are raw values for one of the channels: LBC_m52 [0.619210422039032, 0.6193860173225403, 0.6190910935401917, 0.6191729307174683, 0.619414210319519, 0.6191526055335999, 0.619326114654541, 0.6192055344581604, 1.2734897136688232, 1.273591160774231]


**Final Runs in Update:** 430900, 431285, 431304, 431313, 431374, 431570, 431991, 432218, 432548, 432824

**Final Command:** macros/cis/CIS_DB_Update.py --date '-31 days' --ldate 430900 431285 431304 431313 431374 431570 431991 432218 432548 432824 |&tee results/August_SeptemberCIS_FINAL.txt


**Channels in Update:**

**Odd Behaviour:** See `Odd Channel Behavior.xlsx` for catalogue of odd channel behavior. Please double check. **LBC 52** half-gain for some time; may need to recalibrate from the time when it is returned to low gain properly.

**Flag Updates:** See `Flag Updates.xlsx` for list of flags that need to be updated. They are taken from the `Odd Channel Behavior.xlsx` spreadsheet and marked in red.

**Recalibration:** See `Channels to Recalibrate.xlsx` for a list of channels that need to be recalibrated. They are taken from the `Odd Channel Behavior.xlsx` spreadsheet and marked in yellow. This spreadsheet provides the proper formatting to be read into the `toRecalibrate.txt` file.

**Summary Plots:** See folder `Summary-Plots`. 
