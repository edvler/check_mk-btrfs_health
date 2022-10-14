from cmk.gui.plugins.metrics import perfometer_info

#example: \lib\python3\cmk\gui\plugins\metrics\perfometers.py

perfometer_info.append(
    {
        "type": "linear",
        "segments": ["bth_device_allocated"],
        "total": "bth_device_size",
    }
)