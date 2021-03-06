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
    def removeClusterPattern(self, pattern):
        updSeedPointIndexs, neighbors = self.getUpdSeedDelSet(pattern)
        if pattern.getAssignedCluster == -1:
            pass
        elif len(updSeedPointIndexs) == 0: # 1. Removal
            self.Removal(pattern)
        elif self.updSeedDirectlyDensityReachable(updSeedPointIndexs): # 2. Reduction
            self.Reduction(pattern, neighbors)
        else: # 3. Potential Split
            self.Split(pattern, updSeedPointIndexs, neighbors)


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

    def Removal(self, pattern):
        clusterID = pattern.getAssignedCluster()
        if clusterID == -1:
            return
        cluster = self.clustersList[clusterID]
        pointsIDs = cluster.getPointsIDs()
        for id in pointsIDs:
            p = self.dataset[id]
            p.setIsNoise(True)
            p.setAssignedCluster(-1)
        cluster.pointsIDs = set([])
        cluster.setActive(False)

    # 論文のアルゴリズムを修正：q'の近傍点のノイズ性も調べる
    # neighbors: 全てのq'の近傍点の集合
    def Reduction(self, pattern, neighbors):
        for neighbor in neighbors:
            p = self.dataset[neighbor]
            isNoise = True
            for n in p.getPointsAtEpsIndexs():
                node = self.dataset[n]
                if node.isCore(self.minPts):
                    isNoise = False
            if isNoise:
                if p.getAssignedCluster() != -1:
                    cluster = self.clustersList[p.getAssignedCluster()]
                    cluster.removePoint(p.getID())
                    p.setAssignedCluster(-1)
        if pattern.getAssignedCluster() != -1:
            cluster = self.clustersList[pattern.getAssignedCluster()]
            cluster.removePoint(pattern.getID())

    def updSeedDirectlyDensityReachable(self, indexs):
        corePoints = set(indexs)
        for idx in indexs:
            p = self.dataset[idx]
            neighbors = set(p.getPointsAtEpsIndexs())
            if not neighbors.issuperset(corePoints):
                return False
        return True

    def Split(self, pattern ,indexs, neighbors):
        connectivity, connectNodes = self.findDensityConnectivity(pattern, indexs)
        if len(connectivity) == 1:
            # Reduction
            self.Reduction(pattern, neighbors)
        else:
            # Split
            cluster = self.clustersList[pattern.getAssignedCluster()]
            cluster.setActive(False)
            for id in cluster.getPointsIDs():
                p = self.dataset[id]
                p.setAssignedCluster(-1)
            cluster.pointsIDs = set([])
            for connect in connectNodes:
                clusterID = self.clustersCount
                c = Cluster(clusterID)
                self.clustersCount += 1
                for node in connect:
                    p = self.dataset[node]
                    if p.getAssignedCluster() != -1:
                        prev = self.clustersList[p.getAssignedCluster()]
                        prev.setActive(False)
                        prev.removePoint(p.getID())
                    p.setAssignedCluster(clusterID)
                    c.addPoint(p.getID())
                self.clustersList.append(c)

    def findDensityConnectivity(self, pattern, indexs):
        connectivity = []
        connectNodes = []
        updseeds = set(indexs)
        for id in indexs:
            connections = set([id])
            connectSet = set([id])
            for c in connectivity:
                if id in c:
                    continue
            p = self.dataset[id]
            queue = []
            queue.append(p)
            idseen = set([])
            while len(queue) != 0:
                q = queue.pop(0)
                if q.getID() in idseen:
                    continue
                idseen.add(q.getID())
                for n in q.getPointsAtEpsIndexs():
                    if (n in idseen) or (n == pattern.getID()):
                        continue
                    connectSet.add(n)
                    neighbor = self.dataset[n]
                    if neighbor.isCore(self.minPts):
                        queue.append(neighbor)
                        connections.add(neighbor.getID())
                if connections.issuperset(updseeds):
                    return [updseeds], None
            connectivity.append(connections & updseeds)
            connectNodes.append(connectSet)
        return connectivity, connectNodes

    # Return UpdSeed Ins
    def getUpdSeedInsSet(self, pattern):
        updSeedIndex = []
        qdash = []
        neighbors = []
        for p in self.dataset:
            if not p is None:
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
        pattern.removePointsAtEpsIndexs(pattern.getID())
        pointsAtEpsIndexs = pattern.getPointsAtEpsIndexs()
        qdash.add(pattern) # 修正２
        for idx in pointsAtEpsIndexs:
            p = self.dataset[idx]
            p.removePointsAtEpsIndexs(pattern.getID())
            if len(p.getPointsAtEpsIndexs()) == self.minPts - 1:
                qdash.add(p)
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
        return updSeedIndex, neighbors

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
            self.dataset[id] = None  

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
            if not data is None:
                labels.append(data.getAssignedCluster())
        return labels
