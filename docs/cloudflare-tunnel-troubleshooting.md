# Cloudflare Tunnel Troubleshooting Guide

## Overview
This guide covers common Cloudflare Tunnel issues and their solutions, based on real-world troubleshooting experience with k3d Kubernetes clusters.

## Common Issues & Solutions

### Issue 1: HTTP/2 502 Bad Gateway Errors

**Symptoms:**
- All domains return `HTTP/2 502 Bad Gateway`
- Tunnel logs show `i/o timeout` errors
- Local config file changes don't take effect

**Root Cause:**
The tunnel is pointing to an unreachable IP address or port, typically because:
1. The tunnel configuration is stored in Cloudflare's system, not your local config file
2. The tunnel is using old, cached configuration
3. The origin service (k3d ingress controller) is not accessible from the tunnel

**Step-by-Step Solution:**

#### Step 1: Identify the Problem
```bash
# Check tunnel logs for connection errors
cloudflared tunnel run gameapp-tunnel

# Look for errors like:
# "dial tcp 172.20.0.3:80: i/o timeout"
# "Unable to reach the origin service"
```

#### Step 2: Verify Your Local Configuration
```bash
# Check your local config file
cat ~/.cloudflared/config.yml

# Ensure it points to the correct, reachable IP and port
# Example:
# service: http://172.20.10.3:8080  # Correct
# NOT: http://172.20.0.3:80         # Wrong
```

#### Step 3: Check Network Connectivity
```bash
# Verify the target IP is reachable
curl -I "http://172.20.10.3:8080"

# Check what's listening on the target port
lsof -i :8080

# Verify your k3d cluster's external IPs
kubectl get service -n ingress-nginx humor-game-ingress-ingress-nginx-controller
```

#### Step 4: Identify Configuration Mismatch
**Problem:** Your local config file is being ignored because the tunnel is using Cloudflare's stored configuration.

**Solution:** Migrate the tunnel to be dashboard-managed.

#### Step 5: Access Cloudflare Zero Trust Dashboard
1. Go to: `https://one.dash.cloudflare.com/`
2. Navigate to: **Zero Trust** → **Access** → **Tunnels**
3. Find your tunnel (e.g., `gameapp-tunnel`)
4. Look for migration message: "Migrate [tunnel-name]"

#### Step 6: Complete Tunnel Migration
1. Click **"Start migration"**
2. In the migration wizard, verify tunnel name and connectors
3. **CRITICAL:** Update the origin configurations for each hostname:
   - `app.kbsonlong.com` → `http://172.20.10.3:8080`
   - `grafana.kbsonlong.com` → `http://172.20.10.3:8080`
   - `prometheus.kbsonlong.com` → `http://172.20.10.3:8080`
4. Click **"Confirm"** to complete migration

#### Step 7: Restart Your Local Tunnel
```bash
# Kill the old tunnel
pkill -f cloudflared

# Start the tunnel with the new configuration
cloudflared tunnel run gameapp-tunnel
```

#### Step 8: Test All Domains
```bash
# Test main app
curl -I "https://app.kbsonlong.com"

# Test monitoring subdomains
curl -I "https://grafana.kbsonlong.com"
curl -I "https://prometheus.kbsonlong.com"
```

**Expected Results:**
- `app.kbsonlong.com` → HTTP/2 200
- `grafana.kbsonlong.com` → HTTP/2 302 (redirect)
- `prometheus.kbsonlong.com` → HTTP/2 405 (method not allowed - normal)

### Issue 2: Tunnel Ignoring Local Config File

**Symptoms:**
- Changes to `~/.cloudflared/config.yml` don't take effect
- Tunnel continues using old configuration
- Local config file appears to be ignored

**Root Cause:**
The tunnel is using configuration stored in Cloudflare's system, not your local file.

**Solution:**
1. **Migrate the tunnel** to dashboard-managed (see Issue 1, Step 5-6)
2. **Or** explicitly specify the config file:
   ```bash
   cloudflared tunnel run --config ~/.cloudflared/config.yml gameapp-tunnel
   ```

### Issue 3: DNS Resolution vs. Tunnel Configuration Mismatch

**Symptoms:**
- DNS records are correct and proxied
- Tunnel is healthy and connected
- Still getting 502 errors

**Root Cause:**
DNS is working correctly, but the tunnel's internal routing is pointing to the wrong origin.

**Solution:**
1. **Verify DNS is correct** (should show orange cloud icons)
2. **Check tunnel's ingress rules** in Cloudflare dashboard
3. **Update origin services** to point to reachable IPs
4. **Ensure no conflicting ingress rules** exist

### Issue 4: k3d Cluster IP Changes

**Symptoms:**
- Tunnel was working, then stopped working
- IP addresses in tunnel config are outdated
- Network changes in k3d cluster

**Solution:**
1. **Check current k3d external IPs:**
   ```bash
   kubectl get service -n ingress-nginx humor-game-ingress-ingress-nginx-controller
   ```
2. **Update tunnel configuration** with new IPs
3. **Verify port mapping** (e.g., `8080:80` in k3d config)
4. **Test connectivity** to new IP:port combination

## Prevention & Best Practices

### 1. Use Dashboard-Managed Tunnels
- Migrate from locally configured to dashboard-managed
- Easier to update and maintain
- Configuration changes take effect immediately

### 2. Regular Health Checks
```bash
# Check tunnel status
cloudflared tunnel info gameapp-tunnel

# Monitor tunnel logs
cloudflared tunnel run gameapp-tunnel

# Test domain accessibility
curl -I "https://your-domain.com"
```

### 3. Document Your Configuration
- Keep track of IP addresses and ports
- Document k3d cluster configuration
- Maintain a troubleshooting checklist

### 4. Test Before and After Changes
- Always test connectivity before making changes
- Verify changes take effect
- Have a rollback plan

## Troubleshooting Checklist

- [ ] Check tunnel logs for specific error messages
- [ ] Verify local config file contents
- [ ] Test network connectivity to target IP:port
- [ ] Check k3d cluster status and external IPs
- [ ] Verify DNS records are correct and proxied
- [ ] Check if tunnel needs migration to dashboard-managed
- [ ] Update tunnel ingress rules with correct origin services
- [ ] Restart tunnel after configuration changes
- [ ] Test all domains after fixes

## Common Error Messages & Solutions

| Error Message | Cause | Solution |
|---------------|-------|----------|
| `HTTP/2 502 Bad Gateway` | Origin unreachable | Check IP:port, update tunnel config |
| `i/o timeout` | Network connectivity issue | Verify target is reachable |
| `dial tcp [IP]:[PORT]` | Wrong IP or port | Update tunnel configuration |
| `Unable to reach origin service` | Service down or misconfigured | Check k3d cluster and ingress |

## Support Resources

- [Cloudflare Tunnel Documentation](https://developers.cloudflare.com/cloudflare-one/connections/connect-apps/)
- [Zero Trust Dashboard](https://one.dash.cloudflare.com/)
- [Cloudflare Community](https://community.cloudflare.com/)

---

**Last Updated:** August 26, 2025  
**Based on:** Real troubleshooting experience with k3d + Cloudflare Tunnel setup
