# Kubernetes Tutorial: Complete Learning Path

*Learn DevOps by building a real application: Docker → Kubernetes → Monitoring → GitOps → Global Deployment*

## 🚨 **CRITICAL: READ THIS BEFORE STARTING**

**⚠️ IMPORTANT:** This project uses a demo domain (`kbsonlong.com`) that you MUST replace with your own domain before beginning.

**🔗 See: [Domain Replacement Guide](docs/domain-replacement-guide.md)** for the complete list of files to update.

**🆓 Need a free domain? See: [Free Domain Setup](docs/07-global.md#step-3a-prerequisites---get-a-domain)** (Freenom, Duck DNS options)

**🌐 For Cloudflare Tunnel setup, see: [Cloudflare Tunnel Setup Guide](docs/cloudflare-tunnel-setup-guide.md)**

**❌ If you don't replace the domain, the card flipping functionality will break and you'll get stuck at Milestone 1.**

## 📚 **Complete Documentation**

This guide has been reorganized into beginner-friendly, step-by-step documentation:

### **🏁 Getting Started**
- **[00-overview.md](docs/00-overview.md)** - Project overview, architecture, and learning path
- **[01-prereqs.md](docs/01-prereqs.md)** - Tool installation and environment setup
- **[name-map.md](docs/name-map.md)** - Complete reference of all names, hosts, and ports used

### **🎯 Learning Tutorials**
- **[02-compose.md](docs/02-compose.md)** - Docker Multi-Container App Tutorial ⏱️ 20-40 min
- **[03-k8s-basics.md](docs/03-k8s-basics.md)** - Kubernetes Production Deployment ⏱️ 30-60 min
- **[04-ingress.md](docs/04-ingress.md)** - Internet Access & Networking ⏱️ 20-40 min
- **[05-observability.md](docs/05-observability.md)** - Performance Monitoring ⏱️ 45-90 min
- **[06-gitops.md](docs/06-gitops.md)** - Automated Deployments ⏱️ 30-60 min
- **[07-global.md](docs/07-global.md)** - Global Scale & Security ⏱️ 60-120 min

### **🛠️ Support & Reference**
- **[08-troubleshooting.md](docs/08-troubleshooting.md)** - Common issues and solutions
- **[09-faq.md](docs/09-faq.md)** - Frequently asked questions
- **[10-glossary.md](docs/10-glossary.md)** - Technical terms and definitions
- **[11-decision-notes.md](docs/11-decision-notes.md)** - Why we made specific choices

## 🚀 **Quick Start**

1. **Setup Environment** → [01-prereqs.md](docs/01-prereqs.md)
2. **Verify Docker Compose** → [02-compose.md](docs/02-compose.md)
3. **Deploy to Kubernetes** → [03-k8s-basics.md](docs/03-k8s-basics.md)
4. **Add Ingress** → [04-ingress.md](docs/04-ingress.md)
5. **Enable Monitoring** → [05-observability.md](docs/05-observability.md)
6. **Implement GitOps** → [06-gitops.md](docs/06-gitops.md)
7. **Production Hardening** → [07-global.md](docs/07-global.md)

## 🎯 **What You'll Build**

![Learning Journey Flow](assets/images/learning_flow.jpg)

*Follow this step-by-step progression from beginner developer to production-ready DevOps engineer*

By the end of this guide, you'll have deployed a complete production-grade application stack featuring:

- **Multi-service application** running on Kubernetes
- **Production networking** with Ingress and TLS termination  
- **Comprehensive monitoring** with Prometheus and Grafana dashboards
- **Database persistence** with PostgreSQL and Redis
- **Professional DevOps workflows** using GitOps and automation

This mirrors the same infrastructure patterns used by companies like Netflix, Airbnb, and GitHub to serve millions of users.

## 📖 **Learning Philosophy**

Rather than just copying commands, you'll understand the **why** behind each decision. Each milestone builds upon the previous one, teaching you to think like a platform engineer who designs systems for scale, reliability, and maintainability.

ℹ️ **Side Note:** This learning path follows the same progression used by professional DevOps teams: start with simple containerization (Docker Compose), progress to orchestration (Kubernetes), add networking (Ingress), implement observability (monitoring), automate deployments (GitOps), and finally harden for production (security, scaling).

## 🔧 **Need Help?**

- **Stuck on a step?** → [08-troubleshooting.md](docs/08-troubleshooting.md)
- **Confused by terms?** → [10-glossary.md](docs/10-glossary.md)
- **Have questions?** → [09-faq.md](docs/09-faq.md)
- **Want to understand decisions?** → [11-decision-notes.md](docs/11-decision-notes.md)

## 💡 **Reset/Rollback Commands**

If you need to start over at any point:

```bash
# Reset entire cluster (nuclear option)
k3d cluster delete homelab
k3d cluster create homelab --servers 1 --agents 2 --port "8080:80@loadbalancer" --port "8443:443@loadbalancer"

# Reset specific milestone
# Milestone 1: docker-compose down -v
# Milestone 2: kubectl delete namespace humor-game
# Milestone 3: kubectl delete namespace ingress-nginx
# Milestone 4: kubectl delete namespace monitoring
# Milestone 5: kubectl delete namespace argocd
# Milestone 6: kubectl delete hpa,networkpolicy --all -n humor-game

# Check current status
./scripts/verify.sh
```

## ✅ **Checkpoint**

Your homelab is production-ready when:
- ✅ **4 pods running** in humor-game namespace (postgres, redis, backend, frontend)
- ✅ **Monitoring stack** in monitoring namespace (prometheus, grafana)
- ✅ **GitOps automation** in argocd namespace
- ✅ **Global access** via Ingress and domain routing
- ✅ **Production security** with network policies and security contexts
- ✅ **Auto-scaling** configured with HPA
- ✅ **TLS/HTTPS** support (optional with cert-manager)

## 🎉 **Success Metrics**

**By the end, you'll have:**
- ✅ **4 pods running** in humor-game namespace (postgres, redis, backend, frontend)
- ✅ **Monitoring stack** in monitoring namespace (prometheus, grafana)
- ✅ **GitOps automation** in argocd namespace
- ✅ **Global access** via Cloudflare CDN
- ✅ **Production security** with network policies and security contexts

## ⚠️ **If It Fails**

**Symptom:** Stuck on any milestone
**Cause:** Configuration mismatch or resource constraints
**Command to confirm:** `./scripts/verify.sh`
**Fix:**
```bash
# Run verification script to identify issues
./scripts/verify.sh

# Check specific milestone troubleshooting
# Milestone 1: See [02-compose.md](docs/02-compose.md) troubleshooting section
# Milestone 2: See [03-k8s-basics.md](docs/03-k8s-basics.md) troubleshooting section
# Milestone 3: See [04-ingress.md](docs/04-ingress.md) troubleshooting section
# Milestone 4: See [05-observability.md](docs/05-observability.md) troubleshooting section
# Milestone 5: See [06-gitops.md](docs/06-gitops.md) troubleshooting section
# Milestone 6: See [07-global.md](docs/07-global.md) troubleshooting section

# Use the comprehensive [troubleshooting guide](docs/08-troubleshooting.md)
```

---

*This guide represents distilled experience from engineers who have built and scaled systems at companies like Google, Netflix, and Airbnb. Use it as a foundation for your continued growth in the DevOps and platform engineering disciplines.*
