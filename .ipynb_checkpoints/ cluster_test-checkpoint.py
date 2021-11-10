import time

from Cluster import Cluster
from IncDBSCAN import IncrementalDBSCAN
from DatasetPattern import DatasetPattern

eps = 5
minpts = 18
start_time = time.time()

data = [[1,2],[2,2],[2,3],[8,7],[8,8],[25,80]]

incDBSCAN = IncrementalDBSCAN(dataset,minpts,eps)
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
