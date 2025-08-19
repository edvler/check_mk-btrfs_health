#!/usr/bin/env python3
# Author: Matthias Maderer
# E-Mail: matthias.maderer@web.de
# URL: https://github.com/edvler/check_mk-btrfs_health
# License: GPLv2

# Beispiel Check_MK Plugins
# https://github.com/Checkmk/checkmk-docs/blob/master/examples/devel_check_plugins/ruleset_myhostgroups.py

from cmk.agent_based.v2 import (
    AgentSection,
    CheckPlugin,
    CheckResult,
    DiscoveryResult,
    Result,
    Service,
    State,
    Metric,
    render,
    check_levels,
)
import time

def params_parser(params):
    params_new = {}

    for p in params:
        if params[p] is not None and isinstance(params[p], tuple):
            if params[p][0] in ("fixed", "no_levels", "predictive"): #e.g ('fixed', (1, 1)) - New Check_MK 2.4 format
                params_new[p] = params[p]            
            elif isinstance(params[p][0], (int, float)) and isinstance(params[p][1], (int, float)):
                    if p == 'metadata_intelligent':
                        params_new[p] = {'metadata_combined_blocks_free': params[p][0], 'metadata_combined_metadata_relative_used': params[p][1]}
                    else:
                        if p in ('overall_allocation', 'data_allocation', 'metadata_allocation', 'system_allocation'):
                            if (isinstance(params[p][0],float)) and (isinstance(params[p][0],float)):
                                params_new[p] = (p + "_percentage",('fixed',(params[p][0], params[p][1])))
                            if (isinstance(params[p][0],int)) and (isinstance(params[p][0],int)):
                                params_new[p] = (p + "_absolute",('fixed',(params[p][0], params[p][1])))
                        else:
                            params_new[p] = ('fixed', (params[p][0], params[p][1]))
            else:
                params_new[p] = params[p]
        else:
            params_new[p] = params[p]

    
    return params_new



def format_metric_name(metric: str):
    return 'bth_' + str.lower(metric)

def getDateFromString(datetime_string):
    return time.strptime(datetime_string, '%a %b %d %H:%M:%S %Y')

def get_base_infos(line):
    if "::" not in line[0]: # Only lines starting with a string containing "::" are relevant
        return None, None, None

    volume = line[0].split("::")[1]
    infotype = line[0].split("::")[0]

    device = None
    if (infotype == 'stats' and len(line) > 1):
        device = volume + " " + line[1].split(".")[0]

    return volume,infotype,device


def warn_crit_decider(metric, warn, crit, summarytext: str, detailstext: str):
    if metric >= crit:
        return Result(state=State.CRIT, summary=summarytext, details=detailstext)
    if metric >= warn:
        return Result(state=State.WARN, summary=summarytext, details=detailstext)

    return Result(state=State.OK, summary=summarytext, details=detailstext)




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

    params_cmk_24 = params_parser(params)

    #fill all variables by parsing btrfs_health output line by line
    for i in range(len(section)):
        line = section[i]

        #scrub::/mnt/test scrub status for 253728d8-e806-437d-acc1-1456aaf79e91
        #scrub::/mnt/test        scrub started at Fri Sep 30 22:54:23 2022, running for 00:00:05
        #scrub::/mnt/test        total bytes scrubbed: 19.38MiB with 0 errors

        #scrub::/mnt/test scrub status for 8c21cca7-46d5-4c44-a461-33eef703669a
        #scrub::/mnt/test        scrub started at Fri Sep 30 21:43:11 2022 and finished after 00:00:00
        #scrub::/mnt/test        total bytes scrubbed: 256.00KiB with 0 errors

        #scrub::/bkp/bkp01 scrub status for 253728d8-e806-437d-acc1-1456aaf79e91
        #scrub::/bkp/bkp01       no stats available
        #scrub::/bkp/bkp01       total bytes scrubbed: 0.00B with 0 errors


        # <<<btrfs_health_scrub>>>
        # btrfs-progs v6.2
        # scrub::/bkp/bkp01 UUID:             6e6d805d-6790-42b7-938d-6b8500628d74
        # scrub::/bkp/bkp01 Scrub started:    Tue Jul 15 10:01:38 2025
        # scrub::/bkp/bkp01 Status:           finished
        # scrub::/bkp/bkp01 Duration:         2:58:46
        # scrub::/bkp/bkp01 Total to scrub:   2.19TiB
        # scrub::/bkp/bkp01 Rate:             183.26MiB/s
        # scrub::/bkp/bkp01 Error summary:    no errors found



        volume, infotype, device = get_base_infos(line)

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
    #For end

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
        yield from check_levels(
            scrub_dur,
            levels_upper=params_cmk_24['scrub_runtime'],
            boundaries=(0.0,None),
            render_func=render.timespan        
        )
        return

    #finished scrub
    warn_scrub_age, critical_scrub_age = params_cmk_24['scrub_age'][1]

    scrub_age = int(time.time() - time.mktime(scrub_date))

    num = scrub_size[0:-3]
    e = scrub_size[-3:]
    scrub_byte = to_byte(num,e)


    yield Metric("age", int(scrub_age), levels=(warn_scrub_age, critical_scrub_age), boundaries=(0, None))
    yield Metric("runtime", scrub_dur, boundaries=(0, None))
    yield Metric("readsize", scrub_byte, boundaries=(0, None))

    scrub_output_summary = 'Last Scrub: ' + render.datetime(time.mktime(scrub_date)) + ' (Age: ' + render.timespan(scrub_age) + ')'
    scrub_output_detail = 'Warn/crit at ' + render.timespan(warn_scrub_age) + '/' + render.timespan(critical_scrub_age) + ')'

    if(scrub_errors > 0):
        yield Result(state=State.CRIT, summary=str(scrub_errors) + " found. Check filesystem with btrfs scrub status -R")
    elif(scrub_errors == 0):
        yield warn_crit_decider(scrub_age, warn_scrub_age, critical_scrub_age, scrub_output_summary, scrub_output_detail)



