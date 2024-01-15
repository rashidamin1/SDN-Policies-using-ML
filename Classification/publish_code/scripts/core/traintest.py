#!/usr/bin/env python3
import sys
import argparse
import os

parser = argparse.ArgumentParser(formatter_class=argparse.RawTextHelpFormatter, epilog = '{}\n{}'.format(
        'example : traintest.py split.py config/splitconf.py train.py config/trainconf.py test.py config/testconf.py',
        'example : traintest.py -vv split.py config/splitconf.py train.py config/trainconf.py test.py config/testconf.py'
))
parser.add_argument('splitscript', help = 'absolute path to the split script')
parser.add_argument('splitconf', help = 'absolute path to the split config file')
parser.add_argument('trainscript', help = 'absolute path to the train script')
parser.add_argument('trainconf', help = 'absolute path to the train config file')
parser.add_argument('testscript', help = 'absolute path to the test script')
parser.add_argument('testconf', help = 'absolute path to the test config file')
parser.add_argument('-i', '--iterations', help = 'number of iterations. Default 100', default = 100, type = int, metavar = 'n')
parser.add_argument('-v', '--verbose', help = 'increase the verbosity level\n  -v  : Level 1 : print for each iteration\n  -vv : Level 2 : enable verbose in the python scripts', action = 'count', default=0)
args = parser.parse_args()

if not os.path.isfile(args.splitscript): sys.exit('Could not find split script at {}'.format(args.splitscript))
if not os.path.isfile(args.splitconf): sys.exit('Could not find split config file at {}'.format(args.splitconf))
if not os.path.isfile(args.trainscript): sys.exit('Could not find train script at {}'.format(args.trainscript))
if not os.path.isfile(args.trainconf): sys.exit('Could not find train config file at {}'.format(args.trainconf))
if not os.path.isfile(args.testscript): sys.exit('Could not find test script at {}'.format(args.testscript))
if not os.path.isfile(args.testconf): sys.exit('Could not find test config file at {}'.format(args.testconf))

#SPLIT
#script file
split_script_path = '/'.join(args.splitscript.split('/')[:-1])     #Get all the path without the file
split_script_file = args.splitscript.split('/')[-1].split('.')[0]  #Get the file without extension
#Config file
split_config_path = '/'.join(args.splitconf.split('/')[:-1])     #Get all the path without the file
split_config_file = args.splitconf.split('/')[-1].split('.')[0]  #Get the file without extension

#TRAIN
#script file
train_script_path = '/'.join(args.trainscript.split('/')[:-1])     #Get all the path without the file
train_script_file = args.trainscript.split('/')[-1].split('.')[0]  #Get the file without extension
#Config file
train_config_path = '/'.join(args.trainconf.split('/')[:-1])     #Get all the path without the file
train_config_file = args.trainconf.split('/')[-1].split('.')[0]  #Get the file without extension

#TEST
#script file
test_script_path = '/'.join(args.testscript.split('/')[:-1])     #Get all the path without the file
test_script_file = args.testscript.split('/')[-1].split('.')[0]  #Get the file without extension
#Config file
test_config_path = '/'.join(args.testconf.split('/')[:-1])     #Get all the path without the file
test_config_file = args.testconf.split('/')[-1].split('.')[0]  #Get the file without extension


sys.path.insert(0, split_script_path)
SPLIT_SCRIPT = __import__(split_script_file)
sys.path.insert(0, split_config_path)
SPLIT_CONFIG = __import__(split_config_file)

sys.path.insert(0, train_script_path)
TRAIN_SCRIPT = __import__(train_script_file)
sys.path.insert(0, train_config_path)
TRAIN_CONFIG = __import__(train_config_file)

sys.path.insert(0, test_script_path)
TEST_SCRIPT = __import__(test_script_file)
sys.path.insert(0, test_config_path)
TEST_CONFIG = __import__(test_config_file)

sys.path.insert(0, SPLIT_CONFIG.MODULES_PATH)
from printer import ecprint

if args.verbose < 2:
    SPLIT_CONFIG.VERBOSE = False
    TRAIN_CONFIG.VERBOSE = False
    TEST_CONFIG.VERBOSE = False
else :
    SPLIT_CONFIG.VERBOSE = True
    TRAIN_CONFIG.VERBOSE = True
    TEST_CONFIG.VERBOSE = True

for i in range(args.iterations):
    TEST_CONFIG.TEST_CODE = i
    if args.verbose > 0: ecprint('Starting iteration {}'.format(i), color = 'cyan', mode=['bold', 'underlined'])
    train, test = SPLIT_SCRIPT.main(config_module = SPLIT_CONFIG, save = False)
    model = TRAIN_SCRIPT.main(config_module = TRAIN_CONFIG, train = train, save = False)
    TEST_SCRIPT.main(config_module = TEST_CONFIG, test = test, model = model)
