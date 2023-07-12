#!/bin/bash

#To read database
#TILE
# from sqlite
# AtlCoolConsole.py "sqlite://x;schema=tileSqlite.db;dbname=CONDBR2"
# directly from oracle db
# AtlCoolConsole.py COOLONL_TILE/CONDBR2
#CALO
# from sqlite
# AtlCoolConsole.py "sqlite://x;schema=caloSqlite.db;dbname=CONDBR2"
# directly from oracle db
# AtlCoolConsole.py COOLONL_CALO/CONDBR2

usage()
{
cat<<EOF
usage: $0 -options

This script makes sqlite replicas of the Tile/Calo COOL databse.
Options:
-h   Help
-C   Copy Calo DB (Cell noise, then ignore -D, -H and -S)
-T   Copy Tile DB (Digi noise)
-M   Copy from MC DB - OFLP200 (default: CONDBR2)
-L   Copy Laser constants
-D   Copy TileDigits folders (Unless asked for something else than noise)
-H   Copy TileRawChan folders
-S   Copy TileDQ status folder
-R   Truncate IOV at runnumber
-G   Tag suffix to read
-O   Tag suffix to create
EOF
}

# Check number of arguments
if [ $# -eq 0 ]
then
	usage
	exit 1
fi


while getopts "hTCMLDHNSR:G:O:" OPTION
do
	case $OPTION in
		h)
			usage
			exit 1
			;;
		T)
			COPY_TILE=1
			;;
		C)
			COPY_CALO=1
			;;
		M)
			COPY_MC=1
			;;
		L)
			COPY_LA=1
			;;
		D)
			COPY_DIGI=1
			;;
		H)
			COPY_RAWCH=1
			;;
		N)
			COPY_ONL=1
			;;
		S)
			COPY_DQ=1
			;;
		R)
			RUNNO=$OPTARG
			;;
		G)
			TAG=$OPTARG
			;;
		O)
			OUTTAG=$OPTARG
			;;
	esac
done

