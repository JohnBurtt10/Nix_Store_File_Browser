def n_choose_k_count(n, k):
    """
    computes the number of combinations of choosing k elements from a set of n elements using factorials and integer division
    """
    
    numerator = 1
    denominator = 1
    for i in range(1, min(k, n - k) + 1):
        numerator *= n - i + 1
        denominator *= i
    return numerator // denominator