# Systemd Journal 配置指南

## 概述

systemd journal 是现代 Linux 系统的核心日志管理系统，提供了统一的日志收集、存储和查询功能。本指南详细介绍如何配置和优化 systemd journal。

## 1. 配置文件位置

### 主要配置文件
```bash
/etc/systemd/journald.conf          # 主配置文件
/etc/systemd/journald.conf.d/       # 配置片段目录
/run/log/journal/                   # 运行时日志存储
/var/log/journal/                   # 持久化日志存储
```

### 查看当前配置
```bash
# 查看当前 journald 配置
sudo systemctl show systemd-journald

# 查看配置文件
cat /etc/systemd/journald.conf

# 查看 journald 状态
sudo systemctl status systemd-journald
```

## 2. 核心配置参数

### 存储配置
```ini
[Journal]
# 存储模式
Storage=persistent          # persistent, volatile, auto, none

# 日志文件大小限制
SystemMaxUse=4G            # 系统日志最大占用空间
SystemKeepFree=1G          # 系统保留空闲空间
SystemMaxFileSize=128M     # 单个日志文件最大大小
SystemMaxFiles=100         # 最大日志文件数量

# 运行时日志配置
RuntimeMaxUse=1G           # 运行时日志最大占用空间
RuntimeKeepFree=512M       # 运行时保留空闲空间
RuntimeMaxFileSize=64M     # 运行时单个文件最大大小
RuntimeMaxFiles=50         # 运行时最大文件数量
```

### 时间和轮转配置
```ini
[Journal]
# 日志保留时间
MaxRetentionSec=1month     # 最大保留时间
MaxFileSec=1week          # 单个文件最大时间跨度

# 同步配置
SyncIntervalSec=5m        # 同步间隔
RateLimitIntervalSec=30s  # 速率限制间隔
RateLimitBurst=10000      # 速率限制突发数量
```

### 转发和压缩配置
```ini
[Journal]
# 转发到 syslog
ForwardToSyslog=yes       # 转发到传统 syslog
ForwardToKMsg=no          # 转发到内核消息
ForwardToConsole=no       # 转发到控制台
ForwardToWall=yes         # 转发到所有登录用户

# 压缩配置
Compress=yes              # 启用压缩
Seal=yes                  # 启用密封（防篡改）
SplitMode=uid             # 分割模式：uid, login, none
```

## 3. 实际配置示例

### 生产环境配置
```bash
# 创建生产环境配置
sudo mkdir -p /etc/systemd/journald.conf.d/

cat << 'EOF' | sudo tee /etc/systemd/journald.conf.d/production.conf
[Journal]
# 存储配置
Storage=persistent
SystemMaxUse=8G
SystemKeepFree=2G
SystemMaxFileSize=256M
SystemMaxFiles=200

# 保留时间
MaxRetentionSec=3month
MaxFileSec=1week

# 性能优化
SyncIntervalSec=1m
Compress=yes
Seal=yes

# 转发配置
ForwardToSyslog=no
ForwardToKMsg=no
ForwardToConsole=no
ForwardToWall=no

# 速率限制
RateLimitIntervalSec=10s
RateLimitBurst=5000
EOF
```

### 开发环境配置
```bash
cat << 'EOF' | sudo tee /etc/systemd/journald.conf.d/development.conf
[Journal]
# 存储配置
Storage=persistent
SystemMaxUse=2G
SystemKeepFree=500M
SystemMaxFileSize=64M
SystemMaxFiles=50

# 保留时间
MaxRetentionSec=1week
MaxFileSec=1day

# 调试配置
ForwardToSyslog=yes
ForwardToConsole=yes
Compress=no

# 更宽松的速率限制
RateLimitIntervalSec=30s
RateLimitBurst=20000
EOF
```

## 4. 日志查询和管理

### 基本查询命令
```bash
# 查看所有日志
journalctl

# 查看特定服务日志
journalctl -u nginx
journalctl -u systemd-journald

# 实时跟踪日志
journalctl -f
journalctl -u nginx -f

# 查看特定时间范围
journalctl --since "2025-01-27 10:00:00"
journalctl --since "1 hour ago"
journalctl --until "2025-01-27 18:00:00"

# 查看特定优先级
journalctl -p err          # 错误级别
journalctl -p warning      # 警告级别
journalctl -p info         # 信息级别
```

