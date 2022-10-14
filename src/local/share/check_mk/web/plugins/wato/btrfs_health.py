#!/usr/bin/env python3
# -*- coding: utf-8 -*-


# Author: Matthias Maderer
# E-Mail: edvler@edvler-blog.de
# URL: https://github.com/edvler/check_mk_urbackup-check
# License: GPLv2

#example: \lib\python3\cmk\gui\plugins\wato\check_parameters\memory.py

from cmk.gui.i18n import _
from cmk.gui.valuespec import (
    Dictionary,
    DropdownChoice,
    Tuple,
    TextAscii,
    Age,
    Integer
)

from cmk.gui.plugins.wato import (
    CheckParameterRulespecWithItem,
    rulespec_registry,
    RulespecGroupCheckParametersStorage
)

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


rulespec_registry.register(
    CheckParameterRulespecWithItem(
        check_group_name="btrfs_health_ruleset_scrub",
        group=RulespecGroupCheckParametersStorage,
        item_spec=lambda: TextAscii(title=_('BTRFS Health scrub status'), ),
        #item_spec=_itemspec_urbackup_check,
        match_type='dict',
        parameter_valuespec=_parameter_btrfs_health_scrub,
        title=lambda: _("BTRFS Health scrub status"),
    ))

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

rulespec_registry.register(
    CheckParameterRulespecWithItem(
        check_group_name="btrfs_health_ruleset_dstats",
        group=RulespecGroupCheckParametersStorage,
        item_spec=lambda: TextAscii(title=_('BTRFS Health device stats'), ),
        #item_spec=_itemspec_urbackup_check,
        match_type='dict',
        parameter_valuespec=_parameter_btrfs_health_dstats,
        title=lambda: _("BTRFS Health device stats"),
    ))


btrfs_usage_info=_(
                        "The BTRFS filesystem stores data in a internal structure called block groups. " 
                        "More informations could be found with: man mkfs.btrfs -> section BLOCK GROUPS, CHUNKS, RAID. "
                        "From the manpage: "
                        "-- A typical size of metadata block group is 256MiB (filesystem smaller than 50GiB) and 1GiB (larger than 50GiB), for data it’s 1GiB. The system block group size is a few megabytes. -- "
                        "The command 'btrfs filesystem usage ' displays the allocated sizes. "
                        "As long as 'Device unallocated' are greater than 1GB new block groups can be always allocated and there is no problem. "
                        "But There are some situations that are cirtical: "
                        "1. No 'Device unallocated' space is avaliable (or less than 1GB) AND Metadata is running out of space "
                        "2. No 'Device unallocated' space is avaliable (or less than 1GB) AND System is running out of space "
                        "For this reason the default warn/crit values for METADATA and SYSTEM are 70%/80%. "
                        "If no 'Device unallocated' space is avaliable two resultions availiable: "
                        "- extend the disk "
                        "OR man btrfs-balance --> See examples for parameter -dusage or -musage "
                    )

def _parameter_btrfs_health_usage():
    return Dictionary(
        required_keys=[],
        elements = [   
            (
                "metadata_allocation",
                Alternative(
                    title=_("Metadata allocation (cmd: btrfs filesystem usage). Activate Help -> Inline Help for more informations."),
                    default_value=(70.0,80.0),
                    
                    help=btrfs_usage_info,
                    elements=[
                        Tuple(
                            title=_("Metadata allocation relative to Metadata size"),
                            elements=[
                                Percentage(title=_("Warning at or above"), unit=_("percent")),
                                Percentage(title=_("Critical at or above"), unit=_("percent")),
                            ],
                        ),
                        Tuple(
                            title=_("Absolute Metadata allocation"),
                            elements=[
                                Integer(title=_("Warning at or above"), unit=_("MiB")),
                                Integer(title=_("Critical at or above"), unit=_("MiB")),
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
                                Integer(title=_("Warning at or above"), unit=_("MiB")),
                                Integer(title=_("Critical at or above"), unit=_("MiB")),
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
                                Integer(title=_("Warning at or above"), unit=_("MiB")),
                                Integer(title=_("Critical at or above"), unit=_("MiB")),
                            ],
                        ),
                    ],
                ),
            ),
            (
                "overall_allocation",
                Alternative(
                    title=_("Overall allocation (cmd: btrfs filesystem usage). Activate Help -> Inline Help for more informations."),
                    help=btrfs_usage_info,
                    elements=[
                        Tuple(
                            title=_("Overall allocation relative to Overall size"),
                            elements=[
                                Percentage(title=_("Warning at or above"), unit=_("percent")),
                                Percentage(title=_("Critical at or above"), unit=_("percent")),
                            ],
                        ),
                        Tuple(
                            title=_("Absolute Overall allocation"),
                            elements=[
                                Integer(title=_("Warning at or above"), unit=_("MiB")),
                                Integer(title=_("Critical at or above"), unit=_("MiB")),
                            ],
                        ),
                    ],
                ),
            ),                                 
        ]
    )

rulespec_registry.register(
    CheckParameterRulespecWithItem(
        check_group_name="btrfs_health_ruleset_usage",
        group=RulespecGroupCheckParametersStorage,
        item_spec=lambda: TextAscii(title=_('BTRFS Health block group allocation'), ),
        #item_spec=_itemspec_urbackup_check,
        match_type='dict',
        parameter_valuespec=_parameter_btrfs_health_usage,
        title=lambda: _("BTRFS Health block group allocation"),
    ))

