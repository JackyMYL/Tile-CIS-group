#!/usr/bin/env python
#Script by Gabriele Bertoli <gabriele.bertoli@fysik.su.se>

from bs4 import BeautifulSoup
import urllib
import sys

hash_file = '/afs/cern.ch/user/t/tilecali/w0/sqlfiles/Noise/cell_hash'
url       = 'http://zenis.dnp.fmph.uniba.sk/tile.html'

def read_table(url):
    '''Function to associate channels to cells.
    
    This function gets the channel, the pmt values and the cell name from the web url and 
    returns an array of dictionaries each containig channel value as key and cell name and 
    pmt value as values for the different modules.'''

    #Open the file and read the content
    ufile = urllib.urlopen(url)
    text  = ufile.read()

    #Parse the HTML code with BeautifulSoup and get the table
    soup  = BeautifulSoup(text)
    table = soup.find("table")

    #Define dictionaries for different modules
    LBA_LBC     = {}
    EBA_EBC     = {}
    EBA15_EBC18 = {}

    #Cycle over rows
    for row in table.findAll('tr'):
        cols = row.findAll('td')
        #fill the dictionaries with channel value as key and (pmt,cell name) as values
        if len(cols) < 8:
            continue
        else:
            LBA_LBC[str(cols[0].find(text=True))]     = (str(cols[1].find(text=True)),str(cols[2].find(text=True)))
            EBA_EBC[str(cols[3].find(text=True))]     = (str(cols[4].find(text=True)),str(cols[5].find(text=True)))
            EBA15_EBC18[str(cols[6].find(text=True))] = (str(cols[7].find(text=True)),str(cols[8].find(text=True)))

    #Save the dictionaries in one dictionary so we can return it
    dicts = {
        'a':LBA_LBC,
        'b':EBA_EBC,
        'c':EBA15_EBC18
        }

    return dicts

def read_hash(hash_file):
    '''Function to read the hash of the cell and to accociate it to the partition name and channel number.

    This function reads the hash file containing the hash for the cells and get for each the partition and 
    the channel numbers, then associate them to the cell name.'''

    #Read each line in the file
    lines = open(hash_file).readlines()

    hash_part_chan_mod_tow = []
    
    #Get from the lines the cell hash, partition and channel number
    for line in lines:
        if len(line.strip()) == 0:
            continue
        hash = line.split()[1]
        part = line.split()[3].split('/')[2]
        chan = line.split()[3].split('/')[4]
        mod  = line.split()[3].split('/')[3]
        tow  = line.split()[5].split('/')[4]

        #Save the tuple in a list
        hash_part_chan_mod_tow.append((hash,part,chan,mod,tow))

    return hash_part_chan_mod_tow

def give_cellName(hash):
    '''Function to find the cell name.

    This function returns the cell name given the hash number.'''
    
    #Call the partition dictionaries and cell hardware id
    LBA_LBC     = read_table(url)['a']
    EBA_EBC     = read_table(url)['b']
    EBA15_EBC18 = read_table(url)['c']
    cell_id     = read_hash(hash_file)

    #Loop over cells
    for cell in cell_id:

        if (int(cell[0]) == hash):

            print hash

            #If partition is LBA or LBC get corresponding cell name
            if (int(cell[1]) == 1):
                cell_name = "partition %s, module %s, name %s, tower %s"
                return cell_name  % ("LBA",cell[3],LBA_LBC[cell[2]][1],cell[4])
            elif (int(cell[1]) == 2):
                cell_name = "partition %s, module %s, name %s, tower %s"
                return cell_name  % ("LBC",cell[3],LBA_LBC[cell[2]][1],cell[4])
            
            #If partition is EBA or EBC get corresponding cell name
            elif (int(cell[1]) == 3):
                #This module is special
                if (int(cell[3]) == 15):
                    cell_name = "partition %s, module %s, name %s, tower %s"
                    return cell_name  % ("EBA15",cell[3],EBA15_EBC18[cell[2]][1],cell[4])
                else:
                    cell_name = "partition %s, module %s, name %s, tower %s"
                    return cell_name  % ("EBA",cell[3],EBA_EBC[cell[2]][1],cell[4])
            else:
                #This module is special
                if (int(cell[3]) == 18):
                    cell_name = "partition %s, module %s, name %s, tower %s"
                    return cell_name  % ("EBC18",cell[3],EBA15_EBC18[cell[2]][1],cell[4])
                else:
                    cell_name = "partition %s, module %s, name %s, tower %s"
                    return cell_name % ("EBC",cell[3],EBA_EBC[cell[2]][1],cell[4])

