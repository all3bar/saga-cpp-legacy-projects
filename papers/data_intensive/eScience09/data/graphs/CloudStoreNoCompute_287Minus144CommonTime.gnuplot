set term postscript eps enhanced color solid "Times-Roman" 17
set output 'CloudStoreNoCompute_287Minus144CommonTime.eps'
set pointsize 2
set key Left reverse
set xlabel 'N_w' font "Times-Italic, 20"
set ylabel 't_{common}(s)' font "Times-Italic, 20"
set mxtics 2
set mytics 5
plot[0:9][-100:1000] "< paste localCloudStore.dat CloudStoreNoComputeLocal.dat" using 1:((2*$4)-$2) title 'S0: [C1, r = 1]' with lp lw 3,\
"< paste remoteCloudStore.dat CloudStoreNoComputeRemote.dat" using 1:((2*$4)-$2) title 'S1: [C2, r = 1]' with lp lw 3,\
"< paste localCloudStore2Chunks.dat CloudStoreNoCompute2Chunkservers.dat" using 1:((2*$4)-$2) title 'S2: [C3, r = 2]' with lp lw 3,\
"< paste 2ChunksReplication1.dat CloudStoreNoComputeMixed.dat" using 1:((2*$4)-$2) title 'S3: [C4, r = 1]' with lp lw 3

