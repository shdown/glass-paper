#!/usr/bin/env python3

# (c) 2025 shdown
# This code is licensed under MIT license (see LICENSE.MIT for details)


MAX_C = 20


def main():
    first = True
    for c in range(1, MAX_C + 1):
        directive = 'if' if first else 'elif'
        first = False
        print(f'#{directive} GLASS_N == {1 << c}')
        print(f'#define GLASS__C {c}')

    print('#else')
    print('#error "GLASS_N is too big, not a power of two, or otherwise defined to something wrong."')
    print('#endif')

    print('@@undef GLASS__C')


if __name__ == '__main__':
    main()
