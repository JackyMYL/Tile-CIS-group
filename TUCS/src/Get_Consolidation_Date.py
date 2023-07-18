#############################################################################################
# Author : Jeff Shahinian                                                                   #
# Date   : November 6, 2013                                                                 #
#                                                                                           #
# The GetConsDate function takes a module as its input and retrieves the date of its        #
# consolidation. The output is the module's consolidation date in the form: 'YYYY-MM-DD'    #
#                                                                                           #
# The IsModCons function checks to see if a specified module has been consolidated or not.  #
# Returns True if module is consolidated and False if module is not consolidated or if the  #
# input region is in the wrong format.                                                      #
#############################################################################################

#import _mysql
import sys
mypath="/afs/cern.ch/user/t/tilebeam/offline/lib/python%d.%d/site-packages" % sys.version_info[:2]
sys.path.append(mypath)
import pymysql


def GetConsDate(region):
    # Expects input in form 'TILECAL_EBA_m01_c01_highgain' or 'EBA_m01_c01_highgain'
    # No channel or gain specification is necessary, but a module number must me given
    # i.e. 'EBA_m01' will work but 'EBA' will not

    mysqldb=pymysql.connect(host='pcata007.cern.ch', user = 'reader', db = 'maintenance')
    
    if 'm' in region: #Check to see if a specific module has been passed to the function
        # Format the input so it is compatible with the information stored in TileLS1Status
        if 'TILECAL' in str(region):
            module = str(region)[8:]
            module = module[:7]
        else:
            module = str(region)[:7]
        module = module.replace("_m", "")

        # Retrieve the consolidation date as it is recorded in TileLS1Status (https://tilecal.web.cern.ch/tilecal/TileLS1Status/current/index.php)
        mysqldb.query("SELECT servicesdate FROM maintenance WHERE drawer = '%s'" % (module,))
        cons_date = mysqldb.store_result()
        # Format the output into the form 'YYYY-MM-DD'
        cons_date = str(cons_date.fetch_row()[0][0])
        cons_date = cons_date[:10]
        
        if cons_date != '0000-00-00':
            print(module, 'Consolidated on:', cons_date)
        return cons_date
    else:
        cons_date = ''
        print('REGION INPUT TO THE GETCONSDATE FUNCTION IS IN WRONG FORMAT \n\
MAKE SURE INPUT SPECIFIES A MODULE NUMBER \n\
OUTPUT IS AN EMPTY STRING \n\
INPUT WAS %s' % region)
         
        return cons_date


def IsModCons(region):
    # Expects the same input as described above for the GetConsDate function
    # Retrieve the consolidation date recorded in TileLS1Status:
    cons_date = GetConsDate(region)
    
    # If the module is listed as unconsolidated, return False:
    if cons_date == '0000-00-00':
        print('%s IS NOT CONSOLIDATED' % region)
        #print 'RETURNING FALSE'
        return False
    
    # If the input region is in wrong format, return False:
    elif cons_date == '':
        print('REGION INPUT TO THE GETCONSDATE FUNCTION IS IN WRONG FORMAT \n\
MAKE SURE INPUT SPECIFIES A MODULE NUMBER \n\
RETURNING FALSE \n\
INPUT WAS %s' % region)
        return False
    
    # If module is listed as consolidated, return True:
    else:
        print('%s IS CONSOLIDATED' % region)
        #print 'RETURNING TRUE'
        return True



