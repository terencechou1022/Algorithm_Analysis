"""效能實測：量測排序演算法與霍夫曼建樹在多種輸入下的執行時間。

執行方式（於 repo 根目錄，需先 pip install -e ".[dev]"）：
    python benchmarks/run_benchmarks.py

輸出：
    benchmarks/results/sorting.csv      排序實測數據
    benchmarks/results/huffman.csv      霍夫曼建樹新舊實作對比
    benchmarks/results/environment.txt  量測環境資訊

量測方法：每個 (演算法, 分佈, 規模) 組合計時多次取中位數；
計時使用 time.perf_counter，輸入以固定 seed 產生確保可重現，
複製輸入的成本排除在計時之外。
"""

import csv
import os
import platform
import statistics
import sys
import time
from datetime import datetime
from pathlib import Path
from random import Random

from algorithms.huffman import TreeNode, build_huffman_tree
from algorithms.sorting import heap_sort, insertion_sort, merge_sort, quick_sort

RESULTS_DIR = Path(__file__).resolve().parent / "results"
REPEATS = 5
SIZES = [2**k for k in range(7, 18)]  # 128 ~ 131072

# Lomuto 快排在已排序/反序/高重複輸入下遞迴深度達 O(n)，
# 退化情境只測到 4096，並將直譯器遞迴上限調高到足夠深度
sys.setrecursionlimit(20000)


def builtin_sorted(A):
    return sorted(A)


SORT_FNS = {
    "insertion_sort": insertion_sort,
    "merge_sort": merge_sort,
    "heap_sort": heap_sort,
    "quick_sort": quick_sort,
    "builtin_sorted": builtin_sorted,  # Timsort（C 實作），作為對照組
}

DISTRIBUTIONS = ["random", "sorted", "reversed", "few_unique"]


def make_input(distribution, n, rng):
    if distribution == "random":
        return [rng.randint(-10**6, 10**6) for _ in range(n)]
    if distribution == "sorted":
        return list(range(n))
    if distribution == "reversed":
        return list(range(n, 0, -1))
    if distribution == "few_unique":  # 只有 10 種相異值的高重複輸入
        return [rng.randint(0, 9) for _ in range(n)]
    raise ValueError(f"unknown distribution: {distribution}")


def max_n(algo, distribution):
    """依演算法特性決定該情境的規模上限，避免 O(n^2) 情境跑到不合理的時間。"""
    if algo == "quick_sort" and distribution != "random":
        return 2**12  # 退化情境（遞迴深度 O(n)）
    if algo == "insertion_sort" and distribution != "sorted":
        return 2**13  # O(n^2)；已排序輸入是其 O(n) 最佳情況，可測到最大規模
    return 2**17


def time_sort(fn, base, repeats=REPEATS):
    times = []
    for _ in range(repeats):
        data = list(base)  # 複製成本排除在計時外
        t0 = time.perf_counter()
        fn(data)
        times.append(time.perf_counter() - t0)
    return times


def run_sorting_suite():
    rows = []
    for algo, fn in SORT_FNS.items():
        for distribution in DISTRIBUTIONS:
            limit = max_n(algo, distribution)
            for n in SIZES:
                if n > limit:
                    continue
                base = make_input(distribution, n, Random(42))
                times = time_sort(fn, base)
                rows.append({
                    "algorithm": algo,
                    "distribution": distribution,
                    "n": n,
                    "median_s": statistics.median(times),
                    "min_s": min(times),
                    "max_s": max(times),
                    "repeats": len(times),
                })
                print(f"sorting: {algo:>16} {distribution:>10} n={n:>7} "
                      f"median={statistics.median(times):.6f}s", flush=True)
    return rows


def _legacy_build_huffman_tree(char_freq):
    """重構前的建樹寫法（取自 Initial commit，保留計時相關的核心邏輯）：
    每輪合併後整列重新排序，總複雜度 O(k^2 log k)。"""
    nodes = sorted(TreeNode(char, freq) for char, freq in char_freq.items())
    while len(nodes) > 1:
        x = nodes.pop(0)
        y = nodes.pop(0)
        z = TreeNode(freq=x.freq + y.freq)
        z.left = x
        z.right = y
        nodes.append(z)
        nodes = sorted(nodes)
    return nodes[0]


HUFFMAN_IMPLS = {
    "heapq": (build_huffman_tree, 2**16),
    "legacy_sorted_list": (_legacy_build_huffman_tree, 2**10),  # 舊版太慢，測到 1024 已足以呈現差距
}


def run_huffman_suite():
    rows = []
    rng = Random(42)
    for k in [2**i for i in range(7, 17)]:
        freq_map = {symbol: rng.randint(1, 10**6) for symbol in range(k)}
        for impl_name, (fn, limit) in HUFFMAN_IMPLS.items():
            if k > limit:
                continue
            times = []
            for _ in range(3):
                t0 = time.perf_counter()
                fn(freq_map)
                times.append(time.perf_counter() - t0)
            rows.append({
                "implementation": impl_name,
                "k": k,
                "median_s": statistics.median(times),
                "min_s": min(times),
                "max_s": max(times),
                "repeats": len(times),
            })
            print(f"huffman: {impl_name:>18} k={k:>6} "
                  f"median={statistics.median(times):.6f}s", flush=True)
    return rows


def write_csv(path, rows):
    with open(path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)


def write_environment(path):
    lines = [
        f"timestamp: {datetime.now().isoformat(timespec='seconds')}",
        f"python: {platform.python_version()}",
        f"platform: {platform.platform()}",
        f"processor: {os.environ.get('PROCESSOR_IDENTIFIER', platform.processor())}",
        f"repeats: {REPEATS} (sorting) / 3 (huffman), 取中位數",
        "timer: time.perf_counter",
    ]
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


if __name__ == "__main__":
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    write_csv(RESULTS_DIR / "sorting.csv", run_sorting_suite())
    write_csv(RESULTS_DIR / "huffman.csv", run_huffman_suite())
    write_environment(RESULTS_DIR / "environment.txt")
    print("done.", flush=True)
