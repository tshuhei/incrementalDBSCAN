from scipy.spatial import distance
from Cluster import Cluster


class IncrementalDBSCAN:

    def __init__(self, dataset, minpts, eps):
        self.dataset = dataset
        self.minPts = minpts
        self.eps = eps
        self.clustersList = []
        self.clustersCount = 0

    # 新たに追加された１点をクラスタリングする
    def clusterPattern(self, pattern):
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

    # 4.Merge UpdSeedに含まれる複数クラスタを統合して１つのクラスタに集約する
    def mergeClusters(self, point, indexs):
        clusters = self.getClusterOfPoints(indexs)
        masterCluster = clusters[0]
        masterClusterID = str(masterCluster.getID())
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
            if clu == "":
                continue
            if not clu in idsSeen.keys():
                clusters.append(self.clustersList[int(clu)])
                idsSeen[clu] = True
        return clusters

    # 間違ってる
    # 挿入されたポイントだけしかクラスタに追加していない
    def joinCluster(self, point, indexs):
        clusterID = self.dataset[indexs[0]].getAssignedCluster()
        c = self.clustersList[int(clusterID)]
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
        clusterID = str(c.getID())
        self.clustersCount += 1
        point.setAssignedCluster(clusterID)
        c.addPoint(point.getID())
        for i, id in enumerate(seedPointsIDs):
            p = self.dataset[id]
            p.setAssignedCluster(clusterID)
            c.addPoint(point.getID())
        self.clustersList.append(c)

    def updSeedContainsCorePatternsWithNoCluster(self, indexs):
        for i, idx in enumerate(indexs):
            p = self.dataset[idx]
            if not p.getAssignedCluster() == "":
                return False
        return True

    def markAsNoise(self, p):
        p.setIsNoise(True)

    # 間違ってる！
    # 論文どおりでない
    def getUpdSeedSet(self, pattern):
        updSeedIndex = []
        for i, p in enumerate(self.dataset):
            if pattern.getID() == p.getID():
                continue
            if not p.getIsVisited():
                #print("Error: there is an unvisited node")
                break
            d = distance.euclidean(
                pattern.getFeatureVector(), p.getFeatureVector())
            if d > self.eps:
                continue
            pattern.addToNeighborhoodPoints(p.getID())
            p.addToNeighborhoodPoints(pattern.getID())
            if len(p.getPointsAtEpsIndexs()) == self.minPts:
                p.setPointCausedToBeCore(pattern.getID())
                updSeedIndex.append(p.getID())
                continue
            if p.isCore(self.minPts):
                updSeedIndex.append(p.getID())
        return updSeedIndex

    # IncrementalDBSCANによるクラスタリングを実行
    def run(self):
        for i, p in enumerate(self.dataset):
            # print(i)
            self.clusterPattern(p)
        self.noiseLabel()

    # この処理は必要？
    # 確かに論文にもupdate後になにか処理をする的なことを書いていたような気がする...
    # 論文を再度要チェック
    def noiseLabel(self):
        for i, p in enumerate(self.dataset):
            if not p.getIsNoise():
                continue
            neighbors = p.getPointsAtEpsIndexs()
            for j, n in enumerate(neighbors):
                neighbor = self.dataset[n]
                if (neighbor.getAssignedCluster() == "") or (not neighbor.isCore(self.minPts)):
                    continue
                p.setAssignedCluster(neighbor.getAssignedCluster())
                c = self.clustersList[int(p.getAssignedCluster())]
                c.addPoint(p.getID())
                break

    def getClustersList(self):
        return self.clustersList

    def printClustersInformation(self):
        cluster_num = 1
        print("Dataset has "+str(len(self.dataset))+" Points")
        for i, c in enumerate(self.clustersList):
            if not c.getIsActive():
                continue
            print("Cluster " + str(cluster_num) + " has " +
                  str(len(c.getPointsIDs())) + " Points")
            cluster_num += 1

    def getLabels(self):
        labels = []
        for data in self.dataset:
            clu = data.getAssignedCluster()
            if clu == "":
                labels.append(-1)
            else:
                labels.append(int(clu))
        return labels
