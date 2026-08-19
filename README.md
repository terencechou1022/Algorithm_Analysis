# 經典演算法實作與複雜度分析

> 六個經典演算法的 Python 手寫實作：正確性測試、理論與實測的複雜度對照，以及兩個由此延伸的命令列工具。

[![CI](https://github.com/terencechou1022/Algorithm_Analysis/actions/workflows/ci.yml/badge.svg)](https://github.com/terencechou1022/Algorithm_Analysis/actions/workflows/ci.yml)

六個演算法都是不借用現成函式庫的手寫實作，每一個都從三個層面驗證：與 Python 內建實作對照的單元測試（共 68 項，涵蓋空輸入、單一元素、全重複、已排序、反向與固定 seed 的隨機案例）、理論複雜度的逐項推導，以及跨輸入規模與分佈的實測曲線對照（[docs/analysis.md](docs/analysis.md)）。實測數據不只用來確認理論，也用來挑戰它：同一份 quick sort 程式碼只改輸入分佈就退化為 O(n²)，4,096 筆資料慢了 180 倍；而「小資料量時插入排序較快」這個常見說法，在 n=128 的隨機輸入下就已經輸給合併排序。

其中霍夫曼編碼與 LCS 兩份實作進一步延伸為能處理真實檔案的命令列工具：[huffzip](tools/huffzip.py) 壓縮檔案並以 SHA-256 驗證位元組級完整還原，[minidiff](tools/minidiff.py) 做行級差異比較並與 `git diff` 對照驗證。這兩個工具在開發與驗收過程中各抓出一個真實缺陷（霍夫曼建樹在頻率平手時的順序依賴、minidiff 把 UTF-8 BOM 併入第一行造成的誤判），都已補上回歸測試。

## 收錄內容

| 演算法 | 分類 | 平均時間 | 最壞時間 | 額外空間 | 原始碼 |
|--------|------|----------|----------|----------|--------|
| 插入排序 Insertion Sort | 排序 | O(n²) | O(n²) | O(1) | [sorting.py](src/algorithms/sorting.py) |
| 合併排序 Merge Sort | 排序 | O(n log n) | O(n log n) | O(n) | [sorting.py](src/algorithms/sorting.py) |
| 堆積排序 Heap Sort | 排序 | O(n log n) | O(n log n) | O(log n)¹ | [sorting.py](src/algorithms/sorting.py) |
| 快速排序 Quick Sort | 排序 | O(n log n) | O(n²)² | O(log n) | [sorting.py](src/algorithms/sorting.py) |
| 霍夫曼編碼 Huffman Coding | 貪婪 | O(n + k log k) | O(n + k log k) | O(k) | [huffman.py](src/algorithms/huffman.py) |
| 最長共同子序列 LCS | 動態規劃 | O(mn) | O(mn) | O(mn) | [lcs.py](src/algorithms/lcs.py) |

¹ 本實作的 heapify 為遞迴版本，呼叫堆疊深度 O(log n)。
² 採 CLRS 的 Lomuto 分割（固定取尾端元素當樞軸），已排序輸入會退化為 O(n²)。這是刻意保留的教科書行為，退化曲線的實測見 [docs/analysis.md](docs/analysis.md)。

## 快速開始

```bash
git clone https://github.com/terencechou1022/Algorithm_Analysis.git
cd Algorithm_Analysis
pip install -e ".[dev]"
pytest
```

```python
from algorithms import quick_sort
from algorithms.huffman import build_freq_map, build_huffman_tree, generate_huffman_codes
from algorithms.lcs import lcs

quick_sort([5, 2, 8, 4, 9, 1])   # [1, 2, 4, 5, 8, 9]
lcs("ABCBDAB", "BDCABA")         # (4, 'BCBA')

codes = generate_huffman_codes(build_huffman_tree(build_freq_map("aaabbc")))
```

## 效能實測分析

完整方法論與解讀在 [docs/analysis.md](docs/analysis.md)，數據與腳本在 [benchmarks/](benchmarks/)。兩個代表性結果：

![四種排序在隨機輸入下的實測曲線](docs/images/sorting_random.png)

四種手寫排序與內建 `sorted()` 的實測曲線（log-log）：merge、heap、quick 的斜率貼合 n log n 參考線，insertion 貼合 n²；C 實作的 Timsort 比最快的手寫排序仍快一個數量級。

![快速排序在不同輸入分佈下的退化](docs/images/quicksort_degeneration.png)

同一份 quick sort 程式碼，只改輸入分佈：已排序輸入退化為 O(n²)，4,096 筆資料比隨機輸入慢 180 倍。理論上的最壞情況，實測看得見。

## 從理論到工具

### huffzip

[tools/huffzip.py](tools/huffzip.py) 把霍夫曼編碼實作變成能壓縮真實檔案的 CLI：逐位元組統計頻率、位元流打包、檔頭帶頻率表，解壓端重建同一棵樹。

```bash
python tools/huffzip.py compress   benchmarks/results/sorting.csv  sorting.huff
python tools/huffzip.py compress   docs/analysis.md                analysis.huff
python tools/huffzip.py decompress sorting.huff  restored.csv
```

實際結果（端對端測試以 SHA-256 驗證位元組級完全還原）：

```
sorting.csv: 17,759 bytes -> 10,217 bytes (57.5% of original)
analysis.md:  6,140 bytes ->  6,175 bytes (100.6% of original)
```

第二行是刻意保留的反例：[docs/analysis.md](docs/analysis.md) 以 UTF-8 中文為主，位元組分佈平坦，單符號霍夫曼編碼吃不到便宜，加上檔頭後反而變大。壓縮效果取決於輸入的位元組熵，這正是理論落在真實檔案上的樣子。

（這兩行是某次執行的實際輸出。`analysis.md` 的內容一改，位元組數與比率就會跟著變——**超過 100% 這件事才是重點**，不是那個特定數字。）

### minidiff

[tools/minidiff.py](tools/minidiff.py) 用同一份 LCS 實作做行級檔案比較：兩個檔案的「最長共同行序列」就是 LCS，不在其中的行即為差異。

```bash
python tools/minidiff.py old.py new.py
```

```
  def total(items):
-     result = 0
-     for x in items:
-         result += x
+     result = sum(items)
      return result
```

端對端測試除了已知案例，還驗證兩個性質：由 diff 輸出可完整重建兩個原檔，且在無歧義的案例下與 `git diff --no-index` 的差異行完全一致。

## 測試怎麼寫

- 四種排序：與 Python 內建 `sorted()` 對照，涵蓋空列表、單一元素、全重複、已排序、反向、負數、浮點數，以及固定 seed 的隨機案例
- LCS：CLRS 書中案例之外，另以隨機字串與暴力解（列舉全部子序列）對照長度，並驗證回傳字串確實是共同子序列
- 霍夫曼：驗證編碼再解碼可完整還原、前綴碼性質、示範頻率表的加權編碼長度，以及單一字元與空輸入的退化情況

## 專案結構

```
src/algorithms/    # 演算法本體（安裝為 Python 套件）
tests/             # pytest 測試
benchmarks/        # 效能量測與繪圖腳本、實測數據 CSV
tools/             # huffzip 等示範 CLI 工具
docs/              # 分析文件與效能圖表
.github/workflows/ # CI：ruff 靜態檢查 + pytest
```

## 後續規劃

- [x] 效能實測：多種輸入規模與分佈的 benchmark，理論 vs 實測曲線分析（[docs/analysis.md](docs/analysis.md)）
- [x] huffzip：以霍夫曼編碼實作、能壓縮真實檔案的 CLI 工具（[tools/huffzip.py](tools/huffzip.py)）
- [x] minidiff：以 LCS 實作的檔案差異比較工具（[tools/minidiff.py](tools/minidiff.py)）
