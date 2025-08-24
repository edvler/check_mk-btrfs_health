#!/usr/bin/env python3
# Author: Matthias Maderer
# E-Mail: matthias.maderer@web.de
# URL: https://github.com/edvler/check_mk-btrfs_health
# License: GPLv2

from cmk.rulesets.v1 import Title, Help
from cmk.rulesets.v1.form_specs import (
    DefaultValue,
    DictElement,
    Dictionary,
    BooleanChoice
)

from cmk.rulesets.v1.rule_specs import AgentConfig, Topic


def _valuespec_agent_config_btrfs_health_bakery():
    return Dictionary(
        title=Title("Agent Plugin Parameters"),
        elements={
            'deployment': DictElement(
                required=True,
                parameter_form=BooleanChoice(    
                    #migrate=lambda model: _migrate_check_backup(model),
                    title=Title('Deploy BTRFS Health plugin'),                
                    prefill=DefaultValue(True),
                )
            ),
        },
    )


rule_spec_agent_config_btrfs_health_bakery = AgentConfig(
    title=Title("BTRFS Health"),
    topic=Topic.OPERATING_SYSTEM,
    name="btrfs_health_bakery",
    parameter_form=_valuespec_agent_config_btrfs_health_bakery,
)
