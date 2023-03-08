# Author: Christopher Tunnell <tunnell@hep.uchicago.edu>
#
# March 04, 2009
#

import os, sys, datetime

def getPlotDirectory(subdir=None):
    topdir = os.getenv('TUCSPLOTS', 'plots')
    if subdir is not None:
        subdir=subdir.replace(".","") if subdir.startswith(".") else subdir #remove "." if they exist
        topdir=os.path.join(topdir,subdir)
    latest = '%s/latest' % topdir
    date = datetime.date.today().strftime('%Y_%m_%d')
    pdir = '%s/%s' % (topdir,date)
    createDir(pdir)
    if os.path.exists(latest):
        os.unlink(latest)
    os.symlink(date, latest)
    return pdir
    
    
def getResultDirectory(subdir=""):
    rdir = os.path.join(os.getenv('TUCSRESULTS', 'results'),subdir,"")
    try:
        if not os.path.isdir(rdir):
            os.makedirs(rdir)
    except:
        print(("Error creating directory: %s" % rdir))
    return rdir
    
    
def getTucsDirectory(subdir=""):
    tdir = os.path.join(os.getenv('TUCS', '.'),subdir,"")
    return tdir
    
    
def createDir(name):
    try:
        if not os.path.isdir(name):
            os.makedirs(name)
    except:
        print(("Error creating directory: %s" % name))
