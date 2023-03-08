import os

def getContents( dir ):

    contents = []

    if( dir[-1] == '/' ):
        dir = dir[0:-1]

    for file in os.listdir( dir ):
        f = dir + "/" + file
        if( os.path.isdir( f ) ):
            contents += getContents( f )
        elif( True ): #file.find('root') != -1 and file.find('D3PD.D3PD') != -1 ):
            contents += [ f ]

    return contents

if __name__ == "__main__":

    print getContents("/home/cjmeyer/data")
