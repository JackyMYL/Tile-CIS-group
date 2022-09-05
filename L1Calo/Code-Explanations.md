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