### 高级查询
```bash
# 按进程 ID 查询
journalctl _PID=1234

# 按用户查询
journalctl _UID=1000

# 按可执行文件查询
journalctl _COMM=nginx

# 组合查询
journalctl -u nginx --since "1 hour ago" -p err

# 输出格式化
journalctl -o json         # JSON 格式
journalctl -o json-pretty  # 格式化 JSON
journalctl -o cat          # 仅消息内容
journalctl -o short-iso    # ISO 时间格式
```

### 日志统计和分析
```bash
# 查看日志占用空间
journalctl --disk-usage

# 查看日志文件列表
ls -lh /var/log/journal/*/

# 验证日志完整性
journalctl --verify

# 清理日志
sudo journalctl --vacuum-time=1month    # 清理1个月前的日志
sudo journalctl --vacuum-size=1G        # 保留最新1G日志
sudo journalctl --vacuum-files=10       # 保留最新10个文件
```

## 5. 性能优化

### 存储优化
```bash
# 检查当前存储使用
journalctl --disk-usage

# 优化配置示例
cat << 'EOF' | sudo tee /etc/systemd/journald.conf.d/performance.conf
[Journal]
# 减少同步频率提高性能
SyncIntervalSec=5m

# 启用压缩节省空间
Compress=yes

# 合理设置文件大小
SystemMaxFileSize=128M
RuntimeMaxFileSize=64M

# 设置合理的速率限制
RateLimitIntervalSec=10s
RateLimitBurst=1000
EOF
```

### 内存优化
```bash
# 限制运行时日志内存使用
RuntimeMaxUse=512M
RuntimeKeepFree=256M

# 对于内存受限环境
RuntimeMaxUse=128M
RuntimeKeepFree=64M
```

## 6. 监控和告警

### 创建监控脚本
```bash
cat << 'EOF' > /usr/local/bin/journal-monitor.sh
#!/bin/bash

# Journal 监控脚本
LOG_FILE="/var/log/journal-monitor.log"
THRESHOLD_SIZE="5G"
THRESHOLD_PERCENT=80

echo "=== Journal Monitor - $(date) ===" >> $LOG_FILE

# 检查磁盘使用
DISK_USAGE=$(journalctl --disk-usage | grep -o '[0-9.]*[KMGT]')
echo "Current journal disk usage: $DISK_USAGE" >> $LOG_FILE

# 检查错误日志数量
ERROR_COUNT=$(journalctl -p err --since "1 hour ago" | wc -l)
echo "Errors in last hour: $ERROR_COUNT" >> $LOG_FILE

# 检查 journald 服务状态
if ! systemctl is-active --quiet systemd-journald; then
    echo "WARNING: systemd-journald is not active!" >> $LOG_FILE
fi

# 检查日志完整性
if ! journalctl --verify >/dev/null 2>&1; then
    echo "WARNING: Journal verification failed!" >> $LOG_FILE
fi

# 清理旧日志（如果超过阈值）
USAGE_BYTES=$(journalctl --disk-usage | grep -o '[0-9]*' | head -1)
if [ "$USAGE_BYTES" -gt 5368709120 ]; then  # 5GB in bytes
    echo "Cleaning old journals due to size threshold" >> $LOG_FILE
    journalctl --vacuum-size=4G
fi

echo "Monitor check completed" >> $LOG_FILE
echo "" >> $LOG_FILE
EOF

chmod +x /usr/local/bin/journal-monitor.sh
```

### 设置定时监控
```bash
# 添加到 crontab
echo "*/30 * * * * /usr/local/bin/journal-monitor.sh" | sudo crontab -

# 或创建 systemd timer
cat << 'EOF' | sudo tee /etc/systemd/system/journal-monitor.service
[Unit]
Description=Journal Monitor Service
After=systemd-journald.service

[Service]
Type=oneshot
ExecStart=/usr/local/bin/journal-monitor.sh
User=root
EOF

cat << 'EOF' | sudo tee /etc/systemd/system/journal-monitor.timer
[Unit]
Description=Run Journal Monitor every 30 minutes
Requires=journal-monitor.service

[Timer]
OnCalendar=*:0/30
Persistent=true

[Install]
WantedBy=timers.target
EOF

# 启用 timer
sudo systemctl enable journal-monitor.timer
sudo systemctl start journal-monitor.timer
```

