#!/usr/bin/env python3
import sys
import pickle

def main(config_module, train = None, save = True):
    import clsModel
    import dataStructure
    from printer import ecprint

    if config_module.VERBOSE:
        ecprint('Model parameters', color = 'green')
        ecprint([config_module.MODEL_CONFIG['layer1_features'], config_module.MODEL_CONFIG['layer1_params']], color = 'yellow', template = '\tLayer1\n\t\tFeatures : {}\n\t\tParams : {}')
        ecprint([config_module.MODEL_CONFIG['layer2_features'], config_module.MODEL_CONFIG['layer2_params']], color = 'yellow', template = '\tLayer2\n\t\tFeatures : {}\n\t\tParams : {}')
        ecprint([config_module.MODEL_CONFIG['layer3_features'], config_module.MODEL_CONFIG['layer3_params']], color = 'yellow', template = '\tLayer3\n\t\tFeatures : {}\n\t\tParams : {}')

    #Load training set
    if train == None:
        if config_module.VERBOSE: ecprint(config_module.TRAINING_SET, color = 'blue', template = 'Loading training set : {}')
        train = pickle.load(open(config_module.TRAINING_SET, 'rb'))

    #Configure and compile the model
    if config_module.VERBOSE: ecprint('Compiling model', color = 'green')
    model = clsModel.clsModel(config_module.MODEL_CONFIG)

    #Train the model
    if config_module.VERBOSE: ecprint('Training model', color='green')
    model.train(train)

    #Save the model
    if save == True:
        if config_module.VERBOSE: ecprint('Saving model', color='green')
        pickle.dump(model, open(config_module.MODEL_FILE, 'wb'))
        if config_module.VERBOSE: ecprint(config_module.MODEL_FILE, color='blue', template = 'Model saved at : {}')
    else : return model


if __name__ == '__main__':
    try:
        config_path = '/'.join(sys.argv[1].split('/')[:-1])     #Get all the path without the file
        config_file = sys.argv[1].split('/')[-1].split('.')[0]  #Get the file without extension
    except IndexError: sys.exit('This scripts needs the absolute path to the config file as argument')

    sys.path.insert(0, config_path)
    CONFIG = __import__(config_file)
    sys.path.insert(0, CONFIG.MODULES_PATH)

    main(config_module = CONFIG)
