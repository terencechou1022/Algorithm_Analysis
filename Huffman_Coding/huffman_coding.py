import re

class TreeNode:
    def __init__(self, char=None, freq=0):
        self.char = char # 字元
        self.freq = freq # 頻率
        self.left = None # 左子樹
        self.right = None # 右子樹

    def __lt__(self, other):
        # 當頻率相同時，依照字元排序
        if self.freq == other.freq:
            return str(self.char) < str(other.char)
        else:
            return self.freq < other.freq

    def __repr__(self):
        if self.char:
            return f"('{self.char}', {self.freq})"
        else:
            return f"({self.freq})"

def build_freq_map(input_str):
    fixed_str = re.sub(r'([a-zA-Z])(?=\s*:)', r"'\1'", input_str) # 處理 key 非字串的情況（加上單引號）
    char_freq = eval('{' + fixed_str + '}') # 轉換成字典
    return {str(k): v for k, v in char_freq.items()}

def build_huffman_tree(char_freq):
    # 將所有字元和頻率建立為節點並儲存在列表中
    nodes = [TreeNode(char, freq) for char, freq in char_freq.items()]
    nodes = sorted(nodes)

    while len(nodes) > 1:
        x = nodes.pop(0) # 取出頻率最小的節點 x
        y = nodes.pop(0) # 取出頻率次小的節點 y

        # 確保左子節點一定小於等於右子節點
        if (y.freq < x.freq) or (y.freq == x.freq and str(y.char) < str(x.char)):
            x, y = y, x

        z = TreeNode(freq=x.freq + y.freq) # 建立新節點 z
        z.left = x
        z.right = y

        # 把新節點 z 放回列表中，繼續參與後續合併
        nodes.append(z)
        nodes = sorted(nodes)

    root = nodes[0] # 當迴圈結束時，列表中只剩下根節點

    return root

def generate_huffman_codes(node, code_str='', char_code={}):
    if node is not None:
        # 若遇到葉節點（有字元），代表這條編碼路徑結束
        if node.char is not None:
            char_code[node.char] = code_str # 儲存葉節點的編碼字串
            print(f'{node.char} → {code_str}')

        generate_huffman_codes(node.left, code_str + '0', char_code) # 遞迴往左子樹走，編碼字串增加 '0'
        generate_huffman_codes(node.right, code_str + '1', char_code) # 遞迴往右子樹走，編碼字串增加 '1'

    return char_code

if __name__ == '__main__':
    input_str = 'a:13,b:7,c:12,d:9,e:55,f:4'
    char_freq = build_freq_map(input_str)
    root = build_huffman_tree(char_freq)
    char_code = generate_huffman_codes(root)