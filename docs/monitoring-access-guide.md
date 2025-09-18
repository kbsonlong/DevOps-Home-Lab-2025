# 📊 Monitoring Access Guide

## Overview
This guide shows you how to access Prometheus and Grafana without port-forwarding using Kubernetes Ingress.

## 🚀 Quick Setup

### Option 1: Automated Setup (Recommended)
```bash
# Run the automated setup script
./scripts/access-monitoring.sh
```

### Option 2: Manual Setup
```bash
# 1. Apply monitoring configuration
kubectl apply -f k8s/monitoring.yaml
kubectl apply -f k8s/monitoring-auth.yaml

# 2. Apply ingress configuration
kubectl apply -f k8s/ingress.yaml

# 3. Wait for services to be ready
kubectl wait --for=condition=ready pod -l app=prometheus -n monitoring
kubectl wait --for=condition=ready pod -l app=grafana -n monitoring
```

## 🌐 Access URLs

### Local Development
- **Prometheus**: http://prometheus.kbsonlong.com:8080
- **Grafana**: http://grafana.kbsonlong.com:8080

### Production
- **Prometheus**: http://prometheus.kbsonlong.com
- **Grafana**: http://grafana.kbsonlong.com

## 🔐 Default Credentials

### Prometheus
- No authentication required (read-only access)

### Grafana
- **Username**: `admin`
- **Password**: `admin123`

## 📱 Local DNS Setup

The setup script automatically detects your ingress IP and adds entries to your `/etc/hosts` file:

```bash
# Local monitoring access (k3d port mapping)
127.0.0.1 prometheus.kbsonlong.com
127.0.0.1 grafana.kbsonlong.com

# Production monitoring access (automatically detected IP)
# Example after script runs:
# 172.18.0.2 prometheus.kbsonlong.com
# 172.18.0.2 grafana.kbsonlong.com
```

### 🔍 How IP Detection Works

**For Local Development (k3d):**
- Uses `127.0.0.1` (localhost) in `/etc/hosts`
- Access via `http://prometheus.kbsonlong.com:8080` (k3d maps port 8080→80)
- This matches your k3d cluster configuration

**For Production:**
The script automatically finds your ingress controller IP using this priority:

1. **LoadBalancer IP** (if using cloud provider)
2. **Cluster IP** (for local k3d clusters)  
3. **Node IP** (fallback for any cluster type)
4. **localhost** (final fallback)

```bash
# You can manually check your ingress IP:
kubectl get svc -n ingress-nginx
kubectl get nodes -o wide

# Or use the same detection logic as the script:
INGRESS_IP=$(kubectl get svc -n ingress-nginx humor-game-nginx-controller -o jsonpath='{.status.loadBalancer.ingress[0].ip}' 2>/dev/null || \
             kubectl get svc -n ingress-nginx humor-game-nginx-controller -o jsonpath='{.spec.clusterIP}' 2>/dev/null || \
             kubectl get nodes -o jsonpath='{.items[0].status.addresses[?(@.type=="InternalIP")].address}' 2>/dev/null)
echo "Detected IP: $INGRESS_IP"
```

## 🔍 Troubleshooting

### Can't Access Services?

1. **Check cluster status**:
   ```bash
   k3d cluster list
   kubectl cluster-info
   ```

2. **Verify ingress is working**:
   ```bash
   kubectl get ingress -A
   kubectl describe ingress monitoring-ingress -n monitoring
   ```

3. **Check service status**:
   ```bash
   kubectl get pods -n monitoring
   kubectl get svc -n monitoring
   ```

4. **Check ingress controller**:
   ```bash
   kubectl get pods -n ingress-nginx
   kubectl get svc -n ingress-nginx
   ```

### Common Issues

#### Issue: "Connection refused"
- **Solution**: Ensure your cluster is running and ingress controller is deployed

#### Issue: "Host not found"
- **Solution**: Check `/etc/hosts` file and verify DNS entries

#### Issue: "Authentication required"
- **Solution**: Use credentials: `admin/admin123`

## 🛠️ Manual Port-Forwarding (Fallback)

If ingress doesn't work, you can still use port-forwarding:

```bash
# Prometheus
kubectl port-forward -n monitoring svc/prometheus 9090:9090

# Grafana
kubectl port-forward -n monitoring svc/grafana 3000:3000
```

Then access:
- Prometheus: http://localhost:9090
- Grafana: http://localhost:3000

## 🔧 Customization

### Change Default Credentials

1. **Generate new password hash**:
   ```bash
   htpasswd -nb admin your_new_password
   ```

2. **Update the secret**:
   ```bash
   kubectl patch secret monitoring-auth -n monitoring --type='json' -p='[{"op": "replace", "path": "/data/auth", "value": "YOUR_BASE64_HASH"}]'
   ```

### Add SSL/TLS

1. **Create TLS secret**:
   ```bash
   kubectl create secret tls monitoring-tls -n monitoring --cert=your-cert.pem --key=your-key.pem
   ```

2. **Update ingress annotations**:
   ```yaml
   nginx.ingress.kubernetes.io/ssl-redirect: "true"
   nginx.ingress.kubernetes.io/force-ssl-redirect: "true"
   ```

## 📊 Dashboard Features

### Prometheus
- Real-time metrics collection
- Query language (PromQL)
- Alerting rules
- Service discovery

### Grafana
- Pre-configured dashboards
- Custom visualization
- Alert notifications
- Data source management

## 🚨 Security Notes

- **Basic auth** is enabled by default
- **HTTPS** is recommended for production
- **Network policies** can restrict access
- **RBAC** controls Kubernetes access

## 🔄 Updates and Maintenance

### Update Monitoring Stack
```bash
# Pull latest configurations
git pull origin main

# Apply updates
kubectl apply -f k8s/monitoring.yaml
kubectl apply -f k8s/ingress.yaml
```

### Backup Dashboards
```bash
# Export Grafana dashboards
kubectl get configmap grafana-dashboards -n monitoring -o yaml > dashboards-backup.yaml
```

---

**Need help?** Check the troubleshooting section or run the automated setup script!
