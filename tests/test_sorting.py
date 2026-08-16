"""排序演算法行為鎖定測試：所有實作皆與內建 sorted() 對照。"""

import random

import pytest

from algorithms.sorting import heap_sort, insertion_sort, merge_sort, quick_sort

ALGORITHMS = [insertion_sort, merge_sort, heap_sort, quick_sort]


def _numeric_cases():
    rng = random.Random(42)
    cases = [
        [],  # 空列表
        [1],  # 單一元素
        [2, 2, 2, 2],  # 全部相同
        [5, 2, 8, 4, 9, 1],  # 最初版本的示範輸入
        [1, 2, 3, 4, 5],  # 已排序
        [5, 4, 3, 2, 1],  # 反向排序
        [-3, 7, 0, -10, 7, 2],  # 含負數與重複
        [3.5, 1.25, 2.75, 3.5],  # 浮點數
    ]
    # 隨機案例：固定 seed 確保可重現
    for size in (10, 100, 1000):
        cases.append([rng.randint(-1000, 1000) for _ in range(size)])
    return cases


@pytest.mark.parametrize("sort_fn", ALGORITHMS)
@pytest.mark.parametrize("case", _numeric_cases())
def test_sorts_match_builtin(sort_fn, case):
    data = list(case)
    result = sort_fn(data)

    assert result == sorted(case)  # 排序結果正確
    assert result is data  # 介面約定：就地排序並回傳同一個列表


@pytest.mark.parametrize("sort_fn", ALGORITHMS)
def test_sorts_any_comparable_type(sort_fn):
    # 合併排序移除無限大哨兵後，任何可互相比較的型別都能排序
    chars = list("insertionsort")
    assert sort_fn(chars) == sorted("insertionsort")

    words = ["merge", "heap", "quick", "insertion", "heap"]
    assert sort_fn(words) == sorted(words)
