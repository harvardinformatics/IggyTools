import os.path as path
import logging, sys, imp
from iggytools.util import mkdir_p

# Main settings
IGGYMOD_LIST = ['fastqc', 'trimmomatic']
IGGYPIPE_DIR = path.join( os.environ['HOME'], '.iggypipe' )
PREFERENCES_DIR = path.join(IGGYPIPE_DIR, 'userPreferences')
SRC_DIR = path.dirname(__file__)

# Get LOG_DIR and default TEMP_DIR from user settings
pref_file = path.join(PREFERENCES_DIR, 'userSettings.py')
if path.isfile(pref_file):
    userPref = imp.load_source('userSettings', path.join(PREFERENCES_DIR,'userSettings.py'))
    if hasattr(userPref, 'LOG_DIR') and userPref.LOG_DIR:
        LOG_DIR = userPref.LOG_DIR
    if hasattr(userPref, 'TEMP_DIR') and userPref.TEMP_DIR:
        TEMP_DIR = userPref.TEMP_DIR
else:
    LOG_DIR = path.join(IGGYPIPE_DIR, 'log')
    TEMP_DIR = path.join(IGGYPIPE_DIR, 'temp') 

mkdir_p(LOG_DIR)
mkdir_p(TEMP_DIR)

# Database name
DB_NAME = 'iggypipe'

# Logging configuration
logging.basicConfig(filename = path.join(LOG_DIR, 'iggypipe.log'),
                    format = '%(asctime)s - %(name)s - %(funcName)s - %(levelname)s - %(message)s',
                    datefmt = '%m/%d/%Y %I:%M:%S %p',
                    level = logging.DEBUG)
log = logging.getLogger('iggypipe')
sh = logging.StreamHandler(sys.stdout)
sh.setLevel(logging.DEBUG)
sh.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(funcName)s - %(levelname)s - %(message)s'))
log.addHandler(sh)

