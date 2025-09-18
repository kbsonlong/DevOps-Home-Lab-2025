# 🔧 Troubleshooting Guide - Humor Memory Game

## **Overview**
This guide covers common issues you might encounter while setting up and running your Humor Memory Game with monitoring, and provides step-by-step solutions.

## **🚨 Common Issues & Quick Fixes**

### **1. "No Data" in Grafana Dashboards**

#### **Problem**
Grafana panels show "No data" instead of metrics.

#### **Causes & Solutions**

**A. Prometheus Not Scraping Targets**
```bash
# Check if Prometheus can see your pods
kubectl get pods -n humor-game -o yaml | grep -A 5 -B 5 prometheus

# Expected: Should see prometheus.io/scrape annotations
```

**B. Missing Prometheus Annotations**
```bash
# Check if your pods have the right labels
kubectl get pods -n humor-game --show-labels

# Should see: app=backend, app=frontend
```

**C. Prometheus Targets Empty**
```bash
# Check Prometheus targets page
# Go to: http://localhost:9090/targets
# Should see: kubernetes-pods targets
```

#### **Fix**
```bash
# Redeploy with proper annotations
kubectl apply -f k8s/backend.yaml
kubectl apply -f k8s/frontend.yaml
```

### **2. Port-Forwarding Issues**

#### **Problem**
```bash
# Error: Unable to listen on port XXXX: bind: address already in use
```

#### **Solution**
```bash
# Kill existing port-forwards
lsof -ti:3000 | xargs kill -9
lsof -ti:9090 | xargs kill -9
lsof -ti:3001 | xargs kill -9

# Start fresh port-forwards
kubectl port-forward -n monitoring svc/grafana 3000:3000 &
kubectl port-forward -n monitoring svc/prometheus 9090:9090 &
kubectl port-forward -n humor-game svc/backend 3001:3001 &
```

### **3. Backend Connection Issues**

#### **Problem**
Scripts get HTTP 000 errors when trying to connect to backend.

#### **Solution**
```bash
# Check if backend port-forward is running
lsof -i :3001

# If not running, start it
kubectl port-forward -n humor-game svc/backend 3001:3001 &

# Test connection
curl -s http://localhost:3001/health
```

### **4. Prometheus Pod Won't Start**

#### **Problem**
```bash
# Error: service account "prometheus" not found
```

#### **Solution**
```bash
# Check if RBAC is configured
kubectl get serviceaccount -n monitoring

# If missing, apply RBAC
kubectl apply -f k8s/prometheus-rbac.yaml

# Check cluster roles
kubectl get clusterrole | grep prometheus
```

### **5. Grafana Dashboard Import Issues**

#### **Problem**
```bash
# Error: Dashboard title cannot be empty
# Dashboard creation loop
```

#### **Solution**
```bash
# Use the fixed dashboard files
# Import: k8s/working-dashboard.json
# Import: k8s/advanced-custom-dashboard.json

# Or export existing dashboard and edit
# In Grafana: Dashboard → Settings → Export → Export for sharing externally
```

### **6. Monitoring Ingress Access Issues (Browser Loading Problems)**

#### **Problem**
- Browser never loads `http://prometheus.kbsonlong.com:8080`
- Browser never loads `http://grafana.kbsonlong.com:8080`
- Pages keep loading indefinitely
- "This site can't be reached" errors

#### **Root Cause**
k3d cluster port mapping requires localhost instead of cluster IP in `/etc/hosts`.

