import time
import matplotlib.pyplot as plt
import numpy as np
from sklearn.cluster import DBSCAN

from Cluster import Cluster
from IncDBSCAN import IncrementalDBSCAN
from DatasetPattern import DatasetPattern
from utils import initDataset

eps = 3
minpts = 2
start_time = time.time()
data = np.array([[1, 2], [2, 2], [2, 3], [8, 7], [8, 8], [25, 80]])

plt.scatter(data[:, 0], data[:, 1])
plt.show()

dbscan = DBSCAN(eps=eps, min_samples=minpts).fit(data)
print(dbscan.labels_)

data = initDataset(data)
incDBSCAN = IncrementalDBSCAN(data, minpts, eps)
incDBSCAN.run()
elapsed_time = time.time() - start_time
clustersList = incDBSCAN.getClustersList()
print("Incremental DBSCAN Results")
print("==========================")
print("")
incDBSCAN.printClustersInformation()
print("")
print("Runtime = {}[sec]".format(elapsed_time))
print("EPS = {}".format(eps))
print("Minpts = {}".format(minpts))
