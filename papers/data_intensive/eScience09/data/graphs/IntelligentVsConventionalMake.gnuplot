set term postscript eps enhanced color solid
set output 'IntelligentVsConventionalFigure.eps'
set xlabel 'Number of workers'
set ylabel 'Time (Seconds)'
plot[0:8] './LocalGridFTP.dat' using 1:2 title 'C1 - [287 MB; P(Y, Y), O(N, N); Local; GridFTP]' with lp,\
     './RemoteGridFTP.dat' using 1:2 title 'C2 - [287 MB; P(Y, N), O(N, Y); Local; GridFTP] ' with lp,\
     './MixedGridFTP.dat' using 1:2 title 'C3 - [287 MB; P(Y, Y), O(Y, Y); Local; GridFTP]' with lp,\
     './IntelligentGridFTP.dat' using 1:2 title 'C4 - Intelligence - [287 MB; P(Y, Y), O(Y, Y); Local; GridFTP]' with lp
