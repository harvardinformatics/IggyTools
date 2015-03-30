import os.path as path
from iggytools.pref.fileClass import BasePrefFile
from iggytools.utils.util import getUserHome
from iggytools.pref.varClass import PrefVar


class Iggypipe_PrefFile(BasePrefFile):


    def __init__(self, prefDir):

        BasePrefFile.__init__(self, 
                              ID = 'iggypipe', 
                              filePath = path.join(prefDir, 'iggypipe_settings.yaml'), 
                              iggytool = 'iggypipe')

        self.vars = [ PrefVar( name = 'IGGYPIPE_DIR',
                               default = path.join(getUserHome(), 'iggypipe'),
                               comment = 'Directory for analysis results and logs',
                               varType = str ),

                      PrefVar( name = 'LOGGING_LEVEL',
                               default = 'info',
                               choices = ['info', 'debug'],
                               comment = 'Logging level',
                               varType = str ),

                      PrefVar( name = 'DB_TYPE',
                               default = 'sqlite',
                               choices = ['sqlite', 'mysql'],
                               comment = 'Database type',
                               varType = str ),
                      
                      PrefVar( name = 'MYSQL_HOST',
                               default = 'localhost',
                               comment = 'If DB_TYPE is sqlite, mysql settings can be ignored',
                               varType = str ),

                      PrefVar( name = 'MYSQL_DB',
                               default = 'iggypipe_db',
                               varType = str ),

                      PrefVar( name = 'MYSQL_USER',
                               default = 'iggypipe',
                               varType = str ),

                      PrefVar( name = 'MYSQL_PASS',
                               default = 'iggypipe',
                               varType = str ),

                      PrefVar( name = 'DEBUG',
                               default = False,
                               comment = 'Debug mode',
                               varType = bool ) ]


    
    def load(self):

        BasePrefFile.load(self)

        # Set some additional variables
        varNames = [x.name for x in self.vars]

        iggypipe_index = varNames.index('IGGYPIPE_DIR')
        iggypipe_dir = self.vars[iggypipe_index].value

        self.vars.append( PrefVar( name = 'LOG_DIR',
                                   value = path.join(iggypipe_dir, 'log') ) )

        self.vars.append( PrefVar( name = 'RESULTS_DIR',
                                   value = path.join(iggypipe_dir, 'analysis') ) )

