"""霍夫曼編碼測試：示範頻率表的加權長度、前綴性質、編解碼往返與邊界案例。"""

import random
from collections import Counter

from algorithms.huffman import (
    build_freq_map,
    build_huffman_tree,
    decode,
    encode,
    generate_huffman_codes,
)

# 示範用頻率表（沿用最初版本的範例輸入）
SAMPLE_FREQ = {"a": 13, "b": 7, "c": 12, "d": 9, "e": 55, "f": 4}


def test_sample_freq_weighted_length():
    root = build_huffman_tree(SAMPLE_FREQ)
    codes = generate_huffman_codes(root)

    # 最優編碼的加權總長度 = Σ(頻率 × 編碼長度)
    weighted = sum(SAMPLE_FREQ[char] * len(code) for char, code in codes.items())
    assert weighted == 201
    assert len(codes["e"]) == 1  # 頻率最高的字元拿到最短編碼


def test_prefix_property():
    codes = generate_huffman_codes(build_huffman_tree(SAMPLE_FREQ))
    values = list(codes.values())

    # 前綴碼性質：任一編碼都不能是另一編碼的前綴，否則解碼會有歧義
    for a in values:
        for b in values:
            if a != b:
                assert not b.startswith(a)


def test_encode_decode_roundtrip():
    rng = random.Random(99)
    for _ in range(20):
        text = "".join(rng.choice("abcdef ") for _ in range(rng.randint(1, 200)))

        root = build_huffman_tree(build_freq_map(text))
        codes = generate_huffman_codes(root)

        assert decode(encode(text, codes), root) == text


def test_single_distinct_char():
    text = "aaaa"
    root = build_huffman_tree(build_freq_map(text))
    codes = generate_huffman_codes(root)

    assert codes == {"a": "0"}  # 退化樹：單一字元的編碼定為 "0"
    assert decode(encode(text, codes), root) == text


def test_empty_input():
    assert build_freq_map("") == {}
    assert build_huffman_tree({}) is None
    assert generate_huffman_codes(None) == {}
    assert encode("", {}) == ""
    assert decode("", None) == ""


def test_tree_independent_of_dict_insertion_order():
    # 內部節點頻率平手時，建樹結果不得依賴頻率表的插入順序：
    # 壓縮端（Counter 首見順序）與解壓端（排序後順序）必須重建出同一棵樹
    text = "Huffman coding assigns shorter codes to more frequent symbols. " * 3
    freq_counter_order = dict(Counter(text))
    freq_sorted_order = dict(sorted(freq_counter_order.items()))

    codes_a = generate_huffman_codes(build_huffman_tree(freq_counter_order))
    codes_b = generate_huffman_codes(build_huffman_tree(freq_sorted_order))
    assert codes_a == codes_b


def test_codes_do_not_leak_between_calls():
    # 舊版以可變預設參數累積編碼表，兩次呼叫會互相污染；此測試鎖定修正後的行為
    codes_1 = generate_huffman_codes(build_huffman_tree({"a": 1, "b": 2}))
    codes_2 = generate_huffman_codes(build_huffman_tree({"x": 3, "y": 4}))

    assert set(codes_1) == {"a", "b"}
    assert set(codes_2) == {"x", "y"}
