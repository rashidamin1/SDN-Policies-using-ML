#!/usr/bin/env python3
import os
import sys
import pickle

def main(config_module, save = True):
    import dataStructure
    from printer import ecprint
    from splitter import Splitter

    #Load the dataset
    if config_module.VERBOSE: ecprint(config_module.DATASET, color = 'blue', template = 'Loading dataset : {}')
    data = pickle.load(open(config_module.DATASET, 'rb'))

    #Split by trace
    if config_module.VERBOSE:
        ecprint('Splitting data', color = 'green')
        ecprint(config_module.TRAIN_RATE, color = 'yellow', template = '\tTRAINING RATE : {}')
        ecprint(1 - config_module.TRAIN_RATE, color = 'yellow', template = '\tTESTING RATE : {}')
        ecprint(config_module.FILTER_SIZE, color = 'yellow', template = '\tWINDOW FILTER : {}')

    train, test = Splitter(
        config_module.TRAIN_RATE,
        config_module.WINDOW_FILTER,
        store_statistics = config_module.STORE_SPLIT_STATISTICS,
        store_file = config_module.SPLIT_FILE
    ).split(data)

    #Save the splitted sets
    if save == True:
        if config_module.VERBOSE: ecprint(['Saving datasets', config_module.TRAIN_FILE, config_module.TEST_FILE], color = ['green', 'blue', 'blue'], template = '{}\n\tTrain: {}\n\tTest: {}')
        pickle.dump(train, open(config_module.TRAIN_FILE, 'wb'))
        pickle.dump(test, open(config_module.TEST_FILE, 'wb'))
    else: return train,test


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
