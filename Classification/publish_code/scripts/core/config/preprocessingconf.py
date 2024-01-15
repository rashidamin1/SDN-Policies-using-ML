main_path = '/media/victor/disco/publish_code'
MODULES_PATH = '{}/modules'.format(main_path) #MUST BE A FULLPATH

mapping_file = '{}/data/mapping.csv'.format(main_path)
with open(mapping_file) as f:
	header = f.readline()[:-1].split(',')
	TRACES = [{header[i] : v for i,v in enumerate(line[:-1].split(','))} for line in f]

for obj in TRACES: obj['file'] = '{}/{}/{}'.format(main_path, 'data/csv', obj['file'])

#MUST BE AT LEAST ONE HOST FOR EACH PCAP FILE
HOSTS_POOL = ['10.0.{}.{}'.format(x, y) for x in range(1, 5) for y in range(1, 100)]
OTHERS_POOL = ['20.{}.{}.{}'.format(x, y, z) for x in range(1, 5) for y in range(1, 200) for z in range(1, 200)]

export_path = '{}/data/preprocessed'.format(main_path)
DATA_FILE = '{}/preprocessed.csv'.format(export_path)
TARGET_FILE = '{}/targetmap.csv'.format(export_path)

VERBOSE = True
