import os.path as path
import sys, os, yaml, imp, re, logging
from collections import namedtuple
from iggytools.utils.util import mkdir_p, copy, getUserHome

def iggytools_prefDir_setup(customPrefDir): #create preferences if not already present
    userHome = getUserHome()
    if not customPrefDir:  
        iggytools_prefDir = path.join(userHome, '.iggytools')
    else:
        iggytools_prefDir = customPrefDir

    iggyref_prefFile = path.join(iggytools_prefDir ,'iggyref_settings.yaml')
    iggytools_srcDir = imp.find_module('iggytools')[1]

    #create iggyref pref file if it doesn't exist
    if not path.isfile(iggyref_prefFile):
        mkdir_p(iggytools_prefDir)
        iggyref_prefTemplate = path.join(iggytools_srcDir, 'config', 'preferenceTemplates', 'iggyref_settings.yaml')
        with open(iggyref_prefTemplate, 'r') as fh:
            contents = fh.read()
        contents = re.sub('<path_to_repository_directory>',path.join(userHome, 'iggyref'), contents) # set repo dir to $HOME/iggyref by default
        with open(iggyref_prefFile, 'w') as fh:
            fh.write(contents)

    return dict(iggyref = iggyref_prefFile)  #dict of prefFiles for iggytools

def get_iggyref_preferences(customPrefDir = None):
    prefFiles = iggytools_prefDir_setup(customPrefDir)
    iggyref_prefFile = prefFiles['iggyref']

    with open(iggyref_prefFile, 'r') as fh:
        pref = yaml.load(fh)

    #preferences container
    p = namedtuple('p', 'WORK_DIR TEMP_DIR LOG_DIR DOWNLOAD_DIR DEBUG_DIR REPO_DIR' \
                             + 'DB_TYPE MYSQL_HOST MYSQL_DB MYSQL_USER MYSQL_PASS' \
                             + 'DEBUG LOG_LEVEL')
    #directory preferencecs
    p.REPO_DIR     = pref['IGGYREF_REPOSITORY_DIR']
    p.WORK_DIR     = path.join( p.REPO_DIR, '.work'    )
    p.LOG_DIR      = path.join( p.WORK_DIR, 'log'      )
    p.DOWNLOAD_DIR = path.join( p.WORK_DIR, 'download' )
    p.INTERMED_DIR = path.join( p.WORK_DIR, 'intermed' )
    p.TEMP_DIR     = path.join( p.WORK_DIR, 'temp'     )
    p.DEBUG_DIR    = path.join( p.WORK_DIR, 'debug'    )

    #database preferences
    p.DB_TYPE    = pref['IGGYREF_DB_TYPE']
    p.MYSQL_HOST = pref['IGGYREF_MYSQL_HOST']
    p.MYSQL_DB   = pref['IGGYREF_MYSQL_DB']
    p.MYSQL_USER = pref['IGGYREF_MYSQL_USER']
    p.MYSQL_PASS = pref['IGGYREF_MYSQL_PASS']

    #other preferences
    debug = pref['DEBUG']
    if ( type(debug) == str and re.match("true", debug, re.IGNORECASE) ) or \
       ( type(debug) == bool and debug ):
        p.DEBUG = True
    else:
        p.DEBUG = False

    levelString = pref['IGGYREF_LOGGING_LEVEL']
    if re.match('warn', levelString, re.IGNORECASE):
        p.LOG_LEVEL = logging.WARNING
    elif re.match('info', levelString, re.IGNORECASE):
        p.LOG_LEVEL = logging.INFO
    elif re.match('debug', levelString, re.IGNORECASE):
        p.LOG_LEVEL = logging.DEBUG
    else:
        raise Exception('Unrecognized logging level: %s' % levelString)

    return p
