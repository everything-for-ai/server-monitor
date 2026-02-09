#!/usr/bin/env python3
"""
Server Monitor - 服务器监控
支持：CPU/内存/磁盘监控、异常告警、飞书发送
"""

import os
import json
import subprocess
import requests
from datetime import datetime
from pathlib import Path
from typing import Dict, List

# 配置
CONFIG_PATH = Path.home() / ".openclaw" / "openclaw.json"
SECRET_PATH = Path.home() / ".openclaw" / "secrets" / "feishu_app_secret"
RECEIVER_ID = "ou_a44cdd1c2064d3c9c22242b61ff8b926"


def load_config():
    default = {
        "thresholds": {"cpu": 80, "memory": 90, "disk": 90},
        "check_items": ["cpu", "memory", "disk", "uptime", "load"]
    }
    if Path("config.json").exists():
        with open("config.json") as f:
            default.update(json.load(f))
    return default


def load_openclaw_config():
    if CONFIG_PATH.exists():
        with open(CONFIG_PATH) as f:
            return json.load(f)
    return {}


def load_secret():
    if SECRET_PATH.exists():
        with open(SECRET_PATH) as f:
            return f.read().strip()
    return None


def run_command(cmd: str) -> str:
    """执行系统命令"""
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, timeout=5)
        return result.stdout.decode('utf-8').strip()
    except Exception as e:
        return f"Error: {e}"


def get_cpu() -> Dict:
    """获取 CPU 使用率"""
    output = run_command("vmstat 1 1 | awk 'NR==3 {print 100-$15}'")
    if output.replace('.', '').replace('-', '').isdigit():
        return {"value": float(output), "unit": "%"}
    
    output = run_command("top -bn1 | grep 'Cpu(s)' | awk '{print $2}'")
    if output and output.replace('.', '').replace('-', '').isdigit():
        return {"value": float(output), "unit": "%"}
    
    return {"value": 0, "unit": "%", "error": "无法获取"}


def get_memory() -> Dict:
    """获取内存使用率"""
    output = run_command("free | grep Mem | awk '{print $3/$2 * 100}'")
    if output.replace('.', '').isdigit():
        return {"value": float(output), "unit": "%"}
    return {"value": 0, "unit": "%", "error": "无法获取"}


def get_disk() -> Dict:
    """获取磁盘使用率"""
    output = run_command("df / | tail -1 | awk '{print $5}'")
    if output.endswith('%'):
        return {"value": float(output[:-1]), "unit": "%"}
    return {"value": 0, "unit": "%", "error": "无法获取"}


def get_load() -> Dict:
    """获取系统负载"""
    output = run_command("cat /proc/loadavg | awk '{print $1, $2, $3}'")
    if output:
        parts = output.split()
        return {"1min": parts[0], "5min": parts[1], "15min": parts[2]}
    return {"1min": "0", "5min": "0", "15min": "0"}


def get_uptime() -> Dict:
    """获取运行时间"""
    output = run_command("uptime -p 2>/dev/null")
    if not output or "Error" in output:
        output = run_command("uptime | awk '{print $3, $4}'")
    return {"uptime": output}


def get_all_status() -> Dict:
    """获取所有状态"""
    return {
        "cpu": get_cpu(),
        "memory": get_memory(),
        "disk": get_disk(),
        "load": get_load(),
        "uptime": get_uptime()
    }


def check_alerts(status: Dict, config: Dict) -> List[str]:
    """检查异常项"""
    alerts = []
    thresholds = config.get("thresholds", {})
    
    cpu = status.get("cpu", {}).get("value", 0)
    mem = status.get("memory", {}).get("value", 0)
    disk = status.get("disk", {}).get("value", 0)
    
    if cpu > thresholds.get("cpu", 80):
        alerts.append(f"⚠️ CPU 过载: {cpu:.1f}% (>80%)")
    if mem > thresholds.get("memory", 90):
        alerts.append(f"⚠️ 内存告警: {mem:.1f}% (>90%)")
    if disk > thresholds.get("disk", 90):
        alerts.append(f"⚠️ 磁盘不足: {disk:.1f}% (>90%)")
    
    return alerts


