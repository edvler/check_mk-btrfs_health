#!/usr/bin/env python3
# Author: Matthias Maderer
# E-Mail: matthias.maderer@web.de
# URL: https://github.com/edvler/check_mk-btrfs_health
# License: GPLv2

#example: \lib\python3\cmk\gui\plugins\wato\check_parameters\memory.py

from cmk.rulesets.v1 import (
    Help,
    Label,
    Title,
)
from cmk.rulesets.v1.form_specs import (
    BooleanChoice,
    DefaultValue,
    DictElement,
    DictGroup,
    Dictionary,
    Integer,
    InputHint,
    LevelDirection,
    List,
    migrate_to_upper_integer_levels,
    migrate_to_upper_float_levels,
    SimpleLevels,
    String,
    TimeMagnitude,
    SIMagnitude,
    IECMagnitude,
    TimeSpan,
    validators,
    DataSize,
    Percentage,
    CascadingSingleChoice,
    CascadingSingleChoiceElement,
    FixedValue,
    MultipleChoice,
    MultipleChoiceElement
    )
from cmk.rulesets.v1.rule_specs import (
    AgentConfig,
    CheckParameters,
    DiscoveryParameters,
    HostAndItemCondition,
    Topic,
)


#Migrations: https://github.com/HeinleinSupport/check_mk_extensions/blob/cmk2.3/sslcertificates/rulesets/sslcertificates.py#L55

def _parameter_btrfs_health_scrub():
    return Dictionary(
        elements = {
            'scrub_age': DictElement(
                parameter_form=SimpleLevels(
                    title = Title('Scrub Age'),
                    help_text = Help('Time period after which the check switches to warn/crit'),
                    migrate = lambda model: migrate_to_upper_float_levels(model),
                    level_direction = LevelDirection.UPPER,
                    form_spec_template = TimeSpan(
                        displayed_magnitudes=[TimeMagnitude.DAY, TimeMagnitude.HOUR],
                    ),
                    prefill_fixed_levels = InputHint(
                        value=(150 * 86400.0, 180 * 86400.0),
                    )
                )
            ),
            'scrub_runtime': DictElement(
                parameter_form=SimpleLevels(
                    title = Title('Scrub runtime'),
                    help_text = Help('Time period after which the check switches to warn/crit'),
                    migrate = lambda model: migrate_to_upper_float_levels(model),
                    level_direction = LevelDirection.UPPER,
                    form_spec_template = TimeSpan(
                        displayed_magnitudes=[TimeMagnitude.DAY, TimeMagnitude.HOUR],
                    ),
                    prefill_fixed_levels = InputHint(
                        value=(0.5 * 86400.0, 1 * 86400.0),
                    )
                )
            )
        }
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
        elements = {
            'write_io_errs': DictElement(
                parameter_form=SimpleLevels(
                    title = Title('Write IO errors (write_io_errs) for devices used by btrfs volume (cmd: btrfs device stats).'),
                    migrate = lambda model: migrate_to_upper_integer_levels(model),
                    form_spec_template = Integer(),
                    level_direction = LevelDirection.UPPER,
                    prefill_fixed_levels = InputHint(
                        value=(1, 1)
                    )
                )			 
            ),

            'read_io_errs': DictElement(
                parameter_form=SimpleLevels(
                    title = Title('Read IO errors (read_io_errs) for devices used by btrfs volume (cmd: btrfs device stats).'),
                    migrate = lambda model: migrate_to_upper_integer_levels(model),
                    form_spec_template = Integer(),
                    level_direction = LevelDirection.UPPER,
                    prefill_fixed_levels = InputHint(
                        value=(1, 1)
                    )
                )			 
            ),

            'flush_io_errs': DictElement(
                parameter_form=SimpleLevels(
                    title = Title('Flush IO errors (flush_io_errs) for devices used by btrfs volume (cmd: btrfs device stats).'),
                    migrate = lambda model: migrate_to_upper_integer_levels(model),
                    form_spec_template = Integer(),
                    level_direction = LevelDirection.UPPER,
                    prefill_fixed_levels = InputHint(
                        value=(1, 1)
                    )
                )			 
            ),

            'corruption_errs': DictElement(
                parameter_form=SimpleLevels(
                    title = Title('Corruption IO errors (corruption_errs) for devices used by btrfs volume (cmd: btrfs device stats).'),
                    migrate = lambda model: migrate_to_upper_integer_levels(model),
                    form_spec_template = Integer(),
                    level_direction = LevelDirection.UPPER,
                    prefill_fixed_levels = InputHint(
                        value=(1, 1)
                    )
                )			 
            ),

            'generation_errs': DictElement(
                parameter_form=SimpleLevels(
                    title = Title('Generation IO errors (generation_errs) for devices used by btrfs volume (cmd: btrfs device stats).'),
                    migrate = lambda model: migrate_to_upper_integer_levels(model),
                    form_spec_template = Integer(),
                    level_direction = LevelDirection.UPPER,
                    prefill_fixed_levels = InputHint(
                        value=(1, 1)
                    )
                )			 
            )
        }
    )

