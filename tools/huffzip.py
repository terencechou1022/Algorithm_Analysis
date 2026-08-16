"""huffzip：以本專案的霍夫曼編碼實作，壓縮與解壓真實檔案的示範 CLI。

用法（於 repo 根目錄，需先 pip install -e "."）：
    python tools/huffzip.py compress   input.txt   output.huff
    python tools/huffzip.py decompress output.huff restored.txt

.huff 檔案格式：
    magic     4 bytes   b"HUF1"
    orig_len  8 bytes   原始檔案位元組數（little-endian）
    k         2 bytes   相異位元組值數量（0~256，little-endian）
    entries   k 組      [位元組值 1 byte][出現次數 8 bytes LE]
    payload   其餘      編碼位元流打包成的位元組（尾端補 0）

解壓端以頻率表重建霍夫曼樹。build_huffman_tree 的建樹結果只取決於
頻率表內容（與字典插入順序無關），因此兩端重建出的樹保證相同，
編碼可正確還原。
"""

import argparse
import sys
from collections import Counter
from pathlib import Path

from algorithms.huffman import build_huffman_tree, generate_huffman_codes

MAGIC = b"HUF1"


def compress(src, dst):
    data = src.read_bytes()
    freq = Counter(data)  # 位元組值 (0~255) -> 出現次數

    # 組 header：magic + 原始長度 + 頻率表
    header = bytearray(MAGIC)
    header += len(data).to_bytes(8, "little")
    header += len(freq).to_bytes(2, "little")
    for value, count in sorted(freq.items()):
        header += bytes([value]) + count.to_bytes(8, "little")

    # 逐位元組編碼成位元字串，再每 8 位打包成 1 byte（尾端補 0）
    codes = generate_huffman_codes(build_huffman_tree(freq))
    bits = "".join(codes[byte] for byte in data)
    payload = bytearray()
    for i in range(0, len(bits), 8):
        payload.append(int(bits[i:i + 8].ljust(8, "0"), 2))

    dst.write_bytes(bytes(header) + bytes(payload))

    original = len(data)
    compressed = dst.stat().st_size
    if original:
        print(f"{src.name}: {original:,} bytes -> {compressed:,} bytes "
              f"({compressed / original:.1%} of original)")
    else:
        print(f"{src.name}: empty file -> {compressed:,} bytes (header only)")


def decompress(src, dst):
    blob = src.read_bytes()
    if blob[:4] != MAGIC:
        sys.exit(f"{src.name} 不是 huffzip 檔案（magic 不符）")

    orig_len = int.from_bytes(blob[4:12], "little")
    k = int.from_bytes(blob[12:14], "little")

    # 讀回頻率表
    freq = {}
    offset = 14
    for _ in range(k):
        value = blob[offset]
        freq[value] = int.from_bytes(blob[offset + 1:offset + 9], "little")
        offset += 9

    root = build_huffman_tree(freq)
    out = bytearray()

    if orig_len and root is not None:
        if root.char is not None:
            # 退化樹：整個檔案只有一種位元組值
            out = bytearray([root.char] * orig_len)
        else:
            # 沿樹走訪位元流：0 往左、1 往右，到葉節點輸出並回到根
            node = root
            done = False
            for byte in blob[offset:]:
                for bit_pos in range(7, -1, -1):  # 打包時高位元在前，展開順序須一致
                    node = node.left if (byte >> bit_pos) & 1 == 0 else node.right
                    if node.char is not None:
                        out.append(node.char)
                        if len(out) == orig_len:  # 達到原始長度即停止，忽略尾端補 0
                            done = True
                            break
                        node = root
                if done:
                    break

    dst.write_bytes(bytes(out))
    print(f"{src.name}: restored {len(out):,} bytes -> {dst.name}")


def main():
    parser = argparse.ArgumentParser(description="霍夫曼編碼檔案壓縮示範工具")
    sub = parser.add_subparsers(dest="command", required=True)
    for name, help_text in (("compress", "壓縮檔案"), ("decompress", "解壓 .huff 檔案")):
        p = sub.add_parser(name, help=help_text)
        p.add_argument("input", type=Path)
        p.add_argument("output", type=Path)
    args = parser.parse_args()

    if args.command == "compress":
        compress(args.input, args.output)
    else:
        decompress(args.input, args.output)


if __name__ == "__main__":
    main()
