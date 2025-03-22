#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Author: Matthias Maderer
# E-Mail: edvler@edvler-blog.de
# URL: https://github.com/edvler/check_mk-btrfs_health
# License: GPLv2

#from ctypes import sizeof
from .agent_based_api.v1 import *
import time
import datetime
import re

def percent_or_absolute(param):
    if (param is not None and isinstance(param, float)):
        return "percent"
    elif(param is not None and isinstance(param, int)):
        return "absolute"

    return None

def format_metric_name(metric: str):
    return 'bth_' + str.lower(metric)

def warn_crit_decider(metric, warn, crit, summarytext: str, detailstext: str):
    if metric >= crit:
        return Result(state=State.CRIT, summary=summarytext, details=detailstext)
    if metric >= warn:
        return Result(state=State.WARN, summary=summarytext, details=detailstext)

    return Result(state=State.OK, summary=summarytext, details=detailstext)


def getDateFromString(datetime_string):
    return time.strptime(datetime_string, '%a %b %d %H:%M:%S %Y')

def get_base_infos(line):
    s = line[0].split("::")

    if 'stats' in s or 'usage' in s or 'scrub' in s: #check if valid type
        volume = line[0].split("::")[1]
        infotype = line[0].split("::")[0]

        device = None
        if (infotype == 'stats' and len(line) > 1):
            device = volume + " " + line[1].split(".")[0]

        return volume,infotype,device
    else:
        return None, None, None




def inventory_btrfs_health_base(section):   
    volumes=[]
    devices=[]
    btrfs_version = "not_found"
    for i in range(len(section)):
        if (i==0):
            btrfs_version = section[i][1]
            continue

        volume, infotype, device = get_base_infos(section[i])

        if (volume != None):
            volumes.append(volume)
        if (device != None):
            devices.append(device)

    distinct_volumes = list(set(volumes))
    distinct_devices = list(set(devices))

    return distinct_volumes, distinct_devices

def inventory_btrfs_health_scrub(section):
    distinct_volumes, distinct_devices = inventory_btrfs_health_base(section)

    for i in range(len(distinct_volumes)):
        yield Service(item=distinct_volumes[i])   

def inventory_btrfs_health_dstats(section):
    distinct_volumes, distinct_devices = inventory_btrfs_health_base(section)
    
    for i in range(len(distinct_volumes)):
        yield Service(item=distinct_volumes[i])

def inventory_btrfs_health_usage(section):
    distinct_volumes, distinct_devices = inventory_btrfs_health_base(section)

    for i in range(len(distinct_volumes)):
        yield Service(item=distinct_volumes[i])





