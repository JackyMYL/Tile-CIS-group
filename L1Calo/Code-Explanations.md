# triggerHistory.py

[9-10] Import files  
[11-12] Change directories to access TUCS framework, executed program    
[14-53] Define parser arguments, read in to use later in code (use dates or list of run numbers). It can optionally produce plots.   
[56-78] Formats date or run number arguments.   
[92-117] Prepare process list to be given to "Go": Use, HistoryTrigger, ReadBchFromCool, CopyLocalChanStat, WriteChanStat (it takes in optional flags about run type, run list,folders).    

# triggerTest.py
[9-10] Import files.   
[11-12] Change directories to access TUCS framework, executed program.   
[13-35] Parse arguments related to single run: run number, gain cuts.   
      -- what are the gain cuts? how are they used?    
[66-73] Define process list for macros:   
`Use(run=runList,runType='L1Calo')`:   
`ReadTriggerChannelFile(processingDir=inputDir)`:   
`DefineTriggerCuts(zeroGainCutValue = zeroGain, lowGainCutValue = lowGain)`:   
`PrintTriggerBadChannels(zeroGainCutValue = zeroGain, lowGainCutValue = lowGain)`:    
-- how does it interface with the plotting scripts?    

Need to still look at all of the subdependencies to see how they operate   

# DefineTriggerCuts.py
I'm not sure what the units are in the histogram x-axes. What is it plotting? Canwe somehow add a summary statistics box, or is this information somehow otherwise accessible?

# PrintBadChannels.py
These plot histograms of the channels under different gain conditions and whether they are bad in L1Calo or Tile or both, for example. This has been edited to display gridlines for readability.

#L1Calo Twiki Experts

* `./bob_dump 228863 0 10 x` instead of `bob_dump 228863 0 10 x` (changed in twiki)
* We should use an example run that is actuall present in the examples so that the code will actually run step-by-step easily
* "Copy here the jobOptions_TileCalibRec.py from the tile beam account (updated August 2016):" There's no quick two lines of code in this file as the subsequent commands suggest. I'm not sure to what it is referring. 
* `asetup 17.4.0,builds,here,slc5
cmt co TileCalorimeter/TileCalib/Tucs 
cd TileCalorimeter/TileCalib/Tucs`: Needs to be changed (not too simple to just change the version). Ask Sasha. We have most of the Tucs environment already installed for CIS work, but there are a few extra folders for L1Calo . Will the verisons compete?
* We don't get the following directories (we have a different directory structure; I'm not sure if it's to do with Tucs version of specific L1Calo problems): ChangeLog         README     TreeMaker.py  data  macros   src NTupleTranslator  TileGUI.C  cmt           doc   scripts  workers
* The commands properly make a root file.it does not update it in the tilebeam account (probably because of permissions). Error:`Run 307771 was not found on EOS`
* `cmt co TileCalorimeter/TileCalib/Tucs 
cd TileCalorimeter/TileCalib/Tuc` following the Athena setup do not correspond to the current version. How do we fix this? (for Sasha).
* The macro scripts seem to run fine running them anyways. I'm not sure what the difference is if the above does not work.


 ## Commands and Errors
 [pcampore@lxplus767 Tucs]$ asetup 20.7.7.6, here
manpath: warning: $MANPATH set, prepending /etc/man_db.conf
Using AtlasProduction/20.7.7.6 [cmt] with platform x86_64-slc6-gcc49-opt
        at /cvmfs/atlas.cern.ch/repo/sw/software/x86_64-slc6-gcc49-opt/20.7.7
Test area: /afs/cern.ch/user/p/pcampore/Tucs
manpath: warning: $MANPATH set, ignoring /etc/man_db.conf
Unchanged: COOL_ORA_ENABLE_ADAPTIVE_OPT=Y
***
[pcampore@lxplus767 Tucs]$ pkgco.py TileCalibAlgs-00-05-52-branch
#CMT---> Info: Working on TileCalorimeter/TileCalib/TileCalibAlgs (TileCalibAlgs-00-05-52-branch)
svn: E210002: Unable to connect to a repository at URL 'svn+ssh://svn.cern.ch/reps/atlasoff/TileCalorimeter/TileCalib/TileCalibAlgs/tags/TileCalibAlgs-00-05-52-branch'
svn: E210002: To better debug SSH connection problems, remove the -q option from 'ssh' in the [tunnels] section of your Subversion configuration file.
svn: E210002: Network connection closed unexpectedly
svn: E210002: Unable to connect to a repository at URL 'svn+ssh://svn.cern.ch/reps/atlasoff/TileCalorimeter/TileCalib/TileCalibAlgs/branches/TileCalibAlgs-00-05-52-branch'
svn: E210002: To better debug SSH connection problems, remove the -q option from 'ssh' in the [tunnels] section of your Subversion configuration file.
svn: E210002: Network connection closed unexpectedly
svn: E210002: Unable to connect to a repository at URL 'svn+ssh://svn.cern.ch/reps/atlasoff/TileCalorimeter/TileCalib/TileCalibAlgs/devbranches/TileCalibAlgs-00-05-52-branch'
svn: E210002: To better debug SSH connection problems, remove the -q option from 'ssh' in the [tunnels] section of your Subversion configuration file.
svn: E210002: Network connection closed unexpectedly
#CMT---> Error: execution failed: python /cvmfs/atlas.cern.ch/repo/sw/software/x86_64-slc6-gcc49-opt/20.7.7/CMT/v1r25p20160527/mgr/cmt_svn_checkout.py  --without_version_directory -r TileCalibAlgs-00-05-52-branch TileCalorimeter/TileCalib/TileCalibAlgs
Traceback (most recent call last):
  File "/cvmfs/atlas.cern.ch/repo/sw/software/x86_64-slc6-gcc49-opt/20.7.7/AtlasProduction/20.7.7.6/InstallArea/share/bin/pkgco.py", line 254, in <module>
    sys.exit(main())
  File "/cvmfs/atlas.cern.ch/repo/sw/software/x86_64-slc6-gcc49-opt/20.7.7/AtlasProduction/20.7.7.6/InstallArea/share/bin/pkgco.py", line 248, in main
    map(safe_checkout, args)
  File "/cvmfs/atlas.cern.ch/repo/sw/software/x86_64-slc6-gcc49-opt/20.7.7/AtlasProduction/20.7.7.6/InstallArea/share/bin/pkgco.py", line 185, in safe_checkout
    checkout(*args)
  File "/cvmfs/atlas.cern.ch/repo/sw/software/x86_64-slc6-gcc49-opt/20.7.7/AtlasProduction/20.7.7.6/InstallArea/share/bin/pkgco.py", line 165, in checkout
    shell=True)
  File "/cvmfs/atlas.cern.ch/repo/sw/software/x86_64-slc6-gcc49-opt/20.7.7/sw/lcg/releases/LCG_81e/Python/2.7.9.p1/x86_64-slc6-gcc49-opt/lib/python2.7/subprocess.py", line 540, in check_call
    raise CalledProcessError(retcode, cmd)
subprocess.CalledProcessError: Command 'cmt co -r TileCalibAlgs-00-05-52-branch TileCalorimeter/TileCalib/TileCalibAlgs' returned non-zero exit status 1
[pcampore@lxplus767 Tucs]$
