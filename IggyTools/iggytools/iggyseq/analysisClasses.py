import os.path as path
from iggytools.iggyseq.seqprep import countUndetInd
from iggytools.iggyseq.seqUtil import parseRunInfo, fastqGz_checksums
from iggytools.utils.util import flatten, mkdir_p, gzNotEmpty
import os, re, glob, traceback
from lxml import etree, html
from abc import ABCMeta, abstractmethod

try:
    from collections import OrderedDict
except ImportError:
    from ordereddict import OrderedDict # for python 2.6 and earlier, use backport 

import locale  #for printing of commas in numbers using format()
ignored = locale.setlocale(locale.LC_ALL, '') # empty string for platform's default setting

highCountThreshold = 1000000  #count above which an undetermined index is reported in demultiplex summary email

class IlluminaNextGenAnalysis:

    __metaclass__ = ABCMeta


    @classmethod
    def getInstance(cls, analysisName, run):

        if run.runType == 'HiSeq':
            return HiSeqAnalysis(analysisName, run)
        elif run.runType == 'NextSeq':
            return NextSeqAnalysis(analysisName, run)
        else:
            raise Exception('Unrecognized run type: %s' % run.runType)


    def __init__(self, analysisName, run):
        self.name = analysisName
        self.Run = run

        self.index1Length = None
        self.index2Length = None

        self.subIDs = list()
        self.sampleIDs = list()

        self.ssSampleLines = list()
        self.ssLineIndices = list()

        self.processingDir = None
        self.finishingDir = None
        self.finalDir = None

        self.ssFile = None

        self.highCountUndetInd_Summary = list() # Summary of high-count undetermined indices.

        if self.Run.processingDir:
            self.processingDir = path.join(self.Run.processingDir, self.name)

        if self.Run.finishingDir:
            self.finishingDir = path.join(self.Run.finishingDir, self.name)

        if self.Run.finalDir:
            self.finalDir = path.join(self.Run.finalDir, self.name)

        self.warnings = list()


    @abstractmethod
    def writeSamplesheet(self, outDir = None):
        pass


    @abstractmethod
    def bcl2fastq(self):
        pass


    @abstractmethod
    def gather_analysis_fastq(self):
        pass


    @abstractmethod
    def copy_reports_to_finishing(self):
        pass


    @abstractmethod
    def summarizeDemuxResults(self):
        pass


    def makeBasesMask(self, index1Length, index2Length):  
        index1Length = int(index1Length)
        index2Length = int(index2Length)
       
        print "Index lengths %d %d"%(index1Length,index2Length) 

        runinfo_index_numcycles = list()

        print "Parsing run info file %s"%self.Run.runinfoFile
        r, ignored = parseRunInfo(self.Run.runinfoFile) #example: {'Read1': {'num_cycles': 76, 'is_index': 'N'}, 'Read2': {'num_cycles': 7, 'is_index': 'Y'}}  

        print r.keys()
        basesMask = 'Y' + str( int(r['Read1']['num_cycles']) - 1 ) + 'N'  #Read1 is never an index

        if 'Read2' in r.keys():

            if r['Read2']['is_index'] == 'Y': #then Read2 is an index

                read2_numcycles = int(r['Read2']['num_cycles'])

                if index1Length > 0:
                    basesMask += ',I' + str(index1Length) + 'N' * (read2_numcycles - index1Length)
                else:
                    basesMask += ',' + 'N' * read2_numcycles

                print "Appending %d"%read2_numcycles
                runinfo_index_numcycles.append(read2_numcycles)

            else: #then Read2 is not an index
                basesMask += ',Y' + str( int(r['Read2']['num_cycles']) - 1 ) + 'N'

            if 'Read3' in r.keys():

                if r['Read3']['is_index'] == 'Y': #then Read3 is an index
                    read3_numcycles = int(r['Read3']['num_cycles'])

                    if index2Length > 0:
                        basesMask += ',I' + str(index2Length) + 'N' * (read3_numcycles - index2Length)

                    else:
                        basesMask += ',' + 'N' * read3_numcycles

                    runinfo_index_numcycles.append(read3_numcycles)

                else: #then Read3 is not an index
                    basesMask += ',Y' + str( int(r['Read3']['num_cycles']) - 1 ) + 'N'

                if 'Read4' in r.keys(): #Read4 is never an index
                    basesMask += ',Y' + str( int(r['Read4']['num_cycles']) - 1 ) + 'N'

        # Check if index lengths in samplesheet and runinfo file agree

        print "Index 1 length %d"%index1Length

        for i in runinfo_index_numcycles:
            print ("%d %s"%(i,runinfo_index_numcycles[0]))

        print "Done"
        #if (index1Length > 0 or len(runinfo_index_numcycles) > 0) \
        #        and index1Length not in [ runinfo_index_numcycles[0], runinfo_index_numcycles[0] - 1 ]:

        #    self.warnings.append('In analysis %s: Unusual combination of samplesheet index length and runinfo num cycles for 1st index. Index length: %s. RunInfo num cycles: %s' 
        #                    % (self.name, index1Length, runinfo_index_numcycles[0]))

        if (index2Length > 0 or len(runinfo_index_numcycles) > 1) \
                and index2Length not in [ runinfo_index_numcycles[1], runinfo_index_numcycles[1] - 1 ]:

            self.warnings.append('In analysis %s: Unusual combination of samplesheet index length and runinfo num cycles for 2nd index. Index length: %s. RunInfo num cycles: %s' 
                            % (self.name, index2Length, runinfo_index_numcycles[1]))

        return basesMask


    def calcCheckSums(self):
        self.Run.log('Calculating checksums...')

        fastqGz_checksums( path.join(self.finishingDir, 'Fastq') )


    def countUndetIndices(self):
        undetFastq = glob.glob(path.join(self.finishingDir, 'Fastq', '*Undetermined*.R1.fastq.gz'))  #index counts should be the same whether tallied from R1 or R2

        if undetFastq:
            undetFastq = undetFastq[0]

            if path.isfile(undetFastq):
                self.Run.log('Tallying undetermined indices...')
                self.highCountUndetInd_Summary = countUndetInd.count(undetFastq, path.join(self.finishingDir, 'QC'), highCountThreshold)
            else:
                self.Run.log('No undetermined indices found to count.')


    def fastQC(self):

        self.Run.log('Running FastQC...')

        outDir = path.join(self.finishingDir, 'QC')
        mkdir_p(outDir)

        fastqDir = path.join(self.finishingDir, 'Fastq')

        for filename in os.listdir(fastqDir):
            if re.match('\S+.fastq.gz', filename) and gzNotEmpty( path.join(fastqDir, filename) ):
                command = 'source new-modules.sh; module load legacy/0.0.1-fasrc01; module load centos6/fastqc-0.10.1 \n' + \
                          'fastqc -t 4 --noextract --nogroup -o ' + outDir + ' ' + path.join(fastqDir,filename)

                self.Run.shell(command, self.Run.logFile)


    def validateFinalDir(self):

        self.Run.log('Checking for required files in finalDir ' + self.finalDir + ' ...')

        warnings = list()

        for item in flatten([self.finalDir_requiredItems, path.basename(self.ssFile)]):
            itemPath = path.join(self.finalDir, item)
            if not path.isfile(itemPath) and not path.isdir(itemPath):
                warnings.append('Item missing from analysis finalDir: ' + itemPath)

        if len(glob.glob(path.join(self.finalDir, 'Fastq', '*.fastq.gz'))) == 0:
                warnings.append('No fastq.gz files found in analysis finalDir ' + self.finalDir)

        return warnings


    def formatTable(self, rows):
        lines = list()
        cols = zip(*rows)
        colWidths = [ max(len(elem) for elem in col) for col in cols ]
        rowFormat = '     ' + '   |   '.join(['%%%ds' % width for width in colWidths ])
        for row in rows:
            lines.append(rowFormat % tuple(row))
        lines.append('\n')
        return lines



