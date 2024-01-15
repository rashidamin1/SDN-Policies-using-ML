#!/usr/bin/env python3
import argparse

parser = argparse.ArgumentParser(formatter_class=argparse.RawTextHelpFormatter, epilog = '{}\n{}'.format(
	'example : pcap2csv.py file.pcap file.csv',
	'example : pcap2csv.py -v -vb 10000 -wb 25000 -se on file.pcap file.csv'
))
parser.add_argument('pcap', help = 'pcap file to read')
parser.add_argument('csv', help = 'csv file to save')
parser.add_argument('-v', '--verbose', help = 'print the progress to stdout', action = 'store_true', default=False)
parser.add_argument('-vb', '--vbuffer', help = 'print progress every n packets.\nshould be used with -v option.\ndefault 5000', type=int, metavar ='n', default=5000)
parser.add_argument('-wb', '--wbuffer', help = 'write to output file every n packets.\ndefault 5000', type=int, metavar='n', default=5000)
parser.add_argument('-se', '--skip_empty', help = 'ignore packets with empty payload.\ndefault on', choices=['off', 'on'], default = 'on')
args = parser.parse_args()


#Get required args
srcfile, dstfile = args.pcap, args.csv

#Get optional args
verbose, vbuffer, wbuffer = args.verbose, args.vbuffer, args.wbuffer
skip_empty = True if (args.skip_empty == 'on') else False

#Required internal vars
pkt_count = 0
buffer_count = 0
verbose_count = 0
data_buffer = []

#Imports
from scapy.utils import RawPcapReader
from scapy.layers.l2 import Ether
from scapy.layers.inet import IP, TCP, UDP

#MAIN
with open(dstfile, 'w') as dst:
	dst.write('time,proto,data_len,ip_src,ip_dst,src_port,dst_port\n')

	#READ THE PCAP FILE
	for (pkt_data, pkt_metadata,) in RawPcapReader(srcfile):
		ether_pkt = Ether(pkt_data)

		#FILTER NON RELEVANT PACKETS
		if 'type' not in ether_pkt.fields: continue		# LLC frames will have 'len' instead of 'type'.
		if ether_pkt.type != 0x0800: continue			# disregard non-IPv4 packets

		ip_pkt = ether_pkt[IP]
		if ip_pkt.proto == 6 or ip_pkt.proto == 17:		# if UDP or TCP
			pkt = ip_pkt[TCP if ip_pkt.proto == 6 else UDP]
			data_len = (len(pkt) - (pkt.dataofs * 4)) if (ip_pkt.proto == 6) else len(pkt)
			sport, dport = ip_pkt.payload.sport, ip_pkt.payload.dport
		else :							# if other IP packet
			continue 					# filter non TCP-UDP packets
			#data_len = len(ip_pkt)
			#sport, dport = '', ''

		if skip_empty and data_len == 0: continue		# Skip packets with an empty payload


		#GET THE CSV LINE FOR THE ACTUAL PACKET
		pkt_timestamp = (pkt_metadata.sec) + (pkt_metadata.usec / 1000000)
		pkt_line = '{},{},{},{},{},{},{}'.format(
		    pkt_timestamp, ip_pkt.proto, data_len,
		    ip_pkt.src, ip_pkt.dst,
		    sport, dport
		)

		#REFRESH INTERNAL VARIABLES
		pkt_count += 1
		verbose_count += 1
		buffer_count += 1
		data_buffer.append(pkt_line)

		#PRINT THE PROGRESS AND RESET THE COUNTER
		if verbose and verbose_count >= vbuffer:
			print('Parsed packets : {}'.format(pkt_count), end='\r')
			verbose_count = 0

		#WRITE TO THE CSV FILE AND RESET COUNTER AND BUFFER
		if buffer_count >= wbuffer:
			dst.write('{}\n'.format('\n'.join(data_buffer)))
			buffer_count = 0
			data_buffer = []

	#PUSH THE LAST LINES IF THEY DID NOT REACH THE BUFFER WRITTING THRESHOLD
	if buffer_count > 0:
		dst.write('{}\n'.format('\n'.join(data_buffer)))
		if verbose: print('Parsed packets : {}'.format(pkt_count))

if verbose: print('Parse finished, csv file in {}'.format(dstfile))
