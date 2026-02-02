#!/usr/bin/env python3
"""Server Monitor"""

import os, json


class ServerMonitor:
    def __init__(self, config_file="config.json"):
        self.config = self.load_config(config_file)
    
    def load_config(self, config_file):
        default_config = {"thresholds": {"cpu": 80, "memory": 80, "disk": 90}}
        if os.path.exists(config_file):
            with open(config_file) as f:
                default_config.update(json.load(f))
        return default_config
    
    def get_status(self):
        try:
            import psutil
            cpu = psutil.cpu_percent()
            mem = psutil.virtual_memory()
            disk = psutil.disk_usage("/")
            return f"CPU: {cpu}%, Memory: {mem.percent}%, Disk: {disk.percent}%"
        except:
            return "CPU: 50%, Memory: 60%, Disk: 70% (mock data)"
    
    def run(self):
        print(self.get_status())


if __name__ == "__main__":
    monitor = ServerMonitor()
    monitor.run()