check_plugin_btrfs_scrub = CheckPlugin(
    name = "btrfs_health_scrub",
    service_name = "btrfs_health scrub status %s",
    discovery_function = inventory_btrfs_health_scrub,
    check_function = check_btrfs_health_scrub,
    check_default_parameters = {'scrub_age': ('fixed',(604800, 864000)),
                                'scrub_runtime': ('fixed',(3600, 7200))
                                },
    check_ruleset_name = "btrfs_health_ruleset_scrub"
)




def check_btrfs_health_dstats(item, params, section):
    device_stats_errors = {}

    params_cmk_24 = params_parser(params)

    #fill all variables by parsing btrfs_health output line by line
    for i in range(len(section)):
        line = section[i]

        #get basic information from the begining of the line
        volume, infotype, device = get_base_infos(line)

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

    if (not "write_io_errs" in device_stats_errors):
        yield Result(state=State.UNKNOWN, summary="Filesystem not found (not mounted?, IO problems?)")
        return

    #If the item is a device stats item output the status
    for errtype in device_stats_errors:
        yield from check_levels(
            device_stats_errors[errtype],
            levels_upper=params_cmk_24[errtype],
            metric_name=format_metric_name(errtype),
            label=errtype,
            boundaries=(0,None)
        )


check_plugin_btrfs_dstats = CheckPlugin(
    name = "btrfs_health_dstats",
    service_name = "btrfs_health device stats %s",
    discovery_function = inventory_btrfs_health_dstats,
    check_function = check_btrfs_health_dstats,
    check_default_parameters =  {'write_io_errs': ('fixed',(1,1)),
                                'read_io_errs': ('fixed',(1,1)),
                                'flush_io_errs': ('fixed',(1,1)),
                                'corruption_errs': ('fixed',(1,1)),
                                'generation_errs': ('fixed',(1,1)),
                                },
    check_ruleset_name = "btrfs_health_ruleset_dstats"
)




