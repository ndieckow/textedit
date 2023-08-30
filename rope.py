# Simple implementation of a rope data structure for text storage.

from typing import Optional

class Node:
    def __init__(self):
        self.value: str = ''
        self.weight: int = 0
        self.left: Optional[Node] = None
        self.right: Optional[Node] = None
    
    @property
    def is_leaf(self) -> bool:
        return self.value != ''

    def collect(self) -> str:
        pass