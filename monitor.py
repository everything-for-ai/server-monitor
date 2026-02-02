#!/usr/bin/env python3
"""
Server Monitor - Alert on CPU, memory, disk, and services
"""

import os
import json
import smtplib
import psutil
from datetime import datetime
from typing import Dict, List


class ServerMonitor:
    def __init__(self, config_file: str = "config.json"):
        self.config = self.load_config(config_file)
    
    def load_config(self, config_file: str) -> Dict:
        default_config = {
            "thresholds": {
                "cpu": 80,
                "memory": 80,
                "disk": 90
            },
            "alert_channels": ["feishu"],
            "recipients": []
        }
        
        if os.path.exists(config_file):
            with open(config_file, 'r') as f:
                default_config.update(json.load(f))
        
        return default_config
    
    def check_cpu(self) -> Dict:
        return {
            "percent": psutil.cpu_percent(interval=1),
            "alert": psutil.cpu_percent() > self.config["thresholds"]["cpu"]
        }
    
    def check_memory(self) -> Dict:
        mem = psutil.virtual_memory()
        return {
            "percent": mem.percent,
            "used_gb": round(mem.used / 1024**3, 2),
            "total_gb": round(mem.total / 1024**3, 2),
            "alert": mem.percent > self.config["thresholds"]["memory"]
        }
    
    def check_disk(self) -> Dict:
        disk = psutil.disk_usage("/")
        return {
            "percent": disk.percent,
            "used_gb": round(disk.used / 1024**3, 2),
            "total_gb": round(disk.total / 1024**3, 2),
            "alert": disk.percent > self.config["thresholds"]["disk"]
        }
    
    def get_status(self) -> str:
        cpu = self.check_cpu()
        mem = self.check_memory()
        disk = self.check_disk()
        
        alerts = []
        if cpu["alert"]: alerts.append("CPU 过高")
        if mem["alert"]: alerts.append("内存不足")
        if disk["alert"]: alerts.append("磁盘空间不足")
        
        status = "✅ 正常" if not alerts else "⚠️ 警告: " + ", ".join(alerts)
        
        return f"""
🖥️ 服务器监控 - {datetime.now().strftime('%H:%M')}

CPU: {cpu['percent']:.1f}%
内存: {mem['percent']:.1f}% ({mem['used_gb']}GB / {mem['total_gb']}GB)
磁盘: {disk['percent']:.1f}% ({disk['used_gb']}GB / {disk['total_gb']}GB)

状态: {status}
        """.strip()
    
    def run(self):
        print(self.get_status())
        return self.get_status()


if __name__ == "__main__":
    monitor = ServerMonitor()
    monitor.run()
