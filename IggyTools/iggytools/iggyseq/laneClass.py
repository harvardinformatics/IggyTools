

class Lane(object):

    def __init__(self, run = None):

        self.Run = run
        self.index1Length = None
        self.index2Length = None

        self.subIDs = list()

        self.ssSampleLines = list()
        self.ssLineIndices = list()
        
        self.userLaneName = None
        self.machineLaneName = None

