# Global Deployment Troubleshooting Guide

*A comprehensive guide to diagnosing and fixing common issues in global deployments using Cloudflare, cert-manager, and Kubernetes*

## 🚨 Critical Issues We Faced and Fixed

### **Issue 1: Redirect Loops (ERR_TOO_MANY_REDIRECTS)**

**Symptoms:**
- Browser shows "ERR_TOO_MANY_REDIRECTS"
- Infinite redirects between HTTP and HTTPS
- Tunnel subdomain not accessible

**Root Cause:**
- SSL redirects enabled in ingress for tunnel subdomain
- Cloudflare tunnel trying to handle SSL while ingress also redirects
- Conflicting SSL configurations

**Solution:**
```bash
# Create separate ingress for tunnel subdomain without SSL redirects
# File: k8s/tunnel-ingress.yaml
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: tunnel-ingress
  namespace: humor-game
  annotations:
    nginx.ingress.kubernetes.io/cors-allow-origin: "*"
    nginx.ingress.kubernetes.io/cors-allow-credentials: "true"
    # No SSL redirect for tunnel to prevent loops
spec:
  ingressClassName: humor-game-nginx
  rules:
    - host: app.yourdomain.com  # Tunnel subdomain
      http:
        paths:
          - path: /
            pathType: Prefix
            backend:
              service:
                name: frontend
                port:
                  number: 80
```

**Prevention:**
- Use separate ingress configurations for tunnel and main domain
- Disable SSL redirects for tunnel subdomains
- Test both configurations independently

### **Issue 2: DNS Propagation Delays**

**Symptoms:**
- Domain still shows old nameservers
- SSL certificates not generating
- Let's Encrypt validation failing

**Root Cause:**
- Nameserver changes take 24-48 hours to propagate globally
- Different DNS providers update at different rates
- Local DNS cache may show old results

**Diagnostic Commands:**
```bash
# Check nameserver status
dig yourdomain.com NS
nslookup yourdomain.com

# Check from different locations
# Use whatsmydns.net for global checking
# Use online DNS checkers from different countries

# Check local DNS cache
sudo dscacheutil -flushcache  # macOS
sudo systemctl restart systemd-resolved  # Linux
```

