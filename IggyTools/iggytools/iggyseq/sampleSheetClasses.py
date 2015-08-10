from abc import ABCMeta, abstractmethod
from os import path
import re
from laneClass import Lane
from analysisClasses import IlluminaNextGenAnalysis
from iggytools.utils.util import unique, flatten, mkdir_p, copy, deleteItem
from iggytools.iggyseq.seqUtil import setPermissions

try:
    from collections import OrderedDict
except ImportError:
    from ordereddict import OrderedDict # for python 2.6 and earlier, use backport                                                                                                   

def get_analysisName(userLaneLabel, indexType):
    return 'Lane%s.indexlength_%s' % (userLaneLabel, indexType)


    
class BaseSampleSheet:

    __metaclass__ = ABCMeta


    @classmethod
    def getInstance(cls, runObj):

        ssFile = runObj.samplesheetFile

        if not path.isfile(ssFile):  #attempt to find samplesheet in run's parent directory.

            altFile = path.join(runObj.primaryParent, '%s.csv' % runObj.flowcell) 

            if path.isfile(altFile):
                copy(altFile, ssFile)
                setPermissions(ssFile)
            else:
                raise Exception('No samplesheet found for run %s at %s or %s' % (runObj.runName, ssFile, altFile))
        
        with open(ssFile, 'r') as fh:
            firstline = fh.readline()

        if re.match('FCID', firstline): #matches from beg.
            return SampleSheet_formatA(runObj)
        else:
            return SampleSheet_formatB(runObj)


    def __init__(self, runObj):

        self.file                     = runObj.samplesheetFile
        self.selectedLanes            = runObj.selectedLanes

        self.Run                      = runObj

        self.nonIndexRead1_numCycles  = None  # Non-index read lengths are not provided in samplesheet format A.
        self.nonIndexRead2_numCycles  = None

        self.analyses                 = list()
        self.lanes                    = list()

        self.warnings                 = list()

        with open(self.file,'r') as fh:
            ss = fh.readlines()

        ss = [ re.sub('\s', '', x) for x in ss if x.rstrip()]  #delete blank lines and other whitespace
        ss = [ re.sub(r'[)(]', '_', x) for x in ss ]                  #replace illegal characters with underscores
        self.ss = [ re.sub(r'(?<=[^AGCTNagtcn]{2})-(?=[^AGCTNagtcn]{2})', '_', x) for x in ss]  #replace dashes with underscores unless they may be in a dual index


    @abstractmethod
    def parse(self):
        pass


    def write_validatedSamplesheet(self):
        ssBkupDir = path.join(path.dirname(self.file),'ss')
        mkdir_p(ssBkupDir)
        ssBkupBase = path.join(ssBkupDir,'SampleSheet.csv.orig')
        ssBkupFile = ssBkupBase
        k = 2
        while path.isfile(ssBkupFile):
            ssBkupFile = ssBkupBase + str(k)
            k += 1
        copy(self.file, ssBkupFile)
        setPermissions(ssBkupFile)
        deleteItem(self.file)  #cannot set permissions if someone else is owner. Therefore delete before openning to rewrite
        with open(self.file, 'w') as fh:
            fh.write('\n'.join(self.ss))
        setPermissions(self.file)


    def validate_indexChars(self, index, lineIndex):
        if not re.match('[AGCT-]*$', index):
            raise Exception('Unexpected index in samplesheet %s, line %s: %s' % (self.file, lineIndex+1, index))


    def validate_indexTypeChars(self, indexType, lineIndex):
        if not re.match('[0-9]+([-_][0-9]+)?$', indexType):
            raise Exception('Unexpected indexType in samplesheet %s, line %s: %s' % (self.file, lineIndex+1, indexType))


    def validate_subIDChars(self, subID, lineIndex):
        if not re.match('SUB[A-Za-z0-9]+$', subID):
            raise Exception('Unexpected subID in samplesheet %s, line %s: %s' % (self.file, lineIndex+1, subID))


    def adjustIndexLength(self, index, rlen):
        rlen = int(rlen)
        if len(index) < rlen: #then lengthen index
            index += 'A' * (rlen - len(index))
        elif len(index) > rlen: #then shorten index
            index = index[:rlen]
        return index


    def makeNewAnalysis(self, analName, index1Length = 0, index2Length = 0):

        a = IlluminaNextGenAnalysis.getInstance(analName, self.Run)

        a.index1Length = index1Length
        a.index2Length = index2Length

        self.analyses.append(a)

        return a


    def makeNewLane(self, userLaneLabel):
        
        lane = Lane(self.Run)
        lane.userLaneLabel = userLaneLabel

        self.lanes.append(lane)

        return lane



