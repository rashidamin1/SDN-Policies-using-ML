#!/bin/bash
#Check for the help option
while getopts 'h' option; do
	case $option in
		h)
			echo "usage : capturepcap.sh interface addr file"
			echo
			echo "positional arguments:"
			echo "  interface			: network interface to capture (eth0, wlan0)"
			echo "  addr				: address of the monitoriced host (10.0.0.1)"
			echo "  file				: filename of the resulting pcap (file.pcap)"
			echo
			echo "optional arguments:"
			echo "  -h				: show this help message and exit"
			echo
			echo "example : capturepcap.sh eth0 10.0.0.1 file.pcap"
			exit
	esac
done

#Check for the correct amount of args
if [ "$#" -ne 3 ]; then
	echo "Error : There are 3 required arguments"
	echo "Usage : capturepcap.sh interface addr file"
	echo "Use option -h for help"
	exit
fi


#Set the segmentation offload off
sudo ethtool -K $1 gro off
sudo ethtool -K $1 gso off
sudo ethtool -K $1 tso off
sudo ethtool -K $1 ufo off
sudo ethtool -K $1 lro off

#Start the capture
sudo tshark -i $1 -w $3 -F pcap host $2

#For continuous capture and rotating files
#sudo tshark -i $1 -F pcap -w $3 -b duration:60 -b files:8 host $2
