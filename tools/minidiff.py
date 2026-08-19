"""minidiff：以本專案的 LCS 實作做行級檔案差異比較的示範 CLI。

用法（於 repo 根目錄，需先 pip install -e "."）：
    python tools/minidiff.py old.txt new.txt

輸出格式（簡化版 diff）：
    - 行   只存在於舊檔
    + 行   只存在於新檔
      行   兩檔共有

原理：兩個檔案的「最長共同行序列」就是 LCS 問題，把 algorithms.lcs 的
動態規劃解法從字元序列換成行序列即可；不在 LCS 中的行就是差異。
結束狀態碼比照 diff 慣例：檔案相同為 0，有差異為 1。
"""

import argparse
import sys
from pathlib import Path

from algorithms.lcs import lcs_sequence


def diff_lines(old_lines, new_lines):
    """回傳 (標記, 行內容) 串列；標記為 '-'、'+' 或 ' '。"""
    common = lcs_sequence(old_lines, new_lines)
    out = []
    i = 0  # 舊檔行索引
    j = 0  # 新檔行索引

    # 以 LCS 中的每一行為錨點：錨點前的舊檔行是刪除、新檔行是新增
    for anchor in common:
        while old_lines[i] != anchor:
            out.append(("-", old_lines[i]))
            i += 1
        while new_lines[j] != anchor:
            out.append(("+", new_lines[j]))
            j += 1
        out.append((" ", anchor))
        i += 1
        j += 1

    # 最後一個錨點之後的殘餘行
    out.extend(("-", line) for line in old_lines[i:])
    out.extend(("+", line) for line in new_lines[j:])
    return out


def main():
    parser = argparse.ArgumentParser(description="以 LCS 實作的行級檔案差異比較")
    parser.add_argument("old_file", type=Path)
    parser.add_argument("new_file", type=Path)
    args = parser.parse_args()

    sys.stdout.reconfigure(encoding="utf-8")  # 輸出固定 UTF-8，避免 Windows 主控台編碼問題

    try:
        # 用 utf-8-sig 讀取：Windows 上不少編輯器會在檔頭寫入 UTF-8 BOM，
        # 若不濾除，BOM 會併入第一行內容，使兩個內容相同的檔案被誤判為有差異
        old_lines = args.old_file.read_text(encoding="utf-8-sig").splitlines()
        new_lines = args.new_file.read_text(encoding="utf-8-sig").splitlines()
    except UnicodeDecodeError:
        sys.exit("minidiff 只支援 UTF-8 文字檔")

    diff = diff_lines(old_lines, new_lines)
    for marker, line in diff:
        print(f"{marker} {line}")

    has_changes = any(marker != " " for marker, _ in diff)
    sys.exit(1 if has_changes else 0)


if __name__ == "__main__":
    main()
