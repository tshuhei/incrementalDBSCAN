from scipy.spatial import distance
from Cluster import Cluster


class IncrementalDBSCAN:

    def __init__(self, minpts, eps):
        self.dataset = []
        self.minPts = minpts
        self.eps = eps
        self.clustersList = []
        self.clustersCount = 0

    # 新たに追加された１点をクラスタリングする
    def addClusterPattern(self, pattern):
        #pattern.setIsVisited(True)
        updSeedPointIndexs = self.getUpdSeedInsSet(pattern)
        if len(updSeedPointIndexs) == 0:
            self.markAsNoise(pattern)
        elif self.updSeedContainsCorePatternsWithNoCluster(updSeedPointIndexs):
            self.createCluster(pattern, updSeedPointIndexs)
        else:
            jc = self.updSeedContainsCorePatternsFromOneCluster(updSeedPointIndexs)
            if not jc == -1:
                self.joinCluster(pattern, updSeedPointIndexs, jc)
            else:
                self.mergeClusters(pattern, updSeedPointIndexs)

    # 論文の削除アルゴリズムを少し修正
    # 修正１：削除対象がノイズであれば、そのまま削除するのみ
    # 修正２：削除対象はコアであるなしにかかわらず、必ずq'の集合に入れる
    # 論文の削除アルゴリズムそのままではうまく削除が成り立たない気がする？？
    # NO
    def removeClusterPattern(self, pattern):
        updSeedPointIndexs = self.getUpdSeedDelSet(pattern)
        if pattern.getAssignedCluster == -1:
            pass
        elif len(updSeedPointIndexs) == 0: # 1. Removal
            self.Removal(pattern)
        elif self.updSeedDirectlyDensityReachable(updSeedPointIndexs): # 2. Reduction
            self.Reduction()
        else: # 3. Potential Split
            self.Split()


    # 4.Merge UpdSeedに含まれる複数クラスタを統合して１つのクラスタに集約する
    def mergeClusters(self, point, indexs):
        clusters = self.getClusterOfPoints(indexs)
        masterCluster = clusters[0]
        masterClusterID = masterCluster.getID()
        for c in clusters[1:]:
            c.setActive(False)
            cPoints = c.getPointsIDs()
            for id in cPoints:
                p = self.dataset[id]
                p.setAssignedCluster(masterClusterID)
                masterCluster.addPoint(p.getID())
        cluster_members = []
        for idx in indexs:
            p = self.dataset[idx]
            cluster_members += p.getPointsAtEpsIndexs()
        cluster_members = set(cluster_members)
        for cluster_member in cluster_members:
            p = self.dataset[cluster_member]
            clu = p.getAssignedCluster()
            if clu == -1 or clu == -2:
                p.setAssignedCluster(masterClusterID)
                masterCluster.addPoint(p.getID())


    # 4.Mergeのケースの際に、UpdSeedに含まれるクラスター郡を返す
    def getClusterOfPoints(self, pointsIDs):
        clusters = []
        for id in pointsIDs:
            p = self.dataset[id]
            clu = p.getAssignedCluster()
            if clu == -1 or clu == -2:
                continue
            else:
                clusters.append(self.clustersList[clu])
        clusters = list(set(clusters))
        return clusters

    def joinCluster(self, point, indexs, clusterID):
        c = self.clustersList[clusterID]
        cluster_members = []
        for idx in indexs:
            p = self.dataset[idx]
            cluster_members += p.getPointsAtEpsIndexs()
        cluster_members = set(cluster_members)
        for cluster_member in cluster_members:
            p = self.dataset[cluster_member]
            c.addPoint(p.getID())
            p.setAssignedCluster(clusterID)

    def updSeedContainsCorePatternsFromOneCluster(self, indexs):
        clusterID = []
        for idx in indexs:
            clu = self.dataset[idx].getAssignedCluster()
            if clu == -1 or clu == -2:
                continue
            elif not (clu in clusterID):
                clusterID.append(clu)
        if len(clusterID) == 1:
            return clusterID[0]
        else:
            return -1

    def createCluster(self, point, seedPointsIDs):
        clusterID = self.clustersCount
        c = Cluster(clusterID)
        self.clustersCount += 1
        cluster_members = []
        for id in seedPointsIDs:
            p = self.dataset[id]
            cluster_members += p.getPointsAtEpsIndexs()
        cluster_members = set(cluster_members)
        for cluster_member in cluster_members:
            p = self.dataset[cluster_member]
            p.setAssignedCluster(clusterID)
            c.addPoint(p.getID())
        self.clustersList.append(c)

    def updSeedContainsCorePatternsWithNoCluster(self, indexs):
        for idx in indexs:
            p = self.dataset[idx]
            clu = p.getAssignedCluster()
            if not (clu == -1 or clu == -2):
                return False
        return True

    def markAsNoise(self, p):
        p.setIsNoise(True)
        p.setAssignedCluster(-1)

    # OK
    def Removal(self, pattern):
        clusterID = pattern.getAssignedCluster()
        cluster = self.clustersList[clusterID]
        pointsIDs = cluster.getPointsIDs()
        for id in pointsIDs:
            p = self.dataset[id]
            p.setIsNoise(True)
            p.setAssignedCluster(-1)
        cluster.setActive(False)

    # NO
    def Reduction(self):
        pass

    # OK
    def updSeedDirectlyDensityReachable(self, indexs):
        corePoints = set(indexs)
        for idx in indexs:
            p = self.dataset[idx]
            neighbors = set(p.getPointsAtEpsIndexs())
            if not neighbors.issuperset(corePoints):
                return False
        return True

    # NO
    def Split(self):
        pass

    # Return UpdSeed Ins
    def getUpdSeedInsSet(self, pattern):
        updSeedIndex = []
        qdash = []
        neighbors = []
        for p in self.dataset:
            if pattern.getID() == p.getID():
                continue
            d = distance.euclidean(pattern.getFeatureVector(), p.getFeatureVector())
            if d > self.eps:
                continue
            pattern.addToNeighborhoodPoints(p.getID())
            p.addToNeighborhoodPoints(pattern.getID())
            if len(p.getPointsAtEpsIndexs()) == self.minPts:
                p.setPointCausedToBeCore(pattern.getID())
                qdash.append(p)
                continue
        pattern.addToNeighborhoodPoints(pattern.getID())
        if len(pattern.getPointsAtEpsIndexs()) >= self.minPts:
            qdash.append(p)
        for p in qdash:
            neighbors += p.getPointsAtEpsIndexs()
        neighbors = set(neighbors)
        for n in neighbors:
            p = self.dataset[n]
            if p.isCore(self.minPts):
                updSeedIndex.append(p.getID())
        return updSeedIndex

    # Return UpdSeed Del
    def getUpdSeedDelSet(self, pattern):
        updSeedIndex = []
        qdash = set([])
        neighbors = []
        pointsAtEpsIndexs = pattern.getPointsAtEpsIndexs()
        #if len(pointsAtEpsIndexs) >= self.minPts:
        #    qdash.add(pattern)
        qdash.add(pattern) # 修正２
        #pattern.pointsAtEpsIndexs = []
        for idx in pointsAtEpsIndexs:
            p = self.dataset[idx]
            if len(p.getPointsAtEpsIndexs()) == self.minPts:
                qdash.add(p)
            p.removePointsAtEpxIndexs(pattern.getID())
        for p in qdash:
            neighbors += p.getPointsAtEpsIndexs()
        neighbors = set(neighbors)
        for n in neighbors:
            p = self.dataset[n]
            if p.isCore(self.minPts):
                updSeedIndex.append(p.getID())
        if pattern.getID() in updSeedIndex:
            updSeedIndex.remove(pattern.getID())
            # 削除対象のデータポイントのpointsAtEpsIndexsは、自身を除いたものになる
        return updSeedIndex

    # Apply incremental DBSCAN to a new data point
    def fit(self,point):
        self.dataset.append(point)
        self.addClusterPattern(point)
        return point.getAssignedCluster()

    # Remove a given data point and apply incremental DBSCAN
    def remove(self,id):
        if id < 0 or id >= len(self.dataset):
            print("Error: Index out of range")
            return False
        else:
            point = self.dataset[id]
            self.removeClusterPattern(point)
            del self.dataset[id]        

    def getClustersList(self):
        return self.clustersList

    # show the summary of clustering results
    def printClustersInformation(self):
        cluster_num = 1
        print("Dataset has "+str(len(self.dataset))+" Points")
        for i, c in enumerate(self.clustersList):
            if not c.getIsActive():
                continue
            print("Cluster " + str(cluster_num) + " has " +
                  str(len(c.getPointsIDs())) + " Points")
            cluster_num += 1

    # return the final clustering labels of each data point
    def getLabels(self):
        labels = []
        for data in self.dataset:
            labels.append(data.getAssignedCluster())
        return labels
