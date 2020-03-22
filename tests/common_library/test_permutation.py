import pytest #type:ignore
from common_library import permutation

nodes = [chr(i) for i in range(ord('A'), ord('F')+1)]

@pytest.mark.parametrize(
    'perm, res', [
        ('ABCDEF', True),
        ('AFDCAB', False),
        ('BFCADE', True),
        ('CADBEF', True),
        ('BAFADC', False),
        ('CABFE' , False),
        ('CACFE' , False),
        ('CABFEDC', False),
        ('CABFEDCA', False),
        ('ABDF', False),
        ('', False),
    ]
)
def test_is_valid(perm, res):
    assert res == permutation.is_valid([c for c in perm], nodes)

