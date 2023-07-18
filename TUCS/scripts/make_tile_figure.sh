#!/bin/bash -f

   
pathresult=$1
if [ -z "$1" ]
  then
    echo "No result path specified, setting path to results/"
    pathresult="results"
fi

inputfile=$2
if [ -z "$2" ]
  then
    echo "No inputfile specified, using default data_cells_var_hg.txt"
    inputfile="data_cells_var_hg.txt"
fi


if [ -f  ${pathresult}/${inputfile} ]; then
    file=${pathresult}/${inputfile} 
else
    file=${pathresult}/data_cells_var_lg.txt 
fi

outputfile="tile_laser_map.eps"
labelside=""
if [[ $file =~ "Aside" ]]; then
    outputfile="tile_laser_map_Aside.eps"
    labelside=" - A side"
fi
if [[ $file =~ "Cside" ]]; then
    outputfile="tile_laser_map_Cside.eps"
    labelside=" - C side"
fi

echo '+------------------------------------------------------+'
echo '| Producing cells mapping of PMT gain variations in '${pathresult}
echo '+------------------------------------------------------+'
echo '| Djamel.Boumediene@cern.ch                            |'
echo '+------------------------------------------------------+'

rm -f ${pathresult}/${outputfile}

echo '%!PS-Adobe-3.0 EPSF-3.0
%%Creator: Adobe Illustrator(TM) 7.0
%%For: 
%%Title: (Tilecal_cells.eps)
%%CreationDate: (9/29/99) (11:32 PM)
%%BoundingBox: -104 -64 774 444
%%HiResBoundingBox: -103.2 -64 773.6 443.2
%%DocumentProcessColors: Black
' > ${pathresult}/${outputfile}



maxdev=450 #if |deviation| > 5% constant colour is used
mindev=`echo $maxdev/2 | bc`
printvals=1
threshold=10 # in 1/10000 unit

date=`date` 

## A cells
Amax=9
Acells=( "A1" "A2" "A3"  "A4" "A5"  "A6"  "A7"  "A8"  "A9" "A10" )
Acellw=( "28" "26" "28"  "28" "28"  "28"  "34"  "34"  "38" "32"  )
Acellh=( "30" "30" "30"  "30" "30"  "30"  "30"  "30"  "30" "30"  )
Acellg=( "1" "1" "1"  "1" "1"  "1"  "1"  "1"  "1" "1"  )

## BC cells
Bmax=8
Bcells=( "B1" "B2" "B3"  "B4" "B5"  "B6"  "B7"  "B8"  "B9" )
Bcellw=( "32" "30" "30"  "32" "34"  "36"  "36"  "40"  "36" )
Bcellh=( "46" "46" "46"  "46" "46"  "46"  "46"  "46"  "44" )
Bcellg=( "1" "1" "1"  "1" "1"  "1"  "1"  "1"  "1" "1"  )
Cmax=7
Ccells=( "C1" "C2" "C3"  "C4" "C5"  "C6"  "C7"  "C8"  "C9" "C10" )
Ccellw=( "36" "34" "38"  "36" "40"  "42"  "42"  "40"  "40" "36"  )
Ccellh=( "48" "48" "48"  "48" "48"  "48"  "48"  "48"  "46" "44"  )


## D cells
Dmax=3
Dcells=( "D0" "D1" "D2"  "D3" "D4"  "D5"  "D7"  "D8"  "D9" "D10" )
Dcellw=( "40" "86" "88"  "102" "34"  "36"  "36"  "40"  "36" "32"  )
Dcellh=( "44" "44" "44"  "44" "44"  "44"  "44"  "44"  "44" "44"  )
Dcellg=( "1" "1" "1" "1" "1"  "1" "1" "1"  "1" "1" )

##### Extended
## A cells
EAmax=4
EAcells=( "A12" "A13" "A14"  "A15" "A16" )
EAcellw=( "20" "50" "56"  "72" "90"  )
EAcellh=( "30" "30" "30"  "30" "30"  )
EAcellg=( "1" "1" "1" "1" "1"  )
##### Extended
## B cells and C10
EBmax=5
EBcells=( "B11" "B12" "B13"  "B14" "B15" "C10")
EBcellw=( "34" "56" "60"  "66" "72"  "10" )
EBcellh=( "60" "60" "60"  "60" "60" "44" )
EBcellg=( "1" "1" "1" "1" "1" "1" )
## D cells
EDmax=2
EDcells=( "D4" "D5" "D6"  )
EDcellw=( "32" "138" "156"  )
EDcellh=( "44" "78" "78"  )
EDcellg=( "1" "1" "1" "1" "1" )

