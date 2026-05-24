def LCS(X, Y):
    m = len(X) # X 字串長度為 m
    n = len(Y) # Y 字串長度為 n

    # 建立 (m+1)*(n+1) 的二維矩陣 C 並預設所有元素為 0
    C = []
    for i in range(m + 1):
        row = []
        for j in range(n + 1):
            row.append(0)
        C.append(row)

    # 填表格
    for i in range(1, m + 1):
        for j in range(1, n + 1):
            # 若當前字元相同，表示這個字元屬於 LCS 字串
            if X[i - 1] == Y[j - 1]:
                C[i][j] = C[i - 1][j - 1] + 1 # 對角線(左上)的值加 1
            # 若當前字元不同，表示這個字元不屬於 LCS 字串
            elif C[i - 1][j] == C[i][j - 1]:
                C[i][j] = C[i - 1][j] # 若上面等於左邊，固定取上面
                # C[i][j] = C[i][j - 1] # 若上面等於左邊，固定取左邊
            else:
                C[i][j] = max(C[i - 1][j], C[i][j - 1]) # 上面和左邊取最大值

    print(f"LCS 長度: {C[m][n]}")

    # 回溯找出實際的 LCS 字串
    i, j = m, n
    lcs = []

    # 當 i 或 j 等於 0 時，表示已經回溯到邊界，跳出迴圈
    while i > 0 and j > 0:
        # 若當前字元相同，表示這個字元屬於 LCS 字串
        if X[i - 1] == Y[j - 1]:
            lcs.append(X[i - 1])
            # 往對角線(左上)回溯
            i -= 1
            j -= 1
        # 若當前字元不同，表示這個字元不屬於 LCS 字串
        elif C[i - 1][j] >= C[i][j - 1]:
            i -= 1 # 若上面大於等於左邊，往上回溯
        else:
            j -= 1 # 往左回溯
        # elif C[i - 1][j] <= C[i][j - 1]:
        #   j -= 1 # 若上面小於等於左邊，往左回溯
        # else:
        #   i -= 1 # 往上回溯

    lcs.reverse() # 因為是往前回溯，所以要反轉字串

    print(f"LCS 字串: {''.join(lcs)}")

if __name__ == '__main__':
    X = 'ABCBDAB'
    Y = 'BDCABA'
    LCS(X, Y)