import os.path as path
import re, glob, logging

def genePred2gtf(inFile, sourceID, outDir = None, outFile = None):
    log = logging.getLogger("iggyref_" + sourceID)
    log.info('Converting %s to GTF format' % inFile)

    if not outFile:
        inFileStem = path.splitext(inFile)[0]
        if outDir:
            outFile = path.join(outDir, inFileStem + ".gtf")
        else:
            outFile = path.join( path.dirname(inFile), inFileStem + ".gtf" )

    fin = open(inFile, 'r')
    fout = open(outFile, 'w')
    g = dict() 
    for line in fin:
        vals = line.rstrip().split('\t')

        #UCSC genePred fields
        g['name'] = vals[1]
        g['chrom'] = vals[2]
        g['strand'] = vals[3]
        g['txStart'] = str(int(vals[4]) + 1)  #add 1 to start to convert from UCSC indexing
        g['txEnd'] = vals[5]
        g['codingStart'] = str(int(vals[6]) + 1)  #add 1 to start to convert from UCSC indexing
        g['codingEnd'] = vals[7]
        g['exonStarts'] = [str(int(x) + 1) for x in vals[9].rstrip(',').split(',')]  #add 1 to start to convert from UCSC indexing
        g['exonEnds'] = vals[10].rstrip(',').split(',')
        g['altName'] = vals[12]
        g['exonFrames'] = vals[15].rstrip(',').split(',')
        numExons = len(g['exonStarts'])

        #GTF fields:
        chromName = g['chrom']
        if g['altName']:
            attribute = 'gene_id "' + g['altName'] + '"; gene_name "' + g['altName'] + '"; transcript_id "' + g['name'] + '";'
        else:
            attribute = 'transcript_id "' + g['name'] + '";'

        for j in range(numExons):
            #write coding sequence line
            feature = 'CDS'
            if j == 0:
                codingStart = g['codingStart']
            else:
                codingStart = g['exonStarts'][j]

            if j == numExons-1:
                codingEnd = g['codingEnd']
            else:
                codingEnd = g['exonEnds'][j]

            if g['exonFrames'] == '-1':
                frame = '.'
            else:
                frame = g['exonFrames'][j]

            #format: chromName, source, feature, start, end, score, strand, frame, attribute
            fout.write('\t'.join([chromName, 'unknown', feature, codingStart, codingEnd, '.', g['strand'], frame, attribute]) + '\n')

            #now write exon line
            feature = 'exon'
            #format: chromName, source, feature, start, end, score, strand, frame, attribute
            fout.write('\t'.join([chromName, 'unknown', feature, g['exonStarts'][j], g['exonEnds'][j], '.', g['strand'], frame, attribute]) + '\n')

    fin.close()
    fout.close()
    return outFile
            
