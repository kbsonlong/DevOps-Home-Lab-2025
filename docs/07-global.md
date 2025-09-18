# Milestone 6: Global Scale and Production Readiness

## 🎯 **Goal**
Transform your local application into a production-ready system with security, scalability, and global access patterns used by enterprise applications.

## ⏱️ **Typical Time: 60-120 minutes**

## Why This Matters

This milestone transforms your local application into one ready for production use, implementing security and scalability patterns used by enterprise applications.

ℹ️ **Side Note:** Production readiness means your application can handle real user traffic, security threats, and operational challenges. This includes implementing security best practices (TLS, network policies), resource management (limits and requests), monitoring (health checks, metrics), and scalability (auto-scaling, load balancing) that enterprise applications require.

## 🚀 **Quick Start Guide for Beginners**

This milestone will teach you how to:
1. **🌍 Make your app globally accessible** using Cloudflare tunnels
2. **🔒 Add enterprise security** with TLS certificates and network policies  
3. **📈 Enable auto-scaling** to handle traffic spikes
4. **🛡️ Implement production monitoring** with health checks

**Time needed:** 60-120 minutes
**Prerequisites:** Completed observability.md and gitops.md milestones

## Do This

## 🎯 **Step-by-Step Implementation Guide**

### **Phase 1: Application Health Verification**

```bash
# Test application health
curl -H "Host: kbsonlong.com" -s http://localhost:8080/api/health | jq .

# Check resource usage
kubectl top nodes
kubectl top pods -n humor-game

# Expected output: healthy status and low resource usage
```

### **Phase 2: Configure Horizontal Pod Autoscaling**

```bash
# Apply HPA configuration
kubectl apply -f k8s/hpa.yaml

# Verify HPA is working
kubectl get hpa -n humor-game

# Expected output: backend-hpa and frontend-hpa created
```

### **Phase 3: Set Up Cloudflare Tunnel**

#### **3.1: Authenticate with Cloudflare**
```bash
# Re-authenticate to get fresh certificates
cloudflared tunnel login

# Expected: Browser opens, successful login message
```

#### **3.2: Create New Tunnel**
```bash
# Delete old tunnel if exists
cloudflared tunnel delete gameapp-tunnel

# Create new tunnel
cloudflared tunnel create gameapp-tunnel

# Note the tunnel ID from output for next step
```

#### **3.3: Configure Tunnel**
Update `~/.cloudflared/config.yml` with new tunnel ID:
```yaml
tunnel: YOUR_NEW_TUNNEL_ID

ingress:
  # Main game application
  - hostname: kbsonlong.com
    service: http://localhost:8080
    originRequest:
      originServerName: kbsonlong.com
      noTLSVerify: true
      disableChunkedEncoding: true
  
  - hostname: app.kbsonlong.com
    service: http://localhost:8080
    originRequest:
      originServerName: kbsonlong.com
      noTLSVerify: true
      disableChunkedEncoding: true
  
  # Monitoring services
  - hostname: grafana.kbsonlong.com
    service: http://localhost:8080
    originRequest:
      originServerName: grafana.kbsonlong.com
      noTLSVerify: true
      disableChunkedEncoding: true
  
  - hostname: prometheus.kbsonlong.com
    service: http://localhost:8080
    originRequest:
      originServerName: prometheus.kbsonlong.com
      noTLSVerify: true
      disableChunkedEncoding: true
  
  - hostname: argocd.kbsonlong.com
    service: http://localhost:8080
    originRequest:
      originServerName: argocd.kbsonlong.com
      noTLSVerify: true
      disableChunkedEncoding: true
  
  # Catch-all for unmatched hostnames
  - service: http_status:404
```

#### **3.4: Create DNS Routes**
```bash
# Create DNS routes for all services
cloudflared tunnel route dns gameapp-tunnel kbsonlong.com
cloudflared tunnel route dns gameapp-tunnel app.kbsonlong.com
cloudflared tunnel route dns gameapp-tunnel grafana.kbsonlong.com
cloudflared tunnel route dns gameapp-tunnel prometheus.kbsonlong.com
cloudflared tunnel route dns gameapp-tunnel argocd.kbsonlong.com
```

#### **3.5: Start Tunnel**
```bash
# Start tunnel in background
nohup cloudflared tunnel run gameapp-tunnel > tunnel.log 2>&1 &

# Verify tunnel is running
ps aux | grep cloudflared
```

### **Phase 4: Configure Production Ingress**

#### **4.1: Update Main Application Ingress**
Add production domains to `k8s/ingress.yaml`:

