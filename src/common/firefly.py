import random
import itertools
import functools
from dataclasses import dataclass
from copy import copy

from typing import Any, Callable, cast, Set, Dict, List, Union, Iterator, Optional, Tuple, Generic
Node = Generic('Node')
Value = Generic('Value')

@dataclass
class Problem(Generic[Node, Value]):
    node_set   : Set[Node]
    calc_value : Callable[[List[Node]], Any]    # Objective function
    is_better  : Callable[[Value, Value], bool] # Comparison function


@dataclass
class Movement(Generic[Node, Value]):
    marked_perm    : Tuple[Node,...]
    marked_value   : Value
    attracted_perm : Tuple[Node,...]
    perm           : Tuple[Node,...]
    value          : Value


@dataclass
class Fireflies(Generic[Node, Value]):
    problem:Problem
    perms:List[Tuple[Node, ...]]

    def __post_init__(self):
        self.values = [self.problem.calc_value(perm) for perm in self.perms]
        self.order = [*range(len(self.values))]
        self.movements:List[Movement] = []
        
        self.sort()
        self.best_perm = self.perms[self.order[0]]
        self.best_value = self.values[self.order[0]]


    def sort(self):
        self.order = sorted(self.order, key=functools.cmp_to_key(
            lambda i1, i2: self.problem.is_better(self.values[i1], self.values[i2])
        ))


    def is_better(self, i1:int, i2:int) -> bool:
        return self.problem.is_better(self.values[i1], self.values[i2])


    def move(self, index:int, marked_index:int, attracted_perm:Tuple[Node,...], perm:Tuple[Node,...]):
        value = self.problem.calc_value(perm)
        self.perms[index] = perm
        self.values[index] = value

        if self.problem.is_better(value, self.best_value):
            self.best_perm = perm
            self.best_value = value

        self.movements.append(Movement(
            self.perms[marked_index],
            self.values[marked_index],
            attracted_perm,
            perm,
            value
        ))


@dataclass
class Configuration(Generic[Node, Value]):
    alpha         : float
    gamma         : float
    continue_cond : Callable[[], bool]                      # Condition to continue
    alpha_shuffle : Callable[[List[int]], List[int]]        # Shuffle function for alpha step
    perm_dist     : Callable[[List[Node], List[Node]], Any] # Distance function between permutations


@dataclass
class Optimizer(Generic[Node, Value]):
    fireflies:Fireflies
    cfg:Configuration

    def optimize(self, cond:Callable[[Fireflies], bool]) -> Fireflies:
        while cond:
            state = self._optimize_once()
        return state


    def optimize_while(self, cond:Callable[[Fireflies], bool]) -> Iterator[Fireflies]:
        while cond:
            yield self._optimize_once()


    def _optimize_once(self) -> Fireflies:
        return self._optimize_with(*next(self._ff_pairs_to_optimize()))


    def _ff_pairs_to_optimize(self) -> Iterator[Tuple[int, int]]:
        while True:
            self.fireflies.sort()
            for i1, i2 in itertools.combinations(self.fireflies.order, 2):
                if self.fireflies.is_better(i1, i2):
                    yield (i1, i2)
        

    def _optimize_with(self, index:int, marked_index:int) -> Fireflies:

        # target permutations
        original_perm = self.fireflies.perms[index]
        marked_perm = self.fireflies.perms[marked_index]

        # Calculate current parameter
        c_beta = 1 / (1 + self.cfg.gamma * self.cfg.perm_dist(original_perm, marked_perm))
        c_alpha = int(random.random() * self.cfg.alpha + 1.0)

        # attract permutations and 
        attracted_perm = beta_step(original_perm, marked_perm, c_beta)
        final_perm = alpha_step(attracted_perm, c_alpha, self.cfg.alpha_shuffle)

        # Record movement
        self.fireflies.move(index, marked_index, attracted_perm, final_perm)

        return self.fireflies


# Beta step (attract between perm1 and perm2 based on beta value)
def beta_step(perm1:Tuple[Node, ...], perm2:Tuple[Node, ...], prob:float) -> List[Node]:

    perm12:List[Optional[Node]] = [node1 if node1 == node2 else None for node1, node2 in zip(perm1, perm2)]
    remains = set(perm1).difference(set(node for node in perm12 if node))
    empties:List[int] = []

    # fill empty indexes in perm12
    for i in [i for i in range(len(perm12)) if perm12[i]]:

        # choose candidate node from perm1's node or perm2's based on beta value
        candidate_node = perm1[i] if random.random() > prob else perm2[i]

        # fill with chosen candidate node if it doesn't already exist in perm12
        if candidate_node in remains:
            perm12[i] = candidate_node
            remains.remove(candidate_node)
            empties.append(i)

    # fill remain indexes randomly
    if remains:
        shuffled_remains = random.sample(remains, len(remains))
        for i, perm12_i in enumerate(empties):
            perm12[perm12_i] = shuffled_remains[i]

    return perm12


# Alpha step (randomly swap node_set in permutation based on alpha value)
def alpha_step(perm:List[Node], n_targets:int, shuffle:Callable[[List[int]], List[int]]) -> List[Node]:

    if n_targets <= 1:
        return perm

    target_indexes = random.sample(range(len(perm)), n_targets)
    shuffled_target_indexes = shuffle(target_indexes)

    # shuffle target indexes
    new_perm = perm.copy()
    for shuffled_index, index in zip(shuffled_target_indexes, target_indexes):
        new_perm[shuffled_index] = perm[index]

    return new_perm