rule_spec_btrfs_health_ruleset_dstats = CheckParameters(
    name="btrfs_health_ruleset_dstats",
    topic=Topic.STORAGE,
    parameter_form=_parameter_btrfs_health_dstats,
    title=Title("BTRFS Health device stats"),
    condition=HostAndItemCondition(item_title=Title("BTRFS Health device stats")),
)





















# btrfs_usage_info=_(
#                        "The BTRFS filesystem stores data in a internal structure called block groups. " 
#                        "More informations could be found in the manpage: man mkfs.btrfs -> section BLOCK GROUPS, CHUNKS, RAID. "
#                        "From the manpage: "
#                        "-- A typical size of metadata block group is 256MiB (filesystem smaller than 50GiB) and 1GiB (larger than 50GiB), for data it’s 1GiB. The system block group size is a few megabytes. -- "
#                        "The command 'btrfs filesystem usage ' displays the allocated sizes. "
#                        "As long as 'Device unallocated' are greater than 1GB new block groups can be always allocated and there is no problem. "
#                        "But There are some situations that are cirtical: "
#                        "1. No 'Device unallocated' space is avaliable (or less than 1GB) AND Metadata is running out of space "
#                        "2. No 'Device unallocated' space is avaliable (or less than 1GB) AND System is running out of space "
#                        "If no 'Device unallocated' space is avaliable two fixes availiable: "
#                        "- extend the disk "
#                        "- OR man btrfs-balance --> See examples for parameter -dusage or -musage "
#                    )


def migrate_metadata_intelligent(model):
    #with open('/tmp/output.txt', 'w') as filehandle:
        #filehandle.write(str(type(model)) + '\n')
        
        #for key in model.keys():
        #    filehandle.write(str(key))
       # filehandle.write(str(model) + '\n')
        #filehandle.write(str(model[1]) + '\n')
    #    filehandle.write(str(model[1]) + '\n')
   #     filehandle.write(str(model[0]))
       #filehandle.write(' '.join(model))

    # check if model is a dict or a tuple/list
    # tuple = old check_mk format
    # dict = new check_mk format
    if isinstance(model, dict):
        return {
            "metadata_combined_blocks_free": model["metadata_combined_blocks_free"],
            "metadata_combined_metadata_relative_used": model["metadata_combined_metadata_relative_used"]
        }
    else:
        return {
            "metadata_combined_blocks_free": model[0], # First value in Tuple = minimum blocks free
            "metadata_combined_metadata_relative_used": model[1] # Second value in Tuple = percentage of metadata used
        }        


