# Instructions related to the laser calibration code

## PMT response to the laser pulses as a function of time

The macro used to plot the PMT evolution is `macros/laser/laser_DQ-combined-method.py`. To run, do:

```
python macros/laser/laser_DQ-combined-method.py --date=2018-06-01 --enddate=2018-06-10 --outputTag myTest
```

With this command you produce the PMT evolution plots from 1st to 10th June 2018. All the plots are inside `plots/myTest` folder. In the same folder you can also find the plots of the evolution of the fiber and global corrections. The same plots are saved in a .root file (`Tucs.HISTmyTest.root`) inside the `results` directory.

The macro can be run also with additional flags, a brief description can be found by running:
`python macros/laser/laser_DQ-combined-method.py --help`


## Calculating laser constants and writing them to an Sqlite file

The macro used to produce the tilesqlite.db file and the Tile cell map with the constants is `macros/laser/laser_autocalib.py`. To run, do:

```
python macros/laser/laser_autocalib.py --first 364147 --correctHV --outputTag myTest2
```

With this command you create the `results/tilesqlite-364147_myTest2.db` Sqlite file with the laser constants determined using the run 364147 data. 
The Tile map with average PMT drifts per cell type should look like the one exemplified in `data/laser/tile_laser_map.pdf`.


## Calculating laser reference values and writing them to an Sqlite file

The PMT signal reference and the PMT gain reference are calculated to evaluate the laser reference values.The used macro is `scripts/mk-las-ref-combined.sh` and to run it, do:

```
source scripts/mk-las-ref-combined.sh
``` 

The mk-las-ref-combined.sh script will use `macros/laser/laser_stab_references_PMTgain.py` macro to evaluate the PMT gain reference and `macros/laser/laser_stab_references.py` macro to evaluate the PMT signal reference. Keep in mind that the PMT gain reference is the average PMT gain value evaluated two weeks before the PMT signal reference.


## Compute a history plot for the global time variation

The macro used to compute the history plot for the global time variation is `macros/laser/laser_DQ-Time.py`. The macro is used to  make this type of [plots](https://hwilkens.web.cern.ch/hwilkens/Tucs/plots/latest/Time.pdf).