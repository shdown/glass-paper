#!/usr/bin/env python3

# (c) 2025 shdown
# This code is licensed under MIT license (see LICENSE.MIT for details)


def gcdex(a, b):
    x, x1 = 0, 1
    g, g1 = b, a

    while g:
        d = g1 // g
        g1, g = g, g1 - d * g
        x1, x = x, x1 - d * x

    if b:
        y = (g1 - x1 * a) // b
    else:
        y = 0

    return x1, y


def modulo(a, b):
    a %= b
    if a < 0:
        a += b
    return a


def invmod(a, n):
    x, y = gcdex(a, n)
    assert a * x + n * y == 1
    return modulo(x, n)


def power_of_two_decompose(n):
    assert n > 0
    lz = 0
    while not (n & 1):
        lz += 1
        n >>= 1
    return n, lz


MAX_C = 20


def main():
    M = 1 << 32

    first = True
    for c in range(1, MAX_C + 1):
        odd_part, lz = power_of_two_decompose(c)
        c1 = invmod(odd_part, M)

        directive = 'if' if first else 'elif'
        first = False
        print(f'#{directive} GLASS__C == {c}')
        print(f'GLASS__CASE({c1}, {lz})')

    print('#else')
    print('#error "Unsupported GLASS__C."')
    print('#endif')


if __name__ == '__main__':
    main()
