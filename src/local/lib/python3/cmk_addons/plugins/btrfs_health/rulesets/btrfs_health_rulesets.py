#!/usr/bin/env python3
# Author: Matthias Maderer
# E-Mail: matthias.maderer@web.de
# URL: https://github.com/edvler/check_mk-btrfs_health
# License: GPLv2

#example: \lib\python3\cmk\gui\plugins\wato\check_parameters\memory.py

from cmk.rulesets.v1 import Title
from cmk.rulesets.v1.form_specs import (
    Dictionary,
    Tuple,
    Age,
    Integer,
    Filesize,
    Alternative,
    Percentage
)
from cmk.rulesets.v1.rule_specs import SpecialAgent, Topic



def _parameter_btrfs_health_scrub():
    return Dictionary(
        required_keys=[],
        elements = [
            ('scrub_age',
             Tuple(
                 title = "Age of last btrfs scrub before changing to warn or critical (cmd: btrfs scrub status).",
                 elements = [
                     Age(title=_("Warning at or above scrub age of"),
                         default_value = 604800, #warn after 7*24*60*60=604800 one week
                         help=_("If the scrub is older than the specified time, the check changes to warn.")
                     ),
                     Age(title=_("Critical at or above scrub age of"),
                         default_value = 864000, #critical after 10*24*60*60=604800 10 days
                         help=_("If the scrub is older than the specified time, the check changes to critical.")
                     ),
                 ]
            )
          ),
            ('scrub_runtime',
             Tuple(
                 title = "Runtime of scrub before changing to warn or critical (cmd: btrfs scrub status).",
                 elements = [
                     Age(title=_("Warning at or above scrub runtime of"),
                         default_value = 3600, #warn after 60*60=3600 one hour
                         help=_("If the scrub is running longer than the specified time, the check changes to warn.")
                     ),
                     Age(title=_("Critical at or above scrub runtime of"),
                         default_value = 7200, #critical after 2*60*60=7200 two hours
                         help=_("If the scrub is running longer than the specified time, the check changes to critical.")
                     ),
                 ]
            )
          ),
        ]
    )

rule_spec_btrfs_health_ruleset_scrub = CheckParameters(
    name="btrfs_health_ruleset_scrub",
    topic=Topic.STORAGE,
    parameter_form=_parameter_btrfs_health_scrub,
    title=Title("BTRFS Health scrub status"),
    condition=HostAndItemCondition(item_title=Title("BTRFS Health scrub status")),
)

def _parameter_btrfs_health_dstats():
    return Dictionary(
        required_keys=[],
        elements = [          
            ('write_io_errs',
             Tuple(
                 title = "Write IO errors (write_io_errs) for devices used by btrfs volume (cmd: btrfs device stats).",
                 elements = [
                     Integer(title=_("Warning at or above error count"),
                         default_value = 1,
                         help=_("If the write_io_errs counter of a device is above the given number, change to warn.")
                     ),
                     Integer(title=_("Critical at or above error count"),
                         default_value = 1,
                         help=_("If the write_io_errs counter of a device is above the given number, change to critical.")
                     ),
                 ]
            )
          ),
            ('read_io_errs',
             Tuple(
                 title = "Read IO errors (read_io_errs) for devices used by btrfs volume (cmd: btrfs device stats).",
                 elements = [
                     Integer(title=_("Warning at or above error count"),
                         default_value = 1,
                         help=_("If the read_io_errs counter of a device is above the given number, change to warn.")
                     ),
                     Integer(title=_("Critical at or above error count"),
                         default_value = 1,
                         help=_("If the read_io_errs counter of a device is above the given number, change to critical.")
                     ),
                 ]
            )
          ),
            ('flush_io_errs',
             Tuple(
                 title = "Flush IO errors (flush_io_errs) for devices used by btrfs volume (cmd: btrfs device stats).",
                 elements = [
                     Integer(title=_("Warning at or above error count"),
                         default_value = 1,
                         help=_("If the flush_io_errs counter of a device is above the given number, change to warn.")
                     ),
                     Integer(title=_("Critical at or above error count"),
                         default_value = 1,
                         help=_("If the flush_io_errs counter of a device is above the given number, change to critical.")
                     ),
                 ]
            )
          ),       
            ('corruption_errs',
             Tuple(
                 title = "Corruption errors (corruption_errs) for devices used by btrfs volume (cmd: btrfs device stats).",
                 elements = [
                     Integer(title=_("Warning at or above error count"),
                         default_value = 1,
                         help=_("If the corruption_errs counter of a device is above the given number, change to warn.")
                     ),
                     Integer(title=_("Critical at or above error count"),
                         default_value = 1,
                         help=_("If the corruption_errs counter of a device is above the given number, change to critical.")
                     ),
                 ]
            )
          ),  
            ('generation_errs',
             Tuple(
                 title = "Generation errors (generation_errs) for devices used by btrfs volume (cmd: btrfs device stats).",
                 elements = [
                     Integer(title=_("Warning at or above error count"),
                         default_value = 1,
                         help=_("If the generation_errs counter of a device is above the given number, change to warn.")
                     ),
                     Integer(title=_("Critical at or above error count"),
                         default_value = 1,
                         help=_("If the generation_errs counter of a device is above the given number, change to critical.")
                     ),
                 ]
            )
          ),
        ]
    )


