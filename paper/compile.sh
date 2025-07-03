#!/usr/bin/env bash

set -e
set -x

./gen_bench_boilerplate.sh > bench_boilerplate_INCLUDE.tex

./gen_graphviz.sh

invoke_pdflatex() {
    pdflatex -shell-escape paper.tex
}

invoke_pdflatex
invoke_pdflatex

bibtex paper

invoke_pdflatex
invoke_pdflatex