####### Gaps
## E cells
Emax=3
Ecells=( "E1" "E2" "E3" "E4"  )
Ecellw=( "2" "2" "2" "2" )
Ecellh=( "42" "42" "42" "42" )
Ecellg=( "1" "1" "1" "1" )

####### Eta
etalines=("2" "28" "54" "82" "106" "134" "162" "194" "228" "260" "298" "338")
etalinee=("2" "52" "104" "152" "206" "264" "320" "382" "448" "512" "584" "666")
etavals=("0.0" "0.1" "0.2" "0.3" "0.4" "0.5" "0.6" "0.7" "0.8" "0.9" "1.0" "1.1")

etalines2=("104" "80" "52" "12")
etalinee2=("328" "274" "224" "152")
etavals2=("1.2" "1.3" "1.4" "1.6")

ABmax=`echo "$Amax+$Bmax+1" | bc`
ABDmax=`echo "$Amax+$Bmax+$Dmax+2" | bc`
ABDEAmax=`echo "$Amax+$Bmax+$Dmax+$EAmax+3" | bc`
ABDEAEBmax=`echo "$Amax+$Bmax+$Dmax+$EAmax+$EBmax+4" | bc`
Allmax=`echo "$Amax+$Bmax+$Dmax+$EAmax+$EBmax+$EDmax+5" | bc`



################################### Lecture des gains
i=0


for gain in ` cat ${file}`
    do

  echo ' | line '$i' value '$gain' | '

  if [ $i -ge 41 ]; then
      daterun=$daterun' '$gain
  else

      let "gain*=-1"
      
      if [ $i -le $Amax ]; then
	  Acellg[$i]=$gain
      elif [ $i -le $ABmax ]; then
	  index=$i
	  let "index-=$Amax"
	  let "index-=1"
	  Bcellg[$index]=$gain
      elif [ $i -le $ABDmax ]; then
	  index=$i
	  let "index-=$ABmax"
	  let "index-=1"
	  Dcellg[$index]=$gain
      elif [ $i -le $ABDEAmax ]; then
	  index=$i
	  let "index-=$ABDmax"
	  let "index-=1"
	  EAcellg[$index]=$gain
      elif [ $i -le $ABDEAEBmax ]; then
	  index=$i
	  let "index-=$ABDEAmax"
	  let "index-=1"
	  EBcellg[$index]=$gain
      elif [ $i -le $Allmax ]; then
	  index=$i
	  let "index-=$ABDEAEBmax"
	  let "index-=1"
	  EDcellg[$index]=$gain
      else
	  index=$i
	  let "index-=$Allmax"
	  let "index-=1"
	  Ecellg[$index]=$gain
      fi
  fi
  echo 'line '$i' index '$index' gain '$gain
  let "i+=1"
done



### tmp tmp
##cp Tilecal_cells.eps.sv ${pathresult}/${outputfile}

##echo '* poids numbre d events processes : '$date > poids.kumac 



##### eta lines

## 

echo 'Eta lines'

et=0
until [ $et -gt 11 ]


  do

xlines=${etalines[$et]}
xlinee=${etalinee[$et]}
etav=${etavals[$et]}

echo '
newpath
'$xlines' 104 moveto
'$xlinee' 350 lineto
1 setlinewidth
stroke
' >> ${pathresult}/${outputfile}


# legende

  textx=$xlinee
  texty=354

  echo '
0 0 0 setrgbcolor
/Times-Bold findfont 12 scalefont setfont 
'$textx' '$texty' moveto 
('$etav') show 
' >> ${pathresult}/${outputfile}


let "et += 1"

done


echo 'Eta lines'

et=0
until [ $et -gt 3 ]


  do

ylines=${etalines2[$et]}
ylinee=${etalinee2[$et]}
etav=${etavals2[$et]}

echo '
newpath
390 '$ylines' moveto
722 '$ylinee' lineto
1 setlinewidth
stroke
' >> ${pathresult}/${outputfile}


# legende

  textx=722
  texty=$ylinee

  echo '
0 0 0 setrgbcolor
/Times-Bold findfont 12 scalefont setfont 
'$textx' '$texty' moveto 
('$etav') show 
' >> ${pathresult}/${outputfile}



let "et += 1"

done

# legende

  textx=720
  texty=362

  echo '
0 0 0 setrgbcolor
/Times-Bold findfont 18 scalefont setfont 
'$textx' '$texty' moveto 
(eta) show 
' >> ${pathresult}/${outputfile}


# legende

  textx=0
  texty=420

### TMP TMP
  echo '
