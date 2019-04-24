from typing import Dict, Tuple
from arcade.buffered_draw_commands import Shape
import arcade


class ShapeCollection():
    def __init__(self):
        self.shapes: Dict[Tuple[int, int], Shape] = {}
        self.shape_list = arcade.ShapeElementList()
        self.meta = {}
        self._dirty = False

    def __getitem__(self, key: Tuple[int, int]) -> Shape:
        return self.shapes[key]

    def __setitem__(self, key: Tuple[int, int], value: Shape):
        if key in self.shapes:
            self.shape_list.remove(self.shapes[key])
        self.shapes[key] = value
        if key in self.meta:
            del self.meta[key]
        self.shape_list.append(value)
        self._dirty = True

    def __delitem__(self, key: Tuple[int, int]):
        self.shape_list.remove(self.shapes[key])
        del self.shapes[key]
        if key in self.meta:
            del self.meta[key]
        self._dirty = True

    def __contains__(self, key: Tuple[int, int]) -> bool:
        return key in self.shapes

    def add_meta(self, key: Tuple[int, int], val):
        if key not in self.shapes:
            raise KeyError()
        self.meta[key] = val

    def get_meta(self, key: Tuple[int, int]):
        if key not in self.shapes:
            raise KeyError()
        return self.meta[key]

    def dirty(self) -> bool:
        return self._dirty

    def clean(self):
        self._dirty = False

    def draw(self):
        if self.shapes:
            self.shape_list.draw()
