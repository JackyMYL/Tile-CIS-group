import sys
import os
os.chdir(os.getenv('TUCS','.'))

exec(open('src/laser/laserGetOpt.py').read(), globals())
exec(open('src/laser/toolbox.py').read(), globals())

exec(open('src/load.py').read(), globals()) # don't remove this!

processors = []

#region = None
print region # at the monent: region has to be a cell that is part of EBA/C, and we only use C-side for now
name = LaserTools().getRegionName(region)
print name

str2 = None
str1=str(name[1][0]+1)
if len(name[1])==2:
    str2=str(name[1][1]+1)

string = ''
for i in range(1,65):
    helpstring = str(i)
    if i<10: helpstring = "0"+helpstring
    if i!=64:
        #string+='EBA_m'+helpstring+'_c'+str1+','
        string+='EBC_m'+helpstring+'_c'+str1+','
    	
        if str2:
            string+='EBC_m'+helpstring+'_c'+str2+','
            #string+='EBA_m'+helpstring+'_c'+str2+','
        #string+='EBA_m'+helpstring+'_c17,'
        string+='EBC_m'+helpstring+'_c17,'
        #string+='EBA_m'+helpstring+'_c18,'
        string+='EBC_m'+helpstring+'_c18,'
    else:
	#string+='EBA_m'+helpstring+'_c'+str1+','
        string+='EBC_m'+helpstring+'_c'+str1+','
    	
        if str2:
            string+='EBC_m'+helpstring+'_c'+str2+','
            #string+='EBA_m'+helpstring+'_c'+str2+','
        #string+='EBA_m'+helpstring+'_c17,'
        string+='EBC_m'+helpstring+'_c17,'
        #string+='EBA_m'+helpstring+'_c18,'
        string+='EBC_m'+helpstring+'_c18'
    
processors.append( Use(run=date, run2=enddate, runType='cesium', region=string,
                       cscomment='sol+tor', keepOnlyActive=True, TWOInput=twoinput,
                       allowC10Errors = True) )

processors.append( ReadCsFile(normalize=True, skipITC=True, verbose=False) )

				    
runs = []				    
runs.append(207490)
runs.append(209899)
runs.append(203027)#c
runs.append(210302)
runs.append(209787)#c
runs.append(212172)
runs.append(202668)#c
runs.append(204955)
runs.append(203277)
runs.append(209995)
runs.append(214777)
runs.append(207306)
runs.append(206248)
runs.append(203636)
runs.append(212144)
runs.append(209183)
runs.append(202798)#b
runs.append(214390)
runs.append(212967)
runs.append(215473)
runs.append(200863)#c#b
runs.append(202660)#b
runs.append(213900)
runs.append(203258)
runs.append(207696)
runs.append(206253)
				
run_type = "MBias"
selected_region = "EBA_m01_c12_highgain"
detectorRegion = region
side = 'C'

processors.append( Use(run=runs, region=selected_region, runType=run_type))	
processors.append( ReadMBias(doSingleRun=False, doRatio = True, modnum=64, detector_region=detectorRegion, detector_side=side))
processors.append( PlotRatioPMTsVsTime(modnum=64, detector_region=detectorRegion) )

processors.append( PlotCsMbias(channels=name) )

Go( processors )
