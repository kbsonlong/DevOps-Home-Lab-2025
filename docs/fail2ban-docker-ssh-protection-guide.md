# Fail2ban 容器特权模式 SSH 防护指南

## 概述

本指南详细介绍如何使用 Docker 容器运行 fail2ban，通过特权模式访问宿主机系统，实现对 SSH 服务的安全防护。这种方案既保持了容器化的便利性，又能有效保护宿主机免受暴力破解攻击。

## 1. 架构设计

### 工作原理
```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   SSH 攻击者    │───▶│   宿主机 SSH     │───▶│  系统日志文件   │
└─────────────────┘    └──────────────────┘    └─────────────────┘
                                                        │
                                                        ▼
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│  iptables 规则  │◀───│ fail2ban 容器    │◀───│   日志监控      │
└─────────────────┘    │  (特权模式)      │    └─────────────────┘
                       └──────────────────┘
```

### 核心特性
- **容器化部署**: 隔离 fail2ban 环境，便于管理和更新
- **特权模式**: 访问宿主机网络和 iptables
- **日志监控**: 实时监控 SSH 登录日志
- **自动封禁**: 基于规则自动封禁恶意 IP
- **持久化配置**: 配置和数据持久化存储

## 2. Docker Compose 配置

### 基础配置文件
```yaml
# docker-compose.fail2ban.yml
version: '3.8'

services:
  fail2ban:
    image: crazymax/fail2ban:latest
    container_name: fail2ban-ssh-protection
    restart: unless-stopped
    
    # 特权模式配置
    privileged: true
    network_mode: host
    cap_add:
      - NET_ADMIN
      - NET_RAW
    
    # 环境变量
    environment:
      - TZ=Asia/Shanghai
      - F2B_LOG_LEVEL=INFO
      - F2B_LOG_TARGET=STDOUT
      - SSMTP_HOST=smtp.gmail.com
      - SSMTP_PORT=587
      - SSMTP_HOSTNAME=your-hostname
      - SSMTP_USER=your-email@gmail.com
      - SSMTP_PASSWORD=your-app-password
      - SSMTP_TLS=YES
    
    # 卷挂载
    volumes:
      # fail2ban 配置
      - ./fail2ban/config:/data
      - ./fail2ban/logs:/var/log/fail2ban
      
      # 宿主机日志文件 (只读)
      - /var/log/auth.log:/var/log/auth.log:ro
      - /var/log/syslog:/var/log/syslog:ro
      - /var/log/journal:/var/log/journal:ro
      
      # 系统信息 (只读)
      - /etc/localtime:/etc/localtime:ro
      - /etc/timezone:/etc/timezone:ro
    
    # 健康检查
    healthcheck:
      test: ["CMD", "fail2ban-client", "status"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 30s
    
    # 标签
    labels:
      - "com.example.service=fail2ban"
      - "com.example.description=SSH Protection Service"

# 网络配置
networks:
  default:
    external: true
    name: host
```

### 高级配置文件
```yaml
# docker-compose.fail2ban-advanced.yml
version: '3.8'

services:
  fail2ban:
    image: crazymax/fail2ban:latest
    container_name: fail2ban-advanced
    restart: unless-stopped
    
    privileged: true
    network_mode: host
    cap_add:
      - NET_ADMIN
      - NET_RAW
      - SYS_ADMIN
    
    environment:
      - TZ=Asia/Shanghai
      - F2B_LOG_LEVEL=DEBUG
      - F2B_LOG_TARGET=/var/log/fail2ban/fail2ban.log
      - F2B_IPTABLES_CHAIN=f2b-sshd
      - F2B_MAX_RETRY=3
      - F2B_BAN_TIME=3600
      - F2B_FIND_TIME=600
    
    volumes:
      # 配置文件
      - ./fail2ban/jail.local:/etc/fail2ban/jail.local:ro
      - ./fail2ban/filter.d:/etc/fail2ban/filter.d:ro
      - ./fail2ban/action.d:/etc/fail2ban/action.d:ro
      
      # 数据目录
      - ./fail2ban/data:/data
      - ./fail2ban/logs:/var/log/fail2ban
      
      # 宿主机日志
      - /var/log:/host/var/log:ro
      - /run/log/journal:/run/log/journal:ro
      
      # 系统文件
      - /etc/localtime:/etc/localtime:ro
      - /proc:/host/proc:ro
      - /sys:/host/sys:ro
    
    # 资源限制
    deploy:
      resources:
        limits:
          memory: 256M
          cpus: '0.5'
        reservations:
          memory: 128M
          cpus: '0.25'
    
    # 日志配置
    logging:
      driver: "json-file"
      options:
        max-size: "10m"
        max-file: "3"

  # 监控服务
  fail2ban-exporter:
    image: gitlab/fail2ban-prometheus-exporter:latest
    container_name: fail2ban-exporter
    restart: unless-stopped
    
    depends_on:
      - fail2ban
    
    ports:
      - "9191:9191"
    
    volumes:
      - ./fail2ban/logs:/var/log/fail2ban:ro
    
    environment:
      - F2B_LOG_PATH=/var/log/fail2ban/fail2ban.log
```

