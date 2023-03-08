from src.ReadGenericCalibration import ReadGenericCalibration
from workers.noise import NoiseWorker
from src.oscalls import *

class ReadACRNoiseFile(ReadGenericCalibration,NoiseWorker):
    '''
    Reads ACR constants from text file.
    Format of file: Partition Channel acr[0] acr[1] acr[2] acr[3] acr[4] acr[5]
    '''

    def __init__(self):
        self.type='readout'
       
    def get_index(self, side, mod, samp, tower, gain):
        return side *64*4*17*6\
            + mod      *4*17*6\
            + samp       *17*6\
            + tower         *6\
            + gain

    def ProcessStart(self):
        self.acrValues = []
        gain = 0

        for part in range(0,5):
            self.acrValues.append([])
            for ch in range(0,48):
                self.acrValues[part].append([0.0,0.0])

        for file in ['acrLG.txt','acrHG.txt']:
            inFile = open(os.path.join(getResultDirectory(),file),'r')
            for line in inFile:
                # Skip comments
                if line[0] == '#': continue
                    # split line into list of fields
                lineHash = line.split()
                # skip empty fields
                if len(lineHash) < 8:
                    continue
            
                # Fill dictionary with value dict[partition][channel]
                self.acrValues[int(lineHash[0])][int(lineHash[1])][gain] = tuple([float(lineHash[2]),float(lineHash[3]),float(lineHash[4]),float(lineHash[5]),float(lineHash[6]),float(lineHash[7])])
                
            inFile.close()
            gain += 1
        print('ACR constants read from file')
            
        
    def ProcessStop(self):
        pass
        
    def ProcessRegion(self, region):
        if region.GetEvents() == 0:
            return
        
        if 'gain' not in region.GetHash():
            return

        for event in region.GetEvents():
            if event.run.runType != 'Ped':
                continue
            
            hash = region.GetHash()
            [part, mod, ch, gain] = region.GetNumber()
            print('Filling acr noise constants for: ', part,ch,gain)
            for i in range(6):
                event.data['autocorr'+str(i)+'_db'] = self.acrValues[part][ch][gain][i]
        
            # FIXME
            # Make db values and non-db values the same to ensure 
            # that values from input file are propagated to DB
            dbList = [ d for d in list(event.data.keys()) if '_db' in d ]
            for datum in dbList:
                print('Copying: ',datum,event.data[datum])
                event.data[datum[:-3]] = event.data[datum]
