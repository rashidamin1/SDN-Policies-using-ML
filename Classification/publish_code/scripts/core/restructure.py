#!/usr/bin/env python3
import os
import sys

def main(config_module):
    from packet import Packet
    import dataStructure
    from printer import ecprint

    if config_module.VERBOSE : ecprint(['Preparing data structure for:', config_module.CAPTURE_NET, config_module.W1, config_module.W2], color=['green', 'yellow', 'yellow', 'yellow'], template = '{}:\n\tNet pattern : {}\n\tW1 Length : {}\n\tW2 Length : {}')
    dataStr = dataStructure.DataStructure(config_module.CAPTURE_NET, config_module.W1, config_module.W2)
    if config_module.VERBOSE : ecprint(config_module.TRAFFIC_FILE, color = 'blue', template = 'Reading traffic file : {}')
    with open(config_module.TRAFFIC_FILE, 'r') as src:
        src.readline()
        for line in src:
            packet = Packet.from_csv_line(line)
            if packet == None: continue
            dataStr.add_packet(packet)

    dataStr.load_tmap(config_module.TARGETMAP_FILE)
    dataStr.save(config_module.RESTRUCTURED_FILE)
    if config_module.VERBOSE : ecprint(config_module.RESTRUCTURED_FILE, color = 'blue', template = 'Restructured data saved at {}')


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