0 0 0 setrgbcolor
/Times-Bold findfont 18 scalefont setfont 
'$textx' '$texty' moveto 
(ATLAS Preliminary) show 
' >> ${pathresult}/${outputfile}

  textx=0
  texty=400

  echo '
0 0 0 setrgbcolor
/Times-Bold findfont 18 scalefont setfont 
'$textx' '$texty' moveto 
(Tile Calorimeter '${labelside}') show 
' >> ${pathresult}/${outputfile} 


################################### Drawing A cells
j=0

# jmax est le nfile de do_plot_vvhh_vienna.kumac 

nextpos=1

until [ $j -gt $Amax ]
	    do 


  ## which colour

  rcol=0
  bcol=0
  deviation=${Acellg[$j]}
  label=${Acells[$j]}

  ## dev negative

  negadev=`echo "c=0;a=$deviation/1;if(0>a)c=1;c"|bc`
  if [ $negadev = 0 ]; then
      if [ $deviation -lt $mindev ]; then
	  vcol=1
	  rcol=`echo "scale=2; $deviation/$mindev" | bc`
      else 
	  rcol=1
	  vcol=`echo "scale=2; ($maxdev-$deviation)/$mindev" | bc`
      fi

      if [ $deviation -gt $maxdev ]; then
	  rcol=1
	  vcol=0
      fi
  fi

  ## dev positive
  if [ $negadev = 1 ]; then
      let "deviation*=-1"
      if [ $deviation -lt $mindev ]; then
	  vcol=1
	  bcol=`echo "scale=2; $deviation/$mindev" | bc`
      else 
	  bcol=1
	  vcol=`echo "scale=2; ($maxdev-$deviation)/$mindev" | bc`
      fi

      if [ $deviation -gt $maxdev ]; then
	  bcol=1
	  vcol=0
      fi
      let "deviation*=-1"
  fi


  echo 'colours = '$rcol' '$vcol' '$bcol' deviation= '$deviation
  ##

  name=${Acells[$j]}
  width=${Acellw[$j]}
  height=${Acellh[$j]}
  originx=$nextpos


  originy=116

  let "nextpos+=$width"
  let "nextpos+=2"


  echo '
newpath
'$originx' '$originy' moveto
0 '$height' rlineto
'$width' 0 rlineto
0 -'$height' rlineto
-'$width' 0 rlineto
closepath
gsave
'$rcol' '$vcol' '$bcol' setrgbcolor
fill' >> ${pathresult}/${outputfile}

# vals
if [ $printvals==1 ]; then
  textx=$originx
  texty=$originy
  let "textx+=2"
  let "texty+=4"
  devcent=`echo "scale=2; $deviation/-100" | bc`
  # abs value
  absdevcent=`echo "a=$deviation/1;if(0>a)a*=-1;a"|bc`
  # show only large variations
  if [ $absdevcent -ge $threshold ]; then
      echo '
0 0 0 setrgbcolor
/Helvetica findfont 12 scalefont setfont 
'$textx' '$texty' moveto 
('$devcent') show 
' >> ${pathresult}/${outputfile}
  fi

fi

# legende

  textx=$originx
  texty=$originy
  let "textx+=2"
  let "texty+=16"


  echo '
0 0 0 setrgbcolor
/Times-Bold findfont 12 scalefont setfont 
'$textx' '$texty' moveto 
('$label') show 
' >> ${pathresult}/${outputfile}


 let "j += 1"

	done



################################### Drawing B cells
j=0

echo 'BC Cells ...'

# jmax est le nfile de do_plot_vvhh_vienna.kumac 

nextpos=1

until [ $j -gt $Bmax ]
	    do 

  name=${Bcells[$j]}
  width=${Bcellw[$j]}
  height=${Bcellh[$j]}
  originx=$nextpos
  deviation=${Bcellg[$j]}
  label=${Bcells[$j]}

  originy=150

  let "nextpos+=$width"
  let "nextpos+=2"

  rcol=0
  bcol=0

  negadev=`echo "c=0;a=$deviation/1;if(0>a)c=1;c"|bc`

  ## which colour
  if [ $negadev -ne 1 ]; then
      if [ $deviation -lt $mindev ]; then
	  vcol=1
	  rcol=`echo "scale=2; $deviation/$mindev" | bc`
      else 
	  rcol=1
	  vcol=`echo "scale=2; ($maxdev-$deviation)/$mindev" | bc`
      fi

      if [ $deviation -gt $maxdev ]; then
	  rcol=1
	  vcol=0
      fi
  fi

  ## dev positive
  if [ $negadev = 1 ]; then
      let "deviation*=-1"
      if [ $deviation -lt $mindev ]; then
	  vcol=1
	  bcol=`echo "scale=2; $deviation/$mindev" | bc`
      else 
	  bcol=1
	  vcol=`echo "scale=2; ($maxdev-$deviation)/$mindev" | bc`
      fi

      if [ $deviation -gt $maxdev ]; then
	  bcol=1
	  vcol=0
      fi
      let "deviation*=-1"
  fi

  echo 'colours = '$rcol' '$vcol' '$bcol' deviation= '$deviation
  ##

  echo '
