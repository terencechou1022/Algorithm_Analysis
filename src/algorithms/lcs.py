"""最長共同子序列（Longest Common Subsequence, LCS），動態規劃解法。"""


def lcs_sequence(X, Y):
    """回傳 X 與 Y 的其中一組最長共同子序列，以 list 呈現。

    X、Y 可為字串或任何支援索引與相等比較的序列（例如檔案的行列表）。
    時間 O(mn)、空間 O(mn)。填表與回溯規則依 CLRS 慣例：
    值相等時優先往上回溯，因此結果具決定性、可重現。
    """
    m = len(X)  # X 序列長度
    n = len(Y)  # Y 序列長度

    # 建立 (m+1) x (n+1) 的 DP 表格，C[i][j] 代表 X 前 i 項與 Y 前 j 項的 LCS 長度
    C = [[0] * (n + 1) for _ in range(m + 1)]

    # 填表
    for i in range(1, m + 1):
        for j in range(1, n + 1):
            # 當前元素相同：這個元素屬於 LCS，長度為左上角的值加 1
            if X[i - 1] == Y[j - 1]:
                C[i][j] = C[i - 1][j - 1] + 1
            # 當前元素不同：取上方與左方的較大值
            else:
                C[i][j] = max(C[i - 1][j], C[i][j - 1])

    # 回溯找出實際的 LCS 內容
    i, j = m, n
    items = []

    while i > 0 and j > 0:
        # 元素相同：屬於 LCS，往左上回溯
        if X[i - 1] == Y[j - 1]:
            items.append(X[i - 1])
            i -= 1
            j -= 1
        # 上方大於等於左方：往上回溯（相等時固定取上方，確保結果唯一）
        elif C[i - 1][j] >= C[i][j - 1]:
            i -= 1
        else:
            j -= 1

    items.reverse()  # 回溯是由後往前收集，需反轉
    return items


def lcs(X, Y):
    """回傳 (LCS 長度, 其中一組 LCS 字串)，為 lcs_sequence 的字串介面。"""
    seq = lcs_sequence(X, Y)
    return len(seq), "".join(seq)