def _parameter_btrfs_health_usage():
    return Dictionary(
        elements = {
            "metadata_intelligent": DictElement (
                parameter_form=Dictionary(
                    title=Title("METADATA combined: If unnallocated blocks below the given limit AND METADATA allocation above the given percent, this check changes to crit. Activate Help -> Inline Help for more informations."),
                    #help_text=Help("If unallocated blocks below the given limit AND metadata allocation above the given percent, this check changes to crit. Activate Help -> Inline Help for more informations."),
                    migrate = lambda model: migrate_metadata_intelligent(model),
                    elements = {
                        'metadata_combined_blocks_free': DictElement(
                            required=True,
                            parameter_form=DataSize(
                                title = Title('Minimum unallocated block groups'),
                                displayed_magnitudes=[IECMagnitude.GIBI, IECMagnitude.MEBI],
                            )
                        ),
                                    
                        'metadata_combined_metadata_relative_used': DictElement(
                            required=True,
                            parameter_form=Percentage(
                                title = Title('Relative used METADATA'),
                            )
                        )
                    }             
                )
            ),

            'metadata_allocation': DictElement(
                parameter_form=CascadingSingleChoice(
                    title=Title('METADATA allocation (cmd: btrfs filesystem usage). Activate Help -> Inline Help for more informations.'),
                    elements=[
                        CascadingSingleChoiceElement(
                            name="metadata_allocation_percentage",          
                            title=Title("Relative"),
                            parameter_form=SimpleLevels(
                                form_spec_template = Percentage(),
                                level_direction = LevelDirection.UPPER,
                                prefill_fixed_levels = InputHint(
                                    value=(80, 90)  # Warning at or above 80%, Critical at or above 90%
                                )
                            )
                        ),
                        CascadingSingleChoiceElement(
                            name="metadata_allocation_absolute",
                            title = Title('Absolute'),
                            parameter_form=SimpleLevels(
                                form_spec_template = DataSize(
                                    displayed_magnitudes=[IECMagnitude.GIBI, IECMagnitude.MEBI],
                                ),
                                level_direction = LevelDirection.UPPER,
                                prefill_fixed_levels = InputHint(
                                    value=(1024*1024*1024*1, 1024*1024*1024*2)
                                )
                            )
                        )                      
                    ]
                )
            ),

            'system_allocation': DictElement(
                parameter_form=CascadingSingleChoice(
                    title=Title('SYSTEM allocation (cmd: btrfs filesystem usage). Activate Help -> Inline Help for more informations.'),
                    elements=[
                        CascadingSingleChoiceElement(
                            name="system_allocation_percentage",
                            title=Title('Relative'),
                            parameter_form=SimpleLevels(
                                form_spec_template = Percentage(),
                                level_direction = LevelDirection.UPPER,
                                prefill_fixed_levels = InputHint(
                                    value=(80, 90)  # Warning at or above 80%, Critical at or above 90%
                                )
                            )
                        ),
                        CascadingSingleChoiceElement(
                            name="system_allocation_absolute",
                            title=Title('Absolute'),
                            parameter_form=SimpleLevels(
                                form_spec_template = DataSize(
                                    displayed_magnitudes=[IECMagnitude.GIBI, IECMagnitude.MEBI],
                                ),
                                level_direction = LevelDirection.UPPER,
                                prefill_fixed_levels = InputHint(
                                    value=(1024*1024*1024*1, 1024*1024*1024*2)
                                )
                            )
                        )                      
                    ]
                )
            ),

            'data_allocation': DictElement(
                parameter_form=CascadingSingleChoice(
                    title=Title('DATA allocation (cmd: btrfs filesystem usage). Activate Help -> Inline Help for more informations.'),
                    elements=[
                        CascadingSingleChoiceElement(
                            name="data_allocation_percentage",
                            title = Title('Relative'),
                            parameter_form=SimpleLevels(
                                form_spec_template = Percentage(),
                                level_direction = LevelDirection.UPPER,
                                prefill_fixed_levels = InputHint(
                                    value=(80, 90)  # Warning at or above 80%, Critical at or above 90%
                                )
                            )
                        ),
                        CascadingSingleChoiceElement(
                            name="data_allocation_absolute",
                            title = Title('Absolute'),
                            parameter_form=SimpleLevels(
                                form_spec_template = DataSize(
                                    displayed_magnitudes=[IECMagnitude.GIBI, IECMagnitude.MEBI],
                                ),
                                level_direction = LevelDirection.UPPER,
                                prefill_fixed_levels = InputHint(
                                    value=(1024*1024*1024*1, 1024*1024*1024*2)
                                )
                            )
                        )                    
                    ]
                )
            ),

            'overall_allocation': DictElement(
                parameter_form=CascadingSingleChoice(
                    title=Title('Absolute DATA allocation (cmd: btrfs filesystem usage). Activate Help -> Inline Help for more informations.'),
                    elements=[
                        CascadingSingleChoiceElement(
                            name="overall_allocation_percentage",
                            title = Title('Relative'),           
                            parameter_form=SimpleLevels(
                                form_spec_template = Percentage(),
                                level_direction = LevelDirection.UPPER,
                                prefill_fixed_levels = InputHint(
                                    value=(80, 90)  # Warning at or above 80%, Critical at or above 90%
                                )
                            )
                        ),
                        CascadingSingleChoiceElement(
                            name="overall_allocation_absolute",
                            title = Title('Absolute'),            
                            parameter_form=SimpleLevels(
                                form_spec_template = DataSize(
                                    displayed_magnitudes=[IECMagnitude.GIBI, IECMagnitude.MEBI],
                                ),
                                level_direction = LevelDirection.UPPER,
                                prefill_fixed_levels = InputHint(
                                    value=(1024*1024*1024*1, 1024*1024*1024*2)
                                )
                            )
                        )                        
                    ]
                )
            )
        }
    )