```yaml
# Add these rules to the humor-game-ingress
    # Production domain
    - host: kbsonlong.com
      http:
        paths:
          - path: /api
            pathType: Prefix
            backend:
              service:
                name: backend
                port:
                  number: 3001
          - path: /health
            pathType: Exact
            backend:
              service:
                name: backend
                port:
                  number: 3001
          - path: /metrics
            pathType: Exact
            backend:
              service:
                name: backend
                port:
                  number: 3001
          - path: /debug
            pathType: Prefix
            backend:
              service:
                name: backend
                port:
                  number: 3001
          - path: /
            pathType: Prefix
            backend:
              service:
                name: frontend
                port:
                  number: 80
    
    # App subdomain (repeat same paths)
    - host: app.kbsonlong.com
      # ... same paths as above ...
```

#### **4.2: Fix ArgoCD Redirect Loops**

**Common Issue**: ArgoCD shows "ERR_TOO_MANY_REDIRECTS" when accessed via tunnel.

**Root Cause**: ArgoCD tries to redirect HTTP to HTTPS, but Cloudflare tunnel already terminates HTTPS.

**Solution Steps**:

1. **Update ArgoCD ingress annotations**:
```yaml
annotations:
  # Disable SSL redirect for tunnel access to prevent redirect loops
  nginx.ingress.kubernetes.io/ssl-redirect: "false"
  nginx.ingress.kubernetes.io/force-ssl-redirect: "false"
  # ArgoCD server configuration for UI access
  nginx.ingress.kubernetes.io/backend-protocol: "HTTP"
  # Handle forwarded headers properly for tunnel access
  nginx.ingress.kubernetes.io/use-forwarded-headers: "true"
  nginx.ingress.kubernetes.io/forwarded-for-header: "X-Forwarded-For"
  nginx.ingress.kubernetes.io/forwarded-proto-header: "X-Forwarded-Proto"
  nginx.ingress.kubernetes.io/forwarded-host-header: "X-Forwarded-Host"
  # ArgoCD specific server snippet for grpc and timeout handling
  nginx.ingress.kubernetes.io/server-snippet: |
    grpc_read_timeout 300;
    grpc_send_timeout 300;
    client_body_timeout 60;
    client_header_timeout 60;
    client_max_body_size 1m;
```

2. **Configure ArgoCD server for insecure mode**:
```bash
# Set ArgoCD to run in insecure mode behind proxy
kubectl patch configmap argocd-cmd-params-cm -n argocd --patch='{"data":{"server.insecure":"true"}}'

# Restart ArgoCD server to apply changes
kubectl rollout restart deployment argocd-server -n argocd

# Wait for rollout to complete
kubectl rollout status deployment argocd-server -n argocd --timeout=60s
```

3. **Add production ArgoCD route**:
```yaml
# Add to argocd-ingress in k8s/ingress.yaml
    - host: argocd.kbsonlong.com
      http:
        paths:
          - path: /
            pathType: Prefix
            backend:
              service:
                name: argocd-server
                port:
                  number: 80
```

#### **4.3: Configure Monitoring Ingress**
Update `k8s/monitoring-tunnel-ingress.yaml` with correct ingress class:
```yaml
spec:
  ingressClassName: nginx  # Change from humor-game-nginx
```

#### **4.4: Apply All Ingress Changes**
```bash
# Apply main application ingress
kubectl apply -f k8s/ingress.yaml

# Apply monitoring ingress
kubectl apply -f k8s/monitoring-tunnel-ingress.yaml
```

### **Phase 5: Apply Security Hardening**

```bash
# Apply security contexts
kubectl apply -f k8s/security-context.yaml

# Apply network policies
kubectl apply -f k8s/network-policies.yaml

# Verify network policies are created
kubectl get networkpolicy -n humor-game
```

### **Phase 6: Comprehensive Testing**

```bash
# Test main application
echo "🎮 Testing Game Application:"
curl -s https://kbsonlong.com/api/health | jq -r '.status + " - " + .timestamp'

# Test monitoring stack
echo "📊 Testing Prometheus:"
curl -s https://prometheus.kbsonlong.com/api/v1/targets | jq -r '.data.activeTargets | length | tostring + " active targets"'

echo "📈 Testing Grafana:"
curl -s https://grafana.kbsonlong.com/api/health | jq -r '.database + " - v" + .version'

# Test ArgoCD
echo "🚀 Testing ArgoCD:"
curl -s https://argocd.kbsonlong.com/healthz

# Test app subdomain
curl -s https://app.kbsonlong.com/api/health | jq .
```

## 🔧 **Comprehensive Troubleshooting Guide**

### **Issue 1: Tunnel Authentication Errors**

**Symptoms**:
```
Tunnel credentials file '/Users/mac/.cloudflared/xxx.json' doesn't exist
```

