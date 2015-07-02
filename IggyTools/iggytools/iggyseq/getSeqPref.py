from os import path

from iggytools.utils.util import getUserHome
from iggytools.pref.iggytools_PrefClass import Iggytools_Preferences

def getSeqPref(prefDir = None):
    if not prefDir:
        prefDir = path.join(getUserHome(), '.iggytools')

    iggyPref = Iggytools_Preferences(prefDir)
    return iggyPref.getPreferences()['iggyseq']