newpath
'$originx' '$originy' moveto
0 '$height' rlineto
'$width' 0 rlineto
0 -'$height' rlineto
-'$width' 0 rlineto
closepath
gsave
'$rcol' '$vcol' '$bcol' setrgbcolor
fill' >> ${pathresult}/${outputfile}

# vals
if [ $printvals==1 ]; then
  textx=$originx
  texty=$originy
  let "textx+=2"
  let "texty+=4"
  devcent=`echo "scale=2; $deviation/-100" | bc`
  # abs value
  absdevcent=`echo "a=$deviation/1;if(0>a)a*=-1;a"|bc`
  # show only large variations
  if [ $absdevcent -ge $threshold ]; then
      echo '
0 0 0 setrgbcolor
/Helvetica findfont 12 scalefont setfont 
'$textx' '$texty' moveto 
('$devcent') show 
' >> ${pathresult}/${outputfile}
  fi

fi

# legende

  textx=$originx
  texty=$originy
  let "textx+=2"
  let "texty+=16"


  echo '
0 0 0 setrgbcolor
/Times-Bold findfont 12 scalefont setfont 
'$textx' '$texty' moveto 
('$label') show 
' >> ${pathresult}/${outputfile}


##let "jk+=1" 
##echo '* '$TARGET ' ' $nlink ' fichiers ' >> poids.kumac  
##echo 've/input gen('$jk') '${numlink}'.' >> poids.kumac

 let "j += 1"

	done






################################### Drawing C cells
j=0

echo 'C Cells ...'

# jmax est le nfile de do_plot_vvhh_vienna.kumac 

nextpos=1

until [ $j -gt $Cmax ]
	    do 

  name=${Ccells[$j]}
  width=${Ccellw[$j]}
  height=${Ccellh[$j]}
  originx=$nextpos
  deviation=${Bcellg[$j]}
  label=${Ccells[$j]}

  originy=196

  let "nextpos+=$width"
  let "nextpos+=2"
  rcol=0
  bcol=0
  negadev=`echo "c=0;a=$deviation/1;if(0>a)c=1;c"|bc`

  ## which colour
  if [ $negadev -ne 1 ]; then
      if [ $deviation -lt $mindev ]; then
	  vcol=1
	  rcol=`echo "scale=2; $deviation/$mindev" | bc`
      else 
	  rcol=1
	  vcol=`echo "scale=2; ($maxdev-$deviation)/$mindev" | bc`
      fi

      if [ $deviation -gt $maxdev ]; then
	  rcol=1
	  vcol=0
      fi
  fi

  ## dev positive
  if [ $negadev = 1 ]; then
      let "deviation*=-1"
      if [ $deviation -lt $mindev ]; then
	  vcol=1
	  bcol=`echo "scale=2; $deviation/$mindev" | bc`
      else 
	  bcol=1
	  vcol=`echo "scale=2; ($maxdev-$deviation)/$mindev" | bc`
      fi

      if [ $deviation -gt $maxdev ]; then
	  bcol=1
	  vcol=0
      fi
      let "deviation*=-1"
  fi

  echo 'colours = '$rcol' '$vcol' '$bcol' deviation= '$deviation
  ##

  echo '
newpath
'$originx' '$originy' moveto
0 '$height' rlineto
'$width' 0 rlineto
0 -'$height' rlineto
-'$width' 0 rlineto
closepath
gsave
'$rcol' '$vcol' '$bcol' setrgbcolor
fill' >> ${pathresult}/${outputfile}

# vals
if [ $printvals==1 ]; then
  textx=$originx
  texty=$originy
  let "textx+=2"
  let "texty+=4"
  devcent=`echo "scale=2; $deviation/-100" | bc`
  # abs value
  absdevcent=`echo "a=$deviation/1;if(0>a)a*=-1;a"|bc`
  # show only large variations
  if [ $absdevcent -ge $threshold ]; then
      echo '
0 0 0 setrgbcolor
/Helvetica findfont 12 scalefont setfont 
'$textx' '$texty' moveto 
('$devcent') show 
' >> ${pathresult}/${outputfile}
  fi

fi