#### **Solution**
```bash
# 1. Fix hosts file entries
sudo sed -i '' '/prometheus.kbsonlong.com/d' /etc/hosts
sudo sed -i '' '/grafana.kbsonlong.com/d' /etc/hosts

# Add correct localhost entries
echo "127.0.0.1 prometheus.kbsonlong.com" | sudo tee -a /etc/hosts
echo "127.0.0.1 grafana.kbsonlong.com" | sudo tee -a /etc/hosts

# 2. Verify ingress controller is running
kubectl get pods -n ingress-nginx

# 3. Check ingress configuration
kubectl get ingress -A

# 4. Test connectivity
curl -s --max-time 5 -u "admin:admin123" -H "Host: prometheus.kbsonlong.com" http://localhost:8080/-/healthy
curl -s --max-time 5 -u "admin:admin123" -H "Host: grafana.kbsonlong.com" http://localhost:8080/api/health
```

#### **Access URLs (Fixed)**
- **Prometheus**: http://prometheus.kbsonlong.com:8080
- **Grafana**: http://grafana.kbsonlong.com:8080
- **Credentials**: admin/admin123

### **7. Monitoring Authentication Issues**

#### **Problem**
```bash
# Error: 401 Authorization Required
# Basic auth not working
```

#### **Root Cause**
Incorrect htpasswd format in monitoring-auth secret.

#### **Solution**
```bash
# 1. Generate proper htpasswd format
htpasswd -bn admin admin123

# 2. Update secret with base64 encoded htpasswd
NEW_AUTH=$(htpasswd -bn admin admin123 | base64 -w 0)
kubectl patch secret monitoring-auth -n monitoring --type='json' -p="[{\"op\": \"replace\", \"path\": \"/data/auth\", \"value\": \"$NEW_AUTH\"}]"

# 3. Restart ingress controller to pick up changes
kubectl rollout restart deployment -n ingress-nginx humor-game-ingress-ingress-nginx-controller

# 4. Wait for restart and test
kubectl wait --for=condition=ready pod -l app.kubernetes.io/name=ingress-nginx -n ingress-nginx --timeout=60s
curl -s -u "admin:admin123" -H "Host: prometheus.kbsonlong.com" http://localhost:8080/-/healthy
```

## **🏗️ Milestone-Specific Troubleshooting**

### **🔧 Milestone 0: Setup & Prerequisites**

#### **Problem: Docker Permission Errors**
```bash
# If you get "permission denied" errors:
sudo usermod -aG docker $USER
newgrp docker
# Then test: docker run hello-world
```

#### **Problem: kubectl Not Found**
```bash
# Ensure kubectl is in your PATH
echo $PATH
# If missing, add to your shell profile:
echo 'export PATH=$PATH:/usr/local/bin' >> ~/.bashrc
source ~/.bashrc
```

#### **Problem: Docker Desktop Missing (macOS)**
```bash
# Alternative: Use Colima (already configured)
brew install colima
colima start --cpu 2 --memory 4 --disk 20

# Or install Docker Desktop from:
# https://www.docker.com/products/docker-desktop
```

#### **Problem: Insufficient Resources**
```bash
# For low RAM systems, use minimal cluster:
k3d cluster create dev-cluster \
  --servers 1 \
  --agents 1 \
  --k3s-arg --disable=traefik@server:0

# Monitor resource usage:
kubectl top nodes
kubectl top pods --all-namespaces
```

### **🏗️ Milestone 1: Docker Compose Issues**

#### **Problem: Containers Keep Restarting**
```bash
# Check logs for the problematic service
docker-compose logs backend
docker-compose logs postgres

# Common fix: Wait longer for database initialization
docker-compose down
docker-compose up -d
sleep 60  # Give more time for startup
```

#### **Problem: Frontend Shows "Cannot Connect to Game Server"**
```bash
# Verify backend is accessible
curl http://localhost:3001/health

# Check backend logs for errors
docker-compose logs backend

# Restart just the backend if needed
docker-compose restart backend
```

#### **Problem: Port Conflicts**
```bash
# Check for port conflicts
lsof -i :3000 -i :3001 -i :5432 -i :6379

# Kill conflicting processes
sudo lsof -ti:3000,3001,5432,6379 | xargs kill -9

# Restart Docker/Colima
colima restart

# Clean rebuild
docker-compose down -v
docker-compose up -d --build
```

