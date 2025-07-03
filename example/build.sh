#!/bin/sh

set -e
set -x

cd -- "$(dirname "$(readlink "$0" || printf '%s\n' "$0")")"

(
    set -e
    cd ..
    ./ato.py ./glass_prevnext.ato > glass_prevnext.h
    ./ato.py ./glass.ato > glass.h
)

gcc -std=c99 -Wall -Wextra -O3 main.c ../common.c

clang -std=c23 -Wall -Wextra -O3 main.c ../common.c

clang++ -std=c++11 -Wall -Wextra -O3 main.c ../common.c -Wno-missing-designated-field-initializers -Wno-missing-field-initializers -Wno-missing-braces