**Solution**:
```bash
# Re-authenticate and create new tunnel
cloudflared tunnel login
cloudflared tunnel delete old-tunnel-name
cloudflared tunnel create gameapp-tunnel

# Update config.yml with new tunnel ID
vim ~/.cloudflared/config.yml
```

### **Issue 2: ArgoCD Redirect Loops (ERR_TOO_MANY_REDIRECTS)**

**Symptoms**:
- Browser shows "This page isn't working"
- "ERR_TOO_MANY_REDIRECTS" error
- ArgoCD accessible locally but not via tunnel

**Diagnosis Commands**:
```bash
# Check ArgoCD server configuration
kubectl get configmap argocd-cmd-params-cm -n argocd -o yaml

# Check ingress annotations
kubectl describe ingress argocd-ingress -n argocd

# Test local access (should work)
curl -k http://localhost:8090/
```

**Solution**:
```bash
# 1. Set ArgoCD to insecure mode
kubectl patch configmap argocd-cmd-params-cm -n argocd --patch='{"data":{"server.insecure":"true"}}'

# 2. Update ingress annotations (see Phase 4.2 above)

# 3. Restart ArgoCD server
kubectl rollout restart deployment argocd-server -n argocd
kubectl rollout status deployment argocd-server -n argocd --timeout=60s

# 4. Test again
curl -s https://argocd.kbsonlong.com/healthz
```

### **Issue 3: Monitoring Services Return 404**

**Symptoms**:
- Prometheus/Grafana return "404 Not Found" via tunnel
- Services work with port-forwarding

**Diagnosis Commands**:
```bash
# Check ingress class
kubectl get ingress -n monitoring
kubectl describe ingress monitoring-tunnel-ingress -n monitoring

# Check service endpoints
kubectl get endpoints -n monitoring
```

**Solution**:
```bash
# Fix ingress class name
kubectl patch ingress monitoring-tunnel-ingress -n monitoring --patch='{"spec":{"ingressClassName":"nginx"}}'

# Reapply if needed
kubectl apply -f k8s/monitoring-tunnel-ingress.yaml
```

### **Issue 4: DNS Not Resolving to Cloudflare**

**Symptoms**:
```bash
nslookup kbsonlong.com
# Returns local IP instead of Cloudflare IPs
```

**Diagnosis**:
```bash
# Check /etc/hosts for overrides
grep gameapp /etc/hosts
```

**Solution**:
```bash
# Remove local DNS overrides
sudo sed -i '' '/127.0.0.1 kbsonlong.com/d' /etc/hosts

# Verify DNS now resolves to Cloudflare
nslookup kbsonlong.com
# Should return Cloudflare IPs (104.x.x.x or 172.x.x.x)
```

### **Issue 5: Tunnel Not Starting**

**Symptoms**:
- `ps aux | grep cloudflared` shows no process
- Tunnel exits immediately

**Diagnosis Commands**:
```bash
# Check tunnel configuration
cloudflared tunnel info gameapp-tunnel

# Test configuration
cloudflared tunnel ingress validate

# Check logs
tail -f tunnel.log
```

**Solution**:
```bash
# Validate and fix config
cloudflared tunnel ingress validate ~/.cloudflared/config.yml

# Restart tunnel with logging
cloudflared tunnel run gameapp-tunnel --loglevel debug
```

### **Issue 6: HPA Shows "Unknown" Metrics**

**Symptoms**:
```bash
kubectl get hpa -n humor-game
# Shows cpu: <unknown>/70%, memory: <unknown>/80%
```

**Diagnosis**:
```bash
# Check metrics server
kubectl get deployment metrics-server -n kube-system
kubectl top nodes
```

**Solution**:
```bash
# Metrics will populate after a few minutes
# Check again after 2-3 minutes
kubectl get hpa -n humor-game

# If still unknown, check metrics server logs
kubectl logs -l k8s-app=metrics-server -n kube-system
```

### **Issue 7: Network Policies Blocking Traffic**

**Symptoms**:
- Application stops working after applying network policies
- Services can't communicate

**Diagnosis**:
```bash
# Check network policies
kubectl get networkpolicy -n humor-game
kubectl describe networkpolicy backend-network-policy -n humor-game

# Test connectivity
kubectl exec -it deploy/backend -n humor-game -- curl postgres:5432
```

**Solution**:
```bash
# Review and adjust network policies
kubectl edit networkpolicy backend-network-policy -n humor-game

# Temporarily remove to test
kubectl delete networkpolicy --all -n humor-game
```

## 🎯 **Quick Diagnostic Commands**