#### **Problem: Database Connection Issues**
```bash
# Check database logs
docker-compose logs postgres

# Check Redis logs
docker-compose logs redis

# Test connections
docker-compose exec postgres psql -U postgres -d humor_game -c "\dt"
docker-compose exec redis redis-cli ping
```

### **🚀 Milestone 2: Kubernetes Core Issues**

#### **Problem: Cluster Won't Start**
```bash
# Check k3d cluster status
k3d cluster list

# If cluster missing, recreate
k3d cluster delete humor-game-cluster
k3d cluster create --config k3d-config.yaml

# Check nodes
kubectl get nodes -o wide
```

#### **Problem: Pods Stuck in Pending**
```bash
# Check what's wrong
kubectl describe pod <pod-name> -n humor-game

# Common cause: Insufficient resources
kubectl top nodes  # Check resource usage

# Check events
kubectl get events -n humor-game --sort-by='.lastTimestamp'

# Common fixes
kubectl delete pod <pod-name> -n humor-game  # Force restart
kubectl apply -f k8s/namespace.yaml          # Recreate namespace
```

#### **Problem: Backend Can't Connect to Database**
```bash
# Check backend logs
kubectl logs -l app=backend -n humor-game

# Verify database service exists
kubectl get svc postgres -n humor-game

# Test database connectivity
kubectl exec -it deployment/postgres -n humor-game -- psql -U gameuser -d humor_memory_game -c "SELECT 1;"
```

#### **Problem: Frontend Not Loading Correctly**
```bash
# Problem: Frontend nginx catch-all location block overriding static asset paths
# Solution: Reorder nginx location blocks with ^~ prefix matching
# Fix: Update frontend/nginx.conf to prioritize /scripts/, /styles/, /components/

# Verify fix:
curl -H "Host: kbsonlong.com" -I http://localhost:8080/scripts/game.js
# Should return: Content-Type: application/javascript, not text/html
```

#### **Problem: Backend Redis Connection Failing**
```bash
# Problem: Kubernetes sets REDIS_PORT=tcp://host:port instead of just port
# Error: redis://:password@redis:tcp://10.43.201.171:6379/0 (ERR_INVALID_URL)

# Solution: Universal Redis connection logic for both environments
# Fix: Update backend/utils/redis.js to handle tcp:// prefix in REDIS_PORT

# Verify fix:
kubectl logs -l app=backend -n humor-game | grep "Redis: Connected"
# Should show: ✅ Redis: Connected and ready!
```

#### **Problem: Frontend JavaScript Configuration Race Condition**
```bash
# Problem: window.API_BASE_URL not set when game.js executes
# Error: "Cannot Connect to Game Server" in browser

# Solution: Async configuration loader with waitForConfig()
# Fix: Implement Promise-based config waiting in frontend/src/scripts/game.js

# Verify fix:
# Browser console should show: ✅ Configuration loaded successfully
```

#### **Problem: Image Pull Errors (ErrImagePull/ImagePullBackOff)**
```bash
# Problem: Kubernetes trying to pull images from external registries
# Error: "Failed to pull image: failed to resolve reference"

# Solution: Use local images with imagePullPolicy: Never
# Fix: Build images locally first, then deploy
docker build -t humor-game-frontend:latest ./frontend
docker build -t humor-game-backend:latest ./backend

# Check image availability
docker images | grep -E "(backend|frontend)"

# Force image pull
docker pull node:18-alpine
docker pull postgres:15-alpine
docker pull redis:7-alpine
```

#### **Problem: Service Discovery Issues**
```bash
# Check services
kubectl get svc -n humor-game

# Check endpoints
kubectl get endpoints -n humor-game

# Test internal connectivity
kubectl run test-pod --image=curlimages/curl -i --rm --restart=Never -- curl backend.humor-game.svc.cluster.local:3001/health
```

