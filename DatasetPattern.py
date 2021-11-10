class DatasetPattern:

    def __init__(self,features,id):
        self.features = features
        self.isBoarder = False
        self.isNoise = False
        self.isVisited = False
        self.ID = id
        self.pointCausedToBeCore = -1
        self.originalCluster = ""
        self.assignedCluster = ""
        self.pointsAtEpsIndexs = []
        self.assignedCentroidID = None
        self.indexInPartition = None

    def addFeature(self,d):
        self.features.append(d)

    def getFeatureVectorLength(self):
        return len(self.features)

    def getFeatureVector(self):
        return self.features

    def getID(self):
        return self.ID

    def getIsVisited(self):
        return self.isVisited

    def getIsNoise(self):
        return self.isNoise

    def getIsBoarder(self):
        return self.isBoarder

    def setIsNoise(self,noise):
        self.isNoise = noise

    def setIsBoarder(self,boarder):
        self.isBoarder = boarder

    def setIsVisited(self,visited):
        self.isVisited = visited

    def getPointCausedToBeCore(self):
        return self.pointCausedToBeCore

    def setAssignedCentroidID(self,assignedCentroidID):
        self.assignedCentroidID = assignedCentroidID

    def getAssignedCentroidID(self):
        return self.assignedCentroidID

    def pointCausedToBeCore(self,pointCausedToBeCore):
        self.pointCausedToBeCore = pointCausedToBeCore

    def getPointsAtEpsIndexs(self):
        return self.pointsAtEpsIndexs

    def addToNeighborhoodPoints(self,i):
        self.pointsAtEpsIndexs.append(i)
    
    def isCore(self,minPts):
        if len(self.pointsAtEpsIndexs) >= minPts:
            return True
        else:
            return False

    def assignedCluster(self, assignedCluster):
        self.assignedCluster = assignedCluster

    def originalCluster(self, originalCluster):
        self.originalCluster = originalCluster

    def getOriginalCluster(self):
        return self.originalCluster

    def getAssignedCluster(self):
        return self.assignedCluster

    def setIndexInPartition(self,indexInPartition):
        self.indexInPartition = indexInPartition

    def getIndexInPartition(self):
        return self.indexInPartition

    