class HiSeqAnalysis(IlluminaNextGenAnalysis):

    def __init__(self, analysisName, Run = None):

        IlluminaNextGenAnalysis.__init__(self, analysisName, Run)
        self.finalDir_requiredItems = ['Fastq', 'QC', 'Basecall_Stats']


    def writeSamplesheet(self, outDir = None):

        if not outDir:
            outDir = self.Run.processingDir  #bcl2fastq for HiSeq 2000 requires that analysis processing dir (self.processingDir) not yet exist. Therefore write to Run.processingDir

        if not path.isdir(outDir):
            mkdir_p(outDir)

        self.ssFile = path.join(outDir, 'SampleSheet.' + self.name + '.csv')

        with open(self.ssFile, 'w') as fh:
            fh.write(self.Run.SampleSheet.ss[0] + '\n')  #write out header line 
            fh.write('\n'.join( [self.Run.SampleSheet.ss[x] for x in self.ssLineIndices] ))  #write out lines corresponding to this analysis


    def bcl2fastq(self):  #run bcl2fastq v1.8.3 analysis 

        self.Run.log('Running bcl2fastq...')

        command = 'source new-modules.sh; module load legacy/0.0.1-fasrc01; module load centos6/bcl2fastq-1.8.3 \n' + \
                  'echo "Using configureBclToFastq.pl:"; which configureBclToFastq.pl\n\n'

        outDir = path.join(self.Run.processingDir, self.name)
        inDir = path.join(self.Run.primaryDir, 'Data', 'Intensities', 'BaseCalls')

        if self.Run.customBasesMask:
            basesMask = self.Run.customBasesMask
        else:
            basesMask = self.makeBasesMask(self.index1Length, self.index2Length)

        command += 'configureBclToFastq.pl --input-dir ' + inDir                         + ' \\\n' \
                                       + ' --output-dir ' + outDir                       + ' \\\n' \
                                       + ' --sample-sheet ' + self.ssFile                + ' \\\n' \
                                       + ' --use-bases-mask ' + basesMask                + ' \\\n' \
                                       + ' --mismatches ' + str(self.Run.numMismatches)  + ' \\\n' \
                                       + ' --ignore-missing-stats'                       + ' \\\n'

        if self.Run.ignoreMissingBcl:
            command += ' --ignore-missing-bcl \\\n'

        if self.Run.ignoreMissingControl:
            command += ' --ignore-missing-control \\\n'

        if self.Run.withFailedReads:
            command += ' --with-failed-reads \\\n'

        if self.Run.tileRegex:
            command += " --tiles '" + self.Run.tileRegex + "' \\\n"

        command += '\n'  #end line continuation

        command += 'cd ' + outDir + '; make -j ' + str(self.Run.numThreads) + '\n'

        self.Run.shell(command, self.Run.logFile)


    def gather_analysis_fastq(self):

        self.Run.log('Concatenating fastq files...')

        #Example file set to concatenate:
        #  SampleA_ACAGTG_L001_R1_001.fastq.gz
        #  SampleA_ACAGTG_L001_R1_002.fastq.gz 
        #  SampleA_ACAGTG_L001_R1_003.fastq.gz 

        projectDir = path.join(self.processingDir, 'Project_Fastq_Files')
        sampDirs = glob.glob( path.join(projectDir, 'Sample_*') )
        undetDir = path.join(self.processingDir, 'Undetermined_indices')
        undetSampDirs = glob.glob( path.join(undetDir, 'Sample_*') )

        outDir = path.join(self.finishingDir, 'Fastq')
        mkdir_p(outDir)

        for sampDir in sampDirs + undetSampDirs:

            for filename in os.listdir(sampDir):

                for readNumStr in ['1', '2']:

                    labelMatch = re.match('(?P<fileLabel>(?P<sampLabel>[\S]+)_L[0-9]+_R'+readNumStr+')_001.fastq.gz', filename)

                    if labelMatch:
                        sampLabel = labelMatch.group('sampLabel')
                        fileLabel = labelMatch.group('fileLabel')

                        mergeFile = path.join(outDir, sampLabel + '.R' + readNumStr + '.fastq.gz')
                        componentFiles = sorted([path.join(projectDir, sampDir, f) for f in os.listdir(sampDir) if re.match(fileLabel + '_[0-9]+.fastq.gz', f)])

                        self.Run.log('Concatenating ' + sampLabel + ' R'+readNumStr+' fastq component files:')
                        self.Run.log('\n'.join(['  %s' % path.basename(x) for x in componentFiles]))

                        fout = file(mergeFile, 'wb')

                        for componentFile in componentFiles:
                            fin  = file(componentFile,'rb')
                            while True:
                                data = fin.read(65536)
                                if not data: break
                                fout.write(data)
                            fin.close()

                        fout.close()


    def copy_reports_to_finishing(self):

        self.Run.log('Copying stats files to finishing dir...')

        #find basecall_stats directory to copy 
        items = glob.glob(path.join(self.processingDir, 'Basecall_Stats_*'))

        if items:
            basecallStatsDir = items[0]
            for item in ['Demultiplex_Stats.htm', 'Plots', 'css', 'All.htm', 'IVC.htm']:
                itemPath = path.join(self.processingDir, basecallStatsDir, item)

                if path.isfile(itemPath) or path.isdir(itemPath):
                    newItem = path.join(self.finishingDir, 'Basecall_Stats', item)
                    self.Run.safeCopy( itemPath, newItem )

        #copy analysis samplesheet to analysis finishingDir
        self.Run.safeCopy( self.ssFile, path.join(self.finishingDir, path.basename(self.ssFile)) )
    
        # copy InterOp directory from /n/illumina/primary_data to analysis_finished
        #inter_op_dir=path.join(self.Run.primaryDir,'InterOp')
        #self.Run.safeCopy( inter_op_dir, path.join(self.finishingDir,'InterOp'))        

    def summarizeDemuxResults(self): #hiseq analysis summary

        summary = list()

        ## Get stats from html report
        statsFile = path.join(self.finalDir, 'Basecall_Stats', 'Demultiplex_Stats.htm')

        if not path.isfile(statsFile):
            summary.append('    No Demultiplex_Stats.htm found in finalDir! Checking finishingDir...\n')
            statsFile = path.join(self.finishingDir, 'Basecall_Stats', 'Demultiplex_Stats.htm')

            if not path.isfile(statsFile):
                summary.append('    No Demultiplex_Stats.htm found in finishingDir.\n')

        with open(statsFile,'r') as fh:
            stats = fh.read()

        stats = re.sub(r'% of &gt;= Q30 Bases \(PF\)','% bases Q ge 30',stats)

        srows = list()
        tree = html.fromstring(stats)
        totalReads = 0
        nsamps = 0
        for tables in tree.xpath('//table')[0:2]:
            for row in tables.xpath('./tr'):
                cols = row.xpath('./th | ./td')

                samp = cols[1].text
                index = cols[3].text
                reads = cols[9].text
                perc = cols[13].text

                srows.append([samp, index, reads, perc])

                if re.sub(',','',reads).isdigit():
                    totalReads += int(re.sub(',','',reads))
                    nsamps += 1

        scols = zip(*srows)
        colWidths = [ max( [len(elem) if elem else 0 for elem in col] ) for col in scols ]
        rowFormat = '     ' + '   |   '.join(['%%%ds' % width for width in colWidths ])

        ## Append analysis read count and num samps
        if self.Run.SampleSheet.nonIndexRead2_numCycles > 0:
            note = 'R1+R2'
        else:
            note = 'R1 only'

        summary.append( 'Reads (%s):  %s\n' % (note, format(totalReads, 'n')) )
        summary.append( 'Number of samples:  %s\n' % str(int(nsamps) - 1) )  #subtract 1 to exclude the undetermined sample

        for row in srows:
            summary.append(rowFormat % tuple(row))

        ## Append list of over-represented undetermined indices
        if self.highCountUndetInd_Summary:
            summary += ['\nHigh-count undetermined indices (count > %s):\n' % highCountThreshold] + self.highCountUndetInd_Summary 
            summary += ['']  #add line break

        return summary



