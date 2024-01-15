#!/usr/bin/env python3
import os
import sys
import random
from datetime import datetime as dt

def main(config_module):
    from packet import Packet
    from printer import ecprint
    from anonymizer import Anonymizer

    common_time = dt.now()                          #OBTENEMOS UN TIEMPO COMÚN AL QUE TRASLADAR LAS TRAZAS
    random.shuffle(config_module.TRACES)            #REORDENAMOS ALEATORIAMENTE LAS TRAZAS
    anonym = Anonymizer(config_module.HOSTS_POOL, config_module.OTHERS_POOL)
    readed_traces = []

    #First pass : write each pcap as a temporal csv file
    for trace_index, trace in enumerate(config_module.TRACES):
        tmpfile = '{}/{}_{}'.format('/'.join(trace['file'].split('/')[:-1]), dt.timestamp(dt.now()), trace['file'].split('/')[-1])
        readed_traces.append({'target' : trace['label'], 'host' : anonym.add_host(trace['host']), 'tmpfile' : tmpfile})
        trace_time = None
        if config_module.VERBOSE : ecprint(trace['file'], color='blue', template = 'reading trace : {}')

        with open(trace['file'], 'r') as f, open(tmpfile, 'w') as dstf:
            f.readline()                                                #ignoramos la cabecera del csv
            for line in f:
                packet = Packet.from_csv_line(line)
                if packet == None: continue                             #error en el parser

                if trace_time == None: trace_time = packet.time         #guardamos el tiempo de inicio de la traza
                packet.time = common_time + (packet.time - trace_time)  #Trasladamos temporalmente el paquete

                anonym.anonimize(packet, original = trace['host'])      #Anonimizamos las ips

                dstf.write(packet.as_csv_line())			#Append packets to the tmp file


    if config_module.VERBOSE : ecprint('Saving preprocessing results', color='green')

    #Second pass : merge the csv files. --> Made in 2 iterations to avoid having to keep all the packets in memory simultaneously
    tmp_files = [open(r['tmpfile'], 'r') for r in readed_traces]				#Open all the files
    tmp_packets = [Packet.from_csv_line(f.readline()) for f in tmp_files]			#Get the first packet of each file
    with open(config_module.DATA_FILE, 'w') as f:
        f.write(Packet.csv_header())
        while len(tmp_packets) > 0:
            tmp_times = [p.time for p in tmp_packets]						#Get an array with the packet times
            next_packet = tmp_times.index(min(tmp_times))					#Find first packet in time
            f.write(tmp_packets[next_packet].as_csv_line())					#Write to output file
            next_line = tmp_files[next_packet].readline()					#Read next line
            if next_line is not '': tmp_packets[next_packet] = Packet.from_csv_line(next_line)	#If not EOF: override the readed packet with the next one in that file
            else :										#else:
                tmp_packets = tmp_packets[:next_packet] + tmp_packets[next_packet + 1:]		#   pop the readed packet
                tmp_files[next_packet].close()							#   close the file
                tmp_files = tmp_files[:next_packet] + tmp_files[next_packet + 1:]		#   pop the full readed file

    for r in readed_traces: os.remove(r['tmpfile'])						#Remove the tmp files

    if config_module.VERBOSE : ecprint(config_module.DATA_FILE, color='blue', template = 'saved merged traces : {}')

    #Save the target map --> address - activity
    if config_module.VERBOSE : ecprint('Saving targetmap', color='green')
    with open(config_module.TARGET_FILE, 'w') as f:
        f.write('host,target\n')
        for t in readed_traces:
            f.write('{},{}\n'.format(t['host'], t['target']))
    if config_module.VERBOSE : ecprint(config_module.TARGET_FILE, color='blue', template = 'saved targets : {}')


if __name__ == '__main__':
    try:
        if not os.path.isfile(sys.argv[1]) : sys.exit('Could not find the config file at {}'.format(sys.argv[1]))
        config_path = '/'.join(sys.argv[1].split('/')[:-1])     #Get all the path without the file
        config_file = sys.argv[1].split('/')[-1].split('.')[0]  #Get the file without extension
    except IndexError: sys.exit('This scripts needs the absolute path to the config file as argument')

    sys.path.insert(0, config_path)
    CONFIG = __import__(config_file)
    sys.path.insert(0, CONFIG.MODULES_PATH)

    main(config_module = CONFIG)
