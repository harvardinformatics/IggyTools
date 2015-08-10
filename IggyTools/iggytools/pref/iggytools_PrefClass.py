import os.path as path
from iggytools.utils.util import getUserHome
from iggytools.pref.derived.iggypipe_prefClass import Iggypipe_Preferences
from iggytools.pref.derived.iggyref_fileClass import Iggyref_PrefFile
from iggytools.pref.derived.iggyseq_fileClass import Iggyseq_PrefFile

class Iggytools_Preferences(object):


    def __init__(self, prefDir = None):  

        if not prefDir:
            prefDir = path.join(getUserHome(), '.iggytools')

        self.prefDir = prefDir

    def getPreferences(self):

        refFile  = Iggyref_PrefFile(self.prefDir)
        seqFile  = Iggyseq_PrefFile(self.prefDir)
        pipePref = Iggypipe_Preferences(self.prefDir)

        p = dict()

        p['iggyref']  = refFile.getVars()
        p['iggyseq']  = seqFile.getVars()
        p['iggypipe'] = pipePref.getPreferences()

        return p