def is_bad_channel(partition,module,channel):
    '''Function to find always off channels.

    This function returns true if the channel is one of those that are always off and forever will.'''

    #Call the dictionaries
    LBA_LBC     = read_table(url)['a']
    EBA_EBC     = read_table(url)['b']
    EBA15_EBC18 = read_table(url)['c']



    
    if ((partition == 'LBA' or partition == 'LBC') and LBA_LBC[str(channel)][1] == "None"): 
#        print "here LBA"
        return True

    elif (partition == 'EBA' and (int(module) == 15 and EBA15_EBC18[str(channel)][1] == "None")): 
#            print "here EBA"
            return True

    elif (partition == 'EBA' and EBA_EBC[str(channel)][1] == "None"):
#            print "here EBA_EBC"
            return True

    elif (partition == 'EBC' and (int(module) == 18 and EBA15_EBC18[str(channel)][1] == "None")): 
#            print "here EBC"
            return True

    elif (partition == 'EBC' and EBA_EBC[str(channel)][1] == "None"):
#        print partition, module, channel
        return True

    else:
#        print "here False"
        return False    

def get_cellName(part, mod, ch):

    #Call the dictionaries
    LBA_LBC     = read_table(url)['a']
    EBA_EBC     = read_table(url)['b']
    EBA15_EBC18 = read_table(url)['c']

    if(part == 'LBA' or part == 'LBC'):

        if '-' in LBA_LBC[str(ch)][1]:
        
            return LBA_LBC[str(ch)][1][:-2]

        else:

            return LBA_LBC[str(ch)][1]

    if(part == 'EBA' or part == 'EBC'):

        if(mod == 15 or mod == 18):

            if '-' in EBA15_EBC18[str(ch)][1]:

                return EBA15_EBC18[str(ch)][1][:-2]

            else:

                return EBA15_EBC18[str(ch)][1]

        else:

            if '-' in EBA_EBC[str(ch)][1]:

                return EBA_EBC[str(ch)][1][:-2]

            else:

                return EBA_EBC[str(ch)][1]
    
 
def main():

    #Call the dictionaries
    LBA_LBC     = read_table(url)['a']
    EBA_EBC     = read_table(url)['b']
    EBA15_EBC18 = read_table(url)['c']

    #Print a table with the values
    print '{0:*^38}'.format(' LBA - LBC '), '{0:*^38}'.format(' EBA - EBC '), '{0:*^38}'.format(' EBA15 - EBC18 ')
    print '{0:-^38}'.format('-'), '{0:-^38}'.format('-'), '{0:-^38}'.format('-')
    print '{0:^10}'.format('Cell Name'), '|', '{0:^10}'.format('Channel'), '|', '{0:^10}'.format('PMT'), '|', \
        '{0:^10}'.format('Cell Name'), '|', '{0:^10}'.format('Channel'), '|', '{0:^10}'.format('PMT'), '|', \
        '{0:^10}'.format('Cell Name'), '|', '{0:^10}'.format('Channel'), '|', '{0:^10}'.format('PMT'), '|'
    
    for key in sorted(LBA_LBC, key = lambda key: int(key)):
        print '{0:<10}'.format(LBA_LBC[key][1]), '|', '{0:>10}'.format(key), '|', '{0:>10}'.format(LBA_LBC[key][0]), '|', \
            '{0:<10}'.format(EBA_EBC[key][1]), '|', '{0:>10}'.format(key), '|', '{0:>10}'.format(EBA_EBC[key][0]), '|', \
            '{0:<10}'.format(EBA15_EBC18[key][1]), '|', '{0:>10}'.format(key), '|', '{0:>10}'.format(EBA15_EBC18[key][0]), '|'

    
if __name__ == '__main__':
    main()