def check_btrfs_health_scrub(item, params, section):
    scrub_date = None
    scrub_size = None
    scrub_errors = None
    scrub_duration = None
    scrub_status = None

    match_count = 0

    #fill all variables by parsing btrfs_health output line by line
    for i in range(len(section)):
        line = section[i]

        #frist line is btrfs tools version
        if (i==0):
            btrfs_version = line[1]
            continue

        #scrub::/mnt/test scrub status for 253728d8-e806-437d-acc1-1456aaf79e91
        #scrub::/mnt/test        scrub started at Fri Sep 30 22:54:23 2022, running for 00:00:05
        #scrub::/mnt/test        total bytes scrubbed: 19.38MiB with 0 errors

        #scrub::/mnt/test scrub status for 8c21cca7-46d5-4c44-a461-33eef703669a
        #scrub::/mnt/test        scrub started at Fri Sep 30 21:43:11 2022 and finished after 00:00:00
        #scrub::/mnt/test        total bytes scrubbed: 256.00KiB with 0 errors

        #scrub::/bkp/bkp01 scrub status for 253728d8-e806-437d-acc1-1456aaf79e91
        #scrub::/bkp/bkp01       no stats available
        #scrub::/bkp/bkp01       total bytes scrubbed: 0.00B with 0 errors

        volume, infotype, device = get_base_infos(line)

        if infotype == None:
            continue

        if (item == volume and infotype == 'scrub'):
            match_count = match_count + 1 

            if (len(line) <= 1):
                continue

            #format from btrfs --version = 4....
            if(len(line) >= 4 and line[1] + ' ' + line[2] + ' ' + line[3] == 'scrub started at'):
                scrub_date_raw = line[4] + ' ' + line[5] + ' ' + line[6] + ' ' + line[7] + ' ' + line[8]
                scrub_date = getDateFromString(scrub_date_raw.replace(",",""))
                if (line[9] == "running"):
                    scrub_status = "running"
                    scrub_duration = line[11]
                elif (line[10] == "finished"):
                    scrub_status = "finished"
                    scrub_duration = line[12]               
            if(len(line) >= 4 and line[1] + ' ' + line[2] + ' ' + line[3] == 'total bytes scrubbed:' and scrub_date != None):
                scrub_size = line[4]
                scrub_errors = int(line[6])

            #format from btrfs --version = 5....
            if(line[1] + ' ' + line[2] == "Scrub started:"):
                scrub_date_raw = line[3] + ' ' + line[4] + ' ' + line[5] + ' ' + line[6] + ' ' + line[7]
                scrub_date = getDateFromString(scrub_date_raw.replace(",",""))
            #Special case only for a short time of seconds after start
            #if(line[1] + ' ' + line[2] + ' ' + line[3] == 'no stats available'):
            #    scrub_status = "running"
            #    scrub_duration = "00:00:01"
            if(line[1] == "Status:"):
                scrub_status = line[2]
            if(line[1] == "Duration:"):
                scrub_duration = line[2]
            if(len(line) >= 5 and line[1] + ' ' + line[2] + ' ' + line[3] == 'Total to scrub:'):
                scrub_size = line[4]
            if(len(line) >= 3 and line[1] + ' ' + line[2] == 'Error summary:'):
                if(len(line) >= 6 and line[3] + ' ' + line[4] + ' ' + line[5] == "no errors found"):
                    scrub_errors = 0
                else:
                    if(len(line) >= 4 and line[3].isnumeric()):
                        scrub_errors = int(line[3])
                    elif(len(line) >= 4 and re.search(r'^.+=[0-9]+$', line[3])):
                        scrub_errors = int(re.sub(r'^.+=', '', line[3]))
                    else:
                        scrub_errors = 9999999

    if (match_count == 0):
        yield Result(state=State.UNKNOWN, summary="Filesystem not found (not mounted?, IO problems?)")
        return

    #No Scrub
    if (scrub_errors == None or scrub_status == None):
        yield Result(state=State.UNKNOWN, summary="No scrub done") 
        return

    #x = time.strptime(scrub_duration, '%H:%M:%S')
    #scrub_dur = datetime.timedelta(hours=x.tm_hour,minutes=x.tm_min,seconds=x.tm_sec).total_seconds()
    x = scrub_duration.split(":")
    scrub_dur = int(x[0])*60*60 + int(x[1])*60 + int(x[2])

    #running scrub
    if(scrub_status == "running" and scrub_errors >= 0):
        warn_scrub_runtime, critical_scrub_runtime = params['scrub_runtime']

        summary_runtime="Scrub running since " + render.datetime(time.mktime(scrub_date)) + "; Errors found " + str(scrub_errors)

        if scrub_dur < warn_scrub_runtime:
            yield Result(state=State.OK, summary=summary_runtime)
        if scrub_dur >= warn_scrub_runtime and scrub_dur < critical_scrub_runtime:
            yield Result(state=State.WARN, summary=summary_runtime)
        if scrub_dur >= critical_scrub_runtime:
            yield Result(state=State.CRIT, summary=summary_runtime)
        return

    #finished scrub
    warn_scrub_age, critical_scrub_age = params['scrub_age']

    scrub_age = int(time.time() - time.mktime(scrub_date))

    num = scrub_size[0:-3]
    e = scrub_size[-3:]
    scrub_byte = to_byte(num,e)

    #/opt/omd/versions/2.0.0p4.cre/lib/python3/cmk/gui/plugins/metrics
    #e.g. grep -r "metric_info" | grep time
    yield Metric("age", int(scrub_age), levels=(warn_scrub_age, critical_scrub_age), boundaries=(0, None))
    yield Metric("runtime", scrub_dur, boundaries=(0, None))
    yield Metric("readsize", scrub_byte, boundaries=(0, None))

    scrub_output_summary = 'Last Scrub: ' + render.datetime(time.mktime(scrub_date)) + ' (Age: ' + render.timespan(scrub_age) + ')'
    scrub_output_detail = 'Warn/crit at ' + render.timespan(warn_scrub_age) + '/' + render.timespan(critical_scrub_age) + ')'

    if(scrub_errors > 0):
        yield Result(state=State.CRIT, summary=str(scrub_errors) + " found. Check filesystem with btrfs scrub status -R")
    elif(scrub_errors == 0):
        yield warn_crit_decider(scrub_age, warn_scrub_age, critical_scrub_age, scrub_output_summary, scrub_output_detail)

