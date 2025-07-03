#!/usr/bin/env bash

set -e

files=(
    bench/br_SYNTH_INSERT.txt
    bench/br_SYNTH_ERASE.txt
    bench/br_SYNTH_FIND_E.txt
    bench/br_SYNTH_FIND_NE.txt

    bench/br_DATA_all.txt
    bench/br_DATA_iter.txt
)

captions=(
    'Synthetic data: \textbf{insert}'
    'Synthetic data: \textbf{erase}'
    'Synthetic data: \textbf{find existing}'
    'Synthetic data: \textbf{find non-existing}'

    'Real market data: \textbf{no amplification}'
    'Real market data: \textbf{iter amplified 100x}'
)

typeset -A custom_ymax=()

N=${#captions[@]}
for (( i = 0; i < N; ++i )); do
    yrange_cmd=
    ymax=${custom_ymax[$i]}
    if [[ -n "$ymax" ]]; then
        yrange_cmd="set yrange [:${ymax}]"
    fi

    printf '%s\n' "
\\begin{figure}[H]
    \\caption{${captions[$i]}}
    \\centering
    \\begin{gnuplot}[terminal=epslatex, terminaloptions=color]

        set style line 1 lt 1 lw 2 lc rgb '#0000ee' pt -1
        set style line 2 lt 1 lw 2 lc rgb '#ee0000' pt -1

        set xtics axis
        set ytics axis

        set grid xtics lc rgb '#555555' lw 1 lt 0
        set grid ytics lc rgb '#555555' lw 1 lt 0

        set xlabel 'Number of copies'
        set ylabel 'Speedup ratio'

        set autoscale xfix
        ${yrange_cmd}

        set key top left Left reverse

        plot \\
            '${files[$i]}' using 1:2 with lines ls 1 ti 'Against std::map', \\
            '${files[$i]}' using 1:3 with lines ls 2 ti 'Against std::map w/ custom allocator'

    \\end{gnuplot}
\\end{figure}"

done
