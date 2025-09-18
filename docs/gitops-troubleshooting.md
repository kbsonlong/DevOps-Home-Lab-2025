# GitOps Troubleshooting Guide: Real-World Solutions from Our Implementation

*This guide covers the actual issues we encountered and how we solved them during our GitOps implementation*

## 🚨 Critical Issues We Faced and Fixed

### Issue 1: Application Downtime After Initial ArgoCD Setup

**Problem:** App went down with 503 errors after first ArgoCD implementation
**Root Cause:** ArgoCD was trying to manage resources with different labels than our working app
**Impact:** Complete app outage

**Solution Applied:**
```bash
# 1. Delete problematic ArgoCD setup
kubectl delete application humor-game-dev -n argocd --force

# 2. Manually recreate services to restore app
kubectl apply -f k8s/redis.yaml
kubectl apply -f k8s/postgres.yaml
kubectl apply -f k8s/backend.yaml
kubectl apply -f k8s/frontend.yaml

# 3. Verify app is working
kubectl get pods -n humor-game
curl http://kbsonlong.com:8080/health
```

**Lesson Learned:** Always test GitOps changes on a copy, never on production first

### Issue 2: "Missing" Health Status in ArgoCD

**Problem:** ArgoCD application showed "Missing" health status
**Root Cause:** Resource configuration conflicts and validation errors

**Solution Applied:**
```bash
# 1. Simplify kustomization to avoid conflicts
# Remove complex resources temporarily
# Start with only ConfigMaps and PVCs

# 2. Force ArgoCD refresh
kubectl patch application humor-game-monitor -n argocd \
  --type='merge' \
  -p='{"metadata": {"annotations": {"argocd.argoproj.io/refresh": "true"}}}'

# 3. Gradually add resources back
# Add infrastructure first, then deployments, then dependent resources
```

**Lesson Learned:** Build GitOps foundation first, add complexity gradually

### Issue 3: SharedResourceWarning with Deleted Application

**Problem:** Warning about resources shared between deleted and current ArgoCD applications
**Root Cause:** Stale `argocd.argoproj.io/tracking-id` annotations

**Solution Applied:**
```bash
# 1. Find the stale annotation
kubectl get configmap humor-game-config -n humor-game -o yaml | grep tracking-id

# 2. Remove the stale annotation
kubectl annotate configmap humor-game-config -n humor-game \
  argocd.argoproj.io/tracking-id-

# 3. Remove old ArgoCD labels
kubectl label configmap humor-game-config -n humor-game \
  app.kubernetes.io/managed-by- \
  app.kubernetes.io/part-of-
```

**Lesson Learned:** ArgoCD leaves hidden annotations that can cause conflicts

### Issue 4: HPA "Unknown" Health Status

**Problem:** HPAs showing "Unknown" health in ArgoCD
**Root Cause:** Normal behavior for dynamic resources like HPAs

**Solution Applied:**
```bash
# 1. Verify HPAs are actually working
kubectl get hpa -n humor-game

# 2. Check if they're scaling correctly
kubectl describe hpa backend-hpa -n humor-game

# 3. Remove HPAs from GitOps (they work fine without it)
# Delete hpa.yaml from gitops-safe/base/
# Remove from kustomization.yaml
```

**Lesson Learned:** Some resources don't need GitOps management if they work fine independently

## 🔍 Diagnostic Commands

### 1. **Check ArgoCD Application Status**
```bash
# Basic status
kubectl get applications -n argocd

# Detailed status
kubectl describe application humor-game-monitor -n argocd

# Resource count
kubectl describe application humor-game-monitor -n argocd | grep "Kind:" | wc -l
```

### 2. **Check Resource Health**
```bash
# All resources in namespace
kubectl get all -n humor-game

# Specific resource types
kubectl get deployments -n humor-game
kubectl get services -n humor-game
kubectl get hpa -n humor-game

# Resource details
kubectl describe deployment backend -n humor-game
```

### 3. **Check ArgoCD Logs**
```bash
# ArgoCD controller logs
kubectl logs -n argocd deployment/argocd-application-controller

# ArgoCD server logs
kubectl logs -n argocd deployment/argocd-server

# Follow logs in real-time
kubectl logs -f -n argocd deployment/argocd-application-controller
```

### 4. **Check Git vs Cluster Differences**
```bash
# Compare specific resource
kubectl diff -f gitops-safe/base/backend.yaml

# Compare entire directory
kubectl diff -f gitops-safe/base/

# Check what ArgoCD sees
kubectl describe application humor-game-monitor -n argocd | grep -A 50 "Resources:"
```

## 🚨 Common Error Messages and Solutions

### Error: "AppProject in version 'v1alpha1' cannot be handled"

**Cause:** Invalid YAML syntax in AppProject
**Solution:**
```yaml
# ❌ Wrong - invalid field
spec:
  syncPolicy: {}  # This field doesn't exist in AppProject

# ✅ Correct - remove invalid fields
spec:
  description: "Safe GitOps for Humor Game"
  sourceRepos:
  - https://github.com/YOUR_USERNAME/YOUR_REPO
```

