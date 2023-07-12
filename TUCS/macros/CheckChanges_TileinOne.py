##########################################################################################################################
# Author: Andry Kamenshchikov <akamensh@cern.ch>
#
# 03.06.2013
#
# Functionality:
#	Iplementation of CheckChanges.py for Tile-in-ONE
#
# Options:
#	h(help):    help.
#	n(number):  Run's number.
#       t(type):    Run's type ('Las' by default; can be 'cesium', 'CIS')
#	f(filter):  Filter position for Use.py macros ('6' or '8').
#	r(region):  Region name (in format XXX_mYY_cZZ: XXX=[EBA,EBC,LBA,LBC], YY=[1-64],
#                   ZZ=[0-47]; example: EBC_m31_c36)
#	w(warnThr):     ERROR threshold (any user-given float)
#	e(errorThr):    WARNING threshold (any user-given float)
#       1(key1):    first key for CheckChanges.py (from: ReadLaserHV_DCS.py ReadLaserHV_REF.py
#                   ReadLaser.py or ReadLaserHV_COOL.py)                                        
#       2(key2):    second key for CheckChanges.py
#       d(draw):    flag for drawing picture
#       p(print):   flag for printing information about problematic regions in file
#       s(sepPlots):flag for print each(requested) partition on the separate plot
#
#       Call example:
#            python macros/CheckChanges_TileinOne.py -n 220567 -f 6 -r EBC_m37_c00 -w 2 -e 10 -1 "HV" -2 "HV_REF" -d -p -s
#
# More information about used workers in presentation:
#   https://indico.cern.ch/getFile.py/access?contribId=8&resId=0&materialId=slides&confId=238219   
#
##########################################################################################################################

import os, sys, getopt
import _mysql
os.chdir(os.getenv('TUCS','.'))
exec(open('src/load.py').read(), globals()) # don't remove this!

letters = "hn:f:r:w:e:1:2:dpt:s"
keywords = ["help","number=","filter=","region=","warnThr=","errorThr=","key1=","key2=","draw","print","type=","sepPlots"]

def usage():
    print 'Usage %s [options]' % sys.argv[0]
    for option in keywords:
        if option.find('=')>0:
            print '--%svalue' % option
        else:
            print '--%s' % option


try:
    opts, extraparams = getopt.getopt(sys.argv[1:],letters,keywords)
except getopt.GetoptError, err:
    print str(err)
    usage()
    sys.exit(2)

filt_pos = ' '
region = None
number=[]
warnThr=0
errorThr=0
key1=''
key2=''
draw=False
Print=False
Type='Las'
separate=False


for o, a in opts:
    if o in ("-f", "--filter"):
        filt_pos = a
    elif o in ("-n","--number"):
        number.append(int(a))
        print "Run number: ", number
    elif o in ("-r","--region"):
        region = a
        print "Using region: ",region
    elif o in ("-h","--help"):
        usage()
        sys.exit(2)
    elif o in ("-w","--warnThr"):
        warnThr=a
        print "WARNING threshold: ", warnThr
    elif o in ("-e","--errorThr"):
        errorThr=a
        print "ERROR threshold: ", errorThr
    elif o in ("-1","--key1"):
        key1=a
        print "Key1: ", key1
    elif o in ("-2","--key2"):
        key2=a
        print "Key2: ", key2
    elif o in ("-d","--draw"):
        draw=True
    elif o in ("-p","--print"):
        Print=True
    elif o in ("-t","--type"):
        Type=a
        print "Run's type: ",Type
    elif o in ("-s","--sepPlots"):
        separate=True
    else:
        assert False, "unhandeled option"

a = ReadLaserHV_DCS()
b = ReadLaserHV_COOL()
c = ReadLaserHV_REF()
d = ReadLaser(diode_num_lg=0, diode_num_hg=0)

keyDict={"DCS_HV_PREV":a,"DCS_HV_NEXT":a,"COOL_HV_PREV":b,"COOL_HV_NEXT":b,"HV_REF":c,"HV":d}
processors = []

processors.append( Use(number, filter=filt_pos, runType=Type,
                       region=region) )
if keyDict.has_key(key1):
    if keyDict[key1] not in processors:
        processors.append(keyDict[key1])
else:
    assert False, "Incorrect key1"

if keyDict.has_key(key2):
    if keyDict[key2] not in processors:
        processors.append(keyDict[key2])
else:
    assert False, "Incorrect key2"

processors.append(CheckChanges(key1,key2,int(warnThr),int(errorThr),draw,Print,separate))

Go(processors)


