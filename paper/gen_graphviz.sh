#!/usr/bin/env bash

set -e
set -x

extra_opts='scale=0.6'

./gen_graphviz.py \
    --latex \
    --latex-caption='A trie' \
    --graph-name='Gsimple' \
    --latex-extra-opts="$extra_opts" \
    000.,010.,101. \
    > graph_cp_simple_INCLUDE.tex

./gen_graphviz.py \
    --latex \
    --latex-caption='A trie with full cached path' \
    --graph-name='Gfull' \
    --latex-extra-opts="$extra_opts" \
    --cached-path=010 \
    000.,010.,101. \
    > graph_cp_full_INCLUDE.tex

./gen_graphviz.py \
    --latex \
    --latex-caption='A trie with a to-be-inserted node' \
    --graph-name='Ginsert' \
    --latex-extra-opts="$extra_opts" \
    --cached-path=010 \
    --insert-path=011. \
    000.,010.,011.,101. \
    > graph_cp_insert_INCLUDE.tex

./gen_graphviz.py \
    --latex \
    --latex-caption='A tree with red and blue paths' \
    --graph-name='Gxxx' \
    --latex-extra-opts="$extra_opts" \
    --custom-path=0:010 \
    --custom-path=1:01/01 \
    0000,0001,0010,0101,0110,1000,1000,1111 \
    > graph_cp_xxx_INCLUDE.tex

./gen_graphviz.py \
    --latex \
    --latex-caption='A trie after erasure: cached path is truncated' \
    --graph-name='Gtrunc' \
    --latex-extra-opts="$extra_opts" \
    --cached-path=01 \
    000.,010.,101. \
    > graph_cp_trunc_INCLUDE.tex
