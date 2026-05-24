def insert_sort(A):
    # 從第 2 個元素開始
    for j in range(1, len(A)):
        key = A[j] # 取出當前元素作為 key
        i = j - 1

        # 當 key 小於前一個元素時，將較大元素往後移
        while i >= 0 and key < A[i]:
            A[i + 1] = A[i] # 將前一個元素往後移動
            i = i - 1 # 繼續往前比較

        A[i + 1] = key # 將 key 插入正確位置

    return A

if __name__ == '__main__':
    A = [5, 2, 8, 4, 9, 1]
    insert_sort(A)
    print(A)