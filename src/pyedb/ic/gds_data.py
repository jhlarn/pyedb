# Copyright (C) 2023 - 2024 ANSYS, Inc. and/or its affiliates.
# SPDX-License-Identifier: MIT
#
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

from dataclasses import dataclass


@dataclass
class CellShapes:
    polygons: list
    paths: list
    labels: list
    boxes: list
    pins: list
    nets: list

    @property
    def is_empty(self):
        if self.polygons:
            return False
        if self.paths:
            return False
        if self.labels:
            return False
        if self.boxes:
            return False
        if self.pins:
            return False
        if self.nets:
            return False
        return True


class ICBox:
    def __init__(self, k_box):
        self._kbox = k_box

    @property
    def is_box(self):
        return self._kbox.is_box()

    @property
    def center(self):
        return self._kbox.box_center

    @property
    def pt1(self):
        return self._kbox.box_p1

    @property
    def pt2(self):
        return self._kbox.box_p2


class ICPath:
    def __init__(self, k_path):
        self._k_path = k_path

    @property
    def is_path(self):
        return self._k_path.is_path()

    @property
    def width(self):
        return self._k_path.path_width

    @property
    def begin_extension(self):
        """Extensions of the path beginning"""
        return self._k_path.path_bgnext()

    @property
    def end_extension(self):
        """Extensions of the path end."""
        return self._k_path.path_endext()

    @property
    def length(self):
        """Return path length."""
        return self._k_path.path_length()

    @property
    def points(self):
        return list(self._k_path.each_point())

    @property
    def contour(self):
        return ICPolygon(self._k_path.polygon)


class ICPolygon:
    def __init__(self, k_polygon):
        self._k_polygon = k_polygon

    @property
    def is_polygon(self):
        return self._k_polygon.is_polygon()

    @property
    def is_simple_polygon(self):
        return self._k_polygon.is_simple_polygon()

    @property
    def points_hull(self):
        """Deliver the points of the outer (hull) contour"""
        return list(self._k_polygon.each_point_hull())

    @property
    def points_hole(self):
        """Deliver the points of a specific hole contour."""
        if self.is_simple_polygon:
            return None
        if self._k_polygon.each_point_hole():
            return list(self._k_polygon.each_point_hole())
        else:
            return None

    @property
    def edges(self):
        return list(self._k_polygon.each_edge())

    @property
    def num_holes(self):
        """Deliver the number of holes. A simple polygon does not have holes, in this case always return 0."""
        if self._k_polygon.holes():
            return list(self._k_polygon.holes())
        else:
            return 0

    @property
    def area(self):
        """Returns the polygon area."""
        return self._k_polygon.area()


class ICLayoutData:
    def __init__(self, klayout, layers, cells):
        self._klayout = klayout
        self._layers = layers
        self._cells = cells

    @property
    def layers(self):
        return self._layers

    @layers.setter
    def layers(self, value):
        if isinstance(value, list):
            self._layers = value

    @property
    def cells(self):
        return self._cells

    @cells.setter
    def cells(self, value):
        if isinstance(value, list):
            self._cells = value


class CellData:
    def __init__(self, klayout, name):
        self._klayout = klayout
        self._name = name
        self._k_polygons = {}
        self._labels = {}
        self._k_boxes = {}
        self._k_paths = {}
        self._pins = {}
        self._nets = []

    @property
    def name(self):
        return self._name

    @name.setter
    def name(self, value):
        if isinstance(value, str):
            pass

    @property
    def kcell(self):
        return self._klayout.cell(self.name)

    @property
    def polygons(self):
        return {layer_name: [ICPolygon(k) for k in k_poly] for layer_name, k_poly in self._k_polygons.items()}

    @property
    def labels(self):
        return self._labels

    @property
    def boxes(self):
        return {layer_name: [ICBox(k) for k in k_box] for layer_name, k_box in self._k_boxes.items()}

    @property
    def paths(self):
        return {layer_name: [ICPath(k) for k in k_path] for layer_name, k_path in self._k_paths.items()}

    @property
    def pins(self):
        return self._pins

    @property
    def bbox(self):
        return self.kcell.dbbox()

    @property
    def nets(self):
        return self._nets


class ICLayerData:
    def __init__(self, klayout, name, index, data_type, purpose, skip_labels=True):
        self._klayout = klayout
        self._name = name
        self._index = index
        self._data_type = data_type
        self._shapes = {}
        self._purpose = purpose
        self._skip_labels = skip_labels

    @property
    def name(self):
        return self._name

    @name.setter
    def name(self, value):
        if isinstance(value, str):
            info = self._klayout.get_info(self.index)
            info.name = value
            self._klayout.set_info(self.index, info)
            self._name = value

    @property
    def index(self):
        return self._index

    @index.setter
    def index(self, value):
        if isinstance(value, int):
            info = self._klayout.get_info(self.index)
            info.layer = value
            self._klayout.set_info(self.index, info)
            self._index = value

    @property
    def data_type(self):
        return self._data_type

    @data_type.setter
    def data_type(self, value):
        if isinstance(value, int):
            info = self._klayout.get_info(self.index)
            info.data_type = value
            self._klayout.set_info(self.index, info)
            self._data_type = value

    @property
    def shapes(self):
        if not self._shapes:
            self._update_shapes()
        return self._shapes

    @property
    def purpose(self):
        return self._purpose

    @purpose.setter
    def purpose(self, value):
        if isinstance(value, str):
            self._purpose = value

    @property
    def skip_labels(self):
        return self._skip_labels

    @skip_labels.setter
    def skip_labels(self, value):
        if isinstance(value, bool):
            self._skip_labels = value

    def _update_cell_shapes(self, kcell):
        pass

    def _update_shapes(self):
        self._shapes = {}
        top_cells = [cell for cell in self._klayout.each_cell()]
        for kcell in top_cells:
            cell = CellShapes(polygons=[], paths=[], labels=[], boxes=[], pins=[], nets=[])
            if not kcell.name in self._shapes:
                self._shapes[kcell.name] = cell
            layer = self._klayout.layer(int(self.index), int(self.data_type))
            shape_list = kcell.shapes(layer)
            if "pin" in self.purpose.lower():
                for shape in shape_list.each():
                    if shape.is_box():
                        pin_position = shape.dbox.center()
                        cell.pins.append([pin_position.x, pin_position.y])
                    if shape.is_polygon():
                        pass
            if not self.skip_labels:
                for shape in shape_list.each():
                    if shape.is_text():
                        cell.labels.append(shape)
            if "net" in self.purpose.lower():
                for shape in shape_list.each():
                    cell.nets.append(shape)
            if "drawing" in self.purpose.lower():
                for shape in shape_list.each():
                    if shape.is_polygon():
                        cell.polygons.append(shape)
                    elif shape.is_box():
                        cell.boxes.append(shape)
                    elif shape.is_path():
                        cell.paths.append(shape)
