set term postscript eps enhanced color solid "Times-Roman" 23
set output 'sphere_mr_varying_workers.eps'
set pointsize 2
set key Left reverse
set xlabel 'Number of workers (MB)' font "Times-Italic, 28"
set ylabel 'Time (s)' font "Times-Italic, 28"
set mxtics 2
set mytics 5
plot[0:11][0:3400] './sphere_mr_varying_workers.dat' using 1:2 title 'SAGA-MapReduce' with lp lw 3,\
'./sphere_mr_varying_workers.dat' using 1:3 title 'SAGA-Sphere' with lp lw 3