## 3. Fail2ban 配置文件

### 主配置文件 (jail.local)
```ini
# fail2ban/jail.local
[DEFAULT]
# 全局配置
bantime = 3600          # 封禁时间 (1小时)
findtime = 600          # 查找时间窗口 (10分钟)
maxretry = 3            # 最大重试次数
backend = systemd       # 日志后端

# 忽略的IP地址 (白名单)
ignoreip = 127.0.0.1/8 ::1 10.0.0.0/8 172.16.0.0/12 192.168.0.0/16

# 邮件通知配置
destemail = admin@yourdomain.com
sender = fail2ban@yourdomain.com
mta = sendmail
protocol = tcp
chain = f2b-<name>

# 动作配置
action = %(action_mwl)s

[sshd]
# SSH 防护配置
enabled = true
port = ssh,22
filter = sshd
logpath = /var/log/auth.log
maxretry = 3
bantime = 3600
findtime = 600

# 自定义动作
action = iptables-multiport[name=SSH, port="ssh", protocol=tcp]
         sendmail-whois-lines[name=SSH, dest=admin@yourdomain.com, logpath=/var/log/auth.log]

[sshd-ddos]
# SSH DDoS 防护
enabled = true
port = ssh,22
filter = sshd-ddos
logpath = /var/log/auth.log
maxretry = 6
bantime = 7200
findtime = 120

[recidive]
# 重复违规者
enabled = true
filter = recidive
logpath = /var/log/fail2ban.log
action = iptables-allports[name=recidive]
         sendmail-whois-lines[name=recidive, dest=admin@yourdomain.com]
bantime = 86400         # 24小时
findtime = 86400        # 24小时
maxretry = 3

[nginx-http-auth]
# Nginx HTTP 认证失败
enabled = false
port = http,https
filter = nginx-http-auth
logpath = /var/log/nginx/error.log
maxretry = 6

[nginx-noscript]
# Nginx 脚本攻击
enabled = false
port = http,https
filter = nginx-noscript
logpath = /var/log/nginx/access.log
maxretry = 6

[nginx-badbots]
# Nginx 恶意机器人
enabled = false
port = http,https
filter = nginx-badbots
logpath = /var/log/nginx/access.log
maxretry = 2
```

### SSH 过滤器配置
```ini
# fail2ban/filter.d/sshd-custom.conf
[Definition]
# 自定义 SSH 过滤规则

# 失败模式
failregex = ^%(__prefix_line)s(?:error: PAM: )?[aA]uthentication (?:failure|error|failed) for .* from <HOST>( via \S+)?\s*$
            ^%(__prefix_line)s(?:error: )?Received disconnect from <HOST>: 3: .*: Auth fail$
            ^%(__prefix_line)sUser .+ from <HOST> not allowed because not listed in AllowUsers\s*$
            ^%(__prefix_line)sUser .+ from <HOST> not allowed because listed in DenyUsers\s*$
            ^%(__prefix_line)sUser .+ from <HOST> not allowed because not in any group\s*$
            ^%(__prefix_line)srefused connect from \S+ \(<HOST>\)\s*$
            ^%(__prefix_line)s(?:error: )?ROOT LOGIN REFUSED.* FROM <HOST>\s*$
            ^%(__prefix_line)s[iI](?:llegal|nvalid) user .* from <HOST>\s*$
            ^%(__prefix_line)sUser .+ not allowed because account is locked from <HOST>\s*$
            ^%(__prefix_line)sDisconnecting: Too many authentication failures for .+ \[preauth\] from <HOST>\s*$

# 忽略模式
ignoreregex = 

# 时间格式
datepattern = {^LN-BEG}

[Init]
# 初始化参数
journalmatch = _SYSTEMD_UNIT=sshd.service + _COMM=sshd
```

