#!/usr/bin/env python3
"""
Server Monitor - 服务器监控
使用系统命令获取真实数据，无需 psutil
"""

import os
import json
import subprocess
from datetime import datetime
from typing import Dict


class ServerMonitor:
    """服务器监控机器人"""
    
    def __init__(self, config_file: str = "config.json"):
        self.config = self.load_config(config_file)
    
    def load_config(self, config_file: str) -> Dict:
        default_config = {
            "schedule": "09:00",
            "thresholds": {
                "cpu": 80,      # CPU 警告阈值 %
                "memory": 90,   # 内存警告阈值 %
                "disk": 90      # 磁盘警告阈值 %
            },
            "check_items": ["cpu", "memory", "disk", "uptime", "load"]
        }
        
        if os.path.exists(config_file):
            with open(config_file, 'r') as f:
                config = json.load(f)
                default_config.update(config)
        
        return default_config
    
    def run_command(self, cmd: str) -> str:
        """执行系统命令"""
        try:
            result = subprocess.run(cmd, shell=True, capture_output=True, timeout=5)
            return result.stdout.decode('utf-8').strip()
        except Exception as e:
            return f"Error: {e}"
    
    def get_cpu(self) -> Dict:
        """获取 CPU 使用率"""
        # 方法1: vmstat
        output = self.run_command("vmstat 1 1 | awk 'NR==3 {print 100-$15}'")
        if output.replace('.', '').replace('-', '').isdigit():
            return {"value": float(output), "unit": "%"}
        
        # 方法2: top 命令
        output = self.run_command("top -bn1 | grep 'Cpu(s)' | awk '{print $2}'")
        if output and output.replace('.', '').replace('-', '').isdigit():
            return {"value": float(output), "unit": "%"}
        
        return {"value": 0, "unit": "%", "error": "无法获取 CPU 数据"}
    
    def get_memory(self) -> Dict:
        """获取内存使用率"""
        output = self.run_command("free | grep Mem | awk '{print $3/$2 * 100}'")
        if output.replace('.', '').isdigit():
            return {"value": float(output), "unit": "%"}
        
        return {"value": 0, "unit": "%", "error": "无法获取内存数据"}
    
    def get_disk(self) -> Dict:
        """获取磁盘使用率"""
        output = self.run_command("df / | tail -1 | awk '{print $5}'")
        if output.endswith('%'):
            return {"value": float(output[:-1]), "unit": "%"}
        
        return {"value": 0, "unit": "%", "error": "无法获取磁盘数据"}
    
    def get_load(self) -> Dict:
        """获取系统负载"""
        output = self.run_command("cat /proc/loadavg | awk '{print $1, $2, $3}'")
        if output:
            parts = output.split()
            return {"1min": parts[0], "5min": parts[1], "15min": parts[2]}
        return {"1min": "0", "5min": "0", "15min": "0"}
    
    def get_uptime(self) -> Dict:
        """获取运行时间"""
        output = self.run_command("uptime -p 2>/dev/null")
        if not output or "Error" in output:
            output = self.run_command("uptime | awk '{print $3, $4}'")
        return {"uptime": output}
    
    def get_all_status(self) -> Dict:
        """获取所有状态"""
        return {
            "cpu": self.get_cpu(),
            "memory": self.get_memory(),
            "disk": self.get_disk(),
            "load": self.get_load(),
            "uptime": self.get_uptime()
        }
    
    def check_alerts(self, status: Dict) -> list:
        """检查异常项"""
        alerts = []
        thresholds = self.config.get("thresholds", {})
        
        cpu = status.get("cpu", {}).get("value", 0)
        mem = status.get("memory", {}).get("value", 0)
        disk = status.get("disk", {}).get("value", 0)
        
        if cpu > thresholds.get("cpu", 80):
            alerts.append(f"⚠️ CPU 使用率过高: {cpu:.1f}%")
        if mem > thresholds.get("memory", 90):
            alerts.append(f"⚠️ 内存使用率过高: {mem:.1f}%")
        if disk > thresholds.get("disk", 90):
            alerts.append(f"⚠️ 磁盘使用率过高: {disk:.1f}%")
        
        return alerts
    
    def format_message(self) -> str:
        """格式化输出"""
        status = self.get_all_status()
        alerts = self.check_alerts(status)
        
        lines = [f"🖥️ 服务器状态 - {datetime.now().strftime('%Y-%m-%d %H:%M')}\n"]
        lines.append("=" * 40)
        
        # CPU
        cpu = status.get("cpu", {})
        cpu_val = cpu.get("value", 0)
        emoji = "✅" if cpu_val < 50 else "🟡" if cpu_val < 80 else "🔴"
        lines.append(f"{emoji} CPU 使用率: {cpu_val:.1f}%")
        
        # Memory
        mem = status.get("memory", {})
        mem_val = mem.get("value", 0)
        emoji = "✅" if mem_val < 70 else "🟡" if mem_val < 90 else "🔴"
        lines.append(f"{emoji} 内存使用率: {mem_val:.1f}%")
        
        # Disk
        disk = status.get("disk", {})
        disk_val = disk.get("value", 0)
        emoji = "✅" if disk_val < 70 else "🟡" if disk_val < 90 else "🔴"
        lines.append(f"{emoji} 磁盘使用率: {disk_val:.1f}%")
        
        # Load
        load = status.get("load", {})
        lines.append(f"\n📊 系统负载: {load.get('1min', 0)} / {load.get('5min', 0)} / {load.get('15min', 0)}")
        
        # Uptime
        uptime = status.get("uptime", {}).get("uptime", "N/A")
        lines.append(f"⏱️  运行时间: {uptime}")
        
        # Alerts
        if alerts:
            lines.append("\n" + "=" * 40)
            for alert in alerts:
                lines.append(alert)
        
        lines.append("\n#服务器 #监控")
        return '\n'.join(lines)
    
    def run(self) -> str:
        message = self.format_message()
        print(message)
        return message


if __name__ == "__main__":
    monitor = ServerMonitor()
    monitor.run()
