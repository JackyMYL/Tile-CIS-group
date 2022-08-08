# August CIS Notes

**Initial Command**: macros/cis/CIS_DB_Update.py --date 'July 14, 2022' 'August 8, 2022'|&tee AugustCIS.txt

**Initial Runs**: 428271, 428437, 428535, 428588, 428791, 429095, 429224, 429253, 429493, 429511, 429799, 429890, 429948, 430406, 430444

run  [428271, 'CIS', '2022-07-14 10:45:55,2022-07-14 10:47:22']

run  [428437, 'CIS', '2022-07-15 16:08:21,2022-07-15 16:09:45']

run  [428535, 'CIS', '2022-07-17 09:00:32,2022-07-17 09:01:59']

run  [428588, 'CIS', '2022-07-18 11:27:40,2022-07-18 11:29:12']

run  [428791, 'CIS', '2022-07-21 10:40:18,2022-07-21 10:41:53']

run  [429095, 'CIS', '2022-07-25 08:09:36,2022-07-25 08:11:10']

run  [429224, 'CIS', '2022-07-26 12:37:02,2022-07-26 12:38:11']

run  [429253, 'CIS', '2022-07-26 14:12:08,2022-07-26 14:13:26']

run  [429493, 'CIS', '2022-07-28 09:31:54,2022-07-28 09:33:22']

run  [429511, 'CIS', '2022-07-28 10:26:09,2022-07-28 10:27:28']

run  [429799, 'CIS', '2022-08-01 08:05:26,2022-08-01 08:06:52']

run  [429890, 'CIS', '2022-08-01 11:32:14,2022-08-01 11:33:33']

run  [429948, 'CIS', '2022-08-01 23:58:32,2022-08-02 00:00:07']

run  [430406, 'CIS', '2022-08-05 15:31:08,2022-08-05 15:32:38']

run  [430444, 'CIS', '2022-08-05 16:17:23,2022-08-05 16:18:35']

**AmpQ and Timing Plots:**
All of the AmpQ plots look realtively flat. There are no outliers that I can see, so all runs should be included from this perspective.
All of the Timing plots do not have the standard timing range $[-10,15]$ (or even shifted by $\pm25$ ns). The timing range is roughly $[-5,20]$ or $[0,25]$ (not consistent even within a run for most cases). We should **email Henric and/or Sasha** about this ASAP and confirm our understanding of what the timing plots actually mean! What is most concerning is actually that LBA mean is consistently around $\approx15$, while mean timing for LBC, EBA, and EBC is $\approx10$.