# legende

  textx=$originx
  texty=$originy
  let "textx+=2"
  let "texty+=16"


  echo '
0 0 0 setrgbcolor
/Times-Bold findfont 12 scalefont setfont 
'$textx' '$texty' moveto 
('$label') show 
' >> ${pathresult}/${outputfile}

##let "jk+=1" 
##echo '* '$TARGET ' ' $nlink ' fichiers ' >> poids.kumac  
##echo 've/input gen('$jk') '${numlink}'.' >> poids.kumac

 let "j += 1"

	done






################################### Drawing D cells
j=0

echo 'D Cells ...'

# jmax est le nfile de do_plot_vvhh_vienna.kumac 

nextpos=1

until [ $j -gt $Dmax ]
	    do 

  name=${Dcells[$j]}
  width=${Dcellw[$j]}
  height=${Dcellh[$j]}
  originx=$nextpos
  deviation=${Dcellg[$j]}
  label=${Dcells[$j]}
  rcol=0
  bcol=0
  originy=248

  let "nextpos+=$width"
  let "nextpos+=2"

  negadev=`echo "c=0;a=$deviation/1;if(0>a)c=1;c"|bc`

  ## which colour
  if [ $negadev -ne 1 ]; then
      if [ $deviation -lt $mindev ]; then
	  vcol=1
	  rcol=`echo "scale=2; $deviation/$mindev" | bc`
      else 
	  rcol=1
	  vcol=`echo "scale=2; ($maxdev-$deviation)/$mindev" | bc`
      fi

      if [ $deviation -gt $maxdev ]; then
	  rcol=1
	  vcol=0
      fi
  fi

  ## dev positive
  if [ $negadev = 1 ]; then
      let "deviation*=-1"
      if [ $deviation -lt $mindev ]; then
	  vcol=1
	  bcol=`echo "scale=2; $deviation/$mindev" | bc`
      else 
	  bcol=1
	  vcol=`echo "scale=2; ($maxdev-$deviation)/$mindev" | bc`
      fi

      if [ $deviation -gt $maxdev ]; then
	  bcol=1
	  vcol=0
      fi
      let "deviation*=-1"
  fi

  echo 'colours = '$rcol' '$vcol' '$bcol' deviation= '$deviation
  ##

  echo '
newpath
'$originx' '$originy' moveto
0 '$height' rlineto
'$width' 0 rlineto
0 -'$height' rlineto
-'$width' 0 rlineto
closepath
gsave
'$rcol' '$vcol' '$bcol' setrgbcolor
fill' >> ${pathresult}/${outputfile}

# vals
if [ $printvals==1 ]; then
  textx=$originx
  texty=$originy
  let "textx+=2"
  let "texty+=4"
  devcent=`echo "scale=2; $deviation/-100" | bc`
  # abs value
  absdevcent=`echo "a=$deviation/1;if(0>a)a*=-1;a"|bc`
  # show only large variations
  if [ $absdevcent -ge $threshold ]; then
      echo '
0 0 0 setrgbcolor
/Helvetica findfont 12 scalefont setfont 
'$textx' '$texty' moveto 
('$devcent') show 
' >> ${pathresult}/${outputfile}
  fi

fi

# legende

  textx=$originx
  texty=$originy
  let "textx+=2"
  let "texty+=16"


  echo '
0 0 0 setrgbcolor
/Times-Bold findfont 12 scalefont setfont 
'$textx' '$texty' moveto 
('$label') show 
' >> ${pathresult}/${outputfile}

 let "j += 1"

	done


############### Extended

################################### Drawing A cells Extended
j=0

echo 'Extended A Cells ...'

# jmax est le nfile de do_plot_vvhh_vienna.kumac 

nextpos=408

until [ $j -gt $EAmax ]
	    do 

  name=${EAcells[$j]}
  width=${EAcellw[$j]}
  height=${EAcellh[$j]}
  originx=$nextpos
  deviation=${EAcellg[$j]}
  label=${EAcells[$j]}
  rcol=0
  bcol=0

  originy=116


  let "nextpos+=$width"
  let "nextpos+=2"

  negadev=`echo "c=0;a=$deviation/1;if(0>a)c=1;c"|bc`

  ## which colour
  if [ $negadev -ne 1 ]; then
      if [ $deviation -lt $mindev ]; then
	  vcol=1
	  rcol=`echo "scale=2; $deviation/$mindev" | bc`
      else 
	  rcol=1
	  vcol=`echo "scale=2; ($maxdev-$deviation)/$mindev" | bc`
      fi

      if [ $deviation -gt $maxdev ]; then
	  rcol=1
	  vcol=0
      fi
  fi

  ## dev positive
  if [ $negadev = 1 ]; then
      let "deviation*=-1"
      if [ $deviation -lt $mindev ]; then
	  vcol=1
	  bcol=`echo "scale=2; $deviation/$mindev" | bc`
      else 
	  bcol=1
	  vcol=`echo "scale=2; ($maxdev-$deviation)/$mindev" | bc`
      fi

      if [ $deviation -gt $maxdev ]; then
	  bcol=1
	  vcol=0
      fi
      let "deviation*=-1"
  fi

  echo 'colours = '$rcol' '$vcol' '$bcol' deviation= '$deviation
  ##

  echo '
