class Cluster:

    def __init__(self,id):
        self.regions = []
        self.ID = id
        self.isActive = True
        self.pointsIDs = []
        self.pointsSeen = {}

    def addPoint(self,index):
        if not (index in self.pointsSeen.keys()):
            self.pointsIDs.append(index)
            self.pointsSeen[index] = True

    def getPointsIDs(self):
        return self.pointsIDs

    def AddListOfPoints(self,pointsIds):
        self.pointsIDs.extend(pointsIds)
    
    def getID(self):
        return self.ID

    def getRegions(self):
        return self.regions

    def setActive(self,isActive):
        self.isActive = isActive

    def getIsActive(self):
        return self.isActive

    def addDenseRegion(self,region):
        self.regions.append(region)

    def addPointsList(self,points):
        self.pointsIDs.extend(points)