from typing import Dict, Tuple
from arcade.buffered_draw_commands import Shape
import arcade


class ShapeCollection():
    def __init__(self):
        self.shapes: Dict[Tuple[int, int], Shape] = {}
        self.shape_list = arcade.ShapeElementList()
        self._dirty = False

    def __getitem__(self, key: Tuple[int, int]) -> Shape:
        return self.shapes[key]

    def __setitem__(self, key: Tuple[int, int], value: Shape):
        if key in self.shapes:
            self.shape_list.remove(self.shapes[key])
        self.shapes[key] = value
        self.shape_list.append(value)
        self._dirty = True

    def __delitem__(self, key: Tuple[int, int]):
        self.shape_list.remove(self.shapes[key])
        del self.shapes[key]
        self._dirty = True

    def __contains__(self, key: Tuple[int, int]) -> bool:
        return key in self.shapes

    def dirty(self) -> bool:
        return self._dirty

    def clean(self):
        self._dirty = False

    def draw(self):
        self.shape_list.draw()
