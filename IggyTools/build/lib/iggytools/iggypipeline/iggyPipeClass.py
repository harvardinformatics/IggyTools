import os, glob, sys, logging, yaml, re, traceback
import os.path as path
from iggypipeline.config.settings import SRC_DIR, IGGYPIPE_DIR, PREFERENCES_DIR, LOG_DIR, TEMP_DIR, IGGYMOD_LIST
from iggypipeline.DBclass import iggypipeDB
from iggypipeline.baseModClass import iggyMod
from iggytools.util import mkdir_p, copy

log = logging.getLogger('iggypipe')

class IggyPipe(object):
    def __init__(self):
        self.db = None
        self.preferences_Setup()

        #get pipeline ID # from iggypipeDB function

    def preferences_Setup():
        #ensure preferences files exist
        mkdir_p(PREFERENCES_DIR)
        for mod in IGGYMOD_LIST.append('moduleBase'):
            if not path.isfile(PREFERENCES_DIR, mod+'.yaml'):
                copy( path.join(SRC_DIR, 'preferences', mod+'.yaml'), path.join(PREFERENCES_DIR, mod+'.yaml') )

    def createModule(self):
        pass

    def runMod(self):
        pass

    def __repr__(self):
        return '<IggyPipe(%s)>' % (', '.join(map(str,self.modules)))