# Make tileSqlite.db
if [ $COPY_TILE ]
then
	## DQ folder
	if [ $COPY_DQ ]
	then
		AtlCoolCopy.exe "COOLONL_TILE/CONDBR2" "sqlite://;schema=tileSqlite.db;dbname=CONDBR2" -create -f /TILE/OFL02/STATUS/ADC   -t TileOfl02StatusAdc-RUN2-HLT-UPD1-00
	fi
	if [ $COPY_LA ]
	then
		echo "hej"
		AtlCoolCopy.exe "COOLOFL_TILE/OFLP200" "sqlite://;schema=tileSqlite.db;dbname=OFLP200" -create -f /TILE/OFL02/CALIB/LAS/LIN -t TileOfl02CalibLasLin-COM-00 -tr -rs $RUNNO
		AtlCoolCopy.exe "COOLOFL_TILE/OFLP200" "sqlite://;schema=tileSqlite.db;dbname=OFLP200" -create -f /TILE/OFL02/CALIB/CIS/LIN -t TileOfl02CalibCisLin-COM-00 -tr -rs $RUNNO
		AtlCoolCopy.exe "COOLOFL_TILE/OFLP200" "sqlite://;schema=tileSqlite.db;dbname=OFLP200" -create -f /TILE/OFL02/CALIB/CES -t TileOfl02CalibCes-SIM-04 -tr -rs $RUNNO
		AtlCoolCopy.exe "COOLOFL_TILE/OFLP200" "sqlite://;schema=tileSqlite.db;dbname=OFLP200" -create -f /TILE/OFL02/CALIB/EMS -t TileOfl02CalibEms-COM-00 -tr -rs $RUNNO
	fi
	## Online folder
	if [ $COPY_ONL ]
	then
				AtlCoolCopy.exe "COOLONL_TILE/CONDBR2" "sqlite://;schema=tileSqlite.db;dbname=CONDBR2" -create -f /TILE/ONL01/NOISE/OFNI  -tr -rs $RUNNO
	fi
	## Digi folders
	if [ $COPY_DIGI ]
	then
		if [ $COPY_MC ]
		then
			AtlCoolCopy.exe "COOLOFL_TILE/OFLP200" "sqlite://;schema=tileSqlite.db;dbname=OFLP200" -create -f /TILE/OFL02/NOISE/SAMPLE -t TileOfl02NoiseSample-$TAG
			AtlCoolCopy.exe "COOLOFL_TILE/OFLP200" "sqlite://;schema=tileSqlite.db;dbname=OFLP200" -create -f /TILE/OFL02/NOISE/AUTOCR -t TileOfl02NoiseAutocr-COM-02
		else
			if [ $RUNNO ] 
			then
				AtlCoolCopy.exe "COOLOFL_TILE/CONDBR2" "sqlite://;schema=tileSqlite.db;dbname=CONDBR2" -create -f /TILE/OFL02/NOISE/SAMPLE -t TileOfl02NoiseSample-RUN2-HLT-UPD1-01 -tr -rs $RUNNO
				AtlCoolCopy.exe "COOLOFL_TILE/CONDBR2" "sqlite://;schema=tileSqlite.db;dbname=CONDBR2" -create -f /TILE/OFL02/NOISE/AUTOCR -t TileOfl02NoiseAutocr-RUN2-HLT-UPD1-00 -ot TileOfl02NoiseAutocr-RUN2-HLT-UPD1-01 -tr -rs $RUNNO
				#AtlCoolCopy.exe "COOLONL_TILE/CONDBR2" "sqlite://;schema=tileSqlite.db;dbname=CONDBR2" -create -f /TILE/OFL02/NOISE/SAMPLE -t TileOfl02NoiseSample-RUN2-HLT-UPD1-01 -tr -rs $RUNNO
				#AtlCoolCopy.exe "COOLONL_TILE/CONDBR2" "sqlite://;schema=tileSqlite.db;dbname=CONDBR2" -create -f /TILE/OFL02/NOISE/AUTOCR -t TileOfl02NoiseAutocr-RUN2-HLT-UPD1-00 -ot TileOfl02NoiseAutocr-RUN2-HLT-UPD1-01 -tr -rs $RUNNO
			else
				AtlCoolCopy.exe "COOLOFL_TILE/CONDBR2" "sqlite://;schema=tileSqlite.db;dbname=CONDBR2" -create -f /TILE/OFL02/NOISE/SAMPLE -t TileOfl02NoiseSample-RUN2-HLT-UPD1-01
				AtlCoolCopy.exe "COOLOFL_TILE/CONDBR2" "sqlite://;schema=tileSqlite.db;dbname=CONDBR2" -create -f /TILE/OFL02/NOISE/AUTOCR -t TileOfl02NoiseAutocr-RUN2-HLT-UPD1-00 -ot TileOfl02NoiseAutocr-RUN2-HLT-UPD1-01
			fi
		fi
	fi
	## Channel folders
	#if [ $COPY_RAWCH ]
	#then
	#	if [ $COPY_MC ]
	#	then
	#		AtlCoolCopy.exe "COOLOFL_TILE/OFLP200" "sqlite://;schema=tileSqlite.db;dbname=OFLP200" -create -f /TILE/OFL02/NOISE/FIT    -t TileOfl02NoiseFit-$TAG
	#		AtlCoolCopy.exe "COOLOFL_TILE/OFLP200" "sqlite://;schema=tileSqlite.db;dbname=OFLP200" -create -f /TILE/OFL02/NOISE/OF1    -t TileOfl02NoiseOf1-$TAG
	#		AtlCoolCopy.exe "COOLOFL_TILE/OFLP200" "sqlite://;schema=tileSqlite.db;dbname=OFLP200" -create -f /TILE/OFL02/NOISE/OF2    -t TileOfl02NoiseOf2-$TAG
	#	else
	#		AtlCoolCopy.exe "COOLONL_TILE/CONDBR2" "sqlite://;schema=tileSqlite.db;dbname=CONDBR2" -create -f /TILE/OFL02/NOISE/FIT    -t TileOfl02NoiseFit-RUN2-HLT-UPD1-01
	#		AtlCoolCopy.exe "COOLONL_TILE/CONDBR2" "sqlite://;schema=tileSqlite.db;dbname=CONDBR2" -create -f /TILE/OFL02/NOISE/OF1    -t TileOfl02NoiseOf1-RUN2-HLT-UPD1-01
	#		AtlCoolCopy.exe "COOLONL_TILE/CONDBR2" "sqlite://;schema=tileSqlite.db;dbname=CONDBR2" -create -f /TILE/OFL02/NOISE/OF2    -t TileOfl02NoiseOf2-RUN2-HLT-UPD1-01
	#	fi
	#fi
