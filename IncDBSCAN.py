from scipy.spacial import distance

class IncrementalDBSCAN:

    def __init__(self,dataset,minpts,eps):
        self.dataset = dataset
        self.minPts = minpts
        self.eps = eps
        self.clustersList = []
        self.clustersCount = 0



    def clusterPattern(self,pattern):
        updSeedPointIndexs = self.getUpdSeedSet(pattern)
        if len(updSeedPointIndexs) == 0:
            self.markAsNoise(pattern)
        elif self.updSeedContainsCorePatternsWithNoCluster(updSeedPointIndexs):
            self.createCluster(pattern, updSeedPointIndexs)
        elif self.updSeedContainsCorePatternsFromOneCluster(updSeedPointIndexs):
            self.joinCluster(pattern, updSeedPointIndexs)
        else:
            self.mergeClusters(pattern, updSeedPointIndexs)
        pattern.setIsVisited(True)

        print("finished")



    def mergeClusters(self,point,indexs):
        pass



    def getClusterOfPoints(self,pointsIDs):
        pass



    def joinCluster(self,point,indexs):
        pass



    def updSeedContainsCorePatternsFromOneCluster(self,indexs):
        return True



    def createCluster(self,point,seedPointsIDs):
        pass



    def updSeedContainsCorePatternsWithNoCluster(self,indexs):
        for i,idx in enumerate(indexs):
            p = self.dataset[idx]
            if not p.getAssignedCluster() == "":
                return False
        return True



    def markAsNoise(self,p):
        p.setIsNoise(True)


    #間違ってる！
    #論文どおりでない
    def getUpdSeedSet(self,pattern):
        updSeedIndex = []
        for i,p in enumerate(self.dataset):
            if pattern.getID() == p.getID():
                continue
            if not p.getIsVisited(): # is this error?
                break
            distance = distance.euclidean(pattern.getFeatureVector(),p.getFeatureVector())
            if distance > self.eps:
                continue
            pattern.addToNeighborhoodPoints(p.getID())
            p.addToNeighborhoodPoints(pattern.getID())
            if len(p.getPointsAtEpsIndexs()) == self.minPts:
                p.pointCausedToBeCore(pattern.getID())
                updSeedIndex.add(p.getID())
                continue
            if p.isCore(self.minPts):
                updSeedIndex.add(p.getID())
        return updSeedIndex



    def run(self):
        for i,p in enumerate(self.dataset):
            print(i)
            self.clusterPattern(p)
        self.noiseLabel()
        
            

    #この処理は必要？
    #確かに論文にもupdate後になにか処理をする的なことを書いていたような気がする...
    #論文を再度要チェック
    def noiseLabel(self):
        for i,p in enumerate(self.dataset):
            if not p.isNoise():
                continue
            neighbors = p.getPointsAtEpsIndexs()
            for j,n in enumerate(neighbors):
                neighbor = self.dataset[n]
                if (neighbor.getAssignedCluster() == "") or (not neighbor.isCore(self.minPts)):
                    continue
                p.assignedCluster(neighbor.getAssignedCluster())
                c = self.clustersList[int(p.getAssignedCluster())]
                c.addPoint(p.getID())
                break



    def getClustersList(self):
        return self.clustersList



    def printClustersInformation(self):
        cluster_num = 1
        print("Dataset has "+str(len(self.dataset))+" Points")
        for i,c in enumerate(self.clustersList):
            if not c.getIsActive():
                continue
            #if len(c.getPointsIDs()) < 30:
            #    continue
            print("Cluster " + str(cluster_num) + " has " + str(len(c.getPointsIDs()) + " Points"))
            cluster_num += 1