class SampleSheet_formatA(BaseSampleSheet):
    
    def __init__(self, runObj):
        BaseSampleSheet.__init__(self, runObj)
        self.format = 'A'

    def parse(self):

        seenLaneIndices = list()

        # Example header line: FCID,Lane,SampleID,SampleRef,Index,Description,Control,Recipe,Operator,SampleProject
        colNames = [x.lower() for x in self.ss[0].rstrip().split(',')] 

        for i in range(1,len(self.ss)): 
            line = self.ss[i].rstrip()
            lineVals = line.split(',')

            if not any(lineVals):
                continue    #skip lines containing only commas

            vDict = OrderedDict(zip(colNames, lineVals))  #dict keys are column names

            laneName = vDict['lane']
            if self.selectedLanes and laneName not in self.selectedLanes:
                continue
            index = vDict['index']
            subID = vDict['description']
            indexType = vDict['recipe']            #examples: '6' for a 6-base index; '8_8' for two indices where each is 8 bases.

            vDict['sampleproject'] = 'Fastq_Files'                        #reset project field, as this will create uniform output directory stucture for all runs
            vDict['sampleid'] = re.sub(r'[- .)(@]','_',vDict['sampleid']) #replace illegal characters in sample name with underscores

            # Error checking and validation
            self.validate_indexChars(index, i)
            self.validate_indexTypeChars(indexType, i)
            self.validate_subIDChars(subID, i)

            if not re.match('[1-8]$', laneName): #matches from beg.
                raise Exception('Unexpected lane in samplesheet %s, line %s: %s' % (self.file, i+1, line))

            if laneName + index in seenLaneIndices:
                raise Exception('Duplicate index in samplesheet %s, line %s: %s' % (self.file, i+1, line))
            else:
                seenLaneIndices.append(laneName + index)

            # Extract index strings from index field
            iMatch = re.match('(?P<index1>[AGCTagct]+)(-(?P<index2>[AGCTagct]+))?$', index)

            if not iMatch or iMatch.group('index1') is None:
                self.warnings.append('No index found in samplesheet %s, line %s: %s' % (self.file, i+1, line))
                index1 = ''
                index2 = ''
            else:    
                index1 = iMatch.group('index1')
                if index1 is None:
                    index1 = ''

                index2 = iMatch.group('index2')
                if index2 is None:
                    index2 = ''

            if not indexType:  #make indexType label if it was not specified 
                indexType = str(len(index1))
                if len(index2) > 0:
                    indexType += '_' + str(len(index2))

            else:  #adjust index lengths according to specified indexType
                tMatch = re.match('(?P<rlen1>[0-9]+)((_|-)(?P<rlen2>[0-9]+))?$', indexType) # 'rlen' denotes 'real length'
                if tMatch:
                    rlen1 = tMatch.group('rlen1')
                    rlen2 = tMatch.group('rlen2')
                    if rlen2 is None:
                        rlen2 = 0
                    index1 = self.adjustIndexLength(index1, rlen1)  #shorten or lengthen indices
                    index2 = self.adjustIndexLength(index2, rlen2)
                    vDict['index'] = index1  #update index in vDict
                    if index2:
                        vDict['index'] += '-' + index2

            ##
            # Lane Obj
            ##

            if laneName not in [x.userLaneLabel for x in self.lanes]:
                lane = self.makeNewLane(laneName)  #start new lane

            #set lane index1 length to maximum of index1 real lengths
            if not lane.index1Length or rlen1 > lane.index1Length:
                lane.index1Length = rlen1

            #set lane index2 length to maximum of index2 real lengths
            if not lane.index2Length or rlen2 > lane.index2Length:
                lane.index2Length = rlen2

            lane.ssSampleLines.append(vDict)  #assign sample line to this lane
            lane.ssLineIndices.append(i)      #record lines in samplesheet that correspond to this lane                                                  

            if subID and subID not in lane.subIDs:
                lane.subIDs.append(subID)  #add subID to this lane

            ##
            # Analysis Obj
            ##

            analName = get_analysisName(lane.userLaneLabel, indexType)

            if analName not in [x.name for x in self.analyses]:
                analysis = self.makeNewAnalysis(analName, rlen1, rlen2)  #start new analysis

            analysis.ssSampleLines.append(vDict)        #assign sample to this analysis
            analysis.ssLineIndices.append(i)            #record lines in samplesheet that correspond to this analysis

            if subID and subID not in analysis.subIDs:  #assign subID to this analysis
                self.validate_subIDChars(subID, i)
                analysis.subIDs.append(subID)  #add subID to this analysis

            #make sample_id's unique w.r.t. other samples in this analysis (required by bcl2fastq)
            if vDict['sampleid'] in analysis.sampleIDs:
                k = 2
                while ('%s_%s' % (vDict['sampleid'], k) in analysis.sampleIDs):
                    k += 1
                newID = '%s_%s' % (vDict['sampleid'], k) 
                vDict['sampleid'] = newID

            analysis.sampleIDs.append(vDict['sampleid'])

            # Build validated samplesheet line
            self.ss[i] = ','.join( [vDict[x] for x in colNames] )

            # Done parsing samplesheet.

        if not self.analyses: #if there was no data in the samplesheet
            self.makeNewAnalysis(get_analysisName('1', '0'))  #set lane to 1, index length to 0.
            self.makeNewLane('1')

        self.subIDs = unique(flatten([x.subIDs for x in self.analyses]))

        self.contentString = '\n'.join(self.ss)  #samplesheet contents, concatenated into a string

        if not self.analyses:
            raise Exception('No analyses matching selected lanes found in samplesheet %s.' % self.file)
        


