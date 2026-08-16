"""huffzip CLI 端對端測試：以子行程實際執行壓縮與解壓，驗證位元組層級完全還原。"""

import hashlib
import subprocess
import sys
from pathlib import Path

TOOL = Path(__file__).resolve().parents[1] / "tools" / "huffzip.py"


def _run(*args):
    result = subprocess.run(
        [sys.executable, str(TOOL), *args], capture_output=True, text=True
    )
    assert result.returncode == 0, result.stderr
    return result.stdout


def _roundtrip(tmp_path, payload):
    """壓縮再解壓，以 SHA-256 驗證與原始內容完全一致；回傳壓縮檔大小。"""
    src = tmp_path / "src.bin"
    packed = tmp_path / "src.huff"
    restored = tmp_path / "restored.bin"
    src.write_bytes(payload)

    _run("compress", str(src), str(packed))
    _run("decompress", str(packed), str(restored))

    original_hash = hashlib.sha256(payload).hexdigest()
    restored_hash = hashlib.sha256(restored.read_bytes()).hexdigest()
    assert restored_hash == original_hash

    return packed.stat().st_size


def test_text_roundtrip_and_shrinks(tmp_path):
    text = ("Huffman coding assigns shorter codes to more frequent symbols. " * 200).encode()
    compressed_size = _roundtrip(tmp_path, text)
    assert compressed_size < len(text)  # 高冗餘文字檔應確實變小


def test_binary_roundtrip(tmp_path):
    # 均勻分佈的位元組是霍夫曼的最劣輸入，可能不會變小，但還原必須完全正確
    payload = bytes(range(256)) * 40
    _roundtrip(tmp_path, payload)


def test_single_byte_value(tmp_path):
    _roundtrip(tmp_path, b"a" * 1000)  # 退化樹：只有一種位元組值


def test_empty_file(tmp_path):
    _roundtrip(tmp_path, b"")
