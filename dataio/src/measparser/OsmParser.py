import numpy as np
from xml.etree import ElementTree

from pyutils.functional import cached_attribute


class Node(object):
    def __init__(self, node_id, lat, lon):
        self.id = node_id
        self.lat = lat
        self.lon = lon
        return


class RoadLine(object):
    def __init__(self, road_id, nodes):
        self.id = road_id
        self.nodes = nodes
        return

    @cached_attribute
    def node_coordinates(self):
        lat = [node.lat for node in self.nodes]
        lon = [node.lon for node in self.nodes]
        return np.array(lon), np.array(lat)


class RoadMap(object):
    def __init__(self, xml_file):
        self.root = ElementTree.parse(xml_file).getroot()
        return

    @cached_attribute
    def road_lines(self):
        road_lines = []
        for road in self.root.findall('way'):
            attributes = road.attrib
            nodes = [self.getNode(node_id.attrib['ref']) for node_id in road.findall('nd')]
            if len(nodes) < 1:  # skip if there is not node reference attached to the road
                continue
            road_lines.append(RoadLine(attributes['id'], nodes))
        return road_lines

    @cached_attribute
    def nodes(self):
        return [Node(node.attrib['id'], float(node.attrib['lat']), float(node.attrib['lon'])) for node in self.root.findall('node')]

    def getNode(self, node_id):
        for node in self.root.findall('node'):
            if node.attrib['id'] == node_id:
                return Node(node_id, float(node.attrib['lat']), float(node.attrib['lon']))
        raise ValueError("Node %s not found" % node_id)
