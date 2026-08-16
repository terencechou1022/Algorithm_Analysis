"""四種經典排序演算法：插入、合併、堆積、快速。

統一介面：每個函式接受一個列表，就地排序後回傳同一個列表。
實作結構依 CLRS《Introduction to Algorithms》的虛擬碼寫法。
"""


def insertion_sort(A):
    """插入排序：平均與最壞 O(n^2)，額外空間 O(1)，穩定排序。"""
    # 從第 2 個元素開始，逐一把元素插入左側已排序區
    for j in range(1, len(A)):
        key = A[j]  # 取出當前元素作為 key
        i = j - 1

        # 當 key 小於前一個元素時，將較大元素往後移
        while i >= 0 and key < A[i]:
            A[i + 1] = A[i]  # 將前一個元素往後移動
            i = i - 1  # 繼續往前比較

        A[i + 1] = key  # 將 key 插入正確位置

    return A


def merge_sort(A):
    """合併排序：任何情況 O(n log n)，額外空間 O(n)，穩定排序。"""
    _merge_sort(A, 0, len(A) - 1)
    return A


def _merge_sort(A, p, r):
    if p < r:
        q = (p + r) // 2  # 取中點
        _merge_sort(A, p, q)  # 排序左半部
        _merge_sort(A, q + 1, r)  # 排序右半部
        _merge(A, p, q, r)  # 合併兩部分


def _merge(A, p, q, r):
    L = A[p:q + 1]  # 複製左子陣列
    R = A[q + 1:r + 1]  # 複製右子陣列
    i = 0  # 左子陣列索引
    j = 0  # 右子陣列索引
    k = p  # 寫回原陣列的位置

    # 雙指標合併：兩邊都還有元素時，取開頭較小者放回原陣列
    # （相等時取左邊以維持穩定性；不依賴無限大哨兵，任何可比較型別都能排序）
    while i < len(L) and j < len(R):
        if L[i] <= R[j]:
            A[k] = L[i]
            i += 1
        else:
            A[k] = R[j]
            j += 1
        k += 1

    # 其中一邊取完後，把另一邊剩餘元素依序放回
    A[k:r + 1] = L[i:] if i < len(L) else R[j:]


def heap_sort(A):
    """堆積排序：任何情況 O(n log n)，額外空間 O(log n)（遞迴 heapify），不穩定。"""
    heap_size = len(A)
    _build_max_heap(A)  # 確保根節點為最大值

    # 反覆把目前的最大值換到未排序區的尾端
    for i in range(len(A) - 1, 0, -1):
        A[0], A[i] = A[i], A[0]  # 根節點與未排序區最後一個節點交換
        heap_size -= 1  # 已排序區擴大，堆積範圍縮小
        _max_heapify(A, 0, heap_size)  # 重新維持 Max Heap 性質

    return A


def _build_max_heap(A):
    heap_size = len(A)

    # 從最後一個非葉節點開始，由下而上建堆
    for i in range(len(A) // 2 - 1, -1, -1):
        _max_heapify(A, i, heap_size)


def _max_heapify(A, i, heap_size):
    left = 2 * i + 1  # 左子節點索引
    right = 2 * i + 2  # 右子節點索引
    largest = i  # 先假設當前節點是最大值

    # 左子節點在堆積範圍內且更大時，更新最大值索引
    if left < heap_size and A[left] > A[largest]:
        largest = left

    # 右子節點在堆積範圍內且更大時，更新最大值索引
    if right < heap_size and A[right] > A[largest]:
        largest = right

    if largest != i:
        A[i], A[largest] = A[largest], A[i]  # 交換節點值
        _max_heapify(A, largest, heap_size)  # 遞迴調整受影響的子樹


def quick_sort(A):
    """快速排序：平均 O(n log n)，最壞 O(n^2)（例如已排序輸入），不穩定。

    採 CLRS 的 Lomuto 分割，固定取子陣列最後一個元素當樞軸，
    因此已排序輸入會退化為 O(n^2) 且遞迴深度達 O(n)。
    這是刻意保留的教科書行為，用來與其他排序做特性對照。
    """
    _quick_sort(A, 0, len(A) - 1)
    return A


def _quick_sort(A, p, r):
    if p < r:  # 子陣列長度大於 1 時才需要處理
        q = _partition(A, p, r)  # 分割並取得樞軸最終位置
        _quick_sort(A, p, q - 1)  # 遞迴排序左半部
        _quick_sort(A, q + 1, r)  # 遞迴排序右半部


def _partition(A, p, r):
    x = A[r]  # 取最後一個元素作為樞軸
    i = p - 1  # i 是「小於等於樞軸區」的右邊界

    for j in range(p, r):
        if A[j] <= x:  # A[j] 應歸入小於等於樞軸區
            i += 1
            A[i], A[j] = A[j], A[i]

    A[i + 1], A[r] = A[r], A[i + 1]  # 樞軸放到正確位置
    return i + 1
