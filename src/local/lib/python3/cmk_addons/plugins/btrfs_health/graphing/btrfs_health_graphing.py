#!/usr/bin/env python3
# Author: Matthias Maderer
# E-Mail: matthias.maderer@web.de
# URL: https://github.com/edvler/check_mk-btrfs_health
# License: GPLv2

from cmk.graphing.v1.perfometers import (
    Closed,
    FocusRange,
    Open,
    Perfometer,
    Stacked
)
from cmk.graphing.v1 import (
    Title
)
from cmk.graphing.v1.graphs import (
    Graph, 
    MinimalRange
)
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
    Difference,
    Unit,
    WarningOf,
)


UNIT_BYTES = Unit(IECNotation("B"), StrictPrecision(2))
UNIT_INT = Unit(DecimalNotation(""), StrictPrecision(0))

metric_bth_device_unallocated = Metric(
    name="bth_device_unallocated",
    title=Title("Block group OVERALL unallocated"),
    unit=UNIT_BYTES,
    color=Color.BLUE,
)


metric_bth_device_allocated = Metric(
    name="bth_device_allocated",
    title=Title("Block group OVERALL used"),
    unit=UNIT_BYTES,
    color=Color.RED,
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
    color=Color.RED,
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
    color=Color.RED,
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
    color=Color.RED,
)




perfometer_btrfs_stacked = Stacked(
    name="perfometer_btrfs_stacked",
    upper=Perfometer(
        name="perfometer_btrfs_overall",
        focus_range=FocusRange(
                                Closed(0), 
                                Closed("bth_device_size")
                            ),
        segments=[
            "bth_device_allocated"
        ],
    ),
    lower=Perfometer(
        name="perfometer_btrfs_metadata",
        focus_range=FocusRange(
                                Closed(0), 
                                Closed("bth_metadata_size")
                            ),
        segments=[
            "bth_metadata_used"           
        ],
    ),
)


#Example https://github.com/Checkmk/checkmk/blob/master/cmk/plugins/memory/graphing/mem.py
graph_bth_overall = Graph(
    name="graph_bth_overall",
    title=Title("block groups OVERALL size and used space"),
    minimal_range=MinimalRange(0,"bth_device_size:max"),
    compound_lines=(
        "bth_device_allocated",
        "bth_device_unallocated"      
    ),
    simple_lines=(
        "bth_device_size",
    )
)


graph_bth_data = Graph(
    name="graph_bth_data",
    title=Title("block groups DATA size and used space"),
    minimal_range=MinimalRange(0,"bth_data_size:max"),
    compound_lines=(
        "bth_data_used",
        Difference(
            title=Title("Block groups DATA free"),
            color=Color.BLUE,
            minuend="bth_data_size",
            subtrahend="bth_data_used"
        )     
    ),
    simple_lines=(
        "bth_data_size",
    )
)

graph_bth_metadata = Graph(
    name="graph_bth_metadata",
    title=Title("block groups METADATA size and used space"),
    minimal_range=MinimalRange(0,"bth_metadata_size:max"),
    compound_lines=(
        "bth_metadata_used",
        Difference(
            title=Title("Block groups METADATA free"),
            color=Color.BLUE,
            minuend="bth_metadata_size",
            subtrahend="bth_metadata_used"
        )     
    ),
    simple_lines=(
        "bth_metadata_size",       
    )
)

graph_bth_system = Graph(
    name="graph_bth_system",
    title=Title("block groups SYSTEM size and used space"),
    minimal_range=MinimalRange(0,"bth_system_size:max"),
    compound_lines=(
        "bth_system_used",
        Difference(
            title=Title("Block groups SYSTEM free"),
            color=Color.BLUE,
            minuend="bth_system_size",
            subtrahend="bth_system_used"
        )     
    ),
    simple_lines=(
        "bth_system_size",
    )
)










metric_bth_write_io_errs = Metric(
    name="bth_write_io_errs",
    title=Title("btrfs device stats - write IO errors"),
    unit=UNIT_INT,
    color=Color.RED,
)
metric_bth_read_io_errs = Metric(
    name="bth_read_io_errs",
    title=Title("btrfs device stats - read_io_errs"),
    unit=UNIT_INT,
    color=Color.PURPLE,
)
metric_bth_flush_io_errs = Metric(
    name="bth_flush_io_errs",
    title=Title("btrfs device stats - flush_io_errs"),
    unit=UNIT_INT,
    color=Color.YELLOW,
)
metric_bth_corruption_errs = Metric(
    name="bth_corruption_errs",
    title=Title("btrfs device stats - corruption_errs"),
    unit=UNIT_INT,
    color=Color.ORANGE,
)
metric_bth_generation_errs = Metric(
    name="bth_generation_errs",
    title=Title("btrfs device stats - generation_errs"),
    unit=UNIT_INT,
    color=Color.BLUE,
)

perfometer_btrfs_device_stats = Perfometer(
        name="perfometer_btrfs_device_stats",
        focus_range=FocusRange(
                                Closed(0), 
                                Open(10)
                            ),
        segments=[
            "bth_write_io_errs",
            "bth_read_io_errs",
            "bth_flush_io_errs",
            "bth_corruption_errs",
            "bth_generation_errs"
        ],
)

graph_bth_device_stats = Graph(
    name="graph_bth_device_stats",
    title=Title("Device stats"),
    simple_lines=(
        "bth_write_io_errs",
        "bth_read_io_errs",
        "bth_flush_io_errs",
        "bth_corruption_errs",
        "bth_generation_errs",
        WarningOf("bth_write_io_errs"),
        CriticalOf("bth_write_io_errs"),
        WarningOf("bth_read_io_errs"),
        CriticalOf("bth_read_io_errs"),
        WarningOf("bth_flush_io_errs"),
        CriticalOf("bth_flush_io_errs"),
        WarningOf("bth_corruption_errs"),
        CriticalOf("bth_corruption_errs"),
        WarningOf("bth_generation_errs"),
        CriticalOf("bth_generation_errs"),         
    )
)