def format_message(status: Dict, alerts: List[str], config: Dict) -> str:
    """格式化消息"""
    message = [f"🖥️ **服务器监控** - {datetime.now().strftime('%m/%d %H:%M')}\n"]
    
    # CPU
    cpu = status.get("cpu", {})
    cpu_val = cpu.get("value", 0)
    emoji = "✅" if cpu_val < 50 else "🟡" if cpu_val < 80 else "🔴"
    message.append(f"{emoji} **CPU** {cpu_val:.1f}%")
    
    # Memory
    mem = status.get("memory", {})
    mem_val = mem.get("value", 0)
    emoji = "✅" if mem_val < 70 else "🟡" if mem_val < 90 else "🔴"
    message.append(f"{emoji} **内存** {mem_val:.1f}%")
    
    # Disk
    disk = status.get("disk", {})
    disk_val = disk.get("value", 0)
    emoji = "✅" if disk_val < 70 else "🟡" if disk_val < 90 else "🔴"
    message.append(f"{emoji} **磁盘** {disk_val:.1f}%")
    
    # Load
    load = status.get("load", {})
    message.append("")
    message.append(f"📊 **负载:** {load.get('1min', 0)} | {load.get('5min', 0)} | {load.get('15min', 0)}")
    
    # Uptime
    uptime = status.get("uptime", {}).get("uptime", "N/A")
    message.append(f"⏱️  **运行时:** {uptime}")
    
    # Alerts
    if alerts:
        message.append("")
        message.append("=" * 40)
        message.append("🚨 **告警:**")
        for alert in alerts:
            message.append(f"  {alert}")
    else:
        message.append("")
        message.append("✅ **状态正常**")
    
    message.append("")
    message.append("#服务器 #监控")
    
    return "\n".join(message)


def get_tenant_access_token(app_id, app_secret):
    """获取 tenant_access_token"""
    url = "https://open.larksuite.com/open-apis/auth/v3/tenant_access_token/internal"
    resp = requests.post(url, json={"app_id": app_id, "app_secret": app_secret})
    result = resp.json()
    return result.get("tenant_access_token") if result.get("code") == 0 else None


def send_to_feishu(token, receiver_id, content):
    """发送飞书消息"""
    url = "https://open.larksuite.com/open-apis/im/v1/messages"
    params = {"receive_id_type": "open_id"}
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    data = {
        "receive_id": receiver_id,
        "msg_type": "text",
        "content": json.dumps({"text": content})
    }
    resp = requests.post(url, params=params, headers=headers, json=data)
    return resp.json().get("code") == 0


def main():
    print(f"\n{'='*50}")
    print(f"🖥️ 服务器监控 - {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    print(f"{'='*50}\n")
    
    # 加载配置
    config = load_config()
    
    # 获取状态
    status = get_all_status()
    alerts = check_alerts(status, config)
    
    # 格式化消息
    message = format_message(status, alerts, config)
    print(message)
    
    # 发送到飞书（仅告警或每小时）
    app_config = load_openclaw_config()
    app_id = app_config.get("channels", {}).get("feishu", {}).get("appId")
    app_secret = load_secret()
    
    # 检查是否需要发送
    should_send = len(alerts) > 0  # 有告警时发送
    should_send = should_send or datetime.now().minute < 5  # 每小时前5分钟发送
    
    if app_id and app_secret and should_send:
        token = get_tenant_access_token(app_id, app_secret)
        if token and send_to_feishu(token, RECEIVER_ID, message):
            print("\n✅ 已发送至飞书！")
        else:
            print("\n⚠️ 飞书发送失败")
    elif not app_id or not app_secret:
        print("\n💡 未配置飞书，仅显示本地")


if __name__ == "__main__":
    main()
