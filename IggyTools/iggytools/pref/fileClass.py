import os.path as path
import re, traceback, yaml, logging
from iggytools.utils.util import mkdir_p, dict2namedtuple


def var2yaml(x):
    if type(x) == list:
        return re.sub("'", "", str(x)) #

    if type(x) == str and re.search(r'[- :]',x):
        x = "'" + x + "'"  #put times in quotes, otherwise yaml will interpret them and convert to minutes.

    return str(x)
   

class BasePrefFile(object):


    def __init__(self, ID, filePath, iggytool):
        self.id = ID
        self.filePath = filePath

        self.iggytool = iggytool  #iggyref, iggypipe, etc


    #get pref file settings
    def getVars(self):  
        
        self.fileSetup()  #ensure pref file exists

        self.load()  #read and process preferences

        return dict2namedtuple( dict( [(v.name, v.value) for v in self.vars] ) )


    def fileSetup(self, verbose = False):  # Create pref file if not present                                                                          

        if not path.isfile(self.filePath):

            if verbose:
                print '\nNo %s preferences file found in %s' % (self.toolName, self.iggytools_prefDir)
                print '  Writing new preferences file: %s' % self.filePath

            self.writeFile()

        else:
            if verbose:
                print '\nFound existing %s preferences file: %s' % (self.toolName, self.filePath)


    def load(self):  #Read in pref file

        self.readYaml()

        if not self.prefYaml:
            raise Exception('Unable to read yaml file: %s ' % self.filePath)

        for v in self.vars:  #error checking

            if v.name not in self.prefYaml:
                raise Exception("Can't find %s in preferences file %s" % (v.name, self.filePath))

            inputValue = self.prefYaml[v.name]

            try:
                if v.varType == list and type(inputValue) != list: #cast to list without splitting strings
                    inputValue = [inputValue]
                elif type(inputValue) == str and re.match('None', inputValue, re.IGNORECASE):  #convert 'None' strings to None
                    inputValue = None
                else:
                    v.value = v.varType(inputValue) #cast
            except:
                raise Exception('Expected type %s for %s in preferences file %s:\n%s' %  (v.varType, v.name, self.filePath, traceback.format_exc()))

            
            if v.choices is not None:
                if v.varType == list:
                    if type(v.value) != list:
                        raise Exception('Expected list for %s in preferences file %s:\n%s' %  ( v.name, self.filePath, traceback.format_exc()))                        
                    for item in v.value:
                        if item not in v.choices:
                            raise Exception('Unexpected item %s in %s in preferences file %s:\n%s' %  (item, v.name, self.filePath, traceback.format_exc()))
                else:
                    if v.value not in v.choices:
                        raise Exception('In preferences file %s, %s value is not in permitted options: %s' % (self.filePath, v.name, ', '.join(v.choices)))
        
        # Transform some preferences variables
                
        varNames = [x.name for x in self.vars]

        #logging_level: convert strings 'info', 'debug' to logging levels
        try:
            ind = varNames.index('LOGGING_LEVEL')
        except ValueError:
            pass
        else:
            logVar = self.vars[ind]
            val = logVar.value

            if re.match('info', val, re.IGNORECASE):
                logVar.value = logging.INFO
            elif re.match('debug', val, re.IGNORECASE):
                logVar.value = logging.DEBUG
            else:
                raise Exception('Unexpected LOGGING_LEVEL in preferences file %s: %s' % (self.filePath, logVar.value)) 

            
    def writeFile(self):  

        mkdir_p( path.dirname(self.filePath) )

        with open(self.filePath, 'w') as f:

            f.write('\n###\n## %s preferences\n###\n\n' % self.id)  #page title
            
            for v in self.vars:

                if v.comment:
                    f.write('# %s.\n' % v.comment)   # write comment

                if v.choices:  #write var choices, if any
                    f.write('# Choices: %s\n' % var2yaml(v.choices))

                f.write( '%s: %s\n\n' % (v.name, var2yaml(v.default)) )  #var name and value
                            

    def readYaml(self):

        try:
            with open(self.filePath, 'r') as fh:
                self.prefYaml = yaml.load(fh)

        except:
            raise Exception('Error occured while reading preferences file %s:\n%s' % (self.prefFile, traceback.format_exc()))