**Solution:**
- Wait for DNS propagation (24-48 hours)
- Monitor progress at [whatsmydns.net](https://whatsmydns.net)
- Use tunnel access while waiting for DNS

**Prevention:**
- Plan DNS changes during low-traffic periods
- Have tunnel access ready before changing nameservers
- Test from multiple locations to confirm propagation

### **Issue 3: Cloudflare Tunnel Configuration Problems**

**Symptoms:**
- Tunnel shows "No ingress rules were defined"
- Tunnel connects but returns 503 errors
- Configuration file not being read

**Root Cause:**
- Configuration file in wrong location
- Incorrect file permissions
- Configuration syntax errors

**Diagnostic Commands:**
```bash
# Check tunnel status
cloudflared tunnel list
cloudflared tunnel info YOUR_TUNNEL_ID

# Check configuration file location
ls -la ~/.cloudflared/
cat ~/.cloudflared/config.yml

# Check tunnel logs
cloudflared tunnel run YOUR_TUNNEL_ID --loglevel=debug
```

**Solution:**
```bash
# Create configuration in correct location
cat > ~/.cloudflared/config.yml << 'EOF'
tunnel: YOUR_TUNNEL_ID
credentials-file: /Users/YOUR_USER/.cloudflared/YOUR_TUNNEL_ID.json

ingress:
  - hostname: app.yourdomain.com
    service: http://localhost:8080
    originRequest:
      originServerName: kbsonlong.com
      noTLSVerify: true
      disableChunkedEncoding: true
  
  - service: http_status:404
EOF

# Restart tunnel
pkill cloudflared
cloudflared tunnel run YOUR_TUNNEL_ID
```

**Prevention:**
- Use absolute paths in configuration
- Verify file permissions (600 for credentials, 644 for config)
- Test configuration syntax before starting tunnel

### **Issue 4: SSL Certificate Generation Failures**

**Symptoms:**
- Certificates show "False" status
- Let's Encrypt challenges pending
- SSL not working on main domain

**Root Cause:**
- Domain not accessible from internet for validation
- ClusterIssuer not properly configured
- DNS not pointing to Cloudflare

**Diagnostic Commands:**
```bash
# Check certificate status
kubectl get certificates -A
kubectl describe certificate YOUR_CERT_NAME -n YOUR_NAMESPACE

# Check ClusterIssuer
kubectl get clusterissuer letsencrypt-prod -o yaml
kubectl describe clusterissuer letsencrypt-prod

# Check challenges
kubectl get challenges -A
kubectl describe challenge CHALLENGE_NAME -n NAMESPACE

# Check DNS resolution
dig yourdomain.com
nslookup yourdomain.com
```

**Solution:**
```bash
# 1. Verify ClusterIssuer is ready
kubectl get clusterissuer letsencrypt-prod
# Should show: READY: True

# 2. Check DNS propagation
dig yourdomain.com NS
# Should show Cloudflare nameservers

# 3. Wait for DNS propagation (24-48 hours)
# 4. Certificates will auto-generate once DNS is ready
```

**Prevention:**
- Ensure ClusterIssuer is properly configured
- Wait for DNS propagation before expecting SSL
- Use tunnel access while waiting for main domain

## 🔍 Diagnostic Commands

### **Tunnel Health Check:**
```bash
# Check tunnel status
cloudflared tunnel list
cloudflared tunnel info YOUR_TUNNEL_ID

# Check tunnel connections
cloudflared tunnel info YOUR_TUNNEL_ID --format=json | jq '.connections'

# Check tunnel logs
cloudflared tunnel run YOUR_TUNNEL_ID --loglevel=info
```

### **DNS Resolution Check:**
```bash
# Check nameservers
dig yourdomain.com NS
dig yourdomain.com A

# Check from different DNS servers
dig @8.8.8.8 yourdomain.com NS
dig @1.1.1.1 yourdomain.com NS

# Check local vs global resolution
nslookup yourdomain.com
nslookup yourdomain.com 8.8.8.8
```

### **Kubernetes Resource Check:**
```bash
# Check all resources in namespace
kubectl get all -n humor-game
kubectl get ingress -n humor-game
kubectl get certificates -n humor-game

# Check pod logs
kubectl logs deployment/ingress-nginx-controller -n ingress-nginx
kubectl logs deployment/cert-manager -n cert-manager

# Check service endpoints
kubectl get endpoints -n humor-game
kubectl describe service frontend -n humor-game
```

### **Network Connectivity Check:**
```bash
# Test local ingress
curl -I -H "Host: app.yourdomain.com" http://localhost:8080/

# Test tunnel access
curl -I "http://app.yourdomain.com"

# Test main domain (after DNS propagation)
curl -I "https://yourdomain.com"
```

## 🚨 Common Error Messages and Solutions

### **Error: "No ingress rules were defined"**
**Cause:** Configuration file not found or not readable
**Solution:**
```bash
# Check configuration file
ls -la ~/.cloudflared/
cat ~/.cloudflared/config.yml

# Create configuration if missing
# Restart tunnel after creating config
```

### **Error: "Failed to create record"**
**Cause:** DNS record already exists or domain not in Cloudflare
**Solution:**
```bash
# Check if domain is in Cloudflare
# Use subdomain instead: app.yourdomain.com
cloudflared tunnel route dns YOUR_TUNNEL_ID app.yourdomain.com
```

### **Error: "Connection refused"**
**Cause:** Local service not running or wrong port
**Solution:**
```bash
# Check if k3d cluster is running
kubectl get pods -n humor-game

# Check if ingress is accessible
curl -I http://localhost:8080/

# Verify tunnel configuration points to correct port
```

### **Error: "SSL certificate not ready"**
**Cause:** Let's Encrypt validation failing
**Solution:**
```bash
# Check DNS propagation
dig yourdomain.com NS

# Wait for DNS to propagate (24-48 hours)
# Use tunnel access while waiting
```

## 🔧 Troubleshooting Process

### **Step 1: Identify the Problem**
1. **Check symptoms** and error messages
2. **Determine scope** (tunnel, DNS, SSL, etc.)
3. **Check recent changes** that might have caused the issue

### **Step 2: Gather Information**
1. **Run diagnostic commands** to collect data
2. **Check logs** for error messages
3. **Verify configuration** files and settings

### **Step 3: Apply Solutions**
1. **Start with simple fixes** (restart services, check configs)
2. **Apply specific solutions** based on root cause
3. **Test changes** to verify they work

### **Step 4: Verify Resolution**
1. **Test functionality** that was broken
2. **Monitor for recurrence** of the issue
3. **Document the solution** for future reference

## 🚑 Emergency Recovery Procedures

### **Tunnel Down - Immediate Access Lost:**
```bash
# 1. Check tunnel status
cloudflared tunnel list

# 2. Restart tunnel
pkill cloudflared
cloudflared tunnel run YOUR_TUNNEL_ID

# 3. Verify connection
cloudflared tunnel info YOUR_TUNNEL_ID

# 4. Test access
curl -I "http://app.yourdomain.com"
```

### **SSL Certificate Expired:**
```bash
# 1. Check certificate status
kubectl get certificates -A

# 2. Check ClusterIssuer
kubectl get clusterissuer letsencrypt-prod

# 3. Force certificate renewal
kubectl delete certificate YOUR_CERT_NAME -n YOUR_NAMESPACE
# cert-manager will recreate it automatically
```

### **DNS Issues - Domain Not Accessible:**
```bash
# 1. Check DNS propagation
dig yourdomain.com NS

# 2. Use tunnel access as backup
# 3. Contact domain registrar if needed
# 4. Wait for DNS propagation (24-48 hours)
```

## 🛡️ Prevention Best Practices

### **Before Making Changes:**
1. **Document current state** of working configuration
2. **Test changes** in development environment first
3. **Have rollback plan** ready
4. **Schedule changes** during low-traffic periods

### **Configuration Management:**
1. **Use version control** for all configuration files
2. **Test configurations** before applying
3. **Use consistent naming** conventions
4. **Document all customizations**

### **Monitoring and Alerting:**
1. **Set up health checks** for critical services
2. **Monitor SSL certificate** expiration
3. **Track tunnel connection** status
4. **Set up alerts** for service failures

### **Regular Maintenance:**
1. **Update cloudflared** regularly
2. **Review security settings** in Cloudflare dashboard
3. **Monitor performance metrics** and optimize
4. **Test failover scenarios** periodically

## 📚 Additional Resources

### **Cloudflare Documentation:**
- [Tunnel Troubleshooting](https://developers.cloudflare.com/cloudflare-one/connections/connect-apps/troubleshooting/)
- [DNS Management](https://developers.cloudflare.com/dns/)
- [SSL/TLS Configuration](https://developers.cloudflare.com/ssl/)

### **Kubernetes Resources:**
- [Ingress Troubleshooting](https://kubernetes.io/docs/concepts/services-networking/ingress/#troubleshooting)
- [cert-manager Troubleshooting](https://cert-manager.io/docs/troubleshooting/)

### **Community Support:**
- [Cloudflare Community](https://community.cloudflare.com/)
- [Kubernetes Slack](https://slack.k8s.io/)
- [Stack Overflow](https://stackoverflow.com/questions/tagged/cloudflare)

---

*This troubleshooting guide covers the most common issues encountered during global deployments. For detailed explanations of concepts and architecture, see the [Cloudflare Deep Dive Guide](cloudflare-deep-dive.md).*
