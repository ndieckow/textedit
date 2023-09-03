FIBONACCI = {0: 0, 1: 1}

def fibonacci(n: int) -> int:
    if n in FIBONACCI:
        return FIBONACCI[n]
    result = fibonacci(n-1) + fibonacci(n-2)
    FIBONACCI[n] = result
    return result

# TODO: store those 4 numbers in one place
def rc2px(line: int, pos: int) -> tuple[int, int]:
    x = 7 + pos * 8
    y = 3 + line * 15
    return x, y

def px2rc(x: int, y: int) -> tuple[int, int]:
    line = (y - 3) // 15  # floor works better for lines
    pos = round((x - 7) / 8)  # nearest rounding works better for pos
    return line, pos