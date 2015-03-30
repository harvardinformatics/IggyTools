import pandas
import re
from lxml import etree

def byLaneStats(tile_df, qual_df):
    codeMap = { 100 : "cluster_density",
                101 : "cluster_density_pf",
                102 : "num_clusters",
                103 : "num_clusters_pf" }

    lanes = dict() 

    ##
    # Get density stats from tile data frame
    ##

    for index, row in tile_df.iterrows():
        if row['code'] in codeMap.keys():
            i = int(row['lane'])
            metricType = codeMap[int(row['code'])]
            if i not in lanes.keys():
                lanes[i] = dict()
            if metricType not in lanes[i].keys():
                lanes[i][metricType] = list()
            lanes[i][metricType].append(row['value'])

    #for each lane, for each metric, average over the tiles
    for i in lanes.keys():
        for metricType in lanes[i].keys():
            m = lanes[i][metricType]
            numTiles = len(m)
            mySum = sum(m)
            if numTiles > 0:
                lanes[i][metricType] = sum(m)/len(m)
            else:
                lanes[i][metricType] = 0
            if "num_tiles" not in lanes[i].keys():
                lanes[i]["num_tiles"] = numTiles

    for i in lanes.keys():
        lanes[i]["percent_pf_clusters"] = 100.0 * lanes[i]["cluster_density_pf"]/lanes[i]["cluster_density"]

    ##
    # Get stats from quality data frame
    ##


    threshold = 30 #threshold quality score 
    # Note: Before changing this threshold consider possible binning of q scores in v.5 format quality metrics file 
    # (See seqstats/illuminate/quality_metrics.py)

    colnames = qual_df.columns.values.tolist()
    qnames = [x for x in colnames if x.startswith('q')]
    qnames_below_threshold = [x for x in qnames if int(x[1:]) <= threshold]
    qnames_above_threshold = [x for x in qnames if int(x[1:]) > threshold]

    for index, row in qual_df.iterrows():
        i = int(row['lane'])
        if "q_below_thresh" not in lanes[i].keys():
            lanes[i]["q_below_thresh"] = sum(row[qnames_below_threshold])
            lanes[i]["q_above_thresh"] = sum(row[qnames_above_threshold])
        else:
            lanes[i]["q_below_thresh"] = lanes[i]["q_below_thresh"] + sum(row[qnames_below_threshold])
            lanes[i]["q_above_thresh"] = lanes[i]["q_above_thresh"] + sum(row[qnames_above_threshold])    

    for i in lanes.keys():
        lanes[i]["perc_q_ge_" + str(threshold)] = 100.0*lanes[i]["q_above_thresh"]/(lanes[i]["q_above_thresh"]+lanes[i]["q_below_thresh"])
        del lanes[i]["q_above_thresh"]
        del lanes[i]["q_below_thresh"]

    return lanes

def parseRunInfo(rifile):
    with open (rifile, 'r') as myfile:
        xmlstr=myfile.read().replace('\n', '')

    root = etree.fromstring(xmlstr)
    datetext=root.find('Run/Date').text

    reads = root.find('Run/Reads').getchildren()
    rdict = dict()
    for read in reads:
        read_num = read.attrib['Number']
        rdict["Read" + read_num] = dict()
        rdict["Read" + read_num]['is_index'] = read.attrib['IsIndexedRead']
        rdict["Read" + read_num]['num_cycles'] = read.attrib['NumCycles']

    return rdict, datetext
