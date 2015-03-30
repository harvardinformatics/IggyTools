<?php

#$topdir = getenv('MINILIMS');  
$topdir = "/n/informatics/seq/minilims";
require_once("$topdir/GlobalConfig.php");
require_once("$topdir/datamodel/Utils.php");
require_once("$topdir/plugins/Illumina/Illumina_RunInfoFile.php");
require_once("$topdir/plugins/Illumina/SampleSheet.php");

$run        = "";
$rundir     = "";
$subIDsList = "";
$store      = "";  #set to 1 to store data, 0 otherwise

$options = getopt("r:d:u:s:");

if (isset($options["r"])) { $run        = $options["r"]; }
if (isset($options["d"])) { $rundir     = $options["d"]; }
if (isset($options["u"])) { $subIDsList = $options["u"]; }
if (isset($options["s"])) { $store      = $options["s"]; }

if ($run == "" || $rundir == "" || $subIDsList == "" || $store == "") {
  print "DBupdate.php Error: All input parameters must be set.\n";
  print "Parameters:\n";
  print " run: $run\n rundir: $rundir\n subIDsList: $subIDsList\n store: $store\n"; 
  exit(1);
}

$table   = new Table('semantic_data');

#Get list of any existing analysis instances for this run
$old  = PGQuery($table,"*:Illumina_BclConversion_Analysis:Illumina_Run:$run","",array("Illumina_BclConversion_Analysis"),0);
$old_analnames = $old->getTypeNameArray('Illumina_BclConversion_Analysis');

#Get name for current analysis instance
$curaname="";
if (count($old_analnames) == 0){ #if no analysis objects exist, get name for a new one
  $curaname = Type::getNewTypeName($table,"Illumina_BclConversion_Analysis");
} elseif (count($old_analnames) == 1){ #if there is one analysis obj, set to current
  $curaname = $old_analnames[0];
} elseif (count($old_analnames) > 1){ #if there are many old analyses, delete all but one
  $curaname = $old_analnames[0];
  for($i=1;$i<count($old_analnames);$i++) {
    $tmpinst = new TypeInstance("Illumina_BclConversion_Analysis",$old_analnames[$i]);
    $tmpinst->delete($table);
  }
}

#Set run properties
$runinst = new TypeInstance("Illumina_Run",$run);  #local Illumina_Run object; may already exist in database
$runinst->fetch($table);
$runinst->setPropertyValue("Illumina_BclConversion_Analysis",$curaname);

#Set analysis properties
$analinst = new TypeInstance("Illumina_BclConversion_Analysis",$curaname); #local instance
$analinst->setPropertyValue("Illumina_Run",$run);
$analinst->setPropertyValue("Status","COMPLETE");
$analinst->setPropertyValue("Timestamp",date('M d Y H:i:s'));
$analinst->setPropertyValue("Data_Directory","/n/ngsdata/".$run);
$analinst->setPropertyValue("Web_Link","https://software.rc.fas.harvard.edu/ngsdata/".$run);

#Add links to/from Submissions and the Run, Analysis objects
$subIDs = explode(",", $subIDsList);
foreach($subIDs as $subID) {
  $subinst = new TypeInstance("Submission",$subID);
  $subinst->fetch($table);
  #print $subinst->printValues();

  #$subinst->deleteProperty($table,"Status"); #remove "NEW" status. 
  $analinst->setPropertyValue("Status","In Progress"); #Not setting to COMPLETE as this submission might span multiple Illumina runs.
  $subinst->addPropertyValue("Illumina_Run",$run);
  $runinst->addPropertyValue("Submission",$subID);
  $analinst->addPropertyValue("Submission",$subID);

  if ($store) { $subinst->store($table); }
}

if ($store) { 
  $analinst->store($table); 
  $runinst->store($table); 
}
exit(0);

?>