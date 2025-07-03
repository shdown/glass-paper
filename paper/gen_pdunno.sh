#!/usr/bin/env bash

set -e
set -x

if command -v pypy3 >/dev/null; then
    prefix=pypy3
else
    prefix=python3
fi
$prefix ./calc_pdunno.py > pdunnoRAW.txt

awk '$1 == "p" {print $2, $3}' pdunnoRAW.txt > pdunnoPLUS.txt
awk '$1 == "m" {print $2, $3}' pdunnoRAW.txt > pdunnoMINUS.txt