register.check_plugin(
    name = "btrfs_health_scrub",
    service_name = "btrfs_health scrub status %s",
    discovery_function = inventory_btrfs_health_scrub,
    check_function = check_btrfs_health_scrub,
    check_default_parameters = {'scrub_age': (604800, 864000),
                                'scrub_runtime': (3600, 7200)
                                },
    check_ruleset_name = "btrfs_health_ruleset_scrub"
)




def check_btrfs_health_dstats(item, params, section):
    device_stats_errors = {}
    device_stats_errors_sum = 0

    #fill all variables by parsing btrfs_health output line by line
    for i in range(len(section)):
        line = section[i]

        #frist line is btrfs tools version
        if (i==0):
            btrfs_version = line[1]
            continue

        #get basic information from the begining of the line
        volume, infotype, device = get_base_infos(line)

        if infotype == None:
            continue

        if (volume == item and infotype == 'stats'):
            #stats::/mnt/test [/dev/loop0].write_io_errs    0
            #stats::/mnt/test [/dev/loop0].read_io_errs     0
            #stats::/mnt/test [/dev/loop0].flush_io_errs    0
            #stats::/mnt/test [/dev/loop0].corruption_errs  0
            #stats::/mnt/test [/dev/loop0].generation_errs  0

            #devicename = line[1].split(".")[1]
            #if (not device in device_stats_errors):
            #    device_stats_errors[device] = {devicename: line[2]}
            #else:
            #    device_stats_errors[device][devicename] = line[2]

            if (len(line) >= 3):
                metric = line[1].split(".")[1]
                device_stats_errors[metric] = int(line[2])
                device_stats_errors_sum += int(line[2])

    if (not "write_io_errs" in device_stats_errors):
        yield Result(state=State.UNKNOWN, summary="Filesystem not found (not mounted?, IO problems?)")
        return

    #If the item is a device stats item output the status
    details = ""
    for errtype in device_stats_errors:
        yield Metric(format_metric_name(errtype), int(device_stats_errors[errtype]), boundaries=(0, None))

        warn, crit = params[errtype]

        details = errtype + ": " + str(device_stats_errors[errtype])

        yield warn_crit_decider(device_stats_errors[errtype], warn, crit, details, None)

register.check_plugin(
    name = "btrfs_health_dstats",
    service_name = "btrfs_health device stats %s",
    discovery_function = inventory_btrfs_health_dstats,
    check_function = check_btrfs_health_dstats,
    check_default_parameters =  {'write_io_errs': (1,1),
                                'read_io_errs': (1,1),
                                'flush_io_errs': (1,1),
                                'corruption_errs': (1,1),
                                'generation_errs': (1,1),
                                },
    check_ruleset_name = "btrfs_health_ruleset_dstats"
)




