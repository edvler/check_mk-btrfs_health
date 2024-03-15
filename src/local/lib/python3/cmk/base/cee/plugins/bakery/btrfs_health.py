#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from typing import Any, List, Dict
from pathlib import Path
from .bakery_api.v1 import Plugin, PluginConfig, register, OS, FileGenerator

def get_btrfs_health_files(conf: Any) -> FileGenerator:
    yield Plugin(
        base_os=OS.LINUX,
        source=Path("btrfs_health"),
        interval=None,
        asynchronous=False,
    )

register.bakery_plugin(
    name="btrfs_health",
    files_function=get_btrfs_health_files,
)
