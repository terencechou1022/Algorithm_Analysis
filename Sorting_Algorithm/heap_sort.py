def max_heapify(A, i, heap_size):
    l = 2 * i + 1 # 左子節點索引
    r = 2 * i + 2 # 右子節點索引

    largest = i # 先假設當前節點是最大值

    # 當左子節點在堆積範圍內，且比當前最大值大時
    if l < heap_size and A[l] > A[largest]:
        largest = l # 更新最大值索引

    # 當右子節點在堆積範圍內，且比當前最大值大時
    if r < heap_size and A[r] > A[largest]:
        largest = r # 更新最大值索引

    if largest != i:
        A[i], A[largest] = A[largest], A[i] # 交換節點值
        max_heapify(A, largest, heap_size) # 遞迴調整子樹

def build_max_heap(A):
    heap_size = len(A)

    # 從最後一個非葉節點開始
    for i in range(len(A) // 2 - 1, -1, -1):
        max_heapify(A, i, heap_size) # 維持 Max Heap 狀態

def heap_sort(A):
    heap_size = len(A)
    build_max_heap(A) # 確保根節點為最大值

    # 從最後一個葉節點開始
    for i in range(len(A) - 1, 0, -1):
        A[0], A[i] = A[i], A[0] # 根節點與當前最後一個葉節點交換
        heap_size -= 1 # 切除最大值
        max_heapify(A, 0, heap_size) # 維持 Max Heap 狀態

    return A

if __name__ == '__main__':
    A = [12, 38, 27, 34, 5, 20, 46, 15]
    heap_sort(A)
    print(A)