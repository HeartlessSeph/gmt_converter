from typing import List, Any

from .graph import *
from .types.format import CurveFormat
from util.dicts import tree


class Curve:
    def __init__(self):
        self.values = []

    curve_format: CurveFormat
    values: List[Any]

    graph: Graph
    anm_data_offset: int
    property_fmt: int
    format: int

    def __horizontal_pos(self):
        if self.curve_format == CurveFormat.POS_VEC3:
            return [[x[0], 0.0, x[2]] for x in self.values]
        elif self.curve_format == CurveFormat.POS_Y:
            return [[0.0] for x in self.values]
        else:
            return self.values

    def __vertical_pos(self):
        if self.curve_format == CurveFormat.POS_VEC3:
            return [[0.0, x[1], 0.0] for x in self.values]
        elif self.curve_format in [CurveFormat.POS_X, CurveFormat.POS_Z]:
            return [[0.0] for x in self.values]
        else:
            return self.values

    def __all_pos(self):
        if self.curve_format == CurveFormat.POS_VEC3:
            return [[x[0], x[1], x[2]] for x in self.values]
        elif self.curve_format in [CurveFormat.POS_X, CurveFormat.POS_Y, CurveFormat.POS_Z]:
            return [[0.0] for x in self.values]
        else:
            return self.values

    def __neutralize_pos(self):
        if not self.curve_format == CurveFormat.POS_VEC3:
            if 'X' in self.curve_format.name:
                self.values = [[v[0], 0.0, 0.0] for v in self.values]
            elif 'Y' in self.curve_format.name:
                self.values = [[0.0, v[0], 0.0] for v in self.values]
            elif 'Z' in self.curve_format.name:
                self.values = [[0.0, 0.0, v[0]] for v in self.values]
            self.curve_format = CurveFormat.POS_VEC3

    def __neutralize_rot(self):
        if not 'QUAT' in self.curve_format.name:
            if 'X' in self.curve_format.name:
                self.values = [[v[0], 0.0, 0.0, v[1]] for v in self.values]
            elif 'Y' in self.curve_format.name:
                self.values = [[0.0, v[0], 0.0, v[1]] for v in self.values]
            elif 'Z' in self.curve_format.name:
                self.values = [[0.0, 0.0, v[0], v[1]] for v in self.values]
        self.curve_format = CurveFormat.ROT_QUAT_SCALED if self.curve_format.value[
            2] == 2 else CurveFormat.ROT_QUAT_HALF_FLOAT

    def __linear_keyframe_blend(self, curve_type):
        # self.neutralize()
        if curve_type in self.curve_format.name:
            new_curve_values = []
            new_curve_keyframes = []
            if len(self.values) > 1:
                c_dict = tree()
                for value_idx, value in enumerate(self.values):
                    if value_idx < len(self.values) - 1:
                        frame_count = self.graph.keyframes[value_idx + 1] - self.graph.keyframes[value_idx]
                        for pos_idx in range(len(self.values[0])):
                            c_dict[pos_idx]["cur"] = value[pos_idx]
                            c_dict[pos_idx]["last"] = self.values[value_idx + 1][pos_idx]
                            c_dict[pos_idx]["first"] = self.values[value_idx][pos_idx]
                        temp_list = []
                        for val in list(c_dict.keys()): temp_list.append(c_dict[val]["cur"])
                        new_curve_values.append(temp_list)
                        new_curve_keyframes.append(self.graph.keyframes[value_idx])
                        if frame_count > 1:
                            temp_dict = tree()
                            for pos_idx in range(len(self.values[0])):
                                curve_additive = (c_dict[pos_idx]["last"] - c_dict[pos_idx]["first"]) / float(frame_count)
                                cur_curve_value = c_dict[pos_idx]["cur"]
                                for frame_num in range(1, frame_count):
                                    cur_curve_value = cur_curve_value + curve_additive
                                    temp_dict[frame_num][pos_idx] = cur_curve_value
                            for frame_num in list(temp_dict.keys()):
                                temp_list = []
                                for val in list(temp_dict[frame_num].keys()): temp_list.append(temp_dict[frame_num][val])
                                new_curve_values.append(temp_list)
                                new_curve_keyframes.append(self.graph.keyframes[value_idx] + frame_num)
                    else:
                        new_curve_values.append(self.values[value_idx])
                        new_curve_keyframes.append(self.graph.keyframes[value_idx])
                if len(new_curve_values) > 0:
                    self.values = new_curve_values
                    self.graph.keyframes = new_curve_keyframes

    def neutralize(self):
        if 'POS' in self.curve_format.name:
            self.__neutralize_pos()
        elif 'ROT' in self.curve_format.name:
            self.__neutralize_rot()

    def add_pos(self, pos):
        self.neutralize()
        pos.neutralize()
        return list(map(lambda v, a: [v[0] + a[0], v[1] + a[1], v[2] + a[2]], self.values, pos.values))

    def to_horizontal(self):
        new_curve = self
        new_curve.values = self.__horizontal_pos()
        return new_curve

    def to_vertical(self):
        new_curve = self
        new_curve.values = self.__vertical_pos()
        return new_curve

    def to_all(self):
        new_curve = self
        new_curve.values = self.__all_pos()
        return new_curve

    def blend_pos_keyframes(self):
        self.__linear_keyframe_blend("POS")

    def blend_rot_keyframes(self):
        self.__linear_keyframe_blend("ROT")


def add_curve(curve1, curve2):
    new_values = []
    if len(curve1.values) > len(curve2.values):
        for f in curve1.graph.keyframes:
            kf = f
            if kf not in curve2.graph.keyframes:
                kf = [k for k in curve2.graph.keyframes if k < kf][-1]
            new_values.append(curve2.values[curve2.graph.keyframes.index(kf)])
        curve2.values = new_values
    else:
        for f in curve2.graph.keyframes:
            kf = f
            if kf not in curve1.graph.keyframes:
                kf = [k for k in curve1.graph.keyframes if k < kf][-1]
            new_values.append(curve1.values[curve1.graph.keyframes.index(kf)])
        curve1.values = new_values
        curve1.graph = curve2.graph
    curve1.values = curve1.add_pos(curve2)
    return curve1


def new_pos_curve():
    pos = Curve()
    pos.graph = zero_graph()
    pos.curve_format = CurveFormat.POS_VEC3
    pos.values = [(0, 0, 0)]
    return pos


def new_rot_curve():
    rot = Curve()
    rot.graph = zero_graph()
    rot.curve_format = CurveFormat.ROT_QUAT_SCALED
    rot.values = [(0, 0, 0, 1)]
    return rot


def generate_curve():
    new = Curve()
    Format_List = [a for a in dir(CurveFormat) if not a.startswith('__')]
    new.graph = zero_graph()
    for format_idx, format in enumerate(Format_List):
        print(str(format_idx) + ": CurveFormat." + format)
        last_idx = format_idx
    print("")
    my_idx = int(input("Select CurveFormat to add: "))
    while my_idx > last_idx or not isinstance(my_idx, int):
        my_b_idx = int(input("Not a valid Curve Format. Please select a correct Curve Format: "))
    new.curve_format = getattr(CurveFormat, Format_List[my_idx])
    new.values = [[(0)]]
    return new
