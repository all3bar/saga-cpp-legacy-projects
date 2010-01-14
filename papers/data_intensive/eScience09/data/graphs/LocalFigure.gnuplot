set term postscript eps enhanced color solid "Times-Roman" 17
set output 'LocalFigure.eps'
set pointsize 2
set xlabel 'N_w' font "Times-Italic, 20"
set ylabel 't_c(s)' font "Times-Italic, 20"
set mxtics 2
set mytics 5
plot[0:8][0:140]'./LocalFileSystem.dat' using 1:2 title 'S0: [287 MB; {/Times-Italic N_c} = 8]' with lp lw 3,\
'./LocalFileSystemHalfChunkSize16Assignments.dat' using 1:2 title 'S1: [144 MB; {/Times-Italic N_c} = 16] ' with lp lw 3,\
'./LocalFileSystemHalfChunkSize8Assignments.dat' using 1:2 title 'S2: [144 MB; {/Times-Italic N_c} = 8] ' with lp lw 3