### 自定义动作配置
```ini
# fail2ban/action.d/iptables-custom.conf
[Definition]
# 自定义 iptables 动作

# 初始化命令
actionstart = <iptables> -t <table> -N f2b-<name>
              <iptables> -t <table> -A f2b-<name> -j <returntype>
              <iptables> -t <table> -I <chain> -p <protocol> -m multiport --dports <port> -j f2b-<name>

# 封禁命令
actionban = <iptables> -t <table> -I f2b-<name> 1 -s <ip> -j <blocktype>
            echo "$(date): Banned <ip> for <name>" >> /var/log/fail2ban/custom-bans.log

# 解封命令
actionunban = <iptables> -t <table> -D f2b-<name> -s <ip> -j <blocktype>
              echo "$(date): Unbanned <ip> for <name>" >> /var/log/fail2ban/custom-bans.log

# 停止命令
actionstop = <iptables> -t <table> -D <chain> -p <protocol> -m multiport --dports <port> -j f2b-<name>
             <iptables> -t <table> -F f2b-<name>
             <iptables> -t <table> -X f2b-<name>

# 检查命令
actioncheck = <iptables> -t <table> -n -L <chain> | grep -q 'f2b-<name>[ \t]'

[Init]
# 默认参数
name = default
port = ssh
protocol = tcp
chain = INPUT
table = filter
iptables = iptables
blocktype = REJECT --reject-with icmp-port-unreachable
returntype = RETURN
```

## 4. 部署和启动

### 创建目录结构
```bash
# 创建项目目录
mkdir -p fail2ban-docker/{config,logs,data}
cd fail2ban-docker

# 创建配置目录
mkdir -p fail2ban/{filter.d,action.d}

# 设置权限
chmod 755 fail2ban
chmod 644 fail2ban/jail.local
```

### 启动服务
```bash
# 启动基础版本
docker-compose -f docker-compose.fail2ban.yml up -d

# 启动高级版本
docker-compose -f docker-compose.fail2ban-advanced.yml up -d

# 查看日志
docker-compose logs -f fail2ban

# 检查状态
docker exec fail2ban-ssh-protection fail2ban-client status
```

### 验证配置
```bash
# 检查 fail2ban 状态
docker exec fail2ban-ssh-protection fail2ban-client status

# 查看 SSH jail 状态
docker exec fail2ban-ssh-protection fail2ban-client status sshd

# 查看当前封禁的IP
docker exec fail2ban-ssh-protection fail2ban-client get sshd banip

# 测试配置
docker exec fail2ban-ssh-protection fail2ban-client reload
```

## 5. 监控和管理

