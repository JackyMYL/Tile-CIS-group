from workers.noise.NoiseWorker import NoiseWorker

class AddRun(NoiseWorker):
    def __init__(self, runNumber, newType, detType='physical'):
        self.runNumber = runNumber
        self.newType = newType
        self.type=detType

    def ProcessStart(self):
        print("AddRun: %d %s" % (self.runNumber, self.newType))
        
    def ProcessStop(self):
        pass

    def ProcessRegion(self, region):
        data = {}
        newRun = Run(self.runNumber, self.newType, 0, data)
        region.AddEvent(Event(newRun, data))
