from django.shortcuts import render, render_to_response
from django.template import RequestContext
from django.http import HttpResponse
from django.forms.models import model_to_dict
from iggytools.iggyapp.models import SeqRun, Lane
from django.core.serializers.json import DjangoJSONEncoder
from django.core.exceptions import ObjectDoesNotExist
from datetime import datetime, timedelta
import json, re

def index(request): #index page has menus to make scatter or bar plots
    return render_to_response('index.html', context_instance=RequestContext(request))

def getRorL(request): #get Run or Lane object
    runName = request.GET["run"]
    try: laneNum = request.GET["lane"]
    except: laneNum = ""

    if laneNum:
        RorL = Lane.objects.get(run_name__exact=runName, lane_num__exact=laneNum)  
    else:
        RorL = SeqRun.objects.get(run_name__exact=runName)
    return RorL

def getLDataObj(**kwargs): #get plot object of historical data, for some data type
    rorl = "run"    #defaults
    data_type = "perc_q_ge_30"
    date_range = ""
    machine_name = ""

    for key, value in kwargs.iteritems():  #get query parameters
        if key == "rorl": rorl = value 
        if key == "machine_name": machine_name = value 
        if key == "date_range": date_range = value 
        if key == "data_type": data_type = value 

    if rorl == "run":
        query = SeqRun.objects.filter()
    else:
        query = Lane.objects.filter()

    if machine_name:
         query = query.filter(machine_name__istartswith=machine_name)

    if date_range:
        if date_range == "last_3_months":
            startdate = last_month = datetime.today() - timedelta(days=30*3)
        elif date_rate == "last_6_months":
            startdate = last_month = datetime.today() - timedelta(days=30.5*6)
        elif date_rate == "last_12_months":
            startdate = datetime.today() - timedelta(days=365)
        query = query.filter(date__gte=startdate)

    if rorl == "run":
        names = list(query.values_list("run_name", flat=True))
    else: 
        runNames = list(query.values_list("run_name", flat=True))
        laneNums = list(query.values_list("lane_num", flat=True))
        names = [runNames[i]  + "_lane" + str(laneNums[i]) for i in range(len(runNames))]        
    data = list(query.values_list(data_type, flat=True))
    dates = list(query.values_list("date", flat=True))
    dates_formatted = [d.isoformat() for d in dates]
    return {"names": names, "dates": dates_formatted, "data": data, "RorL": rorl}        

def minilims(request):  #page requested by minilims to show histogram plots (request may contain run, run+lane, or submission name) 
    subName = ""
    RorL = ""
    try:
        RorL = getRorL(request)
    except:
        try: subName = request.GET["sub"]
        except: subName = ""

    try: resolution = request.GET["reso"]
    except: resolution = "run"

    if subName: #find lanes associated with this submission
        lanes = Lane.objects.filter(sub_name__exact=subName)
        if len(set([lanes[i].machine_name for i in range(len(lanes))])) > 1:
            raise Exception("Multiple machine types found matching request")   
        machineName = lanes[0].machine_name
        runNames = list(lanes.values_list("run_name", flat=True))
        if resolution != "run": #then return lane-wise data for this submission
            laneNums = list(lanes.values_list("lane_num", flat=True))
            itemType = "lane"
            shortName = subName
            selectedNames = [runNames[i]  + "_lane" + str(x) for x in laneNums]
        else: #return run-wise data for this submission
            Runs = list(set([SeqRun.objects.get(run_name__exact=x) for x in runNames]))
            itemType = "run"
            selectedNames = [x.run_name for x in Runs]
            shortName = ", ".join(selectedNames)
        plotObj_ppfc = getLDataObj(machine_name = machineName, rorl = itemType, data_type = "percent_pf_clusters")
        plotObj_cd = getLDataObj(machine_name = machineName, rorl = itemType, data_type = "cluster_density")
    elif RorL:  #a run or lane was requested
        machineName = RorL.machine_name
        if type(RorL) == type(SeqRun()):
            shortName = RorL.run_name
            if resolution != "run": #then return lane-wise data for this run
                itemType = "lane"
                lanes = Lane.objects.filter(run_name__exact=RorL.run_name)
                laneNums = list(lanes.values_list("lane_num", flat=True))
                selectedNames = [RorL.run_name  + "_lane" + str(x) for x in laneNums]
            else: # return run-wise data for this run
                itemType = "run"
                selectedNames = shortName
        elif type(RorL) == type(Lane()): #return lane-wise data for this lane
            itemType = "lane"
            shortName = RorL.run_name + "_lane" + str(RorL.lane_num)
            selectedNames = shortName
    plotObj_ppfc = getLDataObj(machine_name = machineName, rorl = itemType, data_type = "percent_pf_clusters")
    plotObj_cd = getLDataObj(machine_name = machineName, rorl = itemType, data_type = "cluster_density")
    parameters = {"short_name": shortName, "selected_names": selectedNames, "machine_name": machineName, "type": itemType, "plotObj_ppfc": plotObj_ppfc, "plotObj_cd": plotObj_cd}
    return render_to_response('minilims.html', {"parameters": json.dumps(parameters)}, context_instance=RequestContext(request))

def testRorLs(RorLs): #check whether there is data associated with a run or lane
    try:
        for RorL in RorLs:
            throwAwayVal = RorL.cluster_density_pf + RorL.percent_pf_clusters  #test that vals exist and are numbers
            if type(RorL) == type(SeqRun()):
                lanes = Lane.objects.filter(run_name__exact=RorL.run_name)
                for lane in lanes:
                    throwAwayVal = lane.cluster_density_pf + lane.percent_pf_clusters  #test that vals exist and are numbers
    except:
         raise Exception("T'aint no data")

def getLData(request):  #returns data dict for plots
    try: dataType = request.GET["data_type"]
    except: dataType = ""

    try: dateRange = request.GET["date_range"]
    except: dateRange = ""

    try: machineName = request.GET["machine_name"]
    except: machineName = ""

    try: itemType = request.GET["rorl"]
    except: itemType = ""

    dataObj = getLDataObj(data_type = dataType, date_range = dateRange, machine_name = machineName, rorl = itemType)
    return HttpResponse(json.dumps(dataObj), content_type='application/json')

def minilimsPlotTest(request):  #returns result of test of whether a minilims plot can be made for a given run/lane/submission
    RorL = ""
    subName = ""
    try:
        RorL = getRorL(request)
    except:
        try: 
            subName = request.GET["sub"]
        except:
            subName = ""
    try:
        if subName:
            runs = SeqRun.objects.filter(sub_name__exact=subName)
            testRorLs(runs)
        elif RorL:
            testRorLs([RorL])
    except:
        return HttpResponse("Failure", content_type='text/html')
    return HttpResponse("Success", content_type='text/html')

def testMinilims(request): #testing page for minilims view
    return render_to_response('test_minilims.html', context_instance=RequestContext(request))

def showRorL(request): #page to show run/lane info. Requested when user clicks on points/bars in interactive plot
    name = request.GET["rorl"]
    matchObj = re.match( r'^(.*?)_lane([0-9]+)', name)
    if matchObj: #if lane was requested..
        runName = matchObj.group(1)
        laneNum = matchObj.group(2)
        RorL = Lane.objects.get(run_name__exact=runName, lane_num__exact=laneNum)
    else: #if run was requested...
        RorL = SeqRun.objects.get(run_name__exact=name)
    dd = {"rorl": model_to_dict(RorL)}
    return render_to_response('showrorl.html', dd, context_instance=RequestContext(request))