### 管理脚本
```bash
#!/bin/bash
# fail2ban-manager.sh

CONTAINER_NAME="fail2ban-ssh-protection"

case "$1" in
    status)
        echo "=== Fail2ban Status ==="
        docker exec $CONTAINER_NAME fail2ban-client status
        ;;
    
    ssh-status)
        echo "=== SSH Jail Status ==="
        docker exec $CONTAINER_NAME fail2ban-client status sshd
        ;;
    
    banned-ips)
        echo "=== Currently Banned IPs ==="
        docker exec $CONTAINER_NAME fail2ban-client get sshd banip
        ;;
    
    unban)
        if [ -z "$2" ]; then
            echo "Usage: $0 unban <IP_ADDRESS>"
            exit 1
        fi
        echo "Unbanning IP: $2"
        docker exec $CONTAINER_NAME fail2ban-client set sshd unbanip $2
        ;;
    
    ban)
        if [ -z "$2" ]; then
            echo "Usage: $0 ban <IP_ADDRESS>"
            exit 1
        fi
        echo "Banning IP: $2"
        docker exec $CONTAINER_NAME fail2ban-client set sshd banip $2
        ;;
    
    reload)
        echo "Reloading fail2ban configuration..."
        docker exec $CONTAINER_NAME fail2ban-client reload
        ;;
    
    logs)
        echo "=== Recent Fail2ban Logs ==="
        docker logs --tail 50 $CONTAINER_NAME
        ;;
    
    stats)
        echo "=== Fail2ban Statistics ==="
        echo "Total bans today:"
        docker exec $CONTAINER_NAME grep "$(date +%Y-%m-%d)" /var/log/fail2ban/fail2ban.log | grep "Ban" | wc -l
        
        echo "Most banned IPs:"
        docker exec $CONTAINER_NAME grep "Ban" /var/log/fail2ban/fail2ban.log | \
            grep -o '[0-9]\{1,3\}\.[0-9]\{1,3\}\.[0-9]\{1,3\}\.[0-9]\{1,3\}' | \
            sort | uniq -c | sort -nr | head -10
        ;;
    
    *)
        echo "Usage: $0 {status|ssh-status|banned-ips|unban|ban|reload|logs|stats}"
        echo ""
        echo "Commands:"
        echo "  status      - Show overall fail2ban status"
        echo "  ssh-status  - Show SSH jail status"
        echo "  banned-ips  - List currently banned IPs"
        echo "  unban <ip>  - Unban specific IP"
        echo "  ban <ip>    - Ban specific IP"
        echo "  reload      - Reload configuration"
        echo "  logs        - Show recent logs"
        echo "  stats       - Show statistics"
        exit 1
        ;;
esac
```

### 监控脚本
```bash
#!/bin/bash
# fail2ban-monitor.sh

LOG_FILE="/var/log/fail2ban-monitor.log"
CONTAINER_NAME="fail2ban-ssh-protection"

# 检查容器状态
if ! docker ps | grep -q $CONTAINER_NAME; then
    echo "$(date): ERROR - Fail2ban container is not running!" >> $LOG_FILE
    # 尝试重启
    docker-compose up -d fail2ban
fi

# 检查 fail2ban 服务状态
if ! docker exec $CONTAINER_NAME fail2ban-client ping >/dev/null 2>&1; then
    echo "$(date): ERROR - Fail2ban service is not responding!" >> $LOG_FILE
fi

# 统计今日封禁数量
BAN_COUNT=$(docker exec $CONTAINER_NAME grep "$(date +%Y-%m-%d)" /var/log/fail2ban/fail2ban.log 2>/dev/null | grep "Ban" | wc -l)
echo "$(date): INFO - Bans today: $BAN_COUNT" >> $LOG_FILE

# 检查异常高频封禁
if [ "$BAN_COUNT" -gt 100 ]; then
    echo "$(date): WARNING - High number of bans detected: $BAN_COUNT" >> $LOG_FILE
fi

# 清理旧日志
find /var/log -name "fail2ban-monitor.log" -mtime +7 -delete
```

## 6. Prometheus 监控集成

### Prometheus 配置
```yaml
# prometheus.yml
global:
  scrape_interval: 15s

scrape_configs:
  - job_name: 'fail2ban'
    static_configs:
      - targets: ['localhost:9191']
    scrape_interval: 30s
    metrics_path: /metrics
```

### Grafana Dashboard 配置
```json
{
  "dashboard": {
    "title": "Fail2ban Security Dashboard",
    "panels": [
      {
        "title": "Active Bans",
        "type": "stat",
        "targets": [
          {
            "expr": "fail2ban_banned_ips",
            "legendFormat": "Banned IPs"
          }
        ]
      },
      {
        "title": "Ban Rate",
        "type": "graph",
        "targets": [
          {
            "expr": "rate(fail2ban_bans_total[5m])",
            "legendFormat": "Bans per second"
          }
        ]
      },
      {
        "title": "Top Banned Countries",
        "type": "piechart",
        "targets": [
          {
            "expr": "topk(10, fail2ban_banned_ips_by_country)",
            "legendFormat": "{{country}}"
          }
        ]
      }
    ]
  }
}
```

