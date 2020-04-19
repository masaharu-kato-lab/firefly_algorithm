import argparse
import pickle
import sys
from itertools import chain, product
from common import nd_equation
from collections import Counter
from dataclasses import dataclass

from typing import Any, Callable, Dict, Iterable, List, Set, Tuple, Union, Optional, Generic

Node = Generic('Node')

def main():
    argp = argparse.ArgumentParser(description='Generate permutations from set(s) of nodes')
    argp.add_argument('-m' , '--method'  , type=str, required=True, choices=['r', 'rg', 'pamed'], help='Clustering method')
    argp.add_argument('-np', '--n_perms' , type=int, help='Number of permutations to generate')
    argp.add_argument('-uv', '--unit_val', type=int, help='')
    args = argp.parse_args()
    
    indata = pickle.load(sys.stdin.buffer)
    indata['clusters'] = clustering(args.method, indata['graph'], args.n_cluster)
    pickle.dump(indata, sys.stdout.buffer)
    return 0


@dataclass
class Method(Generic[Node]):
    name : str
    func : Callable
    dof  : int      # degree of freedom


@dataclass
class Permutation(Generic[Node]):
    perm   : Tuple[Node, ...]
    method : Method


class Generator(Generic[Node]):
    
    def __init__(self, *,
        methods:Set[Method], # dict(method, tuple(method lambda, degree of freedom)) 
        clusters:Dict[Node, Set[Node]]
    ):
        self.clusters  = clusters
        self.methods   = methods


    def generate_with_dof(self, total_number:int) -> List[PatternedPermutation]:
        return self.generate_with_multiple_pattern(self.calc_number_of_pattern(total_number))


    def generate_with_multiple_pattern(self, number_of_pattern:Dict[Method, int]) -> List[PatternedPermutation]:
        return [*chain.from_iterable((self.generate_with_pattern(pattern) for _ in range(number)) for pattern, number in number_of_pattern.items())]


    def generate_with_pattern(self, pattern:Iterable[Method]) -> PatternedPermutation:
        return chain.from_iterable(Permutation(method(cluster), method) for method, cluster in zip(pattern, self.clusters))


    # Calculate the number of individuals on each pattern with unit value based on the degree of freedom
    def n_of_patterns_with_uval(self, uval:int) -> Dict[Tuple[Method, ...], int]:
        return {pattern : uval ** dof for pattern, dof in self.dof_of_patterns().items()}


    # Calculate the number of individuals on each pattern with the total number of individuals
    def n_of_patterns_with_total(self, n_total:int) -> Dict[Tuple[Method, ...], int]:
        dof_of_pats = self.dof_of_patterns()
        uval = nd_equation.solve(Counter(dof_of_pats.values()), prec=0.00001, init=1)
        n_of_pats = {pat : round(uval ** dof) for pat, dof in dof_of_pats.items()}
        n_of_pats[max(n_of_pats, key=n_of_pats.get)] += n_total - sum(n_of_pats.values())
        
        if not (sum(n_of_pats.values()) == n_total and all(n >= 1 for n in n_of_pats.values())):
            raise RuntimeError('Invalid number of patterns.')

        return n_of_pats


    def dof_of_patterns(self):
        return {
            pattern : sum(method.dof for method in pattern)
            for pattern in product(self.methods, repeat=len(self.clusters))
        }
