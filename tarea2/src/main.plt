set terminal pdfcairo enhanced color font 'Arial-Bold'

set output 'plot.pdf'

set arrow from 4,graph(0,0) to 4,graph(1,1) nohead dashtype 2

if (!exists("name")) name = "Speedup"

set title name." del programa en función de la cantidad de threads"
set xlabel "Cantidad de threads"
set ylabel name

unset key
set xtics 1,1

filelist=system("ls *.dat")

plot for [file in filelist] file using 1:3 with linespoints pt 4 ps 1