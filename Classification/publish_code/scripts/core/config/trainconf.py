main_path = '/media/victor/disco/publish_code'
MODULES_PATH = '{}/modules'.format(main_path)

datapath =  '{}/data'.format(main_path)
TRAINING_SET = '{}/restructured/train.pickle'.format(datapath)

import sys
sys.path.insert(0, MODULES_PATH)
from dataStructure import Features

MODEL_CONFIG = {
    'layer1_features' : Features.BWindow.ALL,
    'layer1_params' : {
        'n_clusters' : 15
    },

    'layer2_features' : Features.Flow.ALL,
    'layer2_params' : {
        'n_clusters': 20
    },

    'layer3_features' : Features.CWindow.ALL,
    'layer3_params' : {
        'kernel' : 'rbf',
        'gamma' : 'auto',
        'C' : 1.0
    }
}

MODEL_FILE = '{}/model/model.pickle'.format(datapath)
VERBOSE = True