class SampleSheet_formatB(BaseSampleSheet):
    

    def __init__(self, runObj):
        BaseSampleSheet.__init__(self, runObj)
        self.format = 'B'


    def parse(self):

        inSampleData = False
        section = ''
        headerSubIDs = set()

        for i in range(len(self.ss)):
            line = self.ss[i]
            vals = line.split(',')

            if not any(vals):
                continue    #skip lines containing only commas

            vDict = None
            if vals[0] == '[Header]':
                section = 'Header'

            if vals[0] == '[Reads]':
                section = 'Reads'

            elif vals[0] == '[Settings]':
                section = 'Settings'

            elif vals[0] == '[Data]':
                section = 'Data'

            elif section == 'Header' and vals[0] == 'Description':
                if vals[1]:
                    for ID in re.split('[-_]', vals[1]):
                        self.validate_subIDChars(ID, i)
                        headerSubIDs.add(ID)
                else:
                    self.warnings.append("Expected subID in Header section's Description field (samplesheet %s, Line %s: %s)" % (self.file, i+1, line))

            elif section == 'Reads':
                if vals[0].isdigit():
                    if self.nonIndexRead1_numCycles is None:
                        self.nonIndexRead1_numCycles = int(vals[0])
                    else:
                        self.nonIndexRead2_numCycles = int(vals[0])

            elif section == 'Settings':
                if vals[0] == 'Adapter' or vals[0] == 'AdapterRead2':
                    if self.Run.suppressAdapterTrimming:
                        vals[1] = ''  #delete adapter sequence
                    elif not re.match('[AGCT]+$',vals[1]):  #matches from beg.
                        self.warnings.append('No adapter sequence found in samplesheet %s, Line %s: %s' % (self.file, i+1, line))

            elif section == 'Data' and inSampleData == False:
                colNames = [x.lower() for x in vals] 
                self.colNamesLineIndex = i
                analyses = OrderedDict()  #store samplesheet info by analysis
                samplesheetLanes = OrderedDict()   #store samplesheet info by lane
                inSampleData = True

                #possible headerline for hiseq:
                #        Lane,Sample_ID,Sample_Plate,Sample_Name,I7_Index_ID,index,I5_Index_ID,index2,Sample_Project,Description
                #possible headerline for nextseq:
                #        Sample_ID,Sample_Name,Sample_Plate,Sample_Well,I7_Index_ID,index,I5_Index_ID,index2,Sample_Project,Description

            elif inSampleData:

                vDict = OrderedDict(zip(colNames, vals))  #convert list of values to dict where keys are column names

                if 'lane' in colNames:
                    lane = vDict['lane']
                    if self.selectedLanes and lane not in self.selectedLanes:
                        continue
                else:
                    lane = 'NoLane'

                if 'index' in colNames:
                    index1 = vDict['index']
                    self.validate_indexChars(index1, i)
                else:
                    index1 = ''
                    self.warnings.append('No index1 found in samplesheet %s, Line %s: %s' % (self.file, i+1, line))                        

                if 'index2' in colNames:
                    index2 = vDict['index2']
                    self.validate_indexChars(index2, i)
                else:
                    index2 = ''

                if lane == 'NoLane':
                    userLaneLabel = '1'
                else:
                    userLaneLabel = lane

                if userLaneLabel not in self.lanes:
                    lane = self.makeNewLane(userLaneLabel) #start new Lane

                rlen1 = len(index1)  #initialize "real" index lengths to index lengths before adjustment
                rlen2 = len(index2)

                #get real index lengths and submission IDs from description column, if present
                lineSubID = ''
                if 'description' in colNames and vDict['description']: 
                    elems = re.split('_|-', vDict['description'])

                    for j in range(len(elems)):
                        if re.match('SUB', elems[j], re.IGNORECASE):
                            subID = elems[j]
                            elems.remove(subID)
                            lineSubID = subID.upper()

                    if len(elems) > 2:
                        self.warnings.append('Too many values in description field in samplesheet %s, Line %s: %s' % (self.file, i+1, line))
                    elif len(elems) > 0 and elems[0].isdigit():
                        rlen1 = elems[0]

                        if len(elems) == 2 and elems[1].isdigit():
                            rlen2 = elems[1]
                        
                        #shorten or lengthen indices according to rlen1 and rlen2
                        if rlen1 != len(index1):
                            index1 = self.adjustIndexLength(index1, rlen1)  
                        if rlen2 != len(index2):
                            index2 = self.adjustIndexLength(index2, rlen2)  

                #set lane index1 length to maximum of index1 real lengths
                if not lane.index1Length or rlen1 > lane.index1Length:
                    lane.index1Length = rlen1

                #set lane index2 length to maximum of index2 real lengths
                if not lane.index2Length or rlen2 > lane.index2Length:
                    lane.index2Length = rlen2

                indexType = str(rlen1)  #make index type label
                if rlen2 > 0:
                    indexType += '_' + str(rlen2)
                self.indexType = indexType

                if lane == 'NoLane':
                    analName = 'indexlength_' + indexType  
                else:
                    analName = get_analysisName(lane.userLaneLabel, indexType)

                if analName not in [x.name for x in self.analyses]: 
                    analysis = self.makeNewAnalysis(analName, rlen1, rlen2) #start new analysis

                #ensure both sample_id and sample_name are set
                if len(vDict['sample_id']) == 0 and len(vDict['sample_name']) > 0:  
                    vDict['sample_id'] == vDict['sample_name']

                elif len(vDict['sample_name']) == 0 and len(vDict['sample_id']) > 0:  
                    vDict['sample_name'] == vDict['sample_id']

                elif len(vDict['sample_name']) == 0 and len(vDict['sample_id']) == 0:
                    self.warnings.append('No Sample_Name or Sample_ID found in samplesheet %s, Line %s: %s' % (self.file, i+1, line))
                    vDict['sample_name'] = 'Sample_' + str(len(analyses[analName].samples))
                    vDict['sample_id'] = vDict['sample_name']

                #make sample_id unique w.r.t. other samples in this analysis (required by bcl2fastq)
                if vDict['sample_id'] in analysis.sampleIDs:
                    k = 2
                    while ('%s_%s' % (vDict['sample_id'], k) in analysis.sampleIDs):
                        k += 1
                    newID = '%s_%s' % (vDict['sample_id'], k) 
                    vDict['sample_id'] = newID

                analysis.sampleIDs.append(vDict['sample_id'])

                vDict['index1'] = index1     # put updated indices in vDict
                vDict['index2'] = index2

                vDict['sample_project'] = '' # suppress Sample_Project field  (changes output directory structure)

                lane.ssSampleLines.append(vDict)   #assign sample line to this lane
                lane.ssLineIndices.append(i)       #record lines in samplesheet that correspond to this lane

                analysis.ssSampleLines.append(vDict)            #assign sample to this analysis
                analysis.ssLineIndices.append(i)                #record lines in samplesheet that correspond to this analysis

                #assign this line's subID to lane and analysis
                if lineSubID:
                    if lineSubID not in lane.subIDs:
                        lane.subIDs.append(lineSubID)

                    if lineSubID not in analysis.subIDs:
                        analysis.subIDs.append(lineSubID)

                else:
                    #use header's subID(s) if no others were provided on this line
                    lane.subIDs = unique(flatten([lane.subIDs,headerSubIDs]))  
                    analysis.subIDs = unique(flatten([lane.subIDs,headerSubIDs]))  

            # Build validated samplesheet line
            if vDict:
                self.ss[i] = ','.join( [vDict[x] for x in colNames] )
            else:
                self.ss[i] = ','.join( vals )

            # Done parsing samplesheet.

        if not self.analyses: #if there were no lines in the SampleData section of the samplesheet

            analysis = self.makeNewAnalysis('All_Reads')
            analysis.subIDs = headerSubIDs

            lane = self.makeNewLane('1')
            lane.subIDs = headerSubIDs

        self.subIDs = unique(flatten(x.subIDs for x in self.analyses))

        if self.nonIndexRead1_numCycles is None:  
            raise Exception('Non-index read 1 has length zero in samplesheet %s' % (self.file))
        if self.nonIndexRead2_numCycles is None:  
            self.nonIndexRead2_numCycles = 0

        self.contentString = '\n'.join(self.ss)  #samplesheet contents, concatenated into a string