newpath
'$originx' '$originy' moveto
0 '$height' rlineto
'$width' 0 rlineto
0 -'$height' rlineto
-'$width' 0 rlineto
closepath
gsave
'$rcol' '$vcol' '$bcol' setrgbcolor
fill' >> ${pathresult}/${outputfile}

# vals
if [ $printvals==1 ]; then
  textx=$originx
  texty=$originy
  let "textx+=2"
  let "texty+=4"
  devcent=`echo "scale=2; $deviation/-100" | bc`
  # abs value
  absdevcent=`echo "a=$deviation/1;if(0>a)a*=-1;a"|bc`
  # show only large variations
  if [ $absdevcent -ge $threshold ]; then
      echo '
0 0 0 setrgbcolor
/Helvetica findfont 12 scalefont setfont 
'$textx' '$texty' moveto 
('$devcent') show 
' >> ${pathresult}/${outputfile}
  fi

fi

# legende

  textx=$originx
  texty=$originy
  let "textx+=2"
  let "texty+=16"


  echo '
0 0 0 setrgbcolor
/Times-Bold findfont 12 scalefont setfont 
'$textx' '$texty' moveto 
('$label') show 
' >> ${pathresult}/${outputfile}


 let "j += 1"

	done




################################### Drawing B cells Extended
j=0

echo 'Extended B Cells ...'

# jmax est le nfile de do_plot_vvhh_vienna.kumac 

nextpos=408

until [ $j -gt $EBmax ]
	    do 

  name=${EBcells[$j]}
  width=${EBcellw[$j]}
  height=${EBcellh[$j]}
  originx=$nextpos
  deviation=${EBcellg[$j]}
  label=${EBcells[$j]}
  rcol=0
  bcol=0

  originy=150

  let "nextpos+=$width"
  let "nextpos+=2"

  ####### special C10 cell

  if [ $j -eq 5 ]; then
      originy=198
      originx=394
  fi
  ######

  negadev=`echo "c=0;a=$deviation/1;if(0>a)c=1;c"|bc`

  ## which colour
  if [ $negadev -ne 1 ]; then
      if [ $deviation -lt $mindev ]; then
	  vcol=1
	  rcol=`echo "scale=2; $deviation/$mindev" | bc`
      else 
	  rcol=1
	  vcol=`echo "scale=2; ($maxdev-$deviation)/$mindev" | bc`
      fi

      if [ $deviation -gt $maxdev ]; then
	  rcol=1
	  vcol=0
      fi
  fi

  ## dev positive
  if [ $negadev -eq 1 ]; then
      let "deviation*=-1"
      if [ $deviation -lt $mindev ]; then
	  vcol=1
	  bcol=`echo "scale=2; $deviation/$mindev" | bc`
      else 
	  bcol=1
	  vcol=`echo "scale=2; ($maxdev-$deviation)/$mindev" | bc`
      fi

      if [ $deviation -gt $maxdev ]; then
	  bcol=1
	  vcol=0
      fi
      let "deviation*=-1"
  fi

  echo 'colours = '$rcol' '$vcol' '$bcol' deviation= '$deviation
  ##

  echo '
newpath
'$originx' '$originy' moveto
0 '$height' rlineto
'$width' 0 rlineto
0 -'$height' rlineto
-'$width' 0 rlineto
closepath
gsave
'$rcol' '$vcol' '$bcol' setrgbcolor
fill' >> ${pathresult}/${outputfile}

# vals
if [ $printvals==1 ]; then
  textx=$originx
  texty=$originy
  let "textx+=2"
  let "texty+=4"
  devcent=`echo "scale=2; $deviation/-100" | bc`
  # abs value
  absdevcent=`echo "a=$deviation/1;if(0>a)a*=-1;a"|bc`
  # show only large variations
  if [ $absdevcent -ge $threshold ]; then
      echo '
0 0 0 setrgbcolor
/Helvetica findfont 12 scalefont setfont 
'$textx' '$texty' moveto 
('$devcent') show 
' >> ${pathresult}/${outputfile}
  fi

