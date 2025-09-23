# ModSecurity 403 错误故障排除指南

## 问题描述
ModSecurity 触发 OWASP CRS 规则，导致出站异常评分超出限制（Outbound Anomaly Score Exceeded），返回 403 错误。

## 错误示例
```
2025/09/23 05:07:31 [error] 560#560: *4219 [client 103.150.184.196] ModSecurity: Access denied with code 403 (phase 4). 
Matched "Operator `Ge' with parameter `4' against variable `TX:BLOCKING_OUTBOUND_ANOMALY_SCORE' (Value: `4' ) 
[msg "Outbound Anomaly Score Exceeded (Total Score: 4)"] 
[file "/etc/nginx/owasp-modsecurity-crs/rules/RESPONSE-959-BLOCKING-EVALUATION.conf"] 
[line "232"] [id "959100"]
```

## 解决方案

### 1. 快速修复（临时）

#### 方法 A：临时禁用 ModSecurity
```bash
# 对特定 Ingress 禁用 ModSecurity
kubectl annotate ingress <your-ingress> nginx.ingress.kubernetes.io/enable-modsecurity=false

# 或者对所有请求禁用规则引擎
kubectl annotate ingress <your-ingress> nginx.ingress.kubernetes.io/modsecurity-snippet='SecRuleEngine DetectionOnly'
```

#### 方法 B：提高异常评分阈值
```bash
# 在 Ingress 注解中添加
kubectl annotate ingress <your-ingress> nginx.ingress.kubernetes.io/modsecurity-snippet='
SecAction "id:900110,phase:1,nolog,pass,t:none,setvar:tx.outbound_anomaly_score_threshold=20"
'
```

### 2. 永久修复（推荐）

#### 步骤 1：应用优化配置
```bash
# 运行部署脚本
chmod +x deploy-modsecurity-fix.sh
./deploy-modsecurity-fix.sh
```

#### 步骤 2：验证配置
```bash
# 检查 Pod 状态
kubectl get pods -n ingress-nginx

# 检查 ConfigMap
kubectl get configmap -n ingress-nginx | grep modsecurity

# 检查 Nginx 配置
NGINX_POD=$(kubectl get pods -n ingress-nginx -l app.kubernetes.io/name=ingress-nginx -o jsonpath='{.items[0].metadata.name}')
kubectl exec -n ingress-nginx $NGINX_POD -- nginx -t
```

### 3. 高级调试

#### 查看详细日志
```bash
# 查看审计日志
kubectl exec -n ingress-nginx $NGINX_POD -- tail -f /var/log/modsecurity/modsec_audit.log

# 查看调试日志
kubectl exec -n ingress-nginx $NGINX_POD -- tail -f /var/log/modsecurity/modsec_debug.log

# 使用监控脚本
./modsecurity-log-monitor.sh analyze
```

#### 分析特定规则
```bash
# 查看触发规则的详细信息
kubectl exec -n ingress-nginx $NGINX_POD -- grep "959100" /var/log/modsecurity/modsec_debug.log

# 查看规则文件内容
kubectl exec -n ingress-nginx $NGINX_POD -- cat /etc/nginx/owasp-modsecurity-crs/rules/RESPONSE-959-BLOCKING-EVALUATION.conf
```

### 4. 针对 Grafana 的特殊配置

#### Grafana 特定异常处理
配置文件中已包含针对 Grafana 的优化：

```apache
# 对 Grafana 主机名放宽规则
SecRule REQUEST_HEADERS:Host "@streq grafana.kbsonlong.com" \
    "id:2001,phase:1,pass,nolog,ctl:ruleRemoveById=959100"

# 对 Grafana API 端点放宽 SQL 注入检测
SecRule REQUEST_URI "@beginsWith /api/" \
    "id:2002,phase:2,pass,nolog,ctl:ruleRemoveById=942100-942450"
```

#### 静态资源处理
```apache
# 对静态资源完全禁用规则引擎
SecRule REQUEST_URI "\.(css|js|png|jpg|jpeg|gif|ico|svg|woff|woff2|ttf|eot|map)$" \
    "id:2003,phase:1,pass,nolog,ctl:ruleEngine=Off"
```

### 5. 性能监控

#### 使用监控脚本
```bash
# 检查当前状态
./modsecurity-log-monitor.sh check

# 分析最近日志
./modsecurity-log-monitor.sh analyze

# 实时监控
./modsecurity-log-monitor.sh monitor
```

#### 关键指标监控
- **异常评分**：出站评分阈值已提高到 15-20
- **误报率**：静态资源和健康检查已排除
- **响应时间**：规则优化减少处理延迟
- **内存使用**：日志轮转和清理机制

### 6. 预防措施

#### 定期维护
```bash
# 清理旧日志（每周运行）
./modsecurity-log-monitor.sh cleanup

# 生成周报
./modsecurity-log-monitor.sh report
```

#### 监控告警
```bash
# 设置告警规则（需要 Prometheus + AlertManager）
# 高异常评分告警
# 大量 403 错误告警
# 规则引擎异常告警
```

## 配置说明

### 主要优化内容

1. **异常评分阈值调整**
   - 入站异常评分阈值：10 → 15
   - 出站异常评分阈值：4 → 20

2. **规则优化**
   - 静态资源完全绕过规则引擎
   - Grafana API 端点放宽 SQL 注入检测
   - 健康检查和监控端点排除

3. **日志增强**
   - 详细的审计日志配置
   - 调试日志级别调整
   - JSON 格式日志便于分析

4. **性能优化**
   - 日志轮转和存储管理
   - 内存使用优化
   - 规则匹配优化

### 配置文件结构

```
k8s/
├── deploy-ingress-nginx.yaml          # 主配置文件
├── modsecurity-exceptions.yaml        # 异常处理配置
├── modsecurity-custom-rules.yaml      # 自定义规则
├── modsecurity-log-collector.yaml     # 日志收集器
├── modsecurity-log-monitor.sh         # 监控脚本
└── deploy-modsecurity-fix.sh          # 部署脚本
```

## 故障排除命令速查

```bash
# 基本检查
kubectl get pods -n ingress-nginx
kubectl logs -n ingress-nginx -l app.kubernetes.io/name=ingress-nginx

# 配置验证
kubectl exec -n ingress-nginx $NGINX_POD -- nginx -t

# 日志查看
kubectl exec -n ingress-nginx $NGINX_POD -- tail -f /var/log/modsecurity/modsec_audit.log
kubectl exec -n ingress-nginx $NGINX_POD -- tail -f /var/log/modsecurity/modsec_debug.log

# 规则调试
kubectl exec -n ingress-nginx $NGINX_POD -- grep "959100" /var/log/modsecurity/modsec_debug.log

# 性能监控
./modsecurity-log-monitor.sh analyze
```

## 联系支持

如果问题仍然存在：
1. 收集完整的错误日志
2. 记录触发错误的具体请求
3. 检查相关的 Ingress 配置
4. 查看 ModSecurity 版本和规则版本