```bash
# Application Health Check
kubectl get pods -n humor-game
kubectl get hpa -n humor-game
curl -H "Host: kbsonlong.com" http://localhost:8080/api/health

# Tunnel Status
ps aux | grep cloudflared
cloudflared tunnel list
tail -f tunnel.log

# Ingress Status
kubectl get ingress -A
kubectl describe ingress humor-game-ingress -n humor-game

# DNS Verification
nslookup kbsonlong.com
dig kbsonlong.com

# Global Access Test
curl -s https://kbsonlong.com/api/health
curl -s https://prometheus.kbsonlong.com/api/v1/targets | jq '.data.activeTargets | length'
curl -s https://grafana.kbsonlong.com/api/health
curl -s https://argocd.kbsonlong.com/healthz
```

---

*Production milestone completed successfully. Application hardened, monitoring active, autoscaling configured, globally accessible via Cloudflare tunnels.*



-------------------------------

### Step 1: Verify Current Setup and Add Production Monitoring

```bash
# Verify your current setup from previous milestones
curl -H "Host: kbsonlong.com" -s http://localhost:8080/api/health
# Should return: {"status":"healthy"}
```

**Expected Output:**
```json
{
  "status": "healthy",
  "services": {
    "database": "connected",
    "redis": "connected"
  },
  "timestamp": "2024-01-15T10:30:00.000Z",
  "uptime": "00:15:45"
}
```

```bash
# Test game functionality
open http://kbsonlong.com:8080

# Add resource monitoring
kubectl top nodes
kubectl top pods -n humor-game
```

**Expected Output:**
```bash
NAME                    CPU(cores)   CPU%   MEMORY(bytes)   MEMORY%
k3d-dev-cluster-server-0   45m          2%     1.2Gi          30%
k3d-dev-cluster-agent-0    23m          1%     856Mi          21%
k3d-dev-cluster-agent-1    18m          1%     789Mi          19%

NAME                                    CPU(cores)   MEMORY(bytes)
humor-game-backend-7d8f9c8f9c-abc12    12m           156Mi
humor-game-frontend-8e9f0d1e2f-def34   5m            45Mi
humor-game-postgres-7d8f9c8f9c-abc12   8m            89Mi
humor-game-redis-8e9f0d1e2f-def34      3m            23Mi
```

### Step 2: Implement Resource Limits and Requests

**✅ Resource limits are already configured in your deployment files!**

```bash
# Verify resources are applied (they're already there from previous milestones)
kubectl describe deployment backend -n humor-game | grep -A 10 "Limits\|Requests"
kubectl describe deployment frontend -n humor-game | grep -A 10 "Limits\|Requests"
```

**Expected Output:**
```bash
    Limits:
      cpu:     500m
      memory:  512Mi
    Requests:
      cpu:     100m
      memory:  128Mi
```

### Step 3: Set Up Cloudflare Tunnel for Global Access 🌍

**🎓 Beginner Explanation:** Cloudflare tunnels let you expose your local application to the internet securely without opening ports on your firewall. Think of it as a secure pipe between your local app and Cloudflare's global network.

**What you'll achieve:**
- Access your app from anywhere: `https://gameapp.yourdomain.com`
- Automatic HTTPS/SSL certificates
- DDoS protection and global CDN
- No firewall configuration needed

#### Step 3a: Prerequisites - Get a Domain

**You need a domain name** (can be free or paid):

