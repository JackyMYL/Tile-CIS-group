rm -f tileSqlite.db
AtlCoolCopy.exe 'COOLOFL_TILE/COMP200' "sqlite://;schema=tileSqlite.db;dbname=COMP200" -folder /TILE/OFL02/CALIB/CES -r 172000 -t TileOfl02CalibCes-HLT-UPD1-01 -nrls 171194 0 -a -create
#AtlCoolCopy.exe 'COOLONL_TILE/COMP200' "sqlite://;schema=tileSqlite.db;dbname=COMP200" -folder /TILE/ONL01/CALIB/CES -r 172000 -nrls 171194 0 -a
cp tileSqlite.db tileSqlite.db_v1

macros/laser/laser_stab_references.py --low=176858 --high=176859 --iov=171195
cp tileSqlite.db tileSqlite.db_v2

macros/laser/laser_stab_references.py --low=179021 --high=179025 --iov=178784
cp tileSqlite.db tileSqlite.db_v3

macros/laser/laser_stab_references.py --low=179255 --high=179258 --iov=179254
cp tileSqlite.db tileSqlite.db_v4

macros/laser/laser_stab_references.py --low=179667 --high=179670 --iov=179520
cp tileSqlite.db tileSqlite.db_v5

macros/laser/laser_stab_references.py --low=179736 --high=179738 --iov=179735
cp tileSqlite.db tileSqlite.db_v6

macros/laser/laser_stab_references.py --low=181234 --high=181235 --iov=180629
cp tileSqlite.db tileSqlite.db_v8

macros/laser/laser_stab_references.py --low=185298 --high=185304 --iov=184800
cp tileSqlite.db tileSqlite.db_v9

#macros/laser/laser_stab_references.py --low=195971 --high=195972 --iov=194628
#macros/laser/laser_stab_variations.py --low=196193 --high=196194 --iov=196193
#macros/laser/laser_stab_variations.py --low=196417 --high=196418 --iov=196417

#macros/laser/laser_stab_references.py --low=195971 --high=195972 --iov=194628
macros/laser/laser_stab_references.py --low=199381 --high=199382 --iov=194628
cp tileSqlite.db tileSqlite.db_v10

macros/update_HV_ref.py 223100 COOL
macros/laser/laser_stab_references.py --low=223131 --high=223132 --iov=223120 --region=LBA,LBC
cp tileSqlite.db tileSqlite.db_v11

rm tileSqlite.db

ln -sf tileSqlite.db_v10 tileSqlite.db

