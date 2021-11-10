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
    def clusterPattern(self, pattern):
        pattern.setIsVisited(True)
        updSeedPointIndexs = self.getUpdSeedSet(pattern)
        if len(updSeedPointIndexs) == 0:
            self.markAsNoise(pattern)
        elif self.updSeedContainsCorePatternsWithNoCluster(updSeedPointIndexs):
            self.createCluster(pattern, updSeedPointIndexs)
        elif self.updSeedContainsCorePatternsFromOneCluster(updSeedPointIndexs):
            self.joinCluster(pattern, updSeedPointIndexs)
        else:
            self.mergeClusters(pattern, updSeedPointIndexs)

    # 4.Merge UpdSeedに含まれる複数クラスタを統合して１つのクラスタに集約する
    def mergeClusters(self, point, indexs):
        clusters = self.getClusterOfPoints(indexs)
        masterCluster = clusters[0]
        masterClusterID = masterCluster.getID()
        point.setAssignedCluster(masterClusterID)
        masterCluster.addPoint(point.getID())
        for i, c in enumerate(clusters):
            c.setActive(False)
            cPoints = c.getPointsIDs()
            for j, id in enumerate(cPoints):
                p = self.dataset[id]
                p.setAssignedCluster(masterClusterID)
                masterCluster.addPoint(p.getID())

    # 4.Mergeのケースの際に、UpdSeedに含まれるクラスター郡を返す
    def getClusterOfPoints(self, pointsIDs):
        clusters = []
        idsSeen = {}
        for i, id in enumerate(pointsIDs):
            p = self.dataset[id]
            clu = p.getAssignedCluster()
            if clu == -1 or clu == -2:
                continue
            if not clu in idsSeen.keys():
                clusters.append(self.clustersList[clu])
                idsSeen[clu] = True
        return clusters

    # 間違ってる
    # 挿入されたポイントだけしかクラスタに追加していない
    def joinCluster(self, point, indexs):
        clusterID = self.dataset[indexs[0]].getAssignedCluster()
        c = self.clustersList[clusterID]
        c.addPoint(point.getID())
        point.setAssignedCluster(clusterID)

    # 多分間違ってる
    # クラスターAと、""が混じってる場合を取りこぼしている？
    def updSeedContainsCorePatternsFromOneCluster(self, indexs):
        clusterID = self.dataset[indexs[0]].getAssignedCluster()
        for i, idx in enumerate(indexs[1:]):
            p = self.dataset[idx]
            if not clusterID == p.getAssignedCluster():
                return False
        return True

    # 間違ってる
    # クラスタ作成方法間違ってる！
    def createCluster(self, point, seedPointsIDs):
        c = Cluster(self.clustersCount)
        clusterID = c.getID()
        self.clustersCount += 1
        point.setAssignedCluster(clusterID)
        c.addPoint(point.getID())
        for i, id in enumerate(seedPointsIDs):
            p = self.dataset[id]
            p.setAssignedCluster(clusterID)
            c.addPoint(point.getID())
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

    # 論文に沿うようにアルゴリズム修正済み
    # UpdSeedInsの集合を返す
    def getUpdSeedSet(self, pattern):
        updSeedIndex = []
        qdash = []
        neighbors = []
        for p in self.dataset:
            if pattern.getID() == p.getID():
                continue
            #if not p.getIsVisited():
            #    print("Error: there is an unvisited node")
            #    break
            d = distance.euclidean(pattern.getFeatureVector(), p.getFeatureVector())
            if d > self.eps:
                continue
            pattern.addToNeighborhoodPoints(p.getID())
            p.addToNeighborhoodPoints(pattern.getID())
            if len(p.getPointsAtEpsIndexs()) == self.minPts:
                p.setPointCausedToBeCore(pattern.getID())
                qdash.append(p)
                #updSeedIndex.append(p.getID())
                continue
            #if p.isCore(self.minPts):
            #    updSeedIndex.append(p.getID())
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

    # IncrementalDBSCANによるクラスタリングを実行
    def fit(self,point):
        # print(i)
        self.dataset.append(point)
        self.clusterPattern(point)
        #self.noiseLabel()
        return point.getAssignedCluster()

    # この処理は必要？
    # 確かに論文にもupdate後になにか処理をする的なことを書いていたような気がする...
    # 論文を再度要チェック
    #def noiseLabel(self):
    #    for i, p in enumerate(self.dataset):
    #        if not p.getIsNoise():
    #            continue
    #        neighbors = p.getPointsAtEpsIndexs()
    #        for j, n in enumerate(neighbors):
    #            neighbor = self.dataset[n]
    #            if (neighbor.getAssignedCluster() == "") or (not neighbor.isCore(self.minPts)):
    #                continue
    #            p.setAssignedCluster(neighbor.getAssignedCluster())
    #            c = self.clustersList[int(p.getAssignedCluster())]
    #            c.addPoint(p.getID())
    #            break

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
