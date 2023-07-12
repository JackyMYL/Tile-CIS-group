from workers.noise.NoiseWorker import NoiseWorker

class CompareConstants(NoiseWorker):
    '''
    Compares noise values from 2 different DBs.
    Noise values outside some fractional tolerance
    are printed to std out.
    '''

    def __init__(self,type='readout',tolerance=0.0001):
        self.initLog()
        self.nDiff=0
        self.type = type
        self.tolerance = tolerance

    def ProcessStart(self):
        pass

    def ProcessStop(self):
        print('Number of regions with constants differing: ',self.nDiff)
            
    def ProcessRegion(self, region):
        if len(region.GetEvents()) == 0:
            return
           
        diff = 0
        # Gather data values from each DB event
        for event in region.GetEvents():
            if event.run.runType == 'Ped':
                for p in event.data:
                    if p=='region': continue
                    if not p.endswith('2'):
                        # Do the Comparison
                        #print 'Comparing constants for: ',region.GetHash(),event.data[p],event.data[p+'2']
                        if abs(event.data[p]-event.data[p+'2']) > abs(self.tolerance*event.data[p]):
                            print('Difference found: region ',region.GetHash(),'parameter=',p)
                            print('                  1st DB Value = ',event.data[p+'2'])
                            print('                  2nd DB Value = ',event.data[p])
                            if abs(event.data[p])>10e-4:
                                print('                  Ratio: ', event.data[p+'2']/event.data[p])
                            diff=1
                            
        self.nDiff += diff            
                    
