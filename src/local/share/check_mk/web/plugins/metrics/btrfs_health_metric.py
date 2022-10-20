#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Author: Matthias Maderer
# E-Mail: edvler@edvler-blog.de
# URL: https://github.com/edvler/check_mk-btrfs_health
# License: GPLv2

from cmk.gui.i18n import _
from cmk.gui.plugins.metrics.utils import graph_info, metric_info

#examples <RELEASE>\lib\python3\cmk\gui\plugins\metrics

metric_info["bth_device_unallocated"] = {
    "title": _("Block group OVERALL unallocated"),
    "unit": "bytes",
    "color": "#e3fff9",
}

metric_info["bth_device_allocated"] = {
    "title": _("Block group OVERALL used"),
    "unit": "bytes",
    "color": "#00ffc6",
}

#metric_info["bth_allocated_percent"] = {
#    "title": _("Used block groups %"),
#    "unit": "%",
#    "color": "#00ffc6",
#}

metric_info["bth_device_size"] = {
    "title": _("Block group OVERALL size"),
    "unit": "bytes",
    "color": "#006040",
}



metric_info["bth_data_size"] = {
    "title": _("Block groups DATA size"),
    "unit": "bytes",
    "color": "#006040",
}

metric_info["bth_data_used"] = {
    "title": _("Block groups DATA used"),
    "unit": "bytes",
    "color": "#00ffc6",
}



metric_info["bth_metadata_size"] = {
    "title": _("Block groups METADATA size"),
    "unit": "bytes",
    "color": "#006040",
}

metric_info["bth_metadata_used"] = {
    "title": _("Block groups METADATA used"),
    "unit": "bytes",
    "color": "#00ffc6",
}



metric_info["bth_system_size"] = {
    "title": _("Block groups SYSTEM size"),
    "unit": "bytes",
    "color": "#006040",
}

metric_info["bth_system_used"] = {
    "title": _("Block groups SYSTEM used"),
    "unit": "bytes",
    "color": "#00ffc6",
}





graph_info["bth_device_allocated"] = {
    "title": _("block groups OVERALL size and used space"),
    "metrics": [
        ("bth_device_allocated", "area"),
        #("bth_device_size,bth_device_allocated,-#e3fff9", "stack", _("Free block groups")),
        ("bth_device_unallocated", "stack"),
        ("bth_device_size", "line"),
    ],
    #"scalars": [
    #    "bth_device_allocated:warn",
    #    "bth_device_allocated:crit",
    #],
    "range": (0, "bth_device_allocated:max"),
    #"conflicting_metrics": ["bth_device_unallocated"],
}


graph_info["bth_data_size"] = {
    "title": _("block groups for DATA size and used space"),
    "metrics": [
        ("bth_data_used", "area"),
        ("bth_data_size,bth_data_used,-#e3fff9", "stack", _("Block groups DATA unused")),
        ("bth_data_size", "line"),
    ],
    #"scalars": [
    #    "bth_device_allocated:warn",
    #    "bth_device_allocated:crit",
    #],
    "range": (0, "bth_data_size:max"),
    #"conflicting_metrics": ["bth_device_unallocated"],
}


graph_info["bth_metadata_size"] = {
    "title": _("block groups for METADATA size and used space"),
    "metrics": [
        ("bth_metadata_used", "area"),
        ("bth_metadata_size,bth_metadata_used,-#e3fff9", "stack", _("Block groups METADATA unused")),
        ("bth_metadata_size", "line"),
    ],
    #"scalars": [
    #    "bth_device_allocated:warn",
    #    "bth_device_allocated:crit",
    #],
    "range": (0, "bth_metadata_size:max"),
    #"conflicting_metrics": ["bth_device_unallocated"],
}



graph_info["bth_system_size"] = {
    "title": _("block groups for SYSTEM size and used space"),
    "metrics": [
        ("bth_system_used", "area"),
        ("bth_system_size,bth_system_used,-#e3fff9", "stack", _("Block groups SYSTEM unused")),
        ("bth_system_size", "line"),
    ],
    #"scalars": [
    #    "bth_device_allocated:warn",
    #    "bth_device_allocated:crit",
    #],
    "range": (0, "bth_system_size:max"),
    #"conflicting_metrics": ["bth_device_unallocated"],
}




metric_info["bth_write_io_errs"] = {
    "title": _("Write IO errors"),
    "unit": "count",
    "color": "#ff0005",
}

metric_info["bth_read_io_errs"] = {
    "title": _("Read IO errors"),
    "unit": "count",
    "color": "#000099",
}

metric_info["bth_flush_io_errs"] = {
    "title": _("Flush IO errors"),
    "unit": "count",
    "color": "#ff00ff",
}

metric_info["bth_corruption_errs"] = {
    "title": _("Block corruption errors"),
    "unit": "count",
    "color": "#ff9933",
}

metric_info["bth_generation_errs"] = {
    "title": _("Generation errors"),
    "unit": "count",
    "color": "#00ffc6",
}

graph_info["bth_write_io_errs"] = {
    "title": _("Error counter of device"),
    "metrics": [
        ("bth_write_io_errs", "line"),
        ("bth_read_io_errs", "line"),
        ("bth_flush_io_errs", "line"),
        ("bth_corruption_errs", "line"),
        ("bth_generation_errs", "line"),
    ],
    #"scalars": [
    #    "bth_device_allocated:warn",
    #    "bth_device_allocated:crit",
    #],
    #"range": (0, "bth_system_size:max"),
    #"conflicting_metrics": ["bth_device_unallocated"],
}