### **🌐 Milestone 3: Ingress Issues**

#### **Problem: Ingress Controller Not Working**
```bash
# Check ingress controller
kubectl get pods -n ingress-nginx

# If missing, reinstall
kubectl apply -f https://raw.githubusercontent.com/kubernetes/ingress-nginx/controller-v1.8.2/deploy/static/provider/cloud/deploy.yaml

# Wait for ready
kubectl wait --namespace ingress-nginx --for=condition=ready pod --selector=app.kubernetes.io/component=controller --timeout=300s
```

#### **Problem: Application Not Accessible via Domain**
```bash
# Check ingress configuration
kubectl get ingress -n humor-game
kubectl describe ingress humor-game-ingress -n humor-game

# Check hosts file
grep kbsonlong.com /etc/hosts

# Should see: 127.0.0.1 kbsonlong.com

# Test connectivity
curl -H "Host: kbsonlong.com" http://localhost:8080/
curl -H "Host: kbsonlong.com" http://localhost:8080/api/health
```

#### **Problem: Ingress Not Routing /api/* Requests to Backend**
```bash
# Problem: Ingress routing correct but backend missing /api/* routes
# Error: {"error":"Not Found","message":"API endpoint not found! 🔍"}

# Solution: Add /api/* routes to backend server.js
# Fix: Ensure backend has app.get('/api/health', ...) and app.use('/api/*', ...)

# Verify fix:
curl -H "Host: kbsonlong.com" -s http://localhost:8080/api/health
# Should return: {"status":"healthy",...}
```

#### **Problem: SSL/TLS Certificate Issues**
```bash
# Check certificate status
kubectl get certificates -n humor-game

# Check cert-manager logs
kubectl logs -n cert-manager deployment/cert-manager

# Force certificate renewal
kubectl delete certificate <cert-name> -n humor-game
kubectl apply -f k8s/ingress.yaml
```

### **📊 Milestone 4: Monitoring Issues**

#### **Problem: Monitoring Stack Status**
```bash
# Check all monitoring pods
kubectl get pods -n monitoring

# Expected: prometheus and grafana pods with "1/1 Running"
# If not running, check logs:
kubectl logs -f deployment/prometheus -n monitoring
kubectl logs -f deployment/grafana -n monitoring
```

#### **Problem: Prometheus Can't Scrape Metrics**
```bash
# Verify targets are being discovered
kubectl get endpoints -n humor-game

# Check if pods have prometheus annotations
kubectl get pods -n humor-game -o yaml | grep -A 5 -B 5 prometheus

# Expected: Should see prometheus.io/scrape: "true"

# Check service monitors
kubectl get servicemonitor -n monitoring

# Test metrics endpoints
kubectl port-forward -n humor-game svc/backend 3001:3001 &
curl http://localhost:3001/metrics
```

#### **Problem: No Metrics Showing in Grafana**
```bash
# Check Prometheus is scraping targets
# Go to http://localhost:9090/targets
# All targets should show "UP" status

# Check ServiceMonitor configuration
kubectl get servicemonitor -n monitoring

# Verify pods have metric endpoints
kubectl get endpoints -n humor-game
```

#### **Problem: Grafana Shows "No Data"**
```bash
# Test Prometheus data source in Grafana
# Go to Configuration -> Data Sources -> Test
# Should show "Data source is working"

# Check Prometheus has data
# In Prometheus UI, try query: up
# Should return 1 for healthy targets
```

#### **Problem: Dashboards Are Empty**
```bash
# Verify correct namespace in queries
# Query should include: {namespace="humor-game"}

# Check metric names are correct
# In Prometheus, use "Metrics" dropdown to see available metrics

# Generate some traffic to create data
curl -H "Host: kbsonlong.com" http://localhost:8080/api/health
```

