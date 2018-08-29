

def of(n):
    factors = []
    divisor = 2
    while n > 1:
        while n % divisor == 0:
            factors.append(divisor)
            n /= divisor
        divisor += 1
    if n > 1:
        factors.append(n)
    return factors