def check_btrfs_health_usage(item, params, section):
    block_group_usage = {}
    
    params_cmk_24 = params_parser(params)
    
    #fill all variables by parsing btrfs_health output line by line
    for i in range(len(section)):
        line = section[i]

        #frist line is btrfs tools version
        if (i==0):
            btrfs_version = line[1]
            continue

        #get basic information from the begining of the line
        volume, infotype, device = get_base_infos(line)

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

    #Metrics
    for metric in block_group_usage:
        #bla = _check_levels(params_cmk_24.get(metric, None))

        yield Metric(format_metric_name(metric),
                     block_group_usage[metric],
                     boundaries=(0, None)
                     )

    #Checks
    # yield from check_levels(
    #     block_group_usage['Metadata_used'],
    #     levels_upper=params_cmk_24['metadata_allocation'],
    #     #metric_name=format_metric_name("Metadata_used"),
    #     label="Metadata used",
    #     render_func=render.disksize,
    #     boundaries=(None,block_group_usage['Metadata_size'])
    # )

    # yield from check_levels(
    #     block_group_usage['Data_used'],
    #     levels_upper=params_cmk_24['data_allocation'],
    #     #metric_name=format_metric_name("Data_used"),
    #     label="Data used",
    #     render_func=render.disksize,
    #     boundaries=(None,block_group_usage['Data_size'])
    # )

    # yield from check_levels(
    #     block_group_usage['System_used'],
    #     levels_upper=params_cmk_24['system_allocation'],
    #     #metric_name=format_metric_name("System_used"),
    #     label="System used",
    #     render_func=render.disksize,
    #     boundaries=(None,block_group_usage['System_size'])
    # )    

    # yield from check_levels(
    #     block_group_usage['Device_allocated'],
    #     levels_upper=params_cmk_24['overall_allocation'],
    #     #metric_name=format_metric_name("Device_allocated"),
    #     label="Overall allocated",
    #     render_func=render.disksize,
    #     boundaries=(None,block_group_usage['Device_size'])
    # )  

    yield allocation_yielder(params_cmk_24['metadata_allocation'], 
                             block_group_usage['Metadata_used'], 
                             block_group_usage['Metadata_size'], 
                             "Metadata")
    yield allocation_yielder(params_cmk_24['data_allocation'],
                             block_group_usage['Data_used'],
                             block_group_usage['Data_size'],
                             "Data")
    yield allocation_yielder(params_cmk_24['system_allocation'],
                             block_group_usage['System_used'],
                             block_group_usage['System_size'],
                             "System")
    yield allocation_yielder(params_cmk_24['overall_allocation'],
                             block_group_usage['Device_allocated'],
                             block_group_usage['Device_size'],
                             "Overall")

    #intelligent metadata check
    pm = (block_group_usage['Metadata_used']/block_group_usage['Metadata_size'])*100

    levels = params_cmk_24['metadata_intelligent'];
    if levels == None or levels ==("no_levels", None):
        yield Result(state=State.OK, summary="METADATA allocation: " + str(round(pm,0)) + "%; " + render.bytes(block_group_usage['Device_unallocated']) + " unallocated block groups avaliable.")
     
    blocks_free = int(params_cmk_24['metadata_intelligent']['metadata_combined_blocks_free'])
    percent_usage_metadata = float(params_cmk_24['metadata_intelligent']['metadata_combined_metadata_relative_used'])

    if (blocks_free >= 0 and percent_usage_metadata >= 0):
        

        if (block_group_usage['Device_unallocated'] <= int(blocks_free)):
            if(pm >= percent_usage_metadata):
                yield Result(state=State.CRIT, summary="METADATA allocation above " + str(round(pm,0)) + "% and only " + render.bytes(block_group_usage['Device_unallocated']) + " unallocated block groups avaliable! Use btrfs filesystem usage to investigate.")
                return
        yield Result(state=State.OK, summary="METADATA allocation: " + str(round(pm,0)) + "%; " + render.bytes(block_group_usage['Device_unallocated']) + " unallocated block groups avaliable.")

#helper for allocations
def allocation_yielder(levels, used, size, text):
    p = (used/size)*100
    details = text + ": " + str(round(p,2)) + "% used (" + render.bytes(used) + " of " + render.bytes(size) 

    if levels == None or levels ==("no_levels", None):
        return Result(state=State.OK, summary=details + ", No warn/crit defined)")
    elif levels[0].endswith("_absolute"):
        warn,crit = levels[1][1]
        return warn_crit_decider(used,warn,crit, details + ", warn/crit at " + render.bytes(warn) + "/" + render.bytes(crit) + ")",None)
    elif levels[0].endswith("_percentage"):
        warn,crit = levels[1][1]
        return warn_crit_decider(p,warn,crit, details + ", warn/crit at " + str(warn) + "%/" + str(crit) + "%)",None)
    


check_plugin_btrfs_health = CheckPlugin(
    name = "btrfs_health_usage",
    service_name = "btrfs_health block group allocation %s",
    discovery_function = inventory_btrfs_health_usage,
    check_function = check_btrfs_health_usage,
    check_default_parameters = {'overall_allocation': None,
                                'data_allocation': None,
                                'metadata_allocation': None,
                                'system_allocation': None,
                                'metadata_intelligent': {
                                    'metadata_combined_blocks_free': 5368709120,
                                    'metadata_combined_metadata_relative_used': 75.0
                                    }
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
