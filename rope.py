# Simple implementation of a rope data structure for text storage.

from __future__ import annotations
from typing import Optional, Tuple

class Node:
    def __init__(self):
        self.value: str = ''
        self._weight: int = 0
        self.left: Optional[Node] = None
        self.right: Optional[Node] = None
    
    @property
    def weight(self) -> int:
        if self._weight > 0:
            return self._weight
        if self.left:
            self._weight = self.left.sum_of_leaves()
        else:
            self._weight = 0
        return self._weight

    @property
    def is_leaf(self) -> bool:
        return self.value != ''

    @property
    def is_consistent(self) -> bool:
        return (not self.is_leaf) or (len(self.value) == self.weight and not self.left and not self.right)
    
    def set_value(self, value):
        self.value = value
        self._weight = len(self.value)
    
    def set_left(self, left):
        self.left = left

    def set_right(self, right):
        self.right = right

    def collect(self) -> str:
        # NOTE: should probably change this to a stack-based implementation in the future
        out = ''
        if self.left:
            out += self.left.collect()
        out += self.value
        if self.right:
            out += self.right.collect()
        return out
    
    def sum_of_leaves(self) -> int:
        out = 0
        if self.weight > 0:
            out += self.weight
        elif self.left:
            out += self.left.sum_of_leaves()
        if self.right:
            out += self.right.sum_of_leaves()
        return out

    def concat(self, o) -> Node:
        # NOTE: this does not create a copy of either of the two ropes
        root = Node()
        root.left = self
        root.right = o
        return root
    
    def split(self, i) -> Tuple[Node]:
        if i == self.weight:
            pass
    
    def __getitem__(self, i) -> Optional[str]:
        if i < self.weight:
            return self.left[i] if self.left else self.value[i]
        else:
            if self.right:
                return self.right[i - self.weight]
            else:
                raise IndexError('Rope index out of bounds')