## 7. 与容器化环境集成

### Docker 日志配置
```bash
# Docker daemon 配置 journald 驱动
cat << 'EOF' | sudo tee /etc/docker/daemon.json
{
  "log-driver": "journald",
  "log-opts": {
    "tag": "docker/{{.Name}}"
  }
}
EOF

# 重启 Docker
sudo systemctl restart docker
```

### Kubernetes 集成
```yaml
# 在 Kubernetes 中收集 journal 日志
apiVersion: apps/v1
kind: DaemonSet
metadata:
  name: journal-collector
spec:
  selector:
    matchLabels:
      name: journal-collector
  template:
    metadata:
      labels:
        name: journal-collector
    spec:
      containers:
      - name: journal-collector
        image: fluent/fluent-bit:latest
        volumeMounts:
        - name: varlog
          mountPath: /var/log
          readOnly: true
        - name: journal
          mountPath: /run/log/journal
          readOnly: true
        env:
        - name: FLUENT_CONF
          value: |
            [INPUT]
                Name systemd
                Path /run/log/journal
                Tag journal.*
            
            [OUTPUT]
                Name stdout
                Match *
      volumes:
      - name: varlog
        hostPath:
          path: /var/log
      - name: journal
        hostPath:
          path: /run/log/journal
      hostNetwork: true
      hostPID: true
```

## 8. 故障排除

### 常见问题诊断
```bash
# 检查 journald 服务状态
sudo systemctl status systemd-journald

# 查看 journald 配置
sudo systemd-analyze cat-config systemd/journald.conf

# 检查日志完整性
sudo journalctl --verify

# 重建日志索引
sudo systemctl stop systemd-journald
sudo rm -rf /var/log/journal/*/system.journal*
sudo systemctl start systemd-journald
```

### 性能问题排查
```bash
# 检查 I/O 使用
sudo iotop -p $(pgrep systemd-journal)

# 检查内存使用
ps aux | grep systemd-journal

# 检查文件描述符使用
sudo lsof -p $(pgrep systemd-journal)

# 分析日志写入速度
journalctl --since "1 minute ago" | wc -l
```

## 9. 安全配置

### 访问控制
```bash
# 设置日志文件权限
sudo chmod 640 /var/log/journal/*/*
sudo chown root:systemd-journal /var/log/journal/*/*

# 创建专用用户组
sudo groupadd journal-readers
sudo usermod -a -G journal-readers username

# 配置 sudo 规则
echo "%journal-readers ALL=(ALL) NOPASSWD: /bin/journalctl" | sudo tee /etc/sudoers.d/journal-readers
```

### 日志密封
```bash
# 启用日志密封（防篡改）
cat << 'EOF' | sudo tee /etc/systemd/journald.conf.d/security.conf
[Journal]
Seal=yes
Compress=yes
SplitMode=uid
EOF

# 重启服务应用配置
sudo systemctl restart systemd-journald
```

## 10. 最佳实践

### 1. 容量规划
```bash
# 根据日志产生速度计算存储需求
# 示例：每天 100MB 日志，保留 30 天
SystemMaxUse=4G    # 100MB * 30 天 + 缓冲
MaxRetentionSec=30day
```

### 2. 性能调优
```bash
# 高负载环境配置
SyncIntervalSec=30s      # 减少同步频率
RateLimitBurst=50000     # 增加突发限制
Compress=yes             # 启用压缩
```

### 3. 监控指标
```bash
# 关键监控指标
- 日志磁盘使用量
- 日志写入速率
- journald 服务状态
- 日志完整性验证结果
```

## 11. 相关命令参考

```bash
# 服务管理
sudo systemctl restart systemd-journald    # 重启 journald
sudo systemctl reload systemd-journald     # 重载配置

# 配置管理
sudo systemd-analyze cat-config systemd/journald.conf  # 查看有效配置
sudo journalctl --flush                     # 刷新日志到磁盘

# 维护命令
sudo journalctl --rotate                    # 轮转日志文件
sudo journalctl --sync                      # 同步日志到磁盘
sudo journalctl --relinquish-var           # 释放 /var 分区
```

---

**创建时间**: 2025-01-27
**修改时间**: 2025-01-27

*本指南提供了 systemd journal 的完整配置和管理方法，适用于云原生环境下的日志管理和监控需求。*