rule_spec_btrfs_health_ruleset_dstats = CheckParameters(
    name="btrfs_health_ruleset_dstats",
    topic=Topic.STORAGE,
    parameter_form=_parameter_btrfs_health_dstats,
    title=Title("BTRFS Health device stats"),
    condition=HostAndItemCondition(item_title=Title("BTRFS Health device stats")),
)



btrfs_usage_info=_(
                        "The BTRFS filesystem stores data in a internal structure called block groups. " 
                        "More informations could be found in the manpage: man mkfs.btrfs -> section BLOCK GROUPS, CHUNKS, RAID. "
                        "From the manpage: "
                        "-- A typical size of metadata block group is 256MiB (filesystem smaller than 50GiB) and 1GiB (larger than 50GiB), for data it’s 1GiB. The system block group size is a few megabytes. -- "
                        "The command 'btrfs filesystem usage ' displays the allocated sizes. "
                        "As long as 'Device unallocated' are greater than 1GB new block groups can be always allocated and there is no problem. "
                        "But There are some situations that are cirtical: "
                        "1. No 'Device unallocated' space is avaliable (or less than 1GB) AND Metadata is running out of space "
                        "2. No 'Device unallocated' space is avaliable (or less than 1GB) AND System is running out of space "
                        "If no 'Device unallocated' space is avaliable two fixes availiable: "
                        "- extend the disk "
                        "- OR man btrfs-balance --> See examples for parameter -dusage or -musage "
                    )

def _parameter_btrfs_health_usage():
    return Dictionary(
        required_keys=[],
        elements = [   
            ('metadata_intelligent',
             Tuple(
                 title = "METADATA combined: If unnallocated blocks below the given limit AND METADATA allocation above the given percent, this check changes to crit. Activate Help -> Inline Help for more informations.",
                 help=btrfs_usage_info,
                 elements = [
                    Filesize(title=_("Minimum unallocated block groups")),
                    Percentage(title=_("METADATA allocation in percent"), unit=_("percent"), default_value=(75.0)),
                 ]
            )
          ),             
            (
                "metadata_allocation",
                Alternative(
                    title=_("METADATA allocation (cmd: btrfs filesystem usage). Activate Help -> Inline Help for more informations."),
                    
                    help=btrfs_usage_info,
                    elements=[
                        Tuple(
                            title=_("METADATA allocation relative to METADATA size"),
                            elements=[
                                Percentage(title=_("Warning at or above"), unit=_("percent")),
                                Percentage(title=_("Critical at or above"), unit=_("percent")),
                            ],
                        ),
                        Tuple(
                            title=_("Absolute METADATA allocation"),
                            elements=[
                                Filesize(title=_("Warning at or above")),
                                Filesize(title=_("Critical at or above")),
                            ],
                        ),
                    ],
                ),
            ),
            (
                "system_allocation",
                Alternative(
                    title=_("SYSTEM allocation (cmd: btrfs filesystem usage). Activate Help -> Inline Help for more informations."),
                    default_value=(70.0,80.0),
                    
                    help=btrfs_usage_info,
                    elements=[
                        Tuple(
                            title=_("SYSTEM allocation relative to SYSTEM size"),
                            elements=[
                                Percentage(title=_("Warning at or above"), unit=_("percent")),
                                Percentage(title=_("Critical at or above"), unit=_("percent")),
                            ],
                        ),
                        Tuple(
                            title=_("Absolute SYSTEM allocation"),
                            elements=[
                                Filesize(title=_("Warning at or above")),
                                Filesize(title=_("Critical at or above")),
                            ],
                        ),
                    ],
                ),
            ),
            (
                "data_allocation",
                Alternative(
                    title=_("DATA allocation (cmd: btrfs filesystem usage). Activate Help -> Inline Help for more informations."),
                    help=btrfs_usage_info,
                    elements=[
                        Tuple(
                            title=_("DATA allocation relative to DATA size"),
                            elements=[
                                Percentage(title=_("Warning at or above"), unit=_("percent")),
                                Percentage(title=_("Critical at or above"), unit=_("percent")),
                            ],
                        ),
                        Tuple(
                            title=_("Absolute DATA allocation"),
                            elements=[
                                Filesize(title=_("Warning at or above")),
                                Filesize(title=_("Critical at or above")),
                            ],
                        ),
                    ],
                ),
            ),
            (
                "overall_allocation",
                Alternative(
                    title=_("OVERALL allocation (cmd: btrfs filesystem usage). Activate Help -> Inline Help for more informations."),
                    help=btrfs_usage_info,
                    elements=[
                        Tuple(
                            title=_("OVERALL allocation relative to OVERALL size"),
                            elements=[
                                Percentage(title=_("Warning at or above"), unit=_("percent")),
                                Percentage(title=_("Critical at or above"), unit=_("percent")),
                            ],
                        ),
                        Tuple(
                            title=_("Absolute OVERALL allocation"),
                            elements=[
                                Filesize(title=_("Warning at or above")),
                                Filesize(title=_("Critical at or above")),
                            ],
                        ),
                    ],
                ),
            ),           
        ]
    )

rule_spec_btrfs_health_ruleset_usage = CheckParameters(
    name="btrfs_health_ruleset_usage",
    topic=Topic.STORAGE,
    parameter_form=_parameter_btrfs_health_usage,
    title=Title("BTRFS Health block group allocation"),
    condition=HostAndItemCondition(item_title=Title("BTRFS Health block group allocation")),
)