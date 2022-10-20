#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Author: Matthias Maderer
# E-Mail: edvler@edvler-blog.de
# URL: https://github.com/edvler/check_mk-btrfs_health
# License: GPLv2

from cmk.gui.plugins.metrics import perfometer_info

#example: \lib\python3\cmk\gui\plugins\metrics\perfometers.py

perfometer_info.append(
    {
        "type": "linear",
        "segments": ["bth_device_allocated"],
        "total": "bth_device_size",
    }
)