"""霍夫曼編碼（Huffman Coding）：以最小堆積建樹的貪婪演算法，含編碼與解碼。"""

import heapq
from collections import Counter


class TreeNode:
    """霍夫曼樹節點：葉節點帶字元，內部節點只帶頻率總和。"""

    def __init__(self, char=None, freq=0):
        self.char = char  # 字元（內部節點為 None）
        self.freq = freq  # 頻率
        self.left = None  # 左子樹
        self.right = None  # 右子樹

    def __lt__(self, other):
        # 頻率相同時依字元字典序，確保建樹結果具決定性
        return (self.freq, str(self.char)) < (other.freq, str(other.char))

    def __repr__(self):
        if self.char is not None:
            return f"('{self.char}', {self.freq})"
        return f"({self.freq})"


def build_freq_map(text):
    """統計字串中每個字元的出現頻率。"""
    return dict(Counter(text))


def build_huffman_tree(char_freq):
    """以最小堆積反覆合併頻率最小的兩個節點，O(k log k)，k 為相異字元數。"""
    if not char_freq:
        return None

    # 先依 (頻率, 字元) 排序固定初始排列：內部節點頻率平手時的合併順序因此
    # 只取決於頻率表「內容」，與字典插入順序無關（解壓端重建同一棵樹的前提）；
    # 排序後的列表本身即滿足最小堆積性質，可直接作為 heapq 的堆積使用
    heap = sorted(TreeNode(char, freq) for char, freq in char_freq.items())

    while len(heap) > 1:
        x = heapq.heappop(heap)  # 頻率最小的節點
        y = heapq.heappop(heap)  # 頻率次小的節點

        z = TreeNode(freq=x.freq + y.freq)  # 合併為新的內部節點
        z.left = x  # 較小者為左子樹
        z.right = y

        heapq.heappush(heap, z)  # 放回堆積繼續參與合併

    return heap[0]  # 最後剩下的節點即為根


def generate_huffman_codes(root):
    """走訪霍夫曼樹產生編碼表：往左補 0、往右補 1。"""
    codes = {}

    def _walk(node, prefix):
        if node is None:
            return
        # 葉節點：這條路徑即為該字元的編碼
        if node.char is not None:
            codes[node.char] = prefix or "0"  # 樹只有單一葉節點時，編碼定為 "0"
            return
        _walk(node.left, prefix + "0")
        _walk(node.right, prefix + "1")

    _walk(root, "")
    return codes


def encode(text, codes):
    """依編碼表把字串轉為 0/1 位元字串。"""
    return "".join(codes[char] for char in text)


def decode(bits, root):
    """沿霍夫曼樹走訪位元字串，還原為原始字串。"""
    if root is None or not bits:
        return ""

    # 退化情況：樹只有單一葉節點，每個位元對應同一個字元
    if root.char is not None:
        return root.char * len(bits)

    chars = []
    node = root
    for bit in bits:
        node = node.left if bit == "0" else node.right
        # 走到葉節點：輸出字元並回到根重新開始
        if node.char is not None:
            chars.append(node.char)
            node = root

    return "".join(chars)
