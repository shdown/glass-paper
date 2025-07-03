#!/usr/bin/env python3

# (c) 2025 shdown
# This code is licensed under MIT license (see LICENSE.MIT for details)

import math


K = 50
C = 5
L = math.ceil(K / C)


def max_num_of_nodes(s):
    r = K % C
    if not r:
        r = C

    sum_ = 0
    res = None

    for i in range(L):
        if i == 0:
            res = min(s, 1)
        elif i == 1:
            res = min(s, 1 << r)
        else:
            res = min(s, res << C)
        sum_ += res

    return sum_


def fmt_nbytes(x):
    suffixes = 'bKMG'
    for i, suffix in enumerate(suffixes):
        is_last = i == len(suffixes) - 1
        if x < 1024 or is_last:
            return f'{x:.2f}{suffix}'
        x /= 1024


def max_capacity(max_size):
    lb = 0
    rb = max_size
    while rb - lb > 1:
        m = (lb + rb) // 2
        if max_num_of_nodes(m) <= max_size:
            lb = m
        else:
            rb = m
    assert max_num_of_nodes(lb) <= max_size
    return lb


def main():
    # Memory usage
    for s in [900, 9000, 90000, 900000]:
        n = max_num_of_nodes(s)

        if n < (0xffff - 3):
            r1 = fmt_nbytes(n * 48)
        else:
            r1 = 'N/A'

        r2 = fmt_nbytes(n * 80)

        print(s, r1, r2)

    # Max capacity
    print('Max capacity (16-bit):', max_capacity(0xffff - 3))


if __name__ == '__main__':
    main()
