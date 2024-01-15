main_path = '/media/victor/disco/publish_code'
MODULES_PATH = '{}/modules'.format(main_path)

datapath =  '{}/data'.format(main_path)
TRAFFIC_FILE = '{}/preprocessed/preprocessed.csv'.format(datapath)
TARGETMAP_FILE = '{}/preprocessed/targetmap.csv'.format(datapath)

CAPTURE_NET = '^10\\.0\\.\\d{1,3}\\.\\d{1,3}'
W1 = 5.0
W2 = 0.5

RESTRUCTURED_FILE = '{}/restructured/restructured.pickle'.format(datapath)

VERBOSE = True
