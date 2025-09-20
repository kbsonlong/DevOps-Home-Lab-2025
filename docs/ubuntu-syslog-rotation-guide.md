# Ubuntu 22.04 Syslog 轮转配置指南

## 概述

Ubuntu 22.04 使用 `logrotate` 工具来管理系统日志的轮转，包括 syslog。本指南将详细介绍如何配置和管理 syslog 轮转。

## 1. 默认配置文件位置

### 主配置文件
```bash
/etc/logrotate.conf          # 主配置文件
/etc/logrotate.d/            # 各服务的轮转配置目录
/etc/logrotate.d/rsyslog     # rsyslog 专用配置
```

### 日志文件位置
```bash
/var/log/syslog              # 主系统日志
/var/log/auth.log            # 认证日志
/var/log/kern.log            # 内核日志
/var/log/daemon.log          # 守护进程日志
```

## 2. 查看当前 syslog 轮转配置

```bash
# 查看 rsyslog 轮转配置
cat /etc/logrotate.d/rsyslog

# 查看主配置文件
cat /etc/logrotate.conf

# 测试轮转配置（不实际执行）
sudo logrotate -d /etc/logrotate.d/rsyslog

# 强制执行轮转（用于测试）
sudo logrotate -f /etc/logrotate.d/rsyslog
```

## 3. 默认 rsyslog 轮转配置

Ubuntu 22.04 默认的 `/etc/logrotate.d/rsyslog` 配置：

```bash
/var/log/syslog
{
    rotate 7
    daily
    missingok
    notifempty
    delaycompress
    compress
    postrotate
        /usr/lib/rsyslog/rsyslog-rotate
    endscript
}

/var/log/mail.info
/var/log/mail.warn
/var/log/mail.err
/var/log/mail.log
/var/log/daemon.log
/var/log/kern.log
/var/log/auth.log
/var/log/user.log
/var/log/lpr.log
/var/log/cron.log
/var/log/debug
/var/log/messages
{
    rotate 4
    weekly
    missingok
    notifempty
    compress
    delaycompress
    sharedscripts
    postrotate
        /usr/lib/rsyslog/rsyslog-rotate
    endscript
}
```

## 4. 配置参数说明

### 轮转频率
- `daily` - 每天轮转
- `weekly` - 每周轮转
- `monthly` - 每月轮转
- `yearly` - 每年轮转

### 保留数量
- `rotate 7` - 保留 7 个轮转文件

### 压缩选项
- `compress` - 压缩轮转的日志文件
- `delaycompress` - 延迟压缩（下次轮转时压缩）
- `nocompress` - 不压缩

### 其他选项
- `missingok` - 如果日志文件不存在，不报错
- `notifempty` - 如果日志文件为空，不轮转
- `create 640 syslog adm` - 创建新日志文件的权限和所有者
- `sharedscripts` - 多个文件共享脚本

## 5. 自定义 syslog 轮转配置

### 创建自定义配置
```bash
# 备份原配置
sudo cp /etc/logrotate.d/rsyslog /etc/logrotate.d/rsyslog.backup

# 编辑配置
sudo nano /etc/logrotate.d/rsyslog
```

### 示例：更频繁的轮转配置
```bash
/var/log/syslog
{
    rotate 30          # 保留30个文件
    daily              # 每天轮转
    missingok
    notifempty
    compress           # 立即压缩
    create 640 syslog adm
    postrotate
        /usr/lib/rsyslog/rsyslog-rotate
    endscript
}
```

### 示例：基于大小的轮转
```bash
/var/log/syslog
{
    size 100M          # 当文件达到100MB时轮转
    rotate 10
    compress
    missingok
    notifempty
    create 640 syslog adm
    postrotate
        /usr/lib/rsyslog/rsyslog-rotate
    endscript
}
```

## 6. 管理和监控

### 查看轮转状态
```bash
# 查看 logrotate 状态文件
cat /var/lib/logrotate/status

# 查看最近的轮转日志
sudo journalctl -u logrotate

# 手动测试轮转
sudo logrotate -d /etc/logrotate.conf
```