fi

# legende

  textx=$originx
  texty=$originy

  ## C10 case
  if [ $j -eq 5 ]; then
      let "textx-=28"
      let "texty-=10"
  fi

  let "textx+=2"
  let "texty+=16"


  echo '
0 0 0 setrgbcolor
/Times-Bold findfont 12 scalefont setfont 
'$textx' '$texty' moveto 
('$label') show 
' >> ${pathresult}/${outputfile}


 let "j += 1"

	done




################################### Drawing D cells Extended
j=0

echo 'Extended D Cells ...'

# jmax est le nfile de do_plot_vvhh_vienna.kumac 

nextpos=408

until [ $j -gt $EDmax ]
	    do 
  originy=214

  ####### special D4 cell
  if [ $j -le 0 ]; then
      originy=248
      nextpos=372
  fi
  ######


  name=${EDcells[$j]}
  width=${EDcellw[$j]}
  height=${EDcellh[$j]}
  originx=$nextpos
  deviation=${EDcellg[$j]}
  label=${EDcells[$j]}
  rcol=0
  bcol=0


  ####### special D4 cell
  if [ $j -le 0 ]; then
      let "nextpos+=2"
  fi
  ######

  let "nextpos+=$width"
  let "nextpos+=2"

  negadev=`echo "c=0;a=$deviation/1;if(0>a)c=1;c"|bc`

  ## which colour
  if [ $negadev -ne 1 ]; then
      if [ $deviation -lt $mindev ]; then
	  vcol=1
	  rcol=`echo "scale=2; $deviation/$mindev" | bc`
      else 
	  rcol=1
	  vcol=`echo "scale=2; ($maxdev-$deviation)/$mindev" | bc`
      fi

      if [ $deviation -gt $maxdev ]; then
	  rcol=1
	  vcol=0
      fi
  fi

  ## dev positive
  if [ $negadev = 1 ]; then
      let "deviation*=-1"
      if [ $deviation -lt $mindev ]; then
	  vcol=1
	  bcol=`echo "scale=2; $deviation/$mindev" | bc`
      else 
	  bcol=1
	  vcol=`echo "scale=2; ($maxdev-$deviation)/$mindev" | bc`
      fi

      if [ $deviation -gt $maxdev ]; then
	  bcol=1
	  vcol=0
      fi
      let "deviation*=-1"
  fi

  echo 'colours = '$rcol' '$vcol' '$bcol' deviation= '$deviation
  ##

  echo '
newpath
'$originx' '$originy' moveto
0 '$height' rlineto
'$width' 0 rlineto
0 -'$height' rlineto
-'$width' 0 rlineto
closepath
gsave
'$rcol' '$vcol' '$bcol' setrgbcolor
fill' >> ${pathresult}/${outputfile}

# vals
if [ $printvals==1 ]; then
  textx=$originx
  texty=$originy
  let "textx+=2"
  let "texty+=4"
  devcent=`echo "scale=2; $deviation/-100" | bc`
  # abs value
  absdevcent=`echo "a=$deviation/1;if(0>a)a*=-1;a"|bc`
  # show only large variations
  if [ $absdevcent -ge $threshold ]; then
      echo '
0 0 0 setrgbcolor
/Helvetica findfont 12 scalefont setfont 
'$textx' '$texty' moveto 
('$devcent') show 
' >> ${pathresult}/${outputfile}
  fi

fi

# legende

  textx=$originx
  texty=$originy
  let "textx+=2"
  let "texty+=16"


  echo '
0 0 0 setrgbcolor
/Times-Bold findfont 12 scalefont setfont 
'$textx' '$texty' moveto 
('$label') show 
' >> ${pathresult}/${outputfile}


 let "j += 1"

	done

################################### Drawing E cells Extended
j=0

echo 'Extended E Cells ...'

# jmax est le nfile de do_plot_vvhh_vienna.kumac 

nextpos=153

