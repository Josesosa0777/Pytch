# -*- dataeval: init -*-
# -*- coding: utf-8 -*-

import numpy as np
from scipy.spatial import ConvexHull

from interface import iCalc
from primitives.bases import PrimitiveCollection

signals = [{
    "NumOfDetectionsTransmitted":   ("TA", "tracking_in_NumOfDetectionsTransmitted"),
    "DetClusterID":                 ("TA", "tracking_in_DetClusterID"),
}]


def find_vertices(simplices):
    sorted_vertices = []
    unique_vertices = set(simplices.flatten())

    first_vertex = simplices[0][0]
    sorted_vertices.append(first_vertex)
    unique_vertices.remove(first_vertex)

    for _ in xrange(len(unique_vertices)):
        index = sorted_vertices[-1]
        for vertex_from, vertex_to in simplices:
            if vertex_from == index and vertex_to not in sorted_vertices:
                next_vertex = vertex_to
                break
            elif vertex_to == index and vertex_from not in sorted_vertices:
                next_vertex = vertex_from
                break
        sorted_vertices.append(next_vertex)
    return np.array(sorted_vertices, dtype='int32')


class KBCluster(object):
    def __init__(self, _id, x, y, mask, cluster_mask):
        self._id = _id
        self.x = x
        self.y = y

        self.mask = mask
        self.cluster_mask = cluster_mask
        return

    def cluster_vertices(self, index):
        mask = self.cluster_mask[index, :]
        x = self.x[index, mask]
        y = self.y[index, mask]
        # swap between x-y because of Tracknavigator's coordinate system
        points = np.array([y, x]).transpose()

        if x.size > 3:
            hull = ConvexHull(points)
            if hasattr(hull, 'vertices'):
                vertices = points[hull.vertices]
            else:
                # this is needed because scipy 0.12.0 in the 32-bit toolchain
                # doesn't have the attribute 'vertices'
                vertices = points[find_vertices(hull.simplices)]
        else:
            vertices = points
        return vertices


class Calc(iCalc):
    dep = 'calc_mb79_kb_targets',

    def check(self):
        kb_targets = self.modules.fill(self.dep[0])
        group = self.source.selectSignalGroup(signals)
        return kb_targets, group

    def fill(self, kb_targets, group):
        common_time, cluster_ids = group.get_signal("DetClusterID")
        max_det = np.max(group.get_value('NumOfDetectionsTransmitted'))

        cluster_ids = cluster_ids[:, :max_det]

        det_x = np.zeros((common_time.size, max_det))
        det_y = det_x.copy()
        for _id, target in kb_targets.iteritems():
            det_x[:, _id] = target.dx
            det_y[:, _id] = target.dy

        num_of_clusters = np.max(cluster_ids, axis=1)

        clusters = PrimitiveCollection(common_time)
        # loop on valid cluster ids
        for cl_id in xrange(1, np.max(cluster_ids) + 1):
            mask = cl_id < num_of_clusters
            cluster_mask = cluster_ids == cl_id
            # more than 3 points is required to scipy to prevent ConvexHull's QhullError in cluster_vertices()
            mask &= cluster_mask.sum(axis=1, dtype=np.uint16) >= 3
            clusters[cl_id] = KBCluster(cl_id, det_x, det_y, mask, cluster_mask)
        return clusters


if __name__ == '__main__':
    from config.Config import init_dataeval
    from matplotlib.patches import Polygon
    import matplotlib.pyplot as plt
    import time

    meas_path = r'\\file\Messdat\DAS\ConvertedMeas\TurningAssist\06xB365\2016-11-08-Clustering\B365__2016-11-08_11-11-31_resim_2016_12_02-11_23_53_more.mat'
    config, manager, manager_modules = init_dataeval(['-m', meas_path])
    clusters = manager_modules.calc('calc_mb79_kb_clusters@aebs.fill', manager)
    dummy_id, dummy_cluster = clusters.iteritems().next()

    ax = plt.subplot()

    start = time.time()
    vertices = dummy_cluster.cluster_vertices(100)
    end = time.time()
    print end - start

    if vertices.any():
        ax.add_patch(Polygon(vertices, closed=True, fill=False, color='r'))

    plt.plot(dummy_cluster.y[100], dummy_cluster.x[100], 'o')
    plt.show()