### 强制执行轮转
```bash
# 强制轮转所有日志
sudo logrotate -f /etc/logrotate.conf

# 强制轮转特定配置
sudo logrotate -f /etc/logrotate.d/rsyslog
```

### 查看当前日志文件大小
```bash
# 查看 syslog 相关文件大小
ls -lh /var/log/syslog*
ls -lh /var/log/*.log

# 查看总日志目录大小
du -sh /var/log/
```

## 7. 故障排除

### 常见问题

#### 1. 轮转不工作
```bash
# 检查 logrotate 服务状态
systemctl status logrotate.timer

# 检查配置语法
sudo logrotate -d /etc/logrotate.d/rsyslog

# 查看错误日志
sudo journalctl -u logrotate
```

#### 2. 权限问题
```bash
# 检查日志文件权限
ls -l /var/log/syslog

# 修复权限
sudo chown syslog:adm /var/log/syslog
sudo chmod 640 /var/log/syslog
```

#### 3. 磁盘空间不足
```bash
# 清理旧的压缩日志
sudo find /var/log -name "*.gz" -mtime +30 -delete

# 手动清理大日志文件
sudo truncate -s 0 /var/log/syslog
```

## 8. 最佳实践

### 1. 监控磁盘使用
```bash
# 设置磁盘使用监控
df -h /var/log
```

### 2. 定期检查配置
```bash
# 创建检查脚本
cat > /usr/local/bin/check-logrotate.sh << 'EOF'
#!/bin/bash
echo "=== Logrotate Status Check ==="
echo "Last run status:"
tail -5 /var/lib/logrotate/status

echo -e "\n=== Disk Usage ==="
df -h /var/log

echo -e "\n=== Large Log Files ==="
find /var/log -type f -size +100M -exec ls -lh {} \;

echo -e "\n=== Configuration Test ==="
logrotate -d /etc/logrotate.conf > /dev/null 2>&1
if [ $? -eq 0 ]; then
    echo "Configuration is valid"
else
    echo "Configuration has errors"
fi
EOF

chmod +x /usr/local/bin/check-logrotate.sh
```

### 3. 自动化监控
```bash
# 添加到 crontab
echo "0 6 * * * /usr/local/bin/check-logrotate.sh" | sudo crontab -
```

## 9. 与容器化环境集成

在 Kubernetes 环境中，可以通过以下方式管理日志轮转：

### DaemonSet 配置示例
```yaml
apiVersion: apps/v1
kind: DaemonSet
metadata:
  name: logrotate
spec:
  selector:
    matchLabels:
      name: logrotate
  template:
    metadata:
      labels:
        name: logrotate
    spec:
      containers:
      - name: logrotate
        image: ubuntu:22.04
        command: ["/bin/bash"]
        args: ["-c", "while true; do logrotate /etc/logrotate.conf; sleep 3600; done"]
        volumeMounts:
        - name: varlog
          mountPath: /var/log
        - name: logrotate-config
          mountPath: /etc/logrotate.d
      volumes:
      - name: varlog
        hostPath:
          path: /var/log
      - name: logrotate-config
        configMap:
          name: logrotate-config
```

## 10. 相关命令参考

```bash
# 系统日志管理
sudo systemctl status rsyslog          # 检查 rsyslog 状态
sudo systemctl restart rsyslog         # 重启 rsyslog
sudo journalctl -f                     # 实时查看系统日志

# 日志轮转管理
sudo logrotate -v /etc/logrotate.conf  # 详细模式执行
sudo logrotate -s /var/lib/logrotate/status /etc/logrotate.conf  # 指定状态文件

# 日志查看
tail -f /var/log/syslog                # 实时查看 syslog
zcat /var/log/syslog.1.gz              # 查看压缩的轮转日志
```

---

**创建时间**: 2025-01-27
**修改时间**: 2025-01-27

*本指南提供了 Ubuntu 22.04 中 syslog 轮转的完整配置和管理方法，适用于系统管理员和 SRE 工程师。*