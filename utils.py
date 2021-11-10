from Cluster import Cluster
from IncDBSCAN import IncrementalDBSCAN
from DatasetPattern import DatasetPattern
import numpy as np

def initDataset(dataset):
    ret = []
    for id,data in enumerate(dataset):
        data = np.array(data).tolist()
        p = DatasetPattern(data,id)
        ret.append(p)
    return ret