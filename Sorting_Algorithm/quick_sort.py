def partition(A, p, r):
    x = A[r] # 選擇最後一個元素作為樞軸
    i = p - 1 # 初始化 i 為 p - 1

    for j in range(p, r): # 遍歷 p 到 r-1 的元素
        if A[j] <= x: # 如果 A[j] 小於等於樞軸
            i += 1 # i 向右移動
            A[i], A[j] = A[j], A[i] # 交換 A[i] 和 A[j]

    A[i + 1], A[r] = A[r], A[i + 1] # 將樞軸放到正確的位置

    return i + 1 # 返回樞軸的索引

def quick_sort(A, p, r):
    if p < r: # 當子陣列的長度大於 1 時
        q = partition(A, p, r) # 進行分割，取得樞軸索引
        quick_sort(A, p, q - 1) # 遞迴對左半部排序
        quick_sort(A, q + 1, r) # 遞迴對右半部排序

    return A

if __name__ == '__main__':
    A = [5, 2, 8, 4, 9, 1]
    quick_sort(A, 0, len(A) - 1)
    print(A)