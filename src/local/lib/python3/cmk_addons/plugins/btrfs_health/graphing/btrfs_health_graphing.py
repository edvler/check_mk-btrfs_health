#!/usr/bin/env python3
# Author: Matthias Maderer
# E-Mail: matthias.maderer@web.de
# URL: https://github.com/edvler/check_mk-btrfs_health
# License: GPLv2

from cmk.graphing.v1.perfometers import Closed, FocusRange, Open, Perfometer

perfometer_btrfs_allocated = Perfometer(
    name="btrfs_device_allocated",
    focus_range=FocusRange(Closed(0), Closed("bth_device_allocated")),
    segments=["bth_device_allocated"],
)



from cmk.graphing.v1 import Title
from cmk.graphing.v1.graphs import Graph, MinimalRange
from cmk.graphing.v1.metrics import (
    Color,
    Constant,
    CriticalOf,
    DecimalNotation,
    Fraction,
    IECNotation,
    MaximumOf,
    Metric,
    Product,
    StrictPrecision,
    Sum,
    Unit,
    WarningOf,
)





metric_bth_device_unallocated = Metric(
    name="bth_device_unallocated",
    title=Title("Block group OVERALL unallocated"),
    unit=UNIT_BYTES,
    color=Color.GREEN,
)


metric_bth_device_allocated = Metric(
    name="bth_device_allocated",
    title=Title("Block group OVERALL used"),
    unit=UNIT_BYTES,
    color=Color.BLUE,
)

metric_bth_device_size = Metric(
    name="bth_device_size",
    title=Title("Block group OVERALL size"),
    unit=UNIT_BYTES,
    color=Color.GREEN,
)

metric_bth_data_size = Metric(
    name="bth_data_size",
    title=Title("Block groups DATA size"),
    unit=UNIT_BYTES,
    color=Color.GREEN,
)

metric_bth_data_used = Metric(
    name="bth_data_used",
    title=Title("Block groups DATA used"),
    unit=UNIT_BYTES,
    color=Color.LIGHT_GREEN,
)

metric_bth_metadata_size = Metric(
    name="bth_metadata_size",
    title=Title("Block groups METADATA size"),
    unit=UNIT_BYTES,
    color=Color.GREEN,
)

metric_bth_metadata_used = Metric(
    name="bth_metadata_used",
    title=Title("Block groups METADATA used"),
    unit=UNIT_BYTES,
    color=Color.LIGHT_GREEN,
)

metric_bth_system_size = Metric(
    name="bth_system_size",
    title=Title("Block groups SYSTEM size"),
    unit=UNIT_BYTES,
    color=Color.GREEN,
)

metric_bth_system_used = Metric(
    name="bth_system_used",
    title=Title("Block groups SYSTEM used"),
    unit=UNIT_BYTES,
    color=Color.LIGHT_GREEN,
)


#https://github.com/Checkmk/checkmk/blob/master/cmk/plugins/memory/graphing/mem.py
graph_bth_device_allocated = Graph(
    name="bth_device_allocated",
    title=Title("block groups OVERALL size and used space"),
    minimal_range=MinimalRange(0,"bth_device_allocated:max"),
    compound_lines=(
        "bth_device_allocated",
        "bth_device_unallocated",
        "bth_device_size",
        "mem_lnx_cached",
        "mem_lnx_buffers",
        "swap_cached",
    )
)


