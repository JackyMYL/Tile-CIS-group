from workers.noise.NoiseWorker import NoiseWorker

class EnableCalibration(NoiseWorker):
    '''
    '''

    def __init__(self):
        pass

    def ProcessStart(self):
        pass
        
    def ProcessStop(self):
        print(" ")
        
    def ProcessRegion(self, region):
        for event in region.GetEvents():
            event.data['calibration'] = 0.0
