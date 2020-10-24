from typing import List

from .name import Name
from .bone import Bone
from .graph import Graph, zero_graph
from .curve import Curve


class Animation:
    def __init__(self):
        self.bones = []
        self.graphs = []
        self.curves = []

    name: Name
    bones: List[Bone]
    graphs: List[Graph]
    curves: List[Curve]

    index: int
    index1: int
    index2: int
    index3: int
    frame_count: int
    frame_rate: float
    bone_map_start: int
    bone_map_count: int
    curve_count: int
    graph_count: int
    anm_data_size: int
    anm_data_offset: int
    graph_data_size: int
    graph_data_offset: int

    def longest_graph(self):
        g = zero_graph()
        for graph in self.graphs:
            if graph.keyframes[-1] > g.keyframes[-1]:
                g = graph
        return g