fi

# Make caloSqlite.db
#   Cell folder - Copy only tile cells (48)
if [ $COPY_CALO ]
then
	if [ -z $OUTTAG ]
	then
		OUTTAG=$TAG
	fi
	if [ $COPY_MC ]
	then
		AtlCoolCopy.exe "COOLOFL_TILE/OFLP200" "sqlite://;schema=caloSqlite.db;dbname=OFLP200" -create -f /TILE/OFL02/NOISE/CELL -t TileOfl02NoiseCell-$TAG -ot TileOfl02NoiseCell-$OUTTAG
		#AtlCoolCopy.exe "COOLOFL_CALO/OFLP200" "sqlite://;schema=caloSqlite.db;dbname=OFLP200" -create -ch 48 -f /CALO/Ofl/Noise/CellNoise -t CaloOflNoiseCellnoise-$TAG -ot CaloOflNoiseCellnoise-$OUTTAG
		#AtlCoolCopy.exe "COOLONL_CALO/OFLP200" "sqlite://;schema=caloSqlite.db;dbname=OFLP200" -create -ch 48 -f /CALO/Noise/CellNoise -of /TILE/OFL02/NOISE/CELL -t CaloNoiseCellnoise-$TAG -ot TileOfl02NoiseCell-$OUTTAG 
		#AtlCoolCopy.exe "COOLONL_CALO/OFLP200" "sqlite://;schema=caloSqlite.db;dbname=OFLP200" -create -ch 48 -f /CALO/Noise/CellNoise -t CaloNoiseCellnoise-$TAG -ot CaloNoiseCellnoise-$OUTTAG 
	else
		if [ $RUNNO ] 
		then
			AtlCoolCopy.exe "COOLOFL_TILE/CONDBR2" "sqlite://;schema=caloSqlite.db;dbname=CONDBR2" -create -f /TILE/OFL02/NOISE/CELL -t TileOfl02NoiseCell-$TAG -ot TileOfl02NoiseCell-$OUTTAG -rs $RUNNO --alliov -nrls 0 0 
			#AtlCoolCopy.exe "COOLOFL_CALO/CONDBR2" "sqlite://;schema=caloSqlite.db;dbname=CONDBR2" -create -ch 48 -f /CALO/Ofl/Noise/CellNoise -t CaloOflNoiseCellnoise-$TAG -ot CaloOflNoiseCellnoise-$OUTTAG -rs $RUNNO --alliov -nrls 0 0 
			#AtlCoolCopy.exe "COOLOFL_CALO/CONDBR2" "sqlite://;schema=caloSqlite.db;dbname=CONDBR2" -create -ch 48 -f /CALO/Ofl/Noise/CellNoise -t CaloOflNoiseCellnoise-$TAG -ot CaloOflNoiseCellnoise-$OUTTAG -tr -rs $RUNNO -nrlu 165956 4294967295 --alliov 
			#AtlCoolCopy.exe "COOLONL_CALO/CONDBR2" "sqlite://;schema=caloSqlite.db;dbname=CONDBR2" -create -ch 48 -f /CALO/Noise/CellNoise -t CaloNoiseCellnoise-$TAG -ot CaloNoiseCellnoise-$OUTTAG -tr -rs $RUNNO -ru 9999999
		else
			AtlCoolCopy.exe "COOLOFL_TILE/CONDBR2" "sqlite://;schema=caloSqlite.db;dbname=CONDBR2" -create -f /TILE/OFL02/NOISE/CELL -t TileOfl02NoiseCell-$TAG -ot TileOfl02NoiseCell-$OUTTAG
			#echo "should copy cells now"
			#AtlCoolCopy.exe "COOLOFL_CALO/CONDBR2" "sqlite://;schema=caloSqlite.db;dbname=CONDBR2" -create -ch 48 -f /CALO/Ofl/Noise/CellNoise -t CaloOflNoiseCellnoise-$TAG -ot CaloOflNoiseCellnoise-$OUTTAG
			#AtlCoolCopy.exe "COOLONL_CALO/CONDBR2" "sqlite://;schema=caloSqlite.db;dbname=CONDBR2" -create -ch 48 -f /CALO/Noise/CellNoise -t CaloNoiseCellnoise-$TAG -ot CaloNoiseCellnoise-$OUTTAG
		fi
	fi
fi
