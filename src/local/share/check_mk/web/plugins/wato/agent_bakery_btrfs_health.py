#!/usr/bin/env python
# -*- encoding: utf-8; py-indent-offset: 4 -*-

from cmk.gui.i18n import _
from cmk.gui.plugins.wato import (
    HostRulespec,
    rulespec_registry,
)

try:
  from cmk.gui.cee.plugins.wato.agent_bakery.rulespecs.utils import RulespecGroupMonitoringAgentsAgentPlugins
  #only CEE!
  rulespec_registry.register(
    HostRulespec(
        group=RulespecGroupMonitoringAgentsAgentPlugins,
        name="agent_config:btrfs_health",
        valuespec=_valuespec_agent_config_btrfs_health,
  ))

except ModuleNotFoundError:
  # RAW edition
  pass
    
from cmk.gui.valuespec import (
    Alternative,
    FixedValue,
)

def _valuespec_agent_config_btrfs_health():
    return Alternative(
        title = _("btrfs health (Linux)"),
        help = _("This will deploy the agent plugin <tt>btrfs_health</tt> "
                 "for checking the health of mounted btrfs file systems."),
        style = "dropdown",
        elements=[
            FixedValue(value = True, title=_("Deploy the btrfs health plugin"), totext=_("(enabled)")),
            FixedValue(value = None, title=_("Do not deploy the btrfs health plugin"), totext=_("(disabled)")),
        ],
    )

rulespec_registry.register(
    HostRulespec(
        group=RulespecGroupMonitoringAgentsAgentPlugins,
        name="agent_config:btrfs_health",
        valuespec=_valuespec_agent_config_btrfs_health,
    ))
