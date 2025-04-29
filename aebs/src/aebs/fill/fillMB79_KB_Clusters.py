# -*- dataeval: init -*-

import interface


class cFill(interface.iAreaFill):
  dep = 'calc_mb79_kb_clusters',

  def check(self):
    clusters = self.modules.fill(self.dep[0])
    return clusters

  def fill(self, clusters):
    objects = []
    for _id, cluster in clusters.iteritems():
      # create object
      o = dict()
      o["valid"] = cluster.mask
      o["shape"] = 'POLYGON'
      o["type"] = self.get_grouptype('KB_CLUSTERS')
      o["vertices"] = cluster.cluster_vertices
      objects.append(o)
    return clusters.time, objects