#### **Problem: Prometheus Pod Won't Start**
```bash
# Check RBAC configuration
kubectl get serviceaccount -n monitoring
kubectl get clusterrole | grep prometheus

# If missing, apply RBAC
kubectl apply -f k8s/prometheus-rbac.yaml

# Test permissions
kubectl auth can-i list pods --as=system:serviceaccount:monitoring:prometheus
# Expected: "yes"
```

#### **Problem: Port-Forwarding Not Working**
```bash
# Check what's using the ports
lsof -i :3000  # Grafana
lsof -i :9090  # Prometheus
lsof -i :3001  # Backend (if using)

# Kill conflicting processes
lsof -ti:3000 | xargs kill -9
lsof -ti:9090 | xargs kill -9

# Restart port-forwards
kubectl port-forward -n monitoring svc/grafana 3000:3000 &
kubectl port-forward -n monitoring svc/prometheus 9090:9090 &
```

#### **Problem: Test Connectivity**
```bash
# Test Prometheus
curl -s http://localhost:9090/-/healthy
# Expected: "OK"

# Test Grafana
curl -s http://localhost:3000/api/health
# Expected: {"database":"ok","version":"x.x.x"}

# Test Backend (if port-forwarding)
curl -s http://localhost:3001/health
# Expected: {"status":"healthy",...}
```

#### **Problem: Generate Test Data**
```bash
# Run metrics test script
./scripts/production-metrics-test-ingress.sh

# Or manually generate traffic
for i in {1..50}; do
  curl -H "Host: kbsonlong.com" http://localhost:8080/api/health > /dev/null 2>&1
  sleep 0.5
done
```

### **🔄 Milestone 5+: Advanced Issues**

#### **Problem: High Resource Usage**
```bash
# Check system resources
kubectl top nodes
kubectl top pods --all-namespaces

# Check Colima/Docker resources
colima status
docker stats

# Increase resources if needed
colima stop
colima start --cpu 8 --memory 8 --disk 100
```

#### **Problem: Network Policies Blocking Traffic**
```bash
# Check network policies
kubectl get networkpolicy --all-namespaces

# Temporarily disable for testing
kubectl delete networkpolicy --all -n humor-game

# Check for CNI issues
kubectl get pods -n kube-system | grep -E "(flannel|calico|weave)"
```

#### **Problem: Persistent Volume Issues**
```bash
# Check PV and PVC status
kubectl get pv
kubectl get pvc -n humor-game
kubectl get pvc -n monitoring

# Check storage class
kubectl get storageclass

# Force recreate if needed
kubectl delete pvc --all -n humor-game
kubectl apply -f k8s/postgres.yaml
```

## **🔍 Diagnostic Commands**

### **Check Pod Status**
```bash
# All namespaces
kubectl get pods --all-namespaces

# Specific namespace
kubectl get pods -n humor-game
kubectl get pods -n monitoring

# Detailed pod info
kubectl describe pod <pod-name> -n <namespace>
```

### **Check Services**
```bash
# List all services
kubectl get svc --all-namespaces

# Check specific service
kubectl get svc backend -n humor-game
kubectl get svc prometheus -n monitoring
```

### **Check Logs**
```bash
# Backend logs
kubectl logs -f deployment/backend -n humor-game

# Prometheus logs
kubectl logs -f deployment/prometheus -n monitoring

# Grafana logs
kubectl logs -f deployment/grafana -n monitoring
```

### **Check Network Policies**
```bash
# List network policies
kubectl get networkpolicy --all-namespaces

# Check if policies are blocking traffic
kubectl describe networkpolicy <policy-name> -n <namespace>
```

### **Check Resource Usage**
```bash
# Node resources
kubectl top nodes

# Pod resources
kubectl top pods --all-namespaces

# Check if pods are resource-constrained
kubectl describe pod <pod-name> -n <namespace> | grep -A 10 Events
```

## **📊 Monitoring Health Checks**

