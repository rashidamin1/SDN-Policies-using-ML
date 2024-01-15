#!/usr/bin/env python3
import sys
import os

if '-h' in sys.argv : sys.exit('{}\n{}\n\t{}\n\n{}'.format(
	'First argument can be specified to provide the path to the modules folder if they are not in a default one',
	'Now your paths are :',
	'\n\t'.join(sys.path),
	'For adding a path use "export PYTHONPATH=/your/path/to/modules:$PYTHONPATH"'
))

#LINUX PACKAGES
if int(os.system('ethtool --version 2>&1 > /dev/null')) is not 0: print('Package : ethtool : Check failed')
else : print('Package : ethtool : OK')

if int(os.system('tshark -v 2>&1 > /dev/null')) is not 0: print('Package : tshark : Check failed')
else : print('Package : tshark : OK')

if int(os.system('awk -V 2>&1 > /dev/null')) is not 0: print('Package : awk : Check failed')
else : print('Package : awk : OK')

if int(os.system('sleep --version 2>&1 > /dev/null')) is not 0: print('Package : sleep : Check failed')
else : print('Package : sleep : OK')

#PYTHON PACKAGES
def failure(package_name):
	print('Module : {} : Failed to import'.format(package_name))
	return False
def success(package_name):
	print('Module : {} : OK'.format(package_name))
	return True
def imp(package_name):
	try : __import__(package_name)
	except : return failure(package_name)
	else : return success(package_name)

#Python modules
required_modules = [
	're',
	'math',
	'datetime',
	'random',
	'argparse',
	'ipaddress',
	'numpy',
	'pickle',
	'scapy',
	'sklearn'
]
results = [imp(m) for m in required_modules]


if len(sys.argv) >= 2 : sys.path.insert(0, sys.argv[1])
custom_modules = [
	'packet',
	'anonymizer',
	'splitter',
	'dataStructure',
	'clsModel',
	'printer'
]
custom_results = [imp(m) for m in custom_modules]


if False in results:
	try :
		from printer import ecprint
		ecprint('Error in required modules : Some modules could not be imported', color = 'red')
	except : print('Error in required modules : Some modules could not be imported')

if False in custom_results:
	try :
		from printer import ecprint
		ecprint('Error in custom modules : Try providing the absolute path to the custom modules folder as argument', color = 'red')
	except : print('Error in custom modules : Try providing the absolute path to the custom modules folder as argument')

if (not False in results) and (not False in custom_results):
	from printer import ecprint
	ecprint('Check passed without errors', color = 'green')
