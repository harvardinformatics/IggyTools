import os.path as path
import re, glob, logging, traceback
from iggytools.utils.util import reverseComp

class dbsnp2vcf(object):
    # Note: This format conversion function is not complete. For all variant types except forward/reverse strand SNPs, the base preceeding 
    # the event should be included in the VCF's ref/alt sequences. However, this base is not included in the UCSC dbsnp file, so it needs to be
    # retrieved from the genome and included in the VCF file.
    def __init__(self, sourceID):
        self.log = logging.getLogger("iggyref_" + sourceID)

        #VCF var definitions: allowed number of vals, type, description
        vcfVars = dict()
        vcfVars['SC']  = [0, 'Flag', 'Sample type is cDNA (from exemplar submitted SNPs)'] 
        vcfVars['SG']  = [0, 'Flag', 'Sample type is genomic (from exemplar submitted SNPs)']
        vcfVars['SM']  = [0, 'Flag', 'Sample type is mito (from exemplar submitted SNPs)']
        vcfVars['VC']  = [1, 'String', 'Variation class: SNP, INDEL, HET, MIC (microsatellite), NAM (named), MNP (multiple nucleotide polymorphism), ']
        vcfVars['VS']  = ['.', 'String', 'Validation status: CL (by-cluster), FR (by-frequency), SB (by-submitter), ' \
                                   + 'INS, DEL, 2H (by-2hit-2allele), HM (by-hapmap), 1G (by-1000genomes)']
        vcfVars['HT']  = [1, 'Float', 'Average heterozygosity from all observations. Note: may be computed on small number of samples.']
        vcfVars['HTE'] = [1, 'Float', 'Standard Error for the average heterozygosity']
        vcfVars['FC']  = ['.', 'String', 'Functional category: unknown, coding-synon, intron, near-gene-3, near-gene-5, ncRNA, ' \
                              + 'nonsense, missense, stop-loss, frameshift, cds-indel, untranslated-3, untranslated-5, splice-3, splice-5']
        vcfVars['LT']  = [1, 'String', 'Type of mapping inferred from size on reference (may not agree with class): range, ' \
                               + 'exact, between, rangeInsertion, rangeSubstitution, rangeDeletion, fuzzy']
        vcfVars['WGT'] = [1, 'Integer', 'The quality of the alignment: 1 - unique mapping, 2 - non-unique, 3 - many matches']
        vcfVars['EC']  = ['.', 'String', 'Unusual conditions noted by UCSC that may indicate a problem with the data: ' \
                               + 'RefAlleleMismatch, RefAlleleRevComp, DuplicateObserved, MixedObserved, FlankMismatchGenomeLonger, ' \
                               + 'FlankMismatchGenomeEqual, FlankMismatchGenomeShorter, NamedDeletionZeroSpan, NamedInsertionNonzeroSpan, ' \
                               + 'SingleClassLongerSpan, SingleClassZeroSpan, SingleClassTriAllelic, SingleClassQuadAllelic, ' \
                               + 'ObservedWrongFormat, ObservedTooLong, ObservedContainsIupac, ObservedMismatch, MultipleAlignments, ' \
                               + 'NonIntegerChromCount, AlleleFreqSumNot1, SingleAlleleFreq, InconsistentAlleles']
        vcfVars['SBC'] = [1, 'Integer', 'Number of distinct submitter handles for submitted SNPs for this ref SNP']
        vcfVars['SBH'] = ['.', 'String', 'List of submitter handles']
        vcfVars['FAC'] = [1, 'Integer', 'Number of observed alleles with frequency data']
        vcfVars['FAN'] = ['.', 'String', 'Observed alleles for which frequency data are available']        
        vcfVars['FAC'] = ['.', 'Float', 'Count of chromosomes (2N) on which each allele was observed. Note: this is extrapolated by dbSNP ' \
                              + 'from submitted frequencies and total sample 2N, and is not always an integer.']
        vcfVars['AF']  = ['.', 'Float', 'Allele frequencies']
        vcfVars['CA']  = [0, 'Flag', 'clinically-associated']
        vcfVars['MSP'] = [0, 'Flag', 'maf-5-some-pop']
        vcfVars['MAP'] = [0, 'Flag', 'maf-5-all-pops']
        vcfVars['OM']  = [0, 'Flag', 'Has OMIM/OMIA']
        vcfVars['MT']  = [0, 'Flag', 'microattr-tpa']
        vcfVars['SL']  = [0, 'Flag', 'Submitted by LSDB']
        vcfVars['GC']  = [0, 'Flag', 'Genotype conflict']
        vcfVars['RN']  = [0, 'Flag', 'RS cluster non-overlapping alleles']
        vcfVars['OBM'] = [0, 'Flag', 'Observed mismatch']
        vcfVars['RV']  = [0, 'Flag', 'RS orientation is reversed']
        vcfVars['NCBI'] = [1, 'String', 'NCBI reference sequence']
        self.vcfVars = vcfVars

        #format VCF var definitions
        header = '##fileformat=VCFv4.1\n'
        for v in sorted(self.vcfVars.keys()):
            header += '##INFO=<ID=%s,Number=%s,Type=%s,Description="%s">\n' % (v, self.vcfVars[v][0], self.vcfVars[v][1], self.vcfVars[v][2])
        header += '#CHROM\tPOS\tID\tREF\tALT\tQUAL\tFILTER\tINFO\n'
        self.header = header
        self.headerLineCount = len(re.findall('\n', self.header))

    def convert(self, inFile, outDir = None):
        self.log.info('Converting %s to VCF format' % inFile)
        inFileStem = path.splitext(inFile)[0]
        if outDir:
            outFile = path.join(outDir, inFileStem + ".vcf")
        else:
            outFile = path.join( path.dirname(inFile), inFileStem + ".vcf" )

        #infoFields are the fields in the dbSNP schema that are represented in the INFO column in the VCF file
        infoFields = ['strand', 'refNCBI', 'sampleType', 'class', 'valStatus', 'avgHet', 'avgHetSE', 'funcCat', 'locType', 'weight', 
                      'exceptions', 'submitterCount', 'submitters', 'FAcount', 'FAnames', 'FAchromCounts', 'alleleFreqs', 'attributes']

        fin = open(inFile, 'r')
        fout = open(outFile, 'w')
        linenum = 0
        g = dict()
        for line in fin:
            linenum += 1
            vals = [x.rstrip(',') for x in line.rstrip().split('\t')]

            g['chromName'] = vals[1]
            g['start'] = int(vals[2]) + 1  #add 1 to start to convert from UCSC indexing
            g['dbsnpID'] = vals[4]
            g['strand'] = vals[6]
            g['refNCBI'] = vals[7]
            g['refUCSC'] = vals[8]
            g['observedAlleles'] = vals[9]
            g['sampleType'] = vals[10] 
            g['class'] = vals[11]      
            g['valStatus'] = vals[12]  
            g['avgHet'] = vals[13]
            g['avgHetSE'] = vals[14]
            g['funcCat'] = vals[15]  
            g['locType'] = vals[16]  
            g['weight'] = vals[17]  
            g['exceptions'] = vals[18]
            if len(vals) >= 20:
               g['submitterCount'] = vals[19]
            if len(vals) >= 21:
                g['submitters'] = vals[20]
            if len(vals) >= 22:
                g['FAcount'] = vals[21]
            if len(vals) >= 23:
                g['FAnames'] = vals[22]
            if len(vals) >= 24:
                g['FAchromCounts'] = vals[23]
            if len(vals) >= 25:
                g['alleleFreqs'] = vals[24]
            if len(vals) >= 26:
                g['attributes'] = vals[25] 

            if linenum == 1:  #write VCF header
                fout.write(self.header)
                linenum += self.headerLineCount

            outFields = list()  #build VCF INFO column
            for field in infoFields: 
                if field in g.keys() and g[field]:
                    inputVal = g[field]
                    try:
                        formattedVal = getattr(self, 'format_' + field)(inputVal)
                    except:
                        raise Exception( ("Error in %s at line %s:\n" % (inFile, linenum)) + traceback.format_exc() )
                    if formattedVal:
                        outFields.append(formattedVal)

            if g['strand'] == '-': #if snp is on reverse strand, output reverse complement of observed alleles:
                alleles = self.revComp(g['observedAlleles'])
            else:
                alleles = g['observedAlleles']
                
            #write record to file
            fout.write('\t'.join( [g['chromName'], g['start'], g['dbsnpID'], g['refUCSC'], alleles, ';'.join(outFields)] ) + '\n')  
            g.clear()
            
        fin.close()
        fout.close()
        return outFile

    def revComp(myStr):
        if not re.match(r'[AGCTagct/-]+',myStr):
            return myStr
        RCs = [reverseComp(x) for x in myStr.split('/')]
        return '/'.join(RCs)

    def format_alleleFreqs(self, val):
        return 'AF=%s' % val

    def format_attributes(self, val):
        vals = val.split(',')
        outList = list()
        for v in vals:
            if v == 'unknown':
                continue
            elif v == 'clinically-assoc':
                outList.append('CA')
            elif v == 'maf-5-some-pop':
                outList.append('MSP')
            elif v == 'maf-5-all-pops':
                outList.append('MAP')
            elif v == 'has-omim-omia':
                outList.append('OM')
            elif v == 'microattr-tpa':
                outList.append('MT')
            elif v == 'submitted-by-lsdb':
                outList.append('SL')
            elif v == 'genotype-conflict':
                outList.append('GC')
            elif v == 'rs-cluster-nonoverlapping-alleles':
                outList.append('RN')
            elif v == 'observed-mismatch':
                outList.append('OBM')
            else:
                raise Exception('No attribute mapping for %s' % v)
        return ';'.join(outList)

    def format_avgHet(self, val):
        return 'HT=%s' % val

    def format_avgHetSE(self, val):
        return 'HTE=%s' % val

    def format_class(self, val):
        outList = list()
        if val == 'unknown':
            return ''
        elif val == 'single':
            return 'VC=SNP'
        elif val == 'in-del':
            return 'VC=INDEL'
        elif val == 'het':
            return 'VC=HET'
        elif val == 'microsatellite':
            return 'VC=MIC'
        elif val == 'named':
            return 'VC=NAM'
        elif val == 'mnp':
            return 'VC=MNP'        
        elif val == 'insertion':
            return 'VC=INS'
        elif val == 'deletion':
            return 'VC=DEL'
        else:
            raise Exception('No format mapping for %s' % val)

    def format_exceptions(self, val):
        return 'EC=%s' % val

    def format_FAcount(self, val):
        return 'FAC=%s' % val

    def format_FAnames(self, val):
        return 'FAN=%s' % val

    def format_FAchromCounts(self, val):
        return 'FAC=%s' % val

    def format_funcCat(self, val):
        return 'FC=%s' % val

    def format_locType(self, val):
        return 'LT=%s' % val

    def format_refNCBI(self, val):
        return 'NCBI=%s' % val

    def format_sampleType(self, val):
        if val == 'unknown':
            return ''
        elif val == 'cDNA':
            return 'SC'
        elif val == 'genomic':
            return 'SG'
        elif val == 'mito':
            return 'SM'
        else:
            raise Exception('Unrecognized sample type: %s' % val)

    def format_submitterCount(self, val):
        return 'SBC=%s' % val

    def format_submitters(self, val):
        return 'SBH=%s' % val

    def format_valStatus(self, val):
        vals = val.split(',')
        outList = list()
        for v in vals:
            if v == 'unknown':
                continue
            elif v == 'by-cluster':
                outList.append('CL')
            elif v == 'by-frequency':
                outList.append('FR')
            elif v == 'by-submitter':
                outList.append('SB')
            elif v == 'by-2hit-2allele':
                outList.append('2H')
            elif v == 'by-hapmap':
                outList.append('HM')
            elif v == 'by-1000genomes':
                outList.append('1G')
            else:
                raise Exception('No validation_status mapping for %s' % v)
        return 'VS=' + ','.join(outList)

    def format_strand(self, val):
        if val == '-':
            return 'RV'
        else:
            return ''

    def format_weight(self, val):
        return 'WGT=%s' % val
    
