from dataclasses import dataclass
from typing import Any, Callable, Set, Tuple, NewType

Node = NewType('Node', Any)
Value = NewType('Value', Any)

@dataclass
class Problem:
    node_set   : Set[Node]
    calc_value : Callable[[Tuple[Node, ...]], Any]    # Objective function
    is_better  : Callable[[Value, Value], bool] # Comparison function

