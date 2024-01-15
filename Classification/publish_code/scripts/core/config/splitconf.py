main_path = '/media/victor/disco/publish_code'
MODULES_PATH = '{}/modules'.format(main_path)

datapath =  '{}/data'.format(main_path)
DATASET = '{}/restructured/restructured.pickle'.format(datapath)

TRAIN_RATE = 0.6

FILTER_SIZE = 1024 * 3
def WINDOW_FILTER(CW):
    return ((CW.get_pktSizeSum() > FILTER_SIZE) or (CW.target == 'idle'))

STORE_SPLIT_STATISTICS = True
SPLIT_FILE = '{}/results/crossval_split.csv'.format(datapath)

TRAIN_FILE = '{}/restructured/train.pickle'.format(datapath)
TEST_FILE = '{}/restructured/test.pickle'.format(datapath)

VERBOSE = True
