"""LCS 測試：CLRS 書中案例、邊界案例，以及與暴力解對照的隨機測試。"""

import random
from itertools import combinations

from algorithms.lcs import lcs


def _is_subsequence(s, t):
    it = iter(t)
    return all(char in it for char in s)


def _brute_force_lcs_length(X, Y):
    # 由長到短列舉 X 的所有子序列，第一個也是 Y 的子序列者即為最長
    for length in range(len(X), 0, -1):
        for indices in combinations(range(len(X)), length):
            candidate = "".join(X[i] for i in indices)
            if _is_subsequence(candidate, Y):
                return length
    return 0


def test_textbook_case():
    # CLRS 書中經典案例
    assert lcs("ABCBDAB", "BDCABA") == (4, "BCBA")


def test_edge_cases():
    assert lcs("", "") == (0, "")
    assert lcs("ABC", "") == (0, "")
    assert lcs("", "XYZ") == (0, "")
    assert lcs("ABC", "ABC") == (3, "ABC")
    assert lcs("ABC", "XYZ") == (0, "")


def test_random_against_brute_force():
    rng = random.Random(7)
    for _ in range(30):
        X = "".join(rng.choice("ABC") for _ in range(rng.randint(0, 9)))
        Y = "".join(rng.choice("ABC") for _ in range(rng.randint(0, 9)))

        length, subseq = lcs(X, Y)

        assert length == _brute_force_lcs_length(X, Y)  # 長度與暴力解一致
        assert len(subseq) == length
        assert _is_subsequence(subseq, X)  # 回傳字串必須真的是共同子序列
        assert _is_subsequence(subseq, Y)