### Error: "Application is invalid: spec.syncPolicy.automated: Invalid value"

**Cause:** Incorrect automated sync policy syntax
**Solution:**
```yaml
# ❌ Wrong - boolean value
syncPolicy:
  automated: false

# ✅ Correct - empty object
syncPolicy:
  automated: {}
```

### Error: "SharedResourceWarning: ConfigMap is part of multiple applications"

**Cause:** Resource managed by multiple ArgoCD applications
**Solution:**
```bash
# 1. Find all applications managing the resource
kubectl get applications -n argocd

# 2. Delete conflicting applications
kubectl delete application conflicting-app -n argocd

# 3. Clean up annotations
kubectl annotate configmap resource-name -n namespace \
  argocd.argoproj.io/tracking-id-
```

### Error: "ComparisonError: path not found"

**Cause:** GitOps path doesn't exist in repository
**Solution:**
```bash
# 1. Check if path exists
ls -la gitops-safe/overlays/dev/

# 2. Commit and push changes
git add gitops-safe/
git commit -m "Add GitOps configuration"
git push origin gitops

# 3. Verify ArgoCD can access the path
kubectl describe application app-name -n argocd | grep "Source:"
```

## 🔧 Troubleshooting Process

### Step 1: **Assess the Situation**
```bash
# Check immediate status
kubectl get applications -n argocd
kubectl get pods -n humor-game

# Check app functionality
curl http://kbsonlong.com:8080/health
```

### Step 2: **Identify the Problem**
```bash
# Check ArgoCD logs for errors
kubectl logs -n argocd deployment/argocd-application-controller | tail -50

# Check application details
kubectl describe application app-name -n argocd

# Check resource differences
kubectl diff -f gitops-safe/base/
```

### Step 3: **Apply the Fix**
```bash
# Fix configuration files
# Commit and push changes
git add gitops-safe/
git commit -m "Fix: [describe the fix]"
git push origin gitops

# Force ArgoCD refresh if needed
kubectl patch application app-name -n argocd \
  --type='merge' \
  -p='{"metadata": {"annotations": {"argocd.argoproj.io/refresh": "true"}}}'
```

### Step 4: **Verify the Solution**
```bash
# Wait for ArgoCD to process changes
sleep 15

# Check status
kubectl get application app-name -n argocd

# Test app functionality
curl http://kbsonlong.com:8080/health
```

## 🚨 Emergency Recovery Procedures

### If App Goes Down Completely

**Immediate Action:**
```bash
# 1. Stop ArgoCD from making changes
kubectl delete application humor-game-monitor -n argocd

# 2. Restore from working backup
kubectl apply -f k8s/redis.yaml
kubectl apply -f k8s/postgres.yaml
kubectl apply -f k8s/backend.yaml
kubectl apply -f k8s/frontend.yaml

# 3. Verify app is working
kubectl get pods -n humor-game
curl http://kbsonlong.com:8080/health
```

**After Recovery:**
```bash
# 1. Investigate what went wrong
kubectl logs -n argocd deployment/argocd-application-controller

# 2. Fix the GitOps configuration
# 3. Test with a simple setup first
# 4. Gradually add complexity back
```

### If ArgoCD Becomes Unresponsive

**Diagnostic Steps:**
```bash
# 1. Check ArgoCD pod status
kubectl get pods -n argocd

# 2. Check ArgoCD logs
kubectl logs -n argocd deployment/argocd-server

# 3. Restart ArgoCD if needed
kubectl rollout restart deployment/argocd-server -n argocd
kubectl rollout restart deployment/argocd-application-controller -n argocd
```

## 🎯 Prevention Best Practices

### 1. **Always Test First**
- Test GitOps changes on a copy of your app
- Use separate namespaces for testing
- Never apply untested changes to production

### 2. **Start Simple**
- Begin with monitoring-only setup
- Add resources gradually
- Avoid complex configurations initially

### 3. **Keep Backups**
```bash
# Backup current state before changes
mkdir -p ~/gitops-backup
kubectl get all,configmap,secret,ingress -n humor-game -o yaml > ~/gitops-backup/current-state.yaml

# Backup ArgoCD configuration
kubectl get application,appproject -n argocd -o yaml > ~/gitops-backup/argocd-config.yaml
```

### 4. **Monitor Changes**
```bash
# Watch ArgoCD application status
watch kubectl get application humor-game-monitor -n argocd

# Monitor resource changes
kubectl get events -n humor-game --sort-by='.lastTimestamp'
```

## 📚 Additional Resources

### Debugging Tools
- **ArgoCD CLI**: `argocd` command-line tool
- **Kubernetes Lens**: Visual cluster management
- **K9s**: Terminal-based cluster browser

### Documentation
- [ArgoCD Troubleshooting](https://argo-cd.readthedocs.io/en/stable/operator-manual/troubleshooting/)
- [Kubernetes Debugging](https://kubernetes.io/docs/tasks/debug/)
- [GitOps Best Practices](https://www.gitops.tech/)

---

*Remember: GitOps troubleshooting is iterative. Each issue you solve makes your setup more robust. Document your solutions and share them with your team.*
