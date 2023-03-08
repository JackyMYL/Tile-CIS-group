import os, sys
sys.path.insert(0, os.getenv('TUCS','.'))
from src.oscalls import *
import argparse
from TileCalibBlobPython import TileCalibTools

parser = argparse.ArgumentParser(description=
'Creates the SQLite file for bulk reprocessings.',
formatter_class=argparse.RawTextHelpFormatter)

parser.add_argument('--sourcerun', action ='store', type=int, default=0,
                    required=True, help=
"Select run number from which you'd like \n\
to source the database constants used as \n\
the basis of your reprocessing. Must be \n\
in the form of a six-digit number smaller \n\
than the first IOV you are creating. \n \n")

parser.add_argument('--reprocessingstep', action ='store', type=int, default=0,
                    required=True, help=
"If reprocessing fails, or a change needs \n\
to be made, the macro can be set to start \n\
at any IOV of the reprocessing that has \n\
already been created. Takes an integer \n\
argument and defaults to zero. \n")

args = parser.parse_args()

sourcerun = int(args.sourcerun)
print sourcerun
reprocessingstep=args.reprocessingstep
print reprocessingstep

#First order of business, dig up the current tag for UPD1.
#The database and the folder are hardcoded but the global
#tag and thus the folder tag rotate and must be sourced 
#with getCurrent()

folder    = '/TILE/OFL02/CALIB/CIS/LIN'
folderTag = TileCalibTools.getFolderTag('COOLOFL_TILE/CONDBR2', folder, 'CURRENT')

#Create copy of COOL as local SQLite file named tileSqlite.db
#with one infinite IOV and constants from the run number
#specified by the -run argument.
if reprocessingstep==0:
    resDir=getResultDirectory()
    command1="""AtlCoolCopy.exe "oracle://ATLAS_COOLPROD;schema=ATLAS_COOLOFL_TILE;dbname=CONDBR2" \
              "sqlite://;schema={0}tileSqlite0.db;dbname=CONDBR2" \
              -create -f /TILE/OFL02/CALIB/CIS/LIN -t {1} -run {2} -alliov""".format(resDir, folderTag, sourcerun)
    os.system(command1)
    os.system("cp -i "+resDir+"tileSqlite0.db "+resDir+"tileSqlitePrelim.db")
    os.system("cp -i "+resDir+"tileSqlite0.db "+resDir+"tileSqlite1.db")
    reprocessingstep+=1
else:
    pass

months=['January','February','March','April','May','June','July','August','September','October','November','December']

#Read information for creating new IOVs
inputcommands = open(os.path.join(getResultDirectory(),'reprocessing_input.txt'),'r+')

#Parse info from reprocessing_input.txt to appropriate command line argument of update_cis_constants.py
for number, line in enumerate(inputcommands):
    argline=line.split('|')
    print argline
    month1=argline[0].split(' ')[0]
    month2=argline[1].split(' ')[0]

    if (month1 or month2) not in months:
    	print 'EPIC FAIL'
    else:
    	print 'Months are spelled correctly!'
    	pass
    datestart=argline[0]
    datefinish=argline[1]
    recalchans=argline[2]

    #If IOV does not contain channels to default
    if len(argline)==4:
        properiov=argline[3].strip('\n')
        runmacro="python macros/cis/update_cis_constants.py --date '{0}' '{1}'".format(datestart,datefinish)+\
            " --maintregions "+recalchans+" --forcedregions " \
            +recalchans+" --iov "+properiov+" --reprocessing " \
            +str(reprocessingstep)
    #If there are channels to default
    else:
        properiov=argline[3]
        defchans=argline[4].strip('\n')
        runmacro="python macros/cis/update_cis_constants.py --date '{0}' '{1}' --maintregions ".format(datestart, datefinish)\
                 +recalchans+" --forcedregions " \
                 +recalchans+" --defaulttargets "+defchans+" --iov "+properiov+" --reprocessing" \
                 +str(reprocessingstep)
    print runmacro
    os.system(runmacro)
    
    resDir=getResultDirectory();
    oldfilename = resDir+'tileSqlite{0}.db'.format(int(reprocessingstep)-1)
    newfilename = resDir+'tileSqlite{0}.db'.format(int(reprocessingstep))
    
    #only wants the last part of the tag for the comparison script
    tagabbrev="-".join(folderTag.split('-')[1:])
    update_diff="""cd {5}; ReadFromCoolCompare.py --run={0} --folder=/TILE/OFL02/CALIB/CIS/LIN --tag={4} \
               --schema=COOLOFL_TILE --sqlfn={1} --run2={2} --folder2=/TILE/OFL02/CALIB/CIS/LIN --tag2={4} \
               --schema2=COOLOFL_TILE --sqlfn2={3} --maxdiff=.001""".format(int(properiov)-1,oldfilename,int(properiov)+1,newfilename,tagabbrev,resDir)
    os.system(update_diff)
    diffFile=open(resDir+'output.ascii', 'r')
    updatedchannels=[]
    for linenumber, line in enumerate(diffFile):
        if linenumber>8:
            splitline=line.split(' ')[0:6] ##splitline is a channel name in an unusable format
            if '' in splitline:
                splitline.remove('')
            else:
                del splitline[-1]
            if splitline[-1]=='0':  ##lowgain channel
                if len(splitline[2])==1: ##single digit channel name, needs extra 0
                    channel='{0}_m{1}_c0{2}_{3}'.format(splitline[0][0:3],splitline[0][3:5],splitline[2],'lowgain')
                else:
                    channel='{0}_m{1}_c{2}_{3}'.format(splitline[0][0:3],splitline[0][3:5],splitline[2],'lowgain')
                updatedchannels.append(channel)
            elif splitline[-1]=='1': ##highgain channel
                if len(splitline[2])==1: ##single digit channel name, needs extra 0
                    channel='{0}_m{1}_c0{2}_{3}'.format(splitline[0][0:3],splitline[0][3:5],splitline[2],'highgain')
                else:
                    channel='{0}_m{1}_c{2}_{3}'.format(splitline[0][0:3],splitline[0][3:5],splitline[2],'highgain')
                updatedchannels.append(channel)
    diffFile.close()
    print updatedchannels
    counter=0
    if len(argline)==4:
        inputchannels=recalchans.split(' ')
    else:
        inputchannels=recalchans.split(' ')+defchans.split(' ')
    print inputchannels
    for inputchannel in inputchannels:
        if inputchannel in updatedchannels:
            counter+=1
            print counter
    if len(inputchannels) == counter:
        print 'All channels that have been selected for recalibration have received a new value. \
               Macro will now proceed to the next IOV in the input.txt file.'
        updatesqlname = "cp -i {0} {1}".format(oldfilename, newfilename)
        os.system(updatesqlname)
        reprocessingstep+=1
    else:
        raise Exception('\n\n Not all channels selected for recalibration are present in the comparison file. \n \
                         Check the output of the macro manually or try changing the --maxdiff option \n \
                         for the ReadFromCoolCompare.py worker to be more inclusive.') 