**Option 1: Free Domain (Recommended for learning)**
1. Go to [Freenom](https://freenom.com) or [Duck DNS](https://duckdns.org)
2. Register a free domain like `yourname.tk` or `yourname.duckdns.org`

**Option 2: Paid Domain (Recommended for production)**
1. Buy from Namecheap, GoDaddy, or any registrar
2. Example: `yourgame.com`

**Add Domain to Cloudflare:**
1. Go to [Cloudflare.com](https://cloudflare.com) → Sign up (free)
2. Click "Add Site" → Enter your domain
3. Follow the setup wizard
4. Change your domain's nameservers to Cloudflare's

#### Step 3b: Install Cloudflared CLI

**macOS (using Homebrew):**
```bash
# Install cloudflared
brew install cloudflare/cloudflare/cloudflared

# Verify installation
cloudflared --version
```

**Expected Output:**
```bash
cloudflared version 2024.1.5
```

**Alternative Installation (if Homebrew fails):**
```bash
# Download directly
curl -L https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-darwin-amd64 -o cloudflared

# Make executable and move to PATH
chmod +x cloudflared
sudo mv cloudflared /usr/local/bin/

# Verify
cloudflared --version
```

#### Step 3c: Authenticate with Cloudflare

```bash
# Login to Cloudflare (will open browser)
cloudflared tunnel login
```

**What happens:**
1. Browser opens to Cloudflare login
2. Select your domain from the list
3. Authorize the connection
4. Certificate downloaded to `~/.cloudflared/`

**Expected Output:**
```bash
A browser window should have opened at the following URL:
https://dash.cloudflare.com/argotunnel

If the browser failed to open, open it yourself and visit the URL above.
You have successfully logged in.
If you wish to copy your credentials to a server, they have been saved to:
/Users/yourname/.cloudflared/cert.pem
```

#### Step 3d: Create and Configure Tunnel

```bash
# Create a new tunnel
cloudflared tunnel create gameapp-tunnel

# List tunnels to verify
cloudflared tunnel list
```

**Expected Output:**
```bash
Tunnel gameapp-tunnel created with ID: 12345678-1234-1234-1234-123456789abc
Created tunnel gameapp-tunnel with id 12345678-1234-1234-1234-123456789abc
```

**💡 Important:** Save your tunnel ID! You'll need it later.

#### Step 3e: Create Tunnel Configuration

```bash
# Create config directory
mkdir -p ~/.cloudflared

# Create configuration file (REPLACE yourdomain.com and tunnel ID!)
cat > ~/.cloudflared/config.yml << 'EOF'
tunnel: gameapp-tunnel
credentials-file: ~/.cloudflared/12345678-1234-1234-1234-123456789abc.json

ingress:
  # Game application
  - hostname: gameapp.yourdomain.com
    service: http://localhost:8080
  
  # ArgoCD (optional)
  - hostname: argocd.yourdomain.com  
    service: http://localhost:8090
  
  # Grafana monitoring (optional)
  - hostname: grafana.yourdomain.com
    service: http://localhost:3000
  
  # Prometheus metrics (optional)  
  - hostname: prometheus.yourdomain.com
    service: http://localhost:9090
  
  # Catch-all rule (required)
  - service: http_status:404
EOF

# ⚠️ IMPORTANT: Edit the config file with your details:
# 1. Replace 'yourdomain.com' with your actual domain
# 2. Replace the tunnel ID in credentials-file with your actual tunnel ID
echo "📝 Edit ~/.cloudflared/config.yml with your domain and tunnel ID!"
```

#### Step 3f: Create DNS Records

```bash
# Create DNS record for your main app (REPLACE with your domain!)
cloudflared tunnel route dns gameapp-tunnel gameapp.yourdomain.com

# Create additional DNS records (optional)
cloudflared tunnel route dns gameapp-tunnel argocd.yourdomain.com
cloudflared tunnel route dns gameapp-tunnel grafana.yourdomain.com  
cloudflared tunnel route dns gameapp-tunnel prometheus.yourdomain.com
```

**Expected Output:**
```bash
Added CNAME gameapp.yourdomain.com which will route to this tunnel tunnelID.cfargotunnel.com
```

#### Step 3g: Start the Tunnel

```bash
# Start tunnel (this will run in foreground - keep terminal open)
cloudflared tunnel run gameapp-tunnel
```

**Expected Output:**
```bash
2024-01-15T10:30:00Z INF Starting tunnel tunnelID
2024-01-15T10:30:00Z INF Version 2024.1.5  
2024-01-15T10:30:00Z INF GOOS: darwin, GOARCH: amd64, built: 2024-01-15-1000 UTC
2024-01-15T10:30:00Z INF Generated Connector ID: ...
2024-01-15T10:30:00Z INF cloudflared will not automatically update when run from the command line
2024-01-15T10:30:00Z INF Initial protocol quic
2024-01-15T10:30:00Z INF Starting metrics server on 127.0.0.1:37213/metrics
2024-01-15T10:30:00Z INF Connection established at 2024-01-15T10:30:00Z
```

#### Step 3h: Test Global Access

**Open a new terminal** (keep the tunnel running) and test:

```bash
# Test from command line (REPLACE with your domain!)
curl -s https://gameapp.yourdomain.com/api/health

# Expected: {"status":"healthy","services":{"database":"connected","redis":"connected"}...}

# Test in browser
open https://gameapp.yourdomain.com
```

**🎉 Success! Your app is now globally accessible!**

#### Step 3i: Run Tunnel as Background Service (Optional)

To keep the tunnel running permanently:

```bash
# Install as system service
sudo cloudflared service install

# Start the service
sudo cloudflared service start
```

**Or run in background:**
```bash
# Run in background with nohup
nohup cloudflared tunnel run gameapp-tunnel > tunnel.log 2>&1 &

# Check if running
ps aux | grep cloudflared
```

### Step 4: Add TLS/HTTPS Support

**🎉 Good News: If you're using Cloudflare tunnels, TLS/HTTPS is automatic!**

Cloudflare tunnels provide:
- ✅ Automatic SSL certificates
- ✅ HTTPS encryption for all traffic
- ✅ Certificate renewal (no manual management)
- ✅ Modern TLS versions (1.2+)

**For non-Cloudflare setups, you can still add TLS manually:**

```bash
# Install cert-manager for automatic TLS certificates
kubectl apply -f https://github.com/cert-manager/cert-manager/releases/download/v1.13.0/cert-manager.yaml
```

**Expected Output:**
```bash
namespace/cert-manager created
customresourcedefinition.apiextensions.k8s.io/certificaterequests.cert-manager.io created
customresourcedefinition.apiextensions.k8s.io/certificates.cert-manager.io created
customresourcedefinition.apiextensions.k8s.io/challenges.acme.cert-manager.io created
customresourcedefinition.apiextensions.k8s.io/clusterissuers.cert-manager.io created
customresourcedefinition.apiextensions.k8s.io/issuers.cert-manager.io created
customresourcedefinition.apiextensions.k8s.io/orders.acme.cert-manager.io created
deployment.apps/cert-manager created
deployment.apps/cert-manager-cainjector created
deployment.apps/cert-manager-webhook created
```

# Wait for cert-manager to be ready
kubectl wait --for=condition=ready pod -l app=cert-manager -n cert-manager --timeout=120s

# Apply TLS configuration to your ingress
kubectl apply -f k8s/cluster-issuer.yaml

# Verify certificate is issued
kubectl get certificate -n humor-game
kubectl describe certificate game-tls -n humor-game
```

**Expected Output:**
```bash
NAME       READY   SECRET     AGE
game-tls   True    game-tls   5m
```

**Certificate Details:**
```yaml
Name:         game-tls
Namespace:    humor-game
Labels:       <none>
Annotations:  <none>
API Version:  cert-manager.io/v1
Kind:         Certificate
Spec:
  Secret Name:  game-tls
  Issuer Ref:
    Name:  letsencrypt-prod
    Kind:  ClusterIssuer
Status:
  Conditions:
    Last Transition Time:  2024-01-15T10:35:00Z
    Message:               Certificate is up to date and has not expired
    Reason:                Ready
    Status:                True
    Type:                  Ready
```

### Step 5: Implement Health Checks and Monitoring

**✅ Health checks are already configured in your deployments!**

```bash
# Verify health checks are working
kubectl describe deployment backend -n humor-game | grep -A 5 "Liveness\|Readiness"

# Install simple monitoring stack (beginner-friendly)
kubectl apply -f k8s/simple-monitoring.yaml

# Wait for monitoring pods to be ready
kubectl wait --for=condition=ready pod -l app=prometheus -n monitoring --timeout=120s

# Check monitoring is working
kubectl get pods -n monitoring

# Access monitoring dashboards
kubectl port-forward -n monitoring svc/prometheus 9090:9090 &
kubectl port-forward -n monitoring svc/grafana 3000:3000 &

# Open in browser:
# Prometheus: http://localhost:9090
# Grafana: http://localhost:3000 (admin/admin123)
```

### Step 6: Configure Horizontal Pod Autoscaling

Let your application scale automatically based on load:

```bash
# Apply HPA configuration
kubectl apply -f k8s/hpa.yaml

# Verify HPA is working
kubectl get hpa -n humor-game

# Generate some load to test autoscaling
kubectl run load-test --image=busybox --rm -i --tty -- sh
# Inside the pod:
while true; do wget -q -O- http://kbsonlong.com:8080/; done
```

### Step 7: Production Security Hardening

Implement security best practices:

```bash
# Apply network policies to restrict pod communication
kubectl apply -f k8s/network-policies.yaml

# Apply pod security standards
kubectl apply -f k8s/security-context.yaml

# Verify security policies
kubectl get networkpolicy -n humor-game
kubectl describe networkpolicy -n humor-game

# Test if application still functions with policies
curl -H "Host: kbsonlong.com" -s http://localhost:8080/api/health
```

## You Should See...

**Resource Limits Applied:**
```yaml
Limits:
  cpu:     500m
  memory:  256Mi
Requests:
  cpu:     100m
  memory:  128Mi
```

**HPA Status:**
```bash
NAME           REFERENCE             TARGETS                                     MINPODS   MAXPODS   REPLICAS   AGE
backend-hpa    Deployment/backend    cpu: <unknown>/70%, memory: <unknown>/80%   1         5         1          14s
frontend-hpa   Deployment/frontend   cpu: <unknown>/70%                          1         3         1          14s
```

**Network Policies:**
```bash
NAME                      POD-SELECTOR   AGE
backend-network-policy    app=backend    56s
database-network-policy   app=postgres   56s
frontend-network-policy   app=app=frontend   56s
redis-network-policy      app=redis      56s
```

**Monitoring Stack:**
```bash
NAME                       READY   STATUS    RESTARTS   AGE
prometheus-7c8b7c8b7c8b   1/1     Running   0          15m
grafana-9d8e7d6c5b-def34  1/1     Running   0          20m
```

## ✅ Checkpoint

Your production-grade setup is working when:
- ✅ **Resource limits applied** - pods have CPU/memory limits
- ✅ **Health checks enhanced** - liveness and readiness probes active
- ✅ **Monitoring deployed** - Prometheus and Grafana running and accessible
- ✅ **Autoscaling configured** - HPA created and monitoring resource usage
- ✅ **Real domain access** - Ingress configured for both local and production domains
- ✅ **TLS/HTTPS** - Optional: requires cert-manager setup
- ✅ **Security hardening** - Network policies implemented, security contexts configured

## If It Fails

### Symptom: HPA shows "<unknown>" targets
**Cause:** Metrics server not fully configured in k3d
**Command to confirm:** `kubectl get hpa -n humor-game`
**Fix:**
```bash
# This is expected behavior for k3d - HPA is working, just waiting for metrics data
# HPA is working, just waiting for metrics data

# To verify HPA is working:
kubectl describe hpa backend-hpa -n humor-game
# Should show HPA configuration and status
```

### Symptom: Network policies block application functionality
**Cause:** Overly restrictive network policies
**Command to confirm:** `curl -H "Host: kbsonlong.com" -s http://localhost:8080/api/health`
**Fix:**
```bash
# Check network policy configuration
kubectl describe networkpolicy -n humor-game

# If too restrictive, modify k8s/network-policies.yaml
# Ensure frontend can reach backend (port 3001)
# Ensure backend can reach postgres (port 5432) and redis (port 6379)
```

### Symptom: Security contexts cause pods to fail
**Cause:** Container trying to run as non-root without proper configuration
**Command to confirm:** `kubectl describe pod <pod-name> -n humor-game`
**Fix:**
```bash
# Check security context configuration
kubectl describe deployment frontend -n humor-game | grep -A 5 "Security Context"

# Verify containers are running as non-root users
kubectl exec -it deployment/frontend -n humor-game -- whoami
kubectl exec -it deployment/backend -n humor-game -- whoami

# Expected output: Should show non-root users (e.g., "nginx", "backend")
```

### Symptom: Monitoring stack won't start
**Cause:** Resource constraints or RBAC issues
**Command to confirm:** `kubectl get pods -n monitoring`
**Fix:**
```bash
# Check resource usage
kubectl top nodes

# If resources are low, use minimal monitoring
kubectl apply -f k8s/simple-monitoring.yaml

# Check RBAC configuration
kubectl get serviceaccount -n monitoring
kubectl get clusterrole | grep prometheus
```

## 💡 **Reset/Rollback Commands**

If you need to start over or fix issues:

```bash
# Remove HPA (Horizontal Pod Autoscaler)
kubectl delete hpa backend-hpa -n humor-game
kubectl delete hpa frontend-hpa -n humor-game

# Remove network policies
kubectl delete networkpolicy --all -n humor-game

# Remove cert-manager (if causing issues)
kubectl delete namespace cert-manager

# Reset to basic monitoring
kubectl delete -f k8s/simple-monitoring.yaml
kubectl apply -f k8s/simple-monitoring.yaml

# Rollback deployments to previous versions
kubectl rollout undo deployment/backend -n humor-game
kubectl rollout undo deployment/frontend -n humor-game

# Check current status
kubectl get all -n humor-game
kubectl get hpa -n humor-game
kubectl get networkpolicy -n humor-game
```

## Understanding Production Security

**Security features now active:**
- **Network isolation**: Only allowing necessary communication between pods
- **Non-root execution**: Preventing containers from running as root users
- **Capability restrictions**: Removing unnecessary system privileges
- **Security contexts**: Enforcing security policies at the pod level

**Why it matters:**
- **Prevents attacks**: If one pod is compromised, others are protected
- **Compliance**: Meets enterprise security standards
- **Best practices**: Industry-standard security configurations

## What You Learned

You've implemented enterprise-grade production features:
- **Resource management** preventing resource starvation
- **Automatic scaling** handling traffic spikes
- **Security hardening** protecting against threats
- **TLS termination** encrypting user traffic
- **Comprehensive monitoring** observing system health

## Professional Skills Gained

- **Production readiness** patterns used by major platforms
- **Auto-scaling strategies** for handling variable load
- **Security best practices** for multi-tenant environments
- **Certificate management** for encrypted communications
- **Monitoring and observability** for operational excellence

## 🚨 **Troubleshooting Guide for Beginners**

### **Issue: Cloudflared Login Fails**
**Symptoms:** "Failed to fetch API credentials" or browser doesn't open
**Solutions:**
```bash
# 1. Check internet connection
ping cloudflare.com

# 2. Try manual browser login
open https://dash.cloudflare.com/argotunnel

# 3. Verify cloudflared version
cloudflared --version

# 4. Reinstall if needed
brew uninstall cloudflared
brew install cloudflare/cloudflare/cloudflared
```

### **Issue: Tunnel Creation Fails**
**Symptoms:** "Error creating tunnel" or permission denied
**Solutions:**
```bash
# 1. Check if logged in
ls -la ~/.cloudflared/cert.pem

# 2. Re-authenticate
cloudflared tunnel login

# 3. Try with specific domain
cloudflared tunnel login --zone yourdomain.com

# 4. Check existing tunnels
cloudflared tunnel list
```

### **Issue: DNS Records Not Working**
**Symptoms:** "This site can't be reached" or DNS errors
**Solutions:**
```bash
# 1. Check DNS propagation (takes 5-10 minutes)
nslookup gameapp.yourdomain.com

# 2. Verify tunnel is running
cloudflared tunnel list

# 3. Check tunnel logs
cloudflared tunnel run gameapp-tunnel --loglevel debug

# 4. Recreate DNS record
cloudflared tunnel route dns gameapp-tunnel gameapp.yourdomain.com
```

### **Issue: Local App Not Accessible Through Tunnel**
**Symptoms:** 502 Bad Gateway or connection refused
**Solutions:**
```bash
# 1. Check if local app is running
curl http://localhost:8080/api/health

# 2. Verify port-forwards are active
lsof -i :8080 -i :8090 -i :3000 -i :9090

# 3. Check config.yml service URLs
cat ~/.cloudflared/config.yml

# 4. Test direct connection
curl http://localhost:8080
```

### **Issue: SSL/TLS Certificate Errors**
**Symptoms:** "Your connection is not private" warnings
**Solutions:**
```bash
# 1. Wait for certificate provisioning (takes 5-15 minutes)
# 2. Check Cloudflare SSL settings:
#    - Go to Cloudflare dashboard → SSL/TLS
#    - Set to "Full" or "Full (strict)"
# 3. Clear browser cache
# 4. Try incognito/private browsing mode
```

### **Issue: Monitoring Not Working**
**Symptoms:** Prometheus/Grafana not accessible via tunnel
**Solutions:**
```bash
# 1. Check services are running locally
kubectl get pods -n monitoring
kubectl get pods -n humor-game

# 2. Verify port-forwards
kubectl port-forward svc/prometheus 9090:9090 -n monitoring &
kubectl port-forward svc/grafana 3000:3000 -n monitoring &

# 3. Test local access first
curl http://localhost:9090/api/v1/targets
curl http://localhost:3000/api/health

# 4. Check tunnel config for monitoring services
cat ~/.cloudflared/config.yml | grep -A1 grafana
```

### **Issue: Auto-scaling Not Working**
**Symptoms:** Pods not scaling under load
**Solutions:**
```bash
# 1. Check HPA status
kubectl get hpa -n humor-game

# 2. Check metrics server
kubectl top nodes
kubectl top pods -n humor-game

# 3. Generate load to test
# Use the populate-game-metrics.sh script multiple times

# 4. Check HPA details
kubectl describe hpa backend-hpa -n humor-game
```

### **Quick Diagnostic Commands**

```bash
# Check everything is running
kubectl get all -n humor-game
kubectl get all -n monitoring

# Check tunnel status
cloudflared tunnel list
ps aux | grep cloudflared

# Test all local services
curl http://localhost:8080/api/health        # Game app
curl http://localhost:8090/                  # ArgoCD
curl http://localhost:3000/api/health        # Grafana
curl http://localhost:9090/api/v1/targets    # Prometheus

# Check DNS resolution
nslookup gameapp.yourdomain.com
nslookup argocd.yourdomain.com
```

### **Getting Help**

1. **Check logs:** `cloudflared tunnel run gameapp-tunnel --loglevel debug`
2. **Community:** [Cloudflare Community](https://community.cloudflare.com/)
3. **Documentation:** [Cloudflare Tunnel Docs](https://developers.cloudflare.com/cloudflare-one/connections/connect-apps/)
4. **Status:** [Cloudflare Status](https://www.cloudflarestatus.com/)

## 🎉 **Success Checklist**

Your global deployment is successful when:
- ✅ App accessible via `https://gameapp.yourdomain.com`
- ✅ ArgoCD accessible via `https://argocd.yourdomain.com`
- ✅ Grafana accessible via `https://grafana.yourdomain.com`
- ✅ Prometheus accessible via `https://prometheus.yourdomain.com`
- ✅ All have valid HTTPS certificates (🔒 green lock in browser)
- ✅ Auto-scaling working (check `kubectl get hpa`)
- ✅ Monitoring shows data in Grafana dashboards