rule_spec_btrfs_health_ruleset_usage = CheckParameters(
    name="btrfs_health_ruleset_usage",
    topic=Topic.STORAGE,
    parameter_form=_parameter_btrfs_health_usage,
    title=Title("BTRFS Health block group allocation"),
    condition=HostAndItemCondition(item_title=Title("BTRFS Health block group allocation")),
)

    #return Dictionary(
    #    elements = {
            # "test": DictElement (
            #     parameter_form=MultipleChoice(
            #         show_toggle_all=True,
            #         title=Title("Test"),
            #         elements=[
            #             MultipleChoiceElement(
            #                 name="test1",
            #                 title=Title("Test 1"),
            #                 #parameter_form=FixedValue(value=None),
            #             ),
            #             MultipleChoiceElement(
            #                 name="test2",
            #                 title=Title("Test 2"),
            #                 #parameter_form=FixedValue(value=None),
            #             ),
            #         ],
            #         #prefill=DefaultValue(value="test1")

            #     )
            # ),
    
            # "proto": DictElement(
            #     parameter_form=CascadingSingleChoice(
            #         title=Title("Protocol"),
            #         #prefill=DefaultValue("https"),
            #         elements=[
            #             CascadingSingleChoiceElement(
            #                 name="tcp4",
            #                 title=Title("TCP v4"),
            #                 parameter_form=FixedValue(value=None),
            #             ),
            #             CascadingSingleChoiceElement(
            #                 name="tcp6",
            #                 title=Title("TCP v6"),
            #                 parameter_form=FixedValue(value=None),
            #             ),
            #             CascadingSingleChoiceElement(
            #                 name="udp4",
            #                 title=Title("UDP v4"),
            #                 parameter_form=FixedValue(value=None),
            #             ),
            #             CascadingSingleChoiceElement(
            #                 name="udp6",
            #                 title=Title("UDP v6"),
            #                 parameter_form=FixedValue(value=None),
            #             ),
            #         ],
            #     ),
            # ),

            #'metadata_intelligent': DictElement(
            #    #title = Title("METADATA combined: If unnallocated blocks below the given limit AND METADATA allocation above the given percent, this check changes to crit. Activate Help -> Inline Help for more informations."),
            #    parameter_form=SimpleLevels(
            #        title = Title('Minimum unallocated block groups'),
            #        migrate = lambda model: migrate_metadata_intelligent(model,"size"),
            #        level_direction = LevelDirection.LOWER,
            #        form_spec_template = DataSize(
            #            displayed_magnitudes=[SIMagnitude.GIGA, SIMagnitude.MEGA],
            #        ),                    
            #        prefill_fixed_levels = InputHint(
            #            value=(1, 1)
            #        )
            #    )
            #),

    #     required_keys=[],
    #     elements = [   
    #         ('metadata_intelligent': DictElement(
    #              title = Title("METADATA combined: If unnallocated blocks below the given limit AND METADATA allocation above the given percent, this check changes to crit. Activate Help -> Inline Help for more informations."),
    #              help=btrfs_usage_info,
    #              elements = [
    #                 Filesize(title = Title("Minimum unallocated block groups")),
    #                 Percentage(title = Title("METADATA allocation in percent"), unit=_("percent"), default_value=(75.0)),
    #              ]
    #         )
    #       ),             
    #         (
    #             "metadata_allocation",
    #             Alternative(
    #                 title = Title("METADATA allocation (cmd: btrfs filesystem usage). Activate Help -> Inline Help for more informations."),
                    
    #                 help=btrfs_usage_info,
    #                 elements=[
    #                     Tuple(
    #                         title = Title("METADATA allocation relative to METADATA size"),
    #                         elements=[
    #                             Percentage(title = Title("Warning at or above"), unit=_("percent")),
    #                             Percentage(title = Title("Critical at or above"), unit=_("percent")),
    #                         ],
    #                     ),
    #                     Tuple(
    #                         title = Title("Absolute METADATA allocation"),
    #                         elements=[
    #                             Filesize(title = Title("Warning at or above")),
    #                             Filesize(title = Title("Critical at or above")),
    #                         ],
    #                     ),
    #                 ],
    #             ),
    #         ),
    #         (
    #             "system_allocation",
    #             Alternative(
    #                 title = Title("SYSTEM allocation (cmd: btrfs filesystem usage). Activate Help -> Inline Help for more informations."),
    #                 default_value=(70.0,80.0),
                    
    #                 help=btrfs_usage_info,
    #                 elements=[
    #                     Tuple(
    #                         title = Title("SYSTEM allocation relative to SYSTEM size"),
    #                         elements=[
    #                             Percentage(title = Title("Warning at or above"), unit=_("percent")),
    #                             Percentage(title = Title("Critical at or above"), unit=_("percent")),
    #                         ],
    #                     ),
    #                     Tuple(
    #                         title = Title("Absolute SYSTEM allocation"),
    #                         elements=[
    #                             Filesize(title = Title("Warning at or above")),
    #                             Filesize(title = Title("Critical at or above")),
    #                         ],
    #                     ),
    #                 ],
    #             ),
    #         ),
    #         (
    #             "data_allocation",
    #             Alternative(
    #                 title = Title("DATA allocation (cmd: btrfs filesystem usage). Activate Help -> Inline Help for more informations."),
    #                 help=btrfs_usage_info,
    #                 elements=[
    #                     Tuple(
    #                         title = Title("DATA allocation relative to DATA size"),
    #                         elements=[
    #                             Percentage(title = Title("Warning at or above"), unit=_("percent")),
    #                             Percentage(title = Title("Critical at or above"), unit=_("percent")),
    #                         ],
    #                     ),
    #                     Tuple(
    #                         title = Title("Absolute DATA allocation"),
    #                         elements=[
    #                             Filesize(title = Title("Warning at or above")),
    #                             Filesize(title = Title("Critical at or above")),
    #                         ],
    #                     ),
    #                 ],
    #             ),
    #         ),
    #         (
    #             "overall_allocation",
    #             Alternative(
    #                 title = Title("OVERALL allocation (cmd: btrfs filesystem usage). Activate Help -> Inline Help for more informations."),
    #                 help=btrfs_usage_info,
    #                 elements=[
    #                     Tuple(
    #                         title = Title("OVERALL allocation relative to OVERALL size"),
    #                         elements=[
    #                             Percentage(title = Title("Warning at or above"), unit=_("percent")),
    #                             Percentage(title = Title("Critical at or above"), unit=_("percent")),
    #                         ],
    #                     ),
    #                     Tuple(
    #                         title = Title("Absolute OVERALL allocation"),
    #                         elements=[
    #                             Filesize(title = Title("Warning at or above")),
    #                             Filesize(title = Title("Critical at or above")),
    #                         ],
    #                     ),
    #                 ],
    #             ),
    #         ),           
    #     ]
    # )


