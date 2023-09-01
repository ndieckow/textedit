# Simple implementation of a rope data structure for text storage.

# TODO: at the moment, weight and depth are computed every time the functions are called,
# since it is a pain to update those values whenever child nodes change
# we would need to store parents and backpropagate each change

from __future__ import annotations
from typing import Optional, Tuple
from utils import fibonacci

class Node:
    def __init__(self, left = None, right = None):
        self.value: str = ''
        self._weight: int = -1
        self.left: Optional[Node] = left
        self.right: Optional[Node] = right
    
    @classmethod
    def make_leaf(cls, value: str) -> Node:
        out = Node()
        out.set_value(value)
        return out

    @classmethod
    def from_leaves(cls, leaves: list[Node]) -> Node:
        n_leaves = len(leaves)
        if n_leaves == 1:
            return leaves[0]
        if n_leaves == 2:
            return Node(*leaves[0:2])
        mid = n_leaves // 2
        return Node(Node.from_leaves(leaves[:mid]), Node.from_leaves(leaves[mid:]))

    @property
    def weight(self) -> int:
        if self.is_leaf:
            return self._weight
        if self.left:
            self._weight = self.left.sum_of_leaves()
        else:
            self._weight = 0
        return self._weight
    
    @property
    def depth(self) -> int:
        depths = [x.depth if x else 0 for x in [self.left, self.right]]
        return max(depths) + (not self.is_leaf) * 1

    @property
    def is_leaf(self) -> bool:
        return self.value != ''

    @property
    def is_consistent(self) -> bool:
        return (not self.is_leaf) or (len(self.value) == self.weight and not self.left and not self.right)
    
    @property
    def is_balanced(self) -> bool:
        return fibonacci(self.depth + 2) <= self.weight
    
    def set_value(self, value: str):
        self.value = value
        self._weight = len(self.value)
    
    def set_left(self, left: Node):
        self.left = left

    def set_right(self, right: Node):
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
    
    def collect_leaves(self) -> list[Node]:
        out = []
        if self.left:
            out += self.left.collect_leaves()
        if self.is_leaf:
            out.append(self)
        if self.right:
            out += self.right.collect_leaves()
        return out
    
    def sum_of_leaves(self) -> int:
        out = 0
        #if self.left:
        #    out += self.left.sum_of_leaves()
        out += self.weight
        if self.right:
            out += self.right.sum_of_leaves()
        return out

    def concat(self, o: Node) -> Node:
        # NOTE: this does not create a copy of either of the two ropes
        root = Node()
        root.left = self
        root.right = o
        return root
    
    def rebalance(self) -> Node:
        return self if self.is_balanced else Node.from_leaves(self.collect_leaves())
    
    def split(self, i: int) -> Tuple[Optional[Node], Optional[Node]]:
        if i == 0:
            return (None, self)
        if i == self.weight:
            if self.is_leaf:
                return (self, None)
            else:
                return (self.left, self.right)
        elif i < self.weight:
            if self.is_leaf:
                self.left, self.right = Node(), Node()
                self.left.set_value(self.value[:i])
                self.right.set_value(self.value[i:])
                self.value = ''
            assert self.left is not None # has to be since i is smaller than weight
            a, b = self.left.split(i)
            return (a.rebalance() if a is not None else None, Node(b, self.right).rebalance())
        else:
            if self.right is None:
                return (self.left, None)
            a, b = self.right.split(i - self.weight)
            return (Node(self.left, a).rebalance(), b.rebalance() if b is not None else None)
    
    def __getitem__(self, i: int) -> Optional[str]:
        if i < self.weight:
            return self.left[i] if self.left else self.value[i]
        else:
            if self.right:
                return self.right[i - self.weight]
            else:
                raise IndexError('Rope index out of bounds')