class NextSeqAnalysis(IlluminaNextGenAnalysis):

    def __init__(self, analysisName, Run = None):

        IlluminaNextGenAnalysis.__init__(self, analysisName, Run)
        self.finalDir_requiredItems = ['Fastq', 'QC', 'Reports', 'Stats']


    def writeSamplesheet(self, outDir = None):

        if not outDir:
            outDir = self.processingDir

        if not path.isdir(outDir):
            mkdir_p(outDir)

        self.ssFile = path.join(outDir, 'SampleSheet.' + self.name + '.csv')

        with open(self.ssFile, 'w') as fh:
            fh.write('\n'.join( self.Run.SampleSheet.ss[:self.Run.SampleSheet.colNamesLineIndex+1] ))  #write out header portion of samplesheet
            fh.write('\n'.join( [self.Run.SampleSheet.ss[x] for x in self.ssLineIndices] ))  #write out lines corresponding to this analysis


    def bcl2fastq(self):

        print "In nextseq bcl2fastq "
        command = 'source new-modules.sh; module load legacy/0.0.1-fasrc01; module load bcl2fastq2; echo "Using bcl2fastq: "; which bcl2fastq; '

        if self.Run.customBasesMask:
            basesMask = self.Run.customBasesMask
        else:
            print "Making basesmasek for %d %d"%(self.index1Length,self.index2Length)
            basesMask = self.makeBasesMask(self.index1Length, self.index2Length)

        print "Made bases mask"

        command += 'bcl2fastq --runfolder-dir '      + self.Run.primaryDir \
                          + ' --barcode-mismatches ' + str(self.Run.numMismatches) \
                          + ' --output-dir '         + self.processingDir \
                          + ' --use-bases-mask '     + basesMask

        if self.Run.maskShortAdapterReads:
            command += ' --mask-short-adapter-reads ' + str(self.Run.maskShortAdapterReads)

        if self.Run.minTrimmedReadLength is not None:
            command += ' --minimum-trimmed-read-length ' + str(self.Run.minTrimmedReadLength)

        if self.Run.writeIndexFastq == True:
            command += ' --create-fastq-for-index-reads \\\n'    

        command += '; '

        self.Run.shell(command, self.Run.logFile)


    def gather_analysis_fastq(self):

        # Merge per-lane fastq.gz files into one fastq.gz file per sample. (Lanes here refer to NextSeq lanes 1-4)

        self.Run.log('Concatenating fastq files...')

        self.Run.clearDir(self.finishingDir)
        os.mkdir(path.join(self.finishingDir,'Fastq'))

        for filename in os.listdir(self.processingDir):
            for readNumStr in ['1', '2']:

                sampNameMatch = re.match('([\S]+)_L001_R'+readNumStr+'_001.fastq.gz', filename)  #example file name: 'mySample_L001_R1_001.fastq.gz'

                if sampNameMatch:
                    sampName = sampNameMatch.groups(1)[0]

                    self.Run.log('Merging ' + sampName + ' R'+readNumStr+' fastq files...')

                    mergeFile = path.join(self.finishingDir,'Fastq',sampName + '.R' + readNumStr + '.fastq.gz')
                    self.Run.safeCopy( path.join(self.processingDir, sampName + '_L001_R' + readNumStr + '_001.fastq.gz'), mergeFile )

                    fout = file(mergeFile, 'ab')
                    for laneNumStr in ['2','3','4']:
                        fin  = file(path.join(self.processingDir, sampName + '_L00' + laneNumStr + '_R' + readNumStr + '_001.fastq.gz'),'rb')
                        while True:
                            data = fin.read(65536)
                            if not data:
                                break
                            fout.write(data)
                        fin.close()
                    fout.close()


    def copy_reports_to_finishing(self):

        self.Run.log('Copying stats files to finishing dir...')

        for dirname in ['Stats', 'Reports']:
            src = path.join(self.processingDir, dirname)
            dest = path.join(self.finishingDir, dirname)

            self.Run.safeCopy(src, dest)

        #copy analysis samplesheet to analysis finishingDir
        self.Run.safeCopy( self.ssFile, path.join(self.finishingDir, path.basename(self.ssFile)) )
         
        # copy InterOp directory from illumina/primary_data to analysis finished
        #inter_op_dir=path.join(self.Run.primaryDir,'InterOp')
        #self.Run.safeCopy( inter_op_dir, path.join(self.finishingDir,'InterOp'))  

    def summarizeDemuxResults(self):  #nextseq analysis summary
        self.Run.log('Summarizing demux results...')

        summary = list()

        ## Append stats from html report to summary

        subDir = path.join('Reports', 'html', self.Run.flowcell, 'all', 'all', 'all')
        statsFile = path.join(self.finalDir, subDir, 'laneBarcode.html')

        if not path.isfile(statsFile):

            summary.append('    No laneBarecode.html found in finalDir! Checking finishingDir...\n')

            statsFile = path.join(self.finishingDir, subDir, 'laneBarcode.html')
            if not path.isfile(statsFile):

                summary.append('    No laneBarecode.html found in finishingDir either.\n')

                return summary

        with open(statsFile,'r') as fh: 
            stats = fh.read()

        tree = html.fromstring(stats)
        table = tree.xpath('//table')[2]  #get "Lane Summary" table
        rows = table.xpath('./tr')
        nsamps = (len(rows) - 2)/4.0 #nsamps is number of samples per lane, including the 'unknown' sample of unassigned reads 

        laneStats = OrderedDict()
        sampStats = OrderedDict()

        totalReads = 0  #across all 4 nextseq lanes
        
        for i in range(2,len(rows)):  #get per-lane and per-sample stats
            row = rows[i]
            cols = row.xpath('./th | ./td')

            # Table cols:
            #   Lane number
            #   Project
            #   Sample
            #   Barcode sequence
            #   Raw data:  Clusters
            #   Raw data:  Perc. of the lane
            #   Raw data:  Perc. perfect barcode
            #   Raw data:  Perc. one mismatch barcode
            #   Filtered data:  Clusters
            #   Filtered data:  Yield (Mbases)
            #   Filtered data:  Perc. PF Clusters
            #   Filtered data:  Perc. >Q30 bases
            #   Filtered data:  Mean quality score

            lane = cols[0].text
            samp = cols[2].text
            index = cols[3].text
            numReads = re.sub(',','',cols[8].text)
            perc_Q30bases = cols[11].text
            
            if not numReads:
                numReads = 0
            else:
                numReads = int(numReads)
                totalReads += numReads

            if not perc_Q30bases: 
                perc_Q30bases = 0.0
            else:
                perc_Q30bases = float(perc_Q30bases)

            if lane not in laneStats:  # start new lane tallys
                laneStats[lane] = {'numReads': 0, 'num_Q30bases': 0, 'perc_Q30bases': 0}

            laneStats[lane]['numReads'] += numReads
            laneStats[lane]['num_Q30bases'] += perc_Q30bases * numReads

            if samp not in sampStats: # start new sample tallys
                sampStats[samp] = {'index': index, 'numReads': 0, 'num_Q30bases': 0, 'perc_Q30bases': 0}

            sampStats[samp]['numReads'] += numReads
            sampStats[samp]['num_Q30bases'] += perc_Q30bases * numReads


        totalReads = 0  #find the total number of reads across all 4 next seq lanes. (A single lane to the user.)
        for lane in laneStats:
            ln = laneStats[lane]
            totalReads += ln['numReads']
            if ln['numReads'] > 0:
                ln['perc_Q30bases'] = ln['num_Q30bases']/ln['numReads']

        for samp in sampStats:
            s = sampStats[samp]
            if s['numReads'] > 0:
                s['perc_Q30bases'] = s['num_Q30bases']/s['numReads']

        laneRows = [ ['Lane', 'Reads', '% Bases >= Q30'] ] \
            + [ [ lane, format(laneStats[lane]['numReads'], 'n'), '%.2f' % laneStats[lane]['perc_Q30bases'] ] for lane in laneStats ]

        sampRows = [ ['Sample', 'Index', 'Reads', '% Bases >= Q30'] ]  \
            + [ [ samp, sampStats[samp]['index'], format(sampStats[samp]['numReads'], 'n'), '%.2f' % sampStats[samp]['perc_Q30bases'] ] for samp in sampStats ]
        
        ## Append analysis read count and num samps
        if self.Run.SampleSheet.nonIndexRead1_numCycles > 0:
            note = 'R1+R2'
        else:
            note = 'R1 only'

        summary.append( 'Reads (%s):  %s\n' % (note, format(totalReads, 'n')) )
        summary.append( 'Number of samples:  %s\n' % str(int(nsamps) - 1) )  #subtract 1 to exclude the undetermined sample

        ## Append detailed stats tables
        summary += self.formatTable(laneRows)
        summary += self.formatTable(sampRows)

        ## Append list of high-count undetermined indices
        if self.highCountUndetInd_Summary:
            summary += ['\nHigh-count undetermined indices (count > %s):\n' % highCountThreshold] + self.highCountUndetInd_Summary
            summary += ['']  #add line break

        return summary