def check_btrfs_health_usage(item, params, section):
    block_group_usage = {}

    #fill all variables by parsing btrfs_health output line by line
    for i in range(len(section)):
        line = section[i]

        #frist line is btrfs tools version
        if (i==0):
            btrfs_version = line[1]
            continue

        #get basic information from the begining of the line
        volume, infotype, device = get_base_infos(line)

        if infotype == None:
            continue
        
        #collect usage informations
        if (item == volume and infotype == 'usage'):
            #Overall:
            #    Device size:                     1288490188800
            #    Device allocated:                1285297274880
            #    Device unallocated:                 3192913920
            #    Device missing:                              0
            #    Used:                            1218484604928
            #    Free (estimated):                  66433708032      (min: 64837251072)
            #    Data ratio:                               1.00
            #    Metadata ratio:                           2.00
            #    Global reserve:                      536870912      (used: 0)
            #
            #Data,single: Size:1276640231424, Used:1213399437312
            #   /dev/sdb     1276640231424
            #
            #Metadata,DUP: Size:4294967296, Used:2542436352
            #   /dev/sdb     8589934592
            #
            #System,DUP: Size:33554432, Used:147456
            #   /dev/sdb       67108864
            #
            #Unallocated:
            #   /dev/sdb     3192913920

            #Size informations
            if (len(line) < 3):
                continue

            if (line[1] + ' ' + line[2] == 'Device size:'):
                block_group_usage['Device_size'] = int(line[3])
            elif (line[1] + ' ' + line[2] == 'Device allocated:'):
                block_group_usage['Device_allocated'] = int(line[3])
            elif (line[1] + ' ' + line[2] == 'Device unallocated:'):
                block_group_usage['Device_unallocated'] = int(line[3])
            elif (line[1].startswith('Data,')):
                block_group_usage['Data_size'] = int(line[2].split(":")[1][:-1])
                block_group_usage['Data_used']  = int(line[3].split(":")[1])
            elif (line[1].startswith('Metadata,')):
                block_group_usage['Metadata_size']  = int(line[2].split(":")[1][:-1])
                block_group_usage['Metadata_used']  = int(line[3].split(":")[1])
            elif (line[1].startswith('System,')):
                block_group_usage['System_size']  = int(line[2].split(":")[1][:-1])
                block_group_usage['System_used']  = int(line[3].split(":")[1])

    if (not "Device_size" in block_group_usage):
        yield Result(state=State.UNKNOWN, summary="Filesystem not found (not mounted?, IO problems?)")
        return

    for metric in block_group_usage:
        yield Metric(format_metric_name(metric), block_group_usage[metric], boundaries=(0, None))


    yield allocation_yielder(params['metadata_allocation'][0], params['metadata_allocation'][1], block_group_usage['Metadata_used'], block_group_usage['Metadata_size'], "Metadata")
    yield allocation_yielder(params['data_allocation'][0], params['data_allocation'][1], block_group_usage['Data_used'], block_group_usage['Data_size'], "Data")
    yield allocation_yielder(params['system_allocation'][0], params['system_allocation'][1], block_group_usage['System_used'], block_group_usage['System_size'], "System")
    yield allocation_yielder(params['overall_allocation'][0], params['overall_allocation'][1], block_group_usage['Device_allocated'], block_group_usage['Device_size'], "Overall")

    #intelligent metadata check
    if (params['metadata_intelligent'][0] >= 0 and params['metadata_intelligent'][1] >= 0):
        pm = (block_group_usage['Metadata_used']/block_group_usage['Metadata_size'])*100
        if (block_group_usage['Device_unallocated'] <= int(params['metadata_intelligent'][0])):
            if(pm >= float(params['metadata_intelligent'][1])):
                yield Result(state=State.CRIT, summary="METADATA allocation above " + str(round(pm,0)) + "% and only " + render.bytes(block_group_usage['Device_unallocated']) + " unallocated block groups avaliable! Use btrfs filesystem usage to investigate.")
                return
        yield Result(state=State.OK, summary="METADATA allocation: " + str(round(pm,0)) + "%; " + render.bytes(block_group_usage['Device_unallocated']) + " unallocated block groups avaliable.")


def allocation_yielder(warn, err, used, size, text):
    p = (used/size)*100

    details = text + ": " + str(round(p,2)) + "% used (" + render.bytes(used) + " of " + render.bytes(size) 

    if (warn == 0 and err == 0):
        return warn_crit_decider(0,1,1, details + ", No warn/crit defined)",None)

    if (percent_or_absolute(warn) == "percent"):
        return warn_crit_decider(p,warn,err, details + ", warn/crit at " + str(warn) + "%/" + str(err) + "%)",None)
    else:
        return warn_crit_decider(used,warn,err, details + ", warn/crit at " + render.bytes(warn) + "/" + render.bytes(err) + ")",None)



register.check_plugin(
    name = "btrfs_health_usage",
    service_name = "btrfs_health block group allocation %s",
    discovery_function = inventory_btrfs_health_usage,
    check_function = check_btrfs_health_usage,
    check_default_parameters = {'overall_allocation': (0,0),
                                'data_allocation': (0,0),
                                'metadata_allocation': (0,0),
                                'system_allocation': (0,0),
                                'metadata_intelligent': (5368709120,75.0), #5GB,75percent
                                },
    check_ruleset_name = "btrfs_health_ruleset_usage"
)

#--iec              use 1024 as a base (KiB, MiB, GiB, TiB)
#--si               use 1000 as a base (kB, MB, GB, TB)
def to_byte(sizenum, size_unit):
    size_cal=0
    sizenum =float(sizenum)
    if size_unit == "TiB":
        size_cal = sizenum*1024*1024*1024*1024
    elif size_unit == "GiB":
        size_cal = sizenum*1024*1024*1024
    elif size_unit == "MiB":
        size_cal = sizenum*1024*1024
    elif size_unit == "KiB":
        size_cal = sizenum*1024
    elif size_unit == "TB":
        size_cal = sizenum*1000*1000*1000*1000
    elif size_unit == "GB":
        size_cal = sizenum*1000*1000*1000
    elif size_unit == "MB":
        size_cal = sizenum*1000*1000        
    elif size_unit == "KB":
        size_cal = sizenum*1000
    elif size_unit == "bytes":
        size_cal = sizenum
    else:
        size_cal = sizenum

    return size_cal
