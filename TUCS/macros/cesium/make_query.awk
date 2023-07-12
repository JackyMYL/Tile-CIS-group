BEGIN{
# priority of statusPMT; do not use 0
# status with biger priority number overwrite others

  priority["integrator malfunction"] = 30;
  priority["overflow"] = 25;
  priority["wrong number of peaks"] = 22;
  priority["big ped RMS"] = 20;
  priority["input data with spikes"] = 15;
  priority["dead channel"] = 10;
  priority["low signal"] = 8;
  priority["OK"] = 3;

  path = ARGV[1];
  match(path,"cs([[:digit:]]+)_.+\\.db",runnum);
  Run=runnum[1];
}

/^time/{Time=$2 " " $3;}
/^module/{Module=$2;}
/^partition/{Partition=$2;}
/^source/{Source=$2;}
/^statusPMT/{
  st=$2;
  for(i=3;i<=NF;i++)
    st = st " " $i;
  if(Status[$1]){
    if(priority[st]>priority[Status[$1]]) Status[$1]=st;
  }else Status[$1] = st;
}
END{
#make a query
#  print "USE test;";
  print "INSERT IGNORE INTO runDescr SET";
  print "run='" Run "'";
  print ",partition='" Partition "'";
  print ",module='" Module "'";
  print ",time='" Time "'";
  print ",source='" Source "'";
  for(itr in Status) print ","itr "='" Status[itr] "'";
  print ";";
}
