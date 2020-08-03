from dataclasses import dataclass
from typing import Any, Callable, Set, Tuple, NewType, TypeVar, Generic

Node = TypeVar('Node', Any)
Value = TypeVar('Value', Any)

@dataclass
class Problem(Generic[Node, Value]):
    node_set        : Set[Node]
    calc_value      : Callable[[Tuple[Node, ...]], Any]    # Objective function
    is_better_value : Callable[[Value, Value], bool] # Comparison function

