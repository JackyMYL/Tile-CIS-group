#!/bin/bash

#                                2012

#        January               February                 March
# Su Mo Tu We Th Fr Sa   Su Mo Tu We Th Fr Sa   Su Mo Tu We Th Fr Sa
#  1  2  3  4  5  6  7             1  2  3  4                1  2  3
#  8  9 10 11 12 13 14    5  6  7  8  9 10 11    4  5  6  7  8  9 10
# 15 16 17 18 19 20 21   12 13 14 15 16 17 18   11 12 13 14 15 16 17
# 22 23 24 25 26 27 28   19 20 21 22 23 24 25   18 19 20 21 22 23 24
# 29 30 31               26 27 28 29            25 26 27 28 29 30 31

#         April                   May                   June
# Su Mo Tu We Th Fr Sa   Su Mo Tu We Th Fr Sa   Su Mo Tu We Th Fr Sa
#  1  2  3  4  5  6  7          1  2  3  4  5                   1  2
#  8  9 10 11 12 13 14    6  7  8  9 10 11 12    3  4  5  6  7  8  9
# 15 16 17 18 19 20 21   13 14 15 16 17 18 19   10 11 12 13 14 15 16
# 22 23 24 25 26 27 28   20 21 22 23 24 25 26   17 18 19 20 21 22 23
# 29 30                  27 28 29 30 31         24 25 26 27 28 29 30

#         July                  August                September
# Su Mo Tu We Th Fr Sa   Su Mo Tu We Th Fr Sa   Su Mo Tu We Th Fr Sa
#  1  2  3  4  5  6  7             1  2  3  4                      1
#  8  9 10 11 12 13 14    5  6  7  8  9 10 11    2  3  4  5  6  7  8
# 15 16 17 18 19 20 21   12 13 14 15 16 17 18    9 10 11 12 13 14 15
# 22 23 24 25 26 27 28   19 20 21 22 23 24 25   16 17 18 19 20 21 22
# 29 30 31               26 27 28 29 30 31      23 24 25 26 27 28 29
#                                               30
#        October               November               December
# Su Mo Tu We Th Fr Sa   Su Mo Tu We Th Fr Sa   Su Mo Tu We Th Fr Sa
#     1  2  3  4  5  6                1  2  3                      1
#  7  8  9 10 11 12 13    4  5  6  7  8  9 10    2  3  4  5  6  7  8
# 14 15 16 17 18 19 20   11 12 13 14 15 16 17    9 10 11 12 13 14 15
# 21 22 23 24 25 26 27   18 19 20 21 22 23 24   16 17 18 19 20 21 22
# 28 29 30 31            25 26 27 28 29 30      23 24 25 26 27 28 29
#                                               30 31


N=0

Mondays=( '2012-04-02' '2012-04-09' '2012-04-16' '2012-04-23' '2012-04-30' \
'2012-05-07' '2012-05-14' '2012-05-21' '2012-05-28' \
'2012-06-04' '2012-06-11' '2012-06-18' '2012-06-25' \
'2012-07-02' '2012-07-09' '2012-07-16' '2012-07-23' '2012-07-30' \
'2012-08-06' '2012-08-13' '2012-08-20' '2012-08-27' \
'2012-09-03' '2012-09-10' '2012-09-17' '2012-09-24' \
'2012-10-01' '2012-10-08' '2012-10-15' '2012-10-22' '2012-10-29' \
'2012-11-05' '2012-11-12' '2012-11-19' '2012-11-26' \
'2012-12-03' '2012-12-10' '2012-12-17' )

Nmax=${#Mondays[@]}
let Nmax-=1

while [ $N -lt $Nmax ]; do 
#    echo ${Mondays[$N]} ${Mondays[$N+1]} $N ${#Mondays[@])} 
   macros/laser/Average.py --date=${Mondays[$N]} --enddate=${Mondays[$N+1]} --pisa 
   B=`printf "%02d" $N`
   sed 's/XX/Week '$B'/' layerXX_Deviation_CF.eps > layer-Deviation_CF-$B.eps
   sed 's/XX/Week '$B'/' layerXX_Deviation_Pisa.eps > layer-Deviation_Pisa-$B.eps
   sed 's/XX/Week '$B'/' layerXX_Deviation_CF-Pisa.eps > layer-Deviation_CF-Pisa-$B.eps
   let N+=1
done


convert -delay 50 layer-Deviation_CF-Pisa-??.eps -loop 0 toto-Henric.gif



