##########################################################################################################################
# Author: Andry Kamenshchikov <akamensh@cern.ch>
#
# 23.11.2013
#
# Functionality:
#	Producing the time dependences for each pmt in cesium runs
#
##########################################################################################################################

import os, sys, getopt
import _mysql
os.chdir(os.getenv('TUCS','.'))
exec(open('src/load.py').read(), globals()) # don't remove this!

processors = []

processors.append( Use(run='2012-01-01', run2='2012-12-31', region='LBC', TWOInput=True, runType='cesium', cscomment='sol+tor') ) #region='LBC_m19', 

processors.append( ReadCsFile(processingDir="/afs/cern.ch/user/t/tilecali/w0/ntuples/cs",normalize=True) )

##processors.append( ReadProblemChFromCool(schema="sqlite://;schema=tileSqlite.bch.db;dbname=CONDBR2",folder="/TILE/OFL02/STATUS/ADC",tag="RUN2-UPD4-08", storeADCinfo=True) )

processors.append( time_evolution_plots() ) #restricted_prod=False

##processors.append( time_evolution_plots_mconvoluted() )

processors.append( Print() )

Go(processors)


