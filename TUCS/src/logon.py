# Author: Christopher Tunnell <tunnell@hep.uchicago.edu>
#
# This is the script that gets run to setup an interactive
# python environment
#
# February 02, 2009
#

import os
os.chdir(os.getenv('TUCS','.'))
exec(compile(open('src/load.py').read(), 'src/load.py', 'exec'), globals()) # don't remove this!
print('Welcome to Tucs')
