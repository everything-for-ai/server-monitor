# Server Monitor / 服务器监控

<div class="tabs">
<details open>
<summary><span>🇨🇳 中文 (默认)</span></summary>

## 🖥️ 服务器监控

实时监控服务器资源状态

### 功能特点
- ✅ **真实数据** - 使用系统命令获取
- 📊 **监控项** - CPU / 内存 / 磁盘 / 负载 / 运行时间
- ⚠️ **异常告警** - 超过阈值时提醒
- ⏰ **定时推送** - 每天 09:00 自动推送

### 监控指标

| 指标 | 说明 | 阈值 |
|------|------|------|
| CPU | CPU 使用率 | 80% |
| Memory | 内存使用率 | 90% |
| Disk | 磁盘使用率 | 90% |
| Load | 系统负载 (1/5/15min) | - |
| Uptime | 运行时间 | - |

### 配置

编辑 `config.json`：

```json
{
    "schedule": "09:00",
    "thresholds": {
        "cpu": 80,
        "memory": 90,
        "disk": 90
    }
}
```

### 快速开始
```bash
cd server-monitor
python monitor.py
```

</details>
<details>
<summary><span>🇺🇸 English</span></summary>

## 🖥️ Server Monitor

Real-time server resource monitoring

### Features
- ✅ **Real Data** - Via system commands
- 📊 **Metrics** - CPU / Memory / Disk / Load / Uptime
- ⚠️ **Alerts** - Threshold warnings
- ⏰ **Scheduled** - Daily at 09:00

### Metrics

| Metric | Description | Threshold |
|--------|-------------|-----------|
| CPU | CPU usage | 80% |
| Memory | Memory usage | 90% |
| Disk | Disk usage | 90% |
| Load | System load | - |
| Uptime | Uptime | - |

### Quick Start
```bash
cd server-monitor
python monitor.py
```

</details>
</div>

---

## 数据来源

| 指标 | 命令 |
|------|------|
| CPU | vmstat |
| Memory | free |
| Disk | df |
| Load | /proc/loadavg |
| Uptime | uptime |

---

*无需安装 psutil，使用系统命令*
