#!/usr/bin/env python3

#Author: Matthias Maderer
#E-Mail: matthias.maderer@web.de
#URL: https://github.com/edvler/check_mk-btrfs_health
#License: GPLv2

#only CEE!
try:
    from pathlib import Path
    from typing import TypedDict
    from .bakery_api.v1 import Plugin, PluginConfig, register, OS, FileGenerator

    class BtrfsHealthBakeryConfig(TypedDict, total=False):
        deployment: bool

    def get_btrfs_health_files(conf: BtrfsHealthBakeryConfig) -> FileGenerator:
        deployment = conf["deployment"]

        if deployment == False:
            return

        yield Plugin(
            base_os=OS.LINUX,
            source=Path("btrfs_health")
        )

    register.bakery_plugin(
        name="btrfs_health_bakery",
        files_function=get_btrfs_health_files,
    )
except ModuleNotFoundError:
    pass