FIBONACCI = {0: 0, 1: 1}

def fibonacci(n: int) -> int:
    if n in FIBONACCI:
        return FIBONACCI[n]
    result = fibonacci(n-1) + fibonacci(n-2)
    FIBONACCI[n] = result
    return result