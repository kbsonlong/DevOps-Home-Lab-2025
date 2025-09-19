# Ingress Nginx Controller Header 透传配置指南

## 概述

本指南说明如何配置 Ingress Nginx Controller 以正确透传客户端协议信息（HTTP/HTTPS）给后端服务，让后端应用能够识别客户端是通过 HTTP 还是 HTTPS 协议访问的。

## 配置说明

### 1. Ingress Nginx Controller ConfigMap 配置

确保在 `ingress-nginx` namespace 中的 ConfigMap 包含以下配置：

```yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: ingress-nginx-controller
  namespace: ingress-nginx
data:
  # 允许使用 snippet annotations
  allow-snippet-annotations: "true"
  # 启用 forwarded headers 处理
  use-forwarded-headers: "true"
  # 完整的 X-Forwarded-For 头处理
  compute-full-forwarded-for: "true"
  # 禁用 PROXY protocol（除非需要）
  use-proxy-protocol: "false"
```

### 2. Ingress 资源注解配置

在你的 Ingress 资源中添加以下 annotations：

```yaml
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: humor-game-ingress
  namespace: humor-game
  annotations:
    # Header透传配置 - 让后端知道客户端协议
    nginx.ingress.kubernetes.io/use-forwarded-headers: "true"
    nginx.ingress.kubernetes.io/forwarded-proto-header: "X-Forwarded-Proto"
    nginx.ingress.kubernetes.io/forwarded-for-header: "X-Forwarded-For"
    nginx.ingress.kubernetes.io/forwarded-host-header: "X-Forwarded-Host"
    
    # 其他有用的配置
    nginx.ingress.kubernetes.io/cors-allow-origin: "*"
    nginx.ingress.kubernetes.io/cors-allow-credentials: "true"
spec:
  ingressClassName: nginx
  # ... 其他配置
```

### 3. 后端应用识别协议

后端应用可以通过以下方式识别客户端协议：

#### Node.js/Express 示例

```javascript
// 获取客户端协议
const clientProtocol = req.headers['x-forwarded-proto'] || req.protocol;
const isSecure = clientProtocol === 'https';

// 获取客户端真实IP
const clientIP = req.headers['x-forwarded-for'] || req.connection.remoteAddress;

// 获取原始Host
const originalHost = req.headers['x-forwarded-host'] || req.headers['host'];
```

#### 调试端点

后端已添加调试端点 `/debug/headers`，可以查看所有接收到的 headers：

```bash
curl http://your-domain/debug/headers
```

返回示例：
```json
{
  "success": true,
  "message": "Header debug endpoint working!",
  "timestamp": "2024-01-01T12:00:00.000Z",
  "headers": {
    "x-forwarded-proto": "https",
    "x-forwarded-for": "192.168.1.100",
    "x-forwarded-host": "your-domain.com",
    "x-real-ip": "192.168.1.100",
    "host": "your-domain.com"
  },
  "protocol": "http",
  "secure": false
}
```

## 工作原理

### Header 透传流程

1. **客户端请求** → **负载均衡器/代理** → **Ingress Nginx Controller** → **后端服务**

2. **X-Forwarded-Proto**: 表示客户端原始协议（http/https）
3. **X-Forwarded-For**: 表示客户端真实IP地址
4. **X-Forwarded-Host**: 表示客户端原始请求的Host

### 配置优先级

1. **ConfigMap 全局配置**: 影响所有 Ingress 资源
2. **Ingress Annotations**: 针对特定 Ingress 的配置
3. **后端应用处理**: 根据接收到的 headers 进行逻辑处理

## 常见问题排查

### 1. Header 未正确传递

检查 ConfigMap 配置：
```bash
kubectl get configmap ingress-nginx-controller -n ingress-nginx -o yaml
```

检查 Ingress annotations：
```bash
kubectl get ingress humor-game-ingress -n humor-game -o yaml
```

### 2. 协议识别错误

使用调试端点验证：
```bash
# HTTP 访问
curl http://your-domain/debug/headers

# HTTPS 访问（如果配置了SSL）
curl https://your-domain/debug/headers
```

### 3. 真实IP获取错误

确保 ConfigMap 中启用了：
```yaml
compute-full-forwarded-for: "true"
use-forwarded-headers: "true"
```

## 安全注意事项

1. **信任代理**: 确保只信任已知的代理服务器
2. **CIDR 配置**: 如果使用 proxy-real-ip-cidr，确保配置正确的IP段
3. **Header 验证**: 后端应用应该验证和清理接收到的 headers

## 相关文档

- [Ingress Nginx Controller Annotations](https://kubernetes.github.io/ingress-nginx/user-guide/nginx-configuration/annotations/)
- [Source IP Address Configuration](https://kubernetes.github.io/ingress-nginx/user-guide/miscellaneous/#source-ip-address)
- [Forwarded Headers](https://kubernetes.github.io/ingress-nginx/user-guide/nginx-configuration/configmap/#use-forwarded-headers)

## 更新记录

- 2024-01-XX: 初始版本，配置 Header 透传功能
- 2024-01-XX: 添加调试端点和故障排查指南