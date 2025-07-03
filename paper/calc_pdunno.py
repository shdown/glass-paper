#!/usr/bin/env python3

# (c) 2025 shdown
# This code is licensed under MIT license (see LICENSE.MIT for details)

import sys


J_MIN, J_MAX = 1, 10
n = 9210
b = 1 << 15


def make_power_table(x, size):
    res = []
    cur = 1
    for _ in range(size):
        res.append(cur)
        cur *= x
    return res


def make_factorials(size):
    res = [1]
    cur = 1
    for i in range(1, size):
        cur *= i
        res.append(cur)
    return res


b_powers = make_power_table(b, n + 2)
b_minus_one_powers = make_power_table(b - 1, n + 2)
factorials = make_factorials(n + 2)


def choice(n, k):
    return factorials[n] // factorials[k] // factorials[n - k]


class Fraction:
    def __init__(self, num, denom):
        self.num = num
        self.denom = denom


def p_bucket(k):
    res = Fraction(choice(n, k), 1)

    res.num *= b_minus_one_powers[n - k]
    res.denom *= b_powers[n]

    return res


def pq_bucket(k, J):
    res = p_bucket(k)
    if k > J:
        res.num *= J
        res.denom *= k
    return res


class KahanSummator:
    def __init__(self):
        self.s = 0.0
        self.c = 0.0

    def add_summand(self, x):
        y = x - self.c
        t = self.s + y
        self.c = (t - self.s) - y
        self.s = t

    def finalize(self):
        return self.s


SUMMATOR = KahanSummator


def p_dunno_plus(J):
    summator = SUMMATOR()
    for k in range(1, n + 1):
        cur = pq_bucket(k, J)
        summator.add_summand(cur.num / cur.denom)
        if not (k & 255):
            print(f'k={k}', file=sys.stderr)

    res = summator.finalize()

    pz_frac = p_bucket(0)
    pz = pz_frac.num / pz_frac.denom

    return 1.0 - res / (1.0 - pz)


def p_dunno_minus(J):
    summator = SUMMATOR()
    for k in range(J + 1, n + 1):
        cur = p_bucket(k)
        summator.add_summand(cur.num / cur.denom)
        if not (k & 255):
            print(f'k={k}', file=sys.stderr)

    return summator.finalize()


def main():
    for J in range(J_MIN, J_MAX + 1):
        p = p_dunno_plus(J)
        m = p_dunno_minus(J)
        print('p', J, p)
        print('m', J, m)


if __name__ == '__main__':
    main()