## 7. 安全最佳实践

### 1. 配置优化
```ini
# 渐进式封禁策略
[sshd]
enabled = true
bantime.increment = true
bantime.rndtime = 300
bantime.maxtime = 86400
bantime.factor = 2
```

### 2. 白名单管理
```bash
# 添加可信IP到白名单
echo "192.168.1.100" >> /etc/fail2ban/jail.local.d/whitelist

# 动态白名单脚本
#!/bin/bash
WHITELIST_FILE="/etc/fail2ban/jail.local.d/whitelist"
CURRENT_IP=$(curl -s ifconfig.me)
echo "$CURRENT_IP" >> $WHITELIST_FILE
docker exec fail2ban-ssh-protection fail2ban-client reload
```

### 3. 日志轮转
```bash
# logrotate 配置
cat << 'EOF' > /etc/logrotate.d/fail2ban-docker
/var/log/fail2ban/*.log {
    daily
    rotate 30
    compress
    delaycompress
    missingok
    notifempty
    postrotate
        docker exec fail2ban-ssh-protection fail2ban-client flushlogs
    endscript
}
EOF
```

## 8. 故障排除

### 常见问题诊断
```bash
# 1. 检查容器权限
docker exec fail2ban-ssh-protection ls -la /var/log/

# 2. 检查 iptables 规则
docker exec fail2ban-ssh-protection iptables -L f2b-sshd -n

# 3. 测试日志文件访问
docker exec fail2ban-ssh-protection tail -f /var/log/auth.log

# 4. 检查配置语法
docker exec fail2ban-ssh-protection fail2ban-client -t

# 5. 调试模式运行
docker run --rm -it --privileged --network host \
  -v /var/log:/var/log:ro \
  -v ./fail2ban/jail.local:/etc/fail2ban/jail.local:ro \
  crazymax/fail2ban:latest fail2ban-server -f -v
```

### 性能优化
```bash
# 1. 限制日志文件大小
echo "maxsize 100M" >> /etc/fail2ban/jail.local

# 2. 优化正则表达式
# 使用更精确的匹配模式

# 3. 调整检查间隔
echo "findtime = 300" >> /etc/fail2ban/jail.local
```

## 9. 自动化部署脚本

```bash
#!/bin/bash
# deploy-fail2ban.sh

set -e

echo "=== Deploying Fail2ban SSH Protection ==="

# 创建目录结构
mkdir -p fail2ban-docker/{fail2ban/{filter.d,action.d},logs,data}
cd fail2ban-docker

# 下载配置文件
curl -o docker-compose.yml https://raw.githubusercontent.com/your-repo/fail2ban-docker/main/docker-compose.yml
curl -o fail2ban/jail.local https://raw.githubusercontent.com/your-repo/fail2ban-docker/main/jail.local

# 设置权限
chmod 755 fail2ban
chmod 644 fail2ban/jail.local

# 启动服务
docker-compose up -d

# 等待服务启动
sleep 30

# 验证部署
if docker exec fail2ban-ssh-protection fail2ban-client status >/dev/null 2>&1; then
    echo "✅ Fail2ban deployed successfully!"
    docker exec fail2ban-ssh-protection fail2ban-client status
else
    echo "❌ Deployment failed!"
    docker-compose logs fail2ban
    exit 1
fi

echo "=== Deployment Complete ==="
echo "Management script: ./fail2ban-manager.sh"
echo "Monitor logs: docker-compose logs -f fail2ban"
```

---

**创建时间**: 2025-01-27
**修改时间**: 2025-01-27

*本指南提供了使用 Docker 容器特权模式部署 fail2ban 进行 SSH 防护的完整解决方案，适用于云原生环境下的安全防护需求。*