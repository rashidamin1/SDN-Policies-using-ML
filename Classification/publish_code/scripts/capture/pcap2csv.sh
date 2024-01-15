#!/bin/bash

v=0
pids=(0)
empty_index=0
#Check for optional arguments
while getopts 'p:vh' option; do
  case $option in
    p) for i in $(seq 1 $(($OPTARG-1))); do pids[$i]=0; done;;
    v) v=1;;
    h)
      echo "usage : pcap2csv.sh [-v] [-p parallel_threads] srcfolder dstfolder"
      echo
      echo "positional arguments:"
      echo "  srcfolder             : folder to read pcaps from"
      echo "  dstfolder             : folder to save csv at"
      echo
      echo "optional arguments:"
      echo "  -h                    : show this help message and exit"
      echo "  -v                    : print progress to stdout."
      echo "  -p parallel_threads   : number of cores / parallel threads. Default 1"
      echo
      echo "example : pcap2csv.sh pcapfolder csvfolder"
      echo "example : pcap2csv.sh -p 4 -v pcapfolder csvfolder"
      exit
  esac
done

#Check for the correct amount of positional arguments
if [ $(( $# - $OPTIND )) -lt 1 ]; then
	echo "Error : There are 2 required arguments"
	echo "Usage : pcap2csv.sh [-v] [-p parallel_threads] srcfolder dstfolder"
	echo "Use option -h for help"
	exit
fi

#Get the arguments
src=${@:$OPTIND:1}
dst=${@:$OPTIND+1:1}

if [ ! -d $src ]; then
	echo "Src folder does not exist"
	exit
fi
if [ ! -d $dst ]; then
	echo "Dst folder does not exist"
	exit
fi


#Loop for each file in the src folder
for filepath in $src/*.pcap; do

	#Run the parser
	file=$(echo $filepath | awk '{n=split($0, a, "/"); split(a[n], b, "."); print b[1]}')
	if [ $v -eq 1 ]; then
		echo "parsing ${file}"
	fi

	python3 pcap2csv.py -wb 25000 ${src}/${file}.pcap ${dst}/${file}.csv &
	pids[$empty_index]=$!
	sleep 1

	#Check if there is an empty slot in the pids array
	nextfile=0
	for index in ${!pids[*]}; do
		PID=${pids[$index]}
		if [ ${PID} -eq 0 ]; then
			empty_index=$index
			nextfile=1
			break
		fi
	done
	if [ $nextfile -eq 1 ]; then
		continue
	fi

	#Wait to any process to end
	break_while=0
	while true; do

		#Check for any ended process
		for index in ${!pids[*]}; do
			PID=${pids[$index]}
			if ! ps -p $PID > /dev/null; then
				pids[$index]=0
				empty_index=$index
				break_while=1
			fi
		done

		#Break the while or wait before next iteration
		if [ $break_while -eq 1 ]; then
			break
		else
			sleep 2
		fi

	done

done


#Check for all processes to end
while true; do

	#Actualice status
	for index in ${!pids[*]}; do
		PID=${pids[$index]}
		if [ $PID -ne 0 ]; then
			if ! ps -p $PID > /dev/null; then
				pids[$index]=0
			fi
		fi
	done

	#Check if any is still on
	break_while=1
	for index in ${!pids[*]}; do
		PID=${pids[$index]}
		if [ ${PID} -ne 0 ]; then
			break_while=0
			break
		fi
	done

	#Break if all are off
	if [ $break_while -eq 1 ]; then
		break
	else
		sleep 2
	fi

done
