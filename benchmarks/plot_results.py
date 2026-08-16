"""讀取 benchmark CSV，繪製理論 vs 實測的 log-log 效能曲線圖。

執行方式（於 repo 根目錄，需先執行 run_benchmarks.py）：
    python benchmarks/plot_results.py

輸出：docs/images/*.png
圖內文字一律英文（避免跨平台中文字型問題），內文解讀見 docs/analysis.md。
"""

import csv
import math
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
# 需先指定 Agg 後端再匯入 pyplot，因此這行 import 晚於程式碼
import matplotlib.pyplot as plt  # noqa: E402

BASE = Path(__file__).resolve().parent
RESULTS = BASE / "results"
IMAGES = BASE.parent / "docs" / "images"

# 用色與線條規格：固定順序的類別色、2px 細線、低調的格線與座標軸、白底輸出
SURFACE = "#fcfcfb"
INK = "#0b0b0b"
INK_2 = "#52514e"
MUTED = "#898781"
GRID = "#e1e0d9"
AXIS = "#c3c2b7"
C1, C2, C3, C4, C5 = "#2a78d6", "#eb6834", "#1baf7a", "#eda100", "#e87ba4"

plt.rcParams["font.family"] = ["Segoe UI", "DejaVu Sans"]


def load(name):
    with open(RESULTS / name, newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def series(rows, key_field, key, x_field, filters=None):
    pts = []
    for row in rows:
        if row[key_field] != key:
            continue
        if filters and any(row[f] != v for f, v in filters.items()):
            continue
        pts.append((int(row[x_field]), float(row["median_s"])))
    return sorted(pts)


def new_axes(title, xlabel, ylabel):
    fig, ax = plt.subplots(figsize=(8, 5), dpi=150, facecolor=SURFACE)
    ax.set_facecolor(SURFACE)
    ax.set_xscale("log", base=2)
    ax.set_yscale("log")
    ax.set_title(title, color=INK, fontsize=12, pad=12, loc="left")
    ax.set_xlabel(xlabel, color=INK_2, fontsize=10)
    ax.set_ylabel(ylabel, color=INK_2, fontsize=10)
    ax.grid(True, which="major", color=GRID, linewidth=0.8)
    ax.grid(False, which="minor")
    for spine in ("top", "right"):
        ax.spines[spine].set_visible(False)
    for spine in ("left", "bottom"):
        ax.spines[spine].set_color(AXIS)
    ax.tick_params(colors=MUTED, labelsize=9)
    ax.margins(x=0.12)
    return fig, ax


def plot_series(ax, pts, label, color, marker):
    xs = [p[0] for p in pts]
    ys = [p[1] for p in pts]
    ax.plot(xs, ys, label=label, color=color, marker=marker, linewidth=2, markersize=5)


def guide(ax, xs, fn, anchor, label):
    # 理論參考線：縮放到通過實測序列的第一個點，看斜率不看常數
    scale = anchor[1] / fn(anchor[0])
    ys = [fn(x) * scale for x in xs]
    ax.plot(xs, ys, color=MUTED, linewidth=1, linestyle=(0, (4, 4)))
    ax.annotate(label, (xs[-1], ys[-1]), color=MUTED, fontsize=8,
                xytext=(5, 0), textcoords="offset points", va="center",
                annotation_clip=False)


def finish(fig, ax, name, legend_loc="upper left"):
    ax.legend(loc=legend_loc, frameon=False, fontsize=9, labelcolor=INK_2)
    IMAGES.mkdir(parents=True, exist_ok=True)
    out = IMAGES / name
    fig.savefig(out, bbox_inches="tight", facecolor=SURFACE)
    plt.close(fig)
    print(f"saved {out}", flush=True)


def fig_sorting_random(rows):
    fig, ax = new_axes("Sorting algorithms, random input (log-log)",
                       "n (elements)", "median time (s)")
    algos = [
        ("insertion_sort", "Insertion sort", C1, "o"),
        ("merge_sort", "Merge sort", C2, "s"),
        ("heap_sort", "Heap sort", C3, "^"),
        ("quick_sort", "Quick sort", C4, "D"),
        ("builtin_sorted", "Built-in sorted (Timsort, C)", C5, "v"),
    ]
    for key, label, color, marker in algos:
        plot_series(ax, series(rows, "algorithm", key, "n", {"distribution": "random"}),
                    label, color, marker)

    ins = series(rows, "algorithm", "insertion_sort", "n", {"distribution": "random"})
    mer = series(rows, "algorithm", "merge_sort", "n", {"distribution": "random"})
    guide(ax, [p[0] for p in ins], lambda x: x * x, ins[0], "~ $n^2$")
    guide(ax, [p[0] for p in mer], lambda x: x * math.log2(x), mer[0], "~ $n \\log n$")
    finish(fig, ax, "sorting_random.png")


DIST_STYLES = [
    ("random", "random", C1, "o"),
    ("sorted", "sorted", C2, "s"),
    ("reversed", "reversed", C3, "^"),
    ("few_unique", "few unique (10 values)", C4, "D"),
]


def fig_quick_degeneration(rows):
    fig, ax = new_axes("Quick sort (Lomuto, last-element pivot) by input distribution",
                       "n (elements)", "median time (s)")
    for key, label, color, marker in DIST_STYLES:
        extra = " (worst case)" if key == "sorted" else ""
        plot_series(ax, series(rows, "algorithm", "quick_sort", "n", {"distribution": key}),
                    label + extra, color, marker)

    rand = series(rows, "algorithm", "quick_sort", "n", {"distribution": "random"})
    srt = series(rows, "algorithm", "quick_sort", "n", {"distribution": "sorted"})
    guide(ax, [p[0] for p in rand], lambda x: x * math.log2(x), rand[0], "~ $n \\log n$")
    guide(ax, [p[0] for p in srt], lambda x: x * x, srt[0], "~ $n^2$")
    finish(fig, ax, "quicksort_degeneration.png")


def fig_insertion_cases(rows):
    fig, ax = new_axes("Insertion sort by input distribution (best vs worst case)",
                       "n (elements)", "median time (s)")
    for key, label, color, marker in DIST_STYLES:
        extra = " (best case)" if key == "sorted" else ""
        plot_series(ax, series(rows, "algorithm", "insertion_sort", "n", {"distribution": key}),
                    label + extra, color, marker)

    srt = series(rows, "algorithm", "insertion_sort", "n", {"distribution": "sorted"})
    rand = series(rows, "algorithm", "insertion_sort", "n", {"distribution": "random"})
    guide(ax, [p[0] for p in srt], lambda x: x, srt[0], "~ $n$")
    guide(ax, [p[0] for p in rand], lambda x: x * x, rand[0], "~ $n^2$")
    finish(fig, ax, "insertion_best_case.png")


def fig_huffman(rows):
    fig, ax = new_axes("Huffman tree build: min-heap vs legacy re-sorting",
                       "k (distinct symbols)", "median time (s)")
    heap_pts = series(rows, "implementation", "heapq", "k")
    legacy_pts = series(rows, "implementation", "legacy_sorted_list", "k")
    plot_series(ax, heap_pts, "heapq, $O(k \\log k)$", C1, "o")
    plot_series(ax, legacy_pts, "legacy re-sort, $O(k^2 \\log k)$", C2, "s")

    guide(ax, [p[0] for p in heap_pts], lambda x: x * math.log2(x), heap_pts[0], "~ $k \\log k$")
    guide(ax, [p[0] for p in legacy_pts], lambda x: x * x * math.log2(x), legacy_pts[0],
          "~ $k^2 \\log k$")
    finish(fig, ax, "huffman_build.png")


if __name__ == "__main__":
    sorting_rows = load("sorting.csv")
    huffman_rows = load("huffman.csv")
    fig_sorting_random(sorting_rows)
    fig_quick_degeneration(sorting_rows)
    fig_insertion_cases(sorting_rows)
    fig_huffman(huffman_rows)