until [ $j -gt $Emax ]
	    do 
  originx=400

  name=${Ecells[$j]}
  width=${Ecellw[$j]}
  height=${Ecellh[$j]}
  originy=$nextpos
  deviation=${Ecellg[$j]}
  label=${Ecells[$j]}
  rcol=0
  bcol=0


  let "nextpos-=$height"
  let "nextpos-=2"

  negadev=`echo "c=0;a=$deviation/1;if(0>a)c=1;c"|bc`

  ## which colour
  if [ $negadev -ne 1 ]; then
      if [ $deviation -lt $mindev ]; then
	  vcol=1
	  rcol=`echo "scale=2; $deviation/$mindev" | bc`
      else 
	  rcol=1
	  vcol=`echo "scale=2; ($maxdev-$deviation)/$mindev" | bc`
      fi

      if [ $deviation -gt $maxdev ]; then
	  rcol=1
	  vcol=0
      fi
  fi

  ## dev positive
  if [ $negadev = 1 ]; then
      let "deviation*=-1"
      if [ $deviation -lt $mindev ]; then
	  vcol=1
	  bcol=`echo "scale=2; $deviation/$mindev" | bc`
      else 
	  bcol=1
	  vcol=`echo "scale=2; ($maxdev-$deviation)/$mindev" | bc`
      fi

      if [ $deviation -gt $maxdev ]; then
	  bcol=1
	  vcol=0
      fi
      let "deviation*=-1"
  fi

  echo 'colours = '$rcol' '$vcol' '$bcol' deviation= '$deviation
  ##

  echo '
newpath
'$originx' '$originy' moveto
0 '$height' rlineto
'$width' 0 rlineto
0 -'$height' rlineto
-'$width' 0 rlineto
closepath
gsave
'$rcol' '$vcol' '$bcol' setrgbcolor
fill' >> ${pathresult}/${outputfile}

# vals
if [ $printvals==1 ]; then
  textx=$originx
  texty=$originy
  let "textx-=28"
  let "texty+=4"
  devcent=`echo "scale=2; $deviation/-100" | bc`
  # abs value
  absdevcent=`echo "a=$deviation/1;if(0>a)a*=-1;a"|bc`
  # show only large variations
  if [ $absdevcent -ge $threshold ]; then
      echo '
0 0 0 setrgbcolor
/Helvetica findfont 12 scalefont setfont 
'$textx' '$texty' moveto 
('$devcent') show 
' >> ${pathresult}/${outputfile}
  fi

fi

# legende

  textx=$originx
  texty=$originy
  let "textx-=20"
  let "texty+=17"


  echo '
0 0 0 setrgbcolor
/Times-Bold findfont 12 scalefont setfont 
'$textx' '$texty' moveto 
('$label') show 
' >> ${pathresult}/${outputfile}


 let "j += 1"

	done



echo 'Scale'

##### scale

j=0

rcol=0
vcol=0
bcol=0
xpos=1

until [ $j -ge 101 ]
  do

let "xpos += 2"

deviation=`echo "500*(50-$j)/50"|bc`
deviationp=`echo "scale=1;-5*(50-$j)/50"|bc`
showval=`echo "$j%25"|bc`

######
  negadev=`echo "c=0;a=$deviation/1;if(0>a)c=1;c"|bc`

  ## which colour
  if [ $negadev -ne 1 ]; then
      if [ $deviation -lt $mindev ]; then
	  vcol=1
	  rcol=`echo "scale=2; $deviation/$mindev" | bc`
      else 
	  rcol=1
	  vcol=`echo "scale=2; ($maxdev-$deviation)/$mindev" | bc`
      fi

      if [ $deviation -gt $maxdev ]; then
	  rcol=1
	  vcol=0
      fi
  fi

  ## dev positive
  if [ $negadev = 1 ]; then
      let "deviation*=-1"
      if [ $deviation -lt $mindev ]; then
	  vcol=1
	  bcol=`echo "scale=2; $deviation/$mindev" | bc`
      else 
	  bcol=1
	  vcol=`echo "scale=2; ($maxdev-$deviation)/$mindev" | bc`
      fi

      if [ $deviation -gt $maxdev ]; then
	  bcol=1
	  vcol=0
      fi
      let "deviation*=-1"
  fi
######

  echo '
newpath
'$xpos' 30 moveto
0 10 rlineto
2 0 rlineto
0 -10 rlineto
-2 0 rlineto
closepath
gsave
'$rcol' '$vcol' '$bcol' setrgbcolor
fill' >> ${pathresult}/${outputfile}

######


if [ $showval -eq 0 ]; then

  textx=$xpos
  texty=45
  let "textx-=2"

symb=''
if [ $j -eq 0 ]; then
    symb="<"
fi
if [ $j -eq 100 ]; then
    symb=">"
fi

  echo '
0 0 0 setrgbcolor
/Times-Bold findfont 12 scalefont setfont 
'$textx' '$texty' moveto 
('$symb$deviationp'\%) show 
' >> ${pathresult}/${outputfile}

fi


 let "j += 1"

	done

echo '
0 0 0 setrgbcolor
/Times findfont 12 scalefont setfont 
0 0 moveto 
('$daterun') show 
' >> ${pathresult}/${outputfile}

exit 
