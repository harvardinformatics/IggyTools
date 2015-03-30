#!/usr/bin/env python 
from lxml import etree
from datetime import date
from iggytools.iggyseq.seqstats import stats, util
from optparse import OptionParser
from iggytools.iggyapp.models import SeqRun, Lane
from iggytools.iggyseq.sampleSheetClasses import BaseSampleSheet
from iggytools.iggyseq.runClasses import IlluminaNextGen, getSeqPref
from iggytools.iggyseq.seqUtil import parseRunInfo
from iggytools.iggyseq.seqstats.illuminate import InteropDataset
import shutil, time, json, sys, re, os
import os.path as path

def getRun(runName): #get run from DB (exception raised if does not exist)
    runs = list(SeqRun.objects.filter(run_name=runName))
    if len(runs) > 1:
        raise Exception("Multiple ("+str(len(runs))+") instances of run " + runName + "found in DB")
    return runs[0]


def add(argv):  #add a new run to DB

    pref = getSeqPref()

    parser = OptionParser(usage="usage: %prog [options] <run_name>")

    parser.add_option("-f","--force", help="Rewrite current DB contents with new run and associated lanes. Default: %default", 
                                             default=False, action="store_true", dest="force")
    parser.add_option("-b","--no-db-rewrite",help="Do not overwrite any existing runs and associated lanes in DB. Default: %default",
                                             default=False, action="store_true", dest="noDBrewrite")
    parser.add_option("-t","--no-hist-rewrite",help="Do not overwrite any existing run files in history directory. Default: %default",
                                             default=False, action="store_true", dest="noHistRewrite")
    parser.add_option("-c","--copy-only",help="Copy run files to history directory. Do not write to database. Default: %default",
                                             default=False, action="store_true", dest="noDB")
    parser.add_option("-v","--verbose", help="Verbose mode. Default: %default",
                                             default=False, action="store_true", dest="verbose")
    parser.add_option("-d","--dir", help="Directory containing run folder. Default: %default",
                                             default=pref.PRIMARY_PARENT, action="store", type="string",  dest="primaryParent")
    options, args = parser.parse_args(argv)
    if len(args) != 1:
        parser.error('Expected one input argument, found %s: %s' % (len(args), ' '.join(args)))

    runName = args[0]

    if not re.match('[0-9]{6}_[0-9A-Za-z]+_', runName):
        parser.error("Expected run name as first argument, got '" + runName + "'. Use -h to see usage.")
    runPath = path.join(options.primaryParent,runName)

    #Copy essential files to history dir, if not already present
    histDir = pref.SEQSTATS_HIST_DIR
    runHistDir = path.join(histDir,runName)
    if path.isdir(runHistDir):
        if options.verbose: print "Run " + runName + " already present in seqstats_hist dir: " + histDir
        if not options.noHistRewrite:
            resp = raw_input("Overwrite current run history with run files in " + runPath + "? [y/n] ")
            if resp.lower().startswith('y'):
                if options.verbose: print ("Deleting old history directory " + runHistDir)
                shutil.rmtree(runHistDir, ignore_errors=True)
                if options.verbose: print "Copying run files to " + histDir + " ..."
                util.copyRunFiles(runPath, histDir)
    if options.noDB: 
        if options.verbose: print 'Exiting.'
        return

    try:
        DBrun = getRun(runName)
    except IndexError:  #thrown if query in getRun() returns an empty list
        DBrun = None

    if DBrun and options.noDBrewrite: 
        if options.verbose: print ("Run " + runName + " is already in DB. Exiting.")
        return
    elif DBrun and not options.force: #check if run and any associated lanes should be deleted
        resp = raw_input("Run " + runName + " found in DB. Delete and save new run and associated lanes? [y/n] ")
        if resp.lower().startswith('n'):
            if options.verbose: print ("Exiting.")
            return

    if DBrun:  #if run was found, and user did not opt to exit (or specified options.force)...
        DBrun.delete() #delete run 
        DBlanes = Lane.objects.filter(run_name = runName) #delete any lanes associated with this run
        for DBlane in DBlanes:
            DBlane.delete()

    #check that run directory exists
    if not path.isdir(runPath):
        raise Exception("Run \"" + runName + "\" not found at: " + runPath)

    if options.verbose: print "Parsing run files for " + runName

    #Read run stats in binary files
    myDataset = InteropDataset(runPath)
    tile = myDataset.TileMetrics()
    quality = myDataset.QualityMetrics()
    quality_summary = quality.read_qscore_results
    layout = tile.flowcell_layout

    #make specs dict from RunInfo.xml and SampleSheet.csv  (specs dict will be saved as json in DB)
    specs = dict()
    seqPrepRun = IlluminaNextGen.getInstance(runName)
    SampleSheet = BaseSampleSheet.getInstance(seqPrepRun)
    SampleSheet.parse()
    specs['SampleSheet'] = SampleSheet.contentString
    reads, datetext = parseRunInfo(path.join(runPath, 'RunInfo.xml'))
    specs['Reads'] = reads

    #get machine name
    match = re.match('^[0-9]{6}_([0-9A-Za-z]+)_', runName)
    machine_id = match.groups(1)[0]
    machine_name = pref.MACHINE_TYPE[machine_id] + ' (' + machine_id + ')'

    lanes = stats.byLaneStats(tile.df, quality.df)
    if options.verbose: print "Adding " + str(len(lanes)) + " lanes to database..."

    run = SeqRun()
    run.run_name = runName
    run.num_clusters = tile.num_clusters
    run.num_clusters_pf = tile.num_clusters_pf
    run.percent_pf_clusters = tile.percent_pf_clusters
    run.cluster_density = tile.mean_cluster_density
    run.cluster_density_pf = tile.mean_cluster_density_pf
    run.num_reads_per_cluster = tile.num_reads
    run.num_tiles = tile.num_tiles
    run.num_lanes = layout['lanecount']
    run.date=date(int('20' + datetext[:2]), int(datetext[2:4]), int(datetext[4:6]))
    run.machine_name = machine_name
    run.specs = json.dumps(specs)
    if options.verbose: printRunFields(run)
    run.save()

    perc_q_ge_30_list = list()
    for laneInt in lanes:
        ldata = lanes[laneInt]
        myLane = Lane()
        myLane.lane_num = laneInt
        myLane.run_name = runName
        myLane.num_clusters = ldata["num_clusters"]
        myLane.num_clusters_pf = ldata["num_clusters_pf"]
        myLane.percent_pf_clusters = ldata["percent_pf_clusters"]
        myLane.cluster_density = ldata["cluster_density"]
        myLane.cluster_density_pf = ldata["cluster_density_pf"]
        myLane.perc_q_ge_30 = ldata["perc_q_ge_30"]
        perc_q_ge_30_list.append(myLane.perc_q_ge_30)
        myLane.num_tiles = ldata["num_tiles"]
        myLane.date = date(int('20' + datetext[:2]), int(datetext[2:4]), int(datetext[4:6]))
        myLane.machine_name = machine_name
        myLane.seqrun = run

        if re.search('nextseq', machine_name, re.IGNORECASE):
            myLane.sub_name = SampleSheet.subIDs[0]  #assume one submission per NextSeq run. ****Issue: user (samplesheet) lane vs. binary file lane (e.g., nextseq)
        elif re.search('hiseq', machine_name, re.IGNORECASE):
            myLane.sub_name = SampleSheet.lanes[laneInt-1].subIDs[0]  #assume one submission per HiSeq lane  ****Make lane indexing more clear
        else:
            raise Exception('Unrecognized machine_name: %s' % machine_name)

        if options.verbose: printLaneFields(myLane)
        myLane.save()

    run.perc_q_ge_30 = sum(perc_q_ge_30_list)/len(perc_q_ge_30_list)
    run.save()

def printLaneFields(myLane):
    print 'Lane: %s, lane %s' % (myLane.run_name, myLane.lane_num)
    for field in ['num_clusters', 'num_clusters_pf', 'percent_pf_clusters', 'cluster_density', 'cluster_density_pf', 
                  'perc_q_ge_30', 'num_tiles', 'date', 'machine_name', 'sub_name']:
        print '      %s: %s' % (field, getattr(myLane, field))

def printRunFields(myRun):
    print 'Run: %s' % myRun.run_name
    for field in ['num_clusters', 'num_clusters_pf', 'percent_pf_clusters', 'cluster_density', 'cluster_density_pf', 
                  'num_tiles', 'num_lanes', 'date', 'machine_name', 'specs']:
        print '     %s: %s' % (field, getattr(myRun, field))
                  
if __name__ == "__main__":
    add(sys.argv[1:])
