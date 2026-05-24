def merge(A, p, q, r):
    n1 = q - p + 1 # 左子陣列長度
    n2 = r - q # 右子陣列長度

    # 建立左右兩個子陣列
    L = A[p:p + n1] + [float('inf')]
    R = A[q + 1:q + 1 + n2] + [float('inf')]
    i = 0 # 左子陣列索引
    j = 0 # 右子陣列索引

    # 合併兩個子陣列
    for k in range(p, r + 1):
        # 當左子陣列的元素小於右子陣列的元素時
        if L[i] <= R[j]:
            A[k] = L[i]
            i += 1
        # 當右子陣列的元素小於左子陣列的元素時
        else:
            A[k] = R[j]
            j += 1

def merge_sort(A, p, r):
    if p < r:
        q = (p + r) // 2 # 取中點
        merge_sort(A, p, q) # 排序左半部
        merge_sort(A, q + 1, r) # 排序右半部
        merge(A, p, q, r) # 合併兩部分

    return A

if __name__ == '__main__':
    A = [5, 2, 8, 4, 9, 1]
    merge_sort(A, 0, len(A) - 1)
    print(A)