### **1. Prometheus Health**
```bash
# Check if Prometheus is responding
curl -s http://localhost:9090/-/healthy

# Check targets
curl -s http://localhost:9090/api/v1/targets | jq '.data.activeTargets | length'

# Expected: Should see multiple targets
```

### **2. Grafana Health**
```bash
# Check if Grafana is responding
curl -s http://localhost:3000/api/health

# Expected: {"database":"ok","version":"x.x.x"}
```

### **3. Backend Health**
```bash
# Check backend health
curl -s http://localhost:3001/health

# Expected: {"status":"healthy","services":{"database":"connected","redis":"connected"}}
```

### **4. Metrics Endpoint**
```bash
# Check if metrics are being generated
curl -s http://localhost:3001/metrics | grep -c "http_requests_total"

# Expected: Should see numbers > 0
```

## **🚀 Performance Issues**

### **1. Slow Pod Creation**
```bash
# Check image pull status
kubectl describe pod <pod-name> -n <namespace> | grep -A 5 Events

# Check if images are being pulled
kubectl get events -n <namespace> --sort-by='.lastTimestamp'
```

**Expected Times:**
- **Prometheus**: 10-15 minutes first time, 2-5 minutes subsequent
- **Grafana**: 5-10 minutes first time, 2-3 minutes subsequent
- **Backend/Frontend**: 2-5 minutes

### **2. High Resource Usage**
```bash
# Check Colima resources
colima status

# If under-resourced, restart with more resources
colima stop
colima start --cpu 8 --memory 8 --disk 100
```

### **3. Slow Metrics Collection**
```bash
# Check Prometheus scrape interval
# Default: 15 seconds
# If too fast: Can cause performance issues

# Check target discovery
# Should see targets in "up" state
```

## **📝 Common Error Messages & Solutions**

### **"connection refused"**
```bash
# Service not running or port-forward not active
kubectl get svc -n <namespace>
lsof -i :<port>
```

### **"permission denied"**
```bash
# RBAC issue
kubectl get serviceaccount -n monitoring
kubectl get clusterrole | grep prometheus
```

### **"no route to host"**
```bash
# Network policy blocking traffic
kubectl get networkpolicy --all-namespaces
```

### **"image pull backoff"**
```bash
# Image not available or registry issue
kubectl describe pod <pod-name> -n <namespace>
```

## **🔧 Quick Fix Scripts**

### **Reset Everything**
```bash
#!/bin/bash
# Kill all port-forwards
lsof -ti:3000 | xargs kill -9
lsof -ti:9090 | xargs kill -9
lsof -ti:3001 | xargs kill -9

# Restart port-forwards
kubectl port-forward -n monitoring svc/grafana 3000:3000 &
kubectl port-forward -n monitoring svc/prometheus 9090:9090 &
kubectl port-forward -n humor-game svc/backend 3001:3001 &

echo "Port-forwards restarted!"
```

### **Check All Services**
```bash
#!/bin/bash
echo "🔍 Checking all services..."

echo "📊 Pods Status:"
kubectl get pods --all-namespaces

echo "🌐 Services Status:"
kubectl get svc --all-namespaces

echo "🔐 RBAC Status:"
kubectl get serviceaccount -n monitoring
kubectl get clusterrole | grep prometheus

echo "✅ Health Checks:"
curl -s http://localhost:3000/api/health || echo "Grafana: ❌"
curl -s http://localhost:9090/-/healthy || echo "Prometheus: ❌"
curl -s http://localhost:3001/health || echo "Backend: ❌"
```

## **📚 Additional Resources**

- [Prometheus RBAC Guide](prometheus-rbac-guide.md) - Detailed RBAC explanation
- [Home Lab Setup](../home-lab.md) - Complete setup guide
- [Kubernetes Troubleshooting](https://kubernetes.io/docs/tasks/debug/) - Official docs

---

**Remember**: Most issues are related to port-forwarding, RBAC, or resource constraints. Start with the basic checks and work your way up! 🔧✅
