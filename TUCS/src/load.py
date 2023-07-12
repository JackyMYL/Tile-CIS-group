#
# Author: Christopher Tunnell <tunnell@hep.uchicago.edu>
#
# March 04, 2009
#
#######################################################
# July, 2011 Henric: Fixed for python 2.6, now using _mysql from release ( lcg/external/pytools )
#
# This loads everything from features and calibrations
#from __future__ import print_function
import os, sys, string, fnmatch, time

# Make sure os.getlogin works in cron jobs as well
import pwd
os.getlogin = lambda: pwd.getpwuid(os.getuid())[0]

_argv = sys.argv        # Hide this programs command line arguements
sys.argv = sys.argv[:1] # from ROOT

# Setup the PythonPath to include the Tucs modules and MySQL modules
sys.path.insert(0, '.')

atlasversion = os.environ.get('AtlasVersion')
cmtconfig = os.environ.get('CMTCONFIG')

if atlasversion==None:
    print("Setup ATLAS environment before running TUCS")
    exit()
    
if sys.version_info[:1][0]==2: # python 2
    # Please contact me (Henric) if you feel you have to change something in the lines below
    if  int(atlasversion.split('.')[0])>21: # Release 22
        mysqlversion = '5.7.26'
        lcgreleasebase = os.environ.get('LCG_RELEASE_BASE')
        lcgplatform = os.environ.get('LCG_PLATFORM')
        if lcgplatform not in ['x86_64-centos7-gcc8-opt']:
            print("This Release doesn't support the %s platform" % lcgplatform)
            exit()

        mysqlpath = '%s/LCG_96/mysql/%s/%s/lib/'%( lcgreleasebase, mysqlversion, lcgplatform)

    elif  int(atlasversion.split('.')[0])>20: #release 21
        mysqlversion = '5.7.11'
        lcgreleasebase = os.environ.get('LCG_RELEASE_BASE')
        lcgplatform = os.environ.get('LCG_PLATFORM')
        mysqlpath = '%s/LCG_87/mysql/%s/%s/lib/'%( lcgreleasebase, mysqlversion, lcgplatform)
    
    if not mysqlpath in sys.path:
        sys.path.insert(0, mysqlpath )
    if not mysqlpath in os.environ['LD_LIBRARY_PATH']:
        os.environ['LD_LIBRARY_PATH'] += ":"+mysqlpath
        os.execve(os.path.realpath(__file__), _argv, os.environ)

    # Obsolete
    # elif  int(atlasversion.split('.')[0])< 17:
    #     # Release 16, python 2.6
    #     pythonversion = '2.6'
    #     mysqlversion = '1.2.3'
    #     sys.path.insert(0, '/afs/cern.ch/user/t/tilebeam/scratch0/MySQL-python-%s/build/lib.linux-%s-%s' % (mysqlversion,cmtconfig.split('-')[0],pythonversion))

    # elif  int(atlasversion.split('.')[0])< 16:
    #     # Release 15 and older
    #     pythonversion = '2.5'
    #     mysqlversion = '1.2.2'
    #     sys.path.insert(0, '/afs/cern.ch/sw/lcg/external/pytools/1.4_python%s/%s/lib/python%s/site-packages/' % (pythonversion,cmtconfig,pythonversion))





try:
    import ROOT
    
    print('Setting root in batch mode')
    ROOT.gROOT.SetBatch()   # Run in batch mode since we don't need X    
    ROOT.gROOT.ProcessLine("gErrorIgnoreLevel = 1001;")
    try:   # loads shared libraries
        ROOT.gInterpreter.EnableAutoLoading()
    except:  # Doesn't work in latest ROOT version
        pass
    try:
       # ROOT5
       import PyCintex
    except:
       # ROOT6
       import cppyy as PyCintex
       sys.modules['PyCintex'] = PyCintex

except ImportError:
    print("FATAL ERROR: You need to setup Athena/ROOT before proceeding")
    sys.exit(-1)


#from optparse import OptionParser

# Load all python files in the directory passed
def execdir(dir, scope):
    for path, dirs, files in os.walk(dir):
        for py in [os.path.abspath(os.path.join(path, filename)) for filename in files if fnmatch.fnmatch(filename, '*.py')]:
            # this file is used by python, but not of interest to us 
            if '__init__.py' in py or '#' in py or '~' in py or '._' in py:
                continue
            #os.system("pwd")
            ts = time.time()
            exec(open(py).read(), scope)
            te = time.time()
            #print(py, " ",1000.*(te-ts),"ms")

execdir('workers', globals())
from src.go import *
sys.argv = _argv
del _argv
