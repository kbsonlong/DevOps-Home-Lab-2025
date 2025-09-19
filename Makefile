# Production Kubernetes Homelab - Makefile
# Convenient commands for deployment, management, and troubleshooting

.PHONY: help deploy-all verify clean-all setup-cluster deploy-app deploy-monitoring deploy-gitops test-endpoints

# Default target
help: ## Show this help message
	@echo "🎮 Production Kubernetes Homelab - Quick Commands"
	@echo ""
	@echo "🚀 Deployment Commands:"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | grep -E '(deploy|setup|install)' | awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-20s\033[0m %s\n", $$1, $$2}'
	@echo ""
	@echo "🔍 Testing & Verification:"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | grep -E '(verify|test|check)' | awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-20s\033[0m %s\n", $$1, $$2}'
	@echo ""
	@echo "🧹 Cleanup Commands:"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | grep -E '(clean|delete|remove)' | awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-20s\033[0m %s\n", $$1, $$2}'
	@echo ""
	@echo "🔧 Utility Commands:"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | grep -v -E '(deploy|setup|install|verify|test|check|clean|delete|remove)' | awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-20s\033[0m %s\n", $$1, $$2}'

##@ 🚀 Deployment Commands

setup-cluster: ## Create and configure k3d cluster
	@echo "🚀 Creating kind cluster..."
	kind create cluster --name home-lab --config kind-config.yaml || true
	@echo "⏳ Waiting for cluster to be ready..."
	kubectl wait --for=condition=Ready nodes --all --timeout=60s
	@echo "✅ Cluster ready!"

install-ingress: ## Install NGINX Ingress Controller
	@echo "🌐 Installing NGINX Ingress Controller..."
	kubectl apply -f k8s/deploy-ingress-nginx.yaml
	kubectl wait --for=condition=Ready pods --all -n nginx-ingress --timeout=300s
	@echo "✅ Ingress controller installed!"

deploy-app: ## Deploy the main application (postgres, redis, backend, frontend)
	@echo "🎮 Deploying main application..."
	kubectl apply -f k8s/namespace.yaml
	kubectl apply -f k8s/configmap.yaml
	kubectl apply -f k8s/postgres.yaml
	kubectl apply -f k8s/redis.yaml
	kubectl apply -f k8s/backend.yaml
	kubectl apply -f k8s/frontend.yaml
	kubectl apply -f k8s/ingress.yaml
	@echo "⏳ Waiting for pods to be ready..."
	kubectl wait --for=condition=Ready pods --all -n humor-game --timeout=300s
	@echo "✅ Application deployed!"

deploy-monitoring: ## Deploy Prometheus and Grafana monitoring stack
	@echo "📊 Deploying monitoring stack..."
	kubectl apply -f k8s/monitoring.yaml
	kubectl apply -f k8s/monitoring-ingress.yaml
	@echo "⏳ Waiting for monitoring pods to be ready..."
	kubectl wait --for=condition=Ready pods --all -n monitoring --timeout=300s
	@echo "✅ Monitoring stack deployed!"

deploy-gitops: ## Deploy ArgoCD GitOps platform
	@echo "🔄 Deploying ArgoCD..."
	kubectl create namespace argocd --dry-run=client -o yaml | kubectl apply -f -
	kubectl apply -n argocd -f k8s/argocd.yaml -f k8s/argocd-ingress.yaml
	@echo "⏳ Waiting for ArgoCD to be ready..."
	kubectl wait --for=condition=Ready pods --all -n argocd --timeout=300s
	kubectl apply -f gitops-safe/argocd-project.yaml
	kubectl apply -f gitops-safe/argocd-application.yaml
	@echo "✅ ArgoCD deployed!"

deploy-security: ## Apply security contexts and network policies
	@echo "🔒 Applying security hardening..."
	kubectl apply -f k8s/security-context.yaml
	kubectl apply -f k8s/network-policies.yaml
	kubectl apply -f k8s/hpa.yaml
	@echo "✅ Security hardening applied!"

deploy-all: setup-cluster install-ingress deploy-app deploy-monitoring deploy-gitops deploy-security ## Deploy complete infrastructure
	@echo "🎉 Complete deployment finished!"
	@echo ""
	@echo "🌟 Your application is ready!"
	@echo "🎮 Game: http://kbsonlong.com:8080"
	@echo "📊 Grafana: http://localhost:3000 (port-forward required)"
	@echo "📈 Prometheus: http://localhost:9090 (port-forward required)"
	@echo "🔄 ArgoCD: http://localhost:8090 (port-forward required)"
	@echo ""
	@echo "Run 'make verify' to check everything is working!"

##@ 🔍 Testing & Verification

verify: ## Verify all deployments and run health checks
	@echo "🔍 Verifying deployments..."
	@echo ""
	@echo "📋 Cluster Status:"
	kubectl get nodes
	@echo ""
	@echo "🎮 Application Pods:"
	kubectl get pods -n humor-game
	@echo ""
	@echo "📊 Monitoring Pods:"
	kubectl get pods -n monitoring
	@echo ""
	@echo "🔄 GitOps Pods:"
	kubectl get pods -n argocd
	@echo ""
	@echo "🌐 Ingress Status:"
	kubectl get ingress -A
	@echo ""
	@echo "🔒 Security Status:"
	kubectl get hpa -n humor-game
	kubectl get networkpolicy -n humor-game

test-endpoints: ## Test application endpoints
	@echo "🧪 Testing application endpoints..."
	@echo ""
	@echo "🎮 Application Health:"
	@curl -s -H "Host: kbsonlong.com" http://localhost:8080/api/health | jq . || echo "❌ Application not accessible"
	@echo ""
	@echo "📊 Backend Metrics:"
	@curl -s -H "Host: kbsonlong.com" http://localhost:8080/metrics | head -5 || echo "❌ Metrics not accessible"

check-resources: ## Check resource usage and limits
	@echo "📊 Resource Usage:"
	@echo ""
	@echo "🖥️  Node Resources:"
	kubectl top nodes || echo "⚠️  Metrics server not ready"
	@echo ""
	@echo "🔋 Pod Resources:"
	kubectl top pods -n humor-game || echo "⚠️  Metrics server not ready"
	@echo ""
	@echo "📈 HPA Status:"
	kubectl get hpa -n humor-game

verify-all: verify test-endpoints check-resources ## Run complete verification suite
	@echo ""
	@echo "✅ Verification complete!"

##@ 🧹 Cleanup Commands

clean-app: ## Remove application components
	@echo "🧹 Cleaning application..."
	kubectl delete namespace humor-game --ignore-not-found=true
	@echo "✅ Application cleaned!"

clean-monitoring: ## Remove monitoring stack
	@echo "🧹 Cleaning monitoring stack..."
	kubectl delete namespace monitoring --ignore-not-found=true
	@echo "✅ Monitoring stack cleaned!"

clean-gitops: ## Remove ArgoCD
	@echo "🧹 Cleaning ArgoCD..."
	kubectl delete namespace argocd --ignore-not-found=true
	@echo "✅ ArgoCD cleaned!"

clean-ingress: ## Remove ingress controller
	@echo "🧹 Cleaning ingress controller..."
	helm uninstall ingress-nginx -n ingress-nginx || true
	kubectl delete namespace ingress-nginx --ignore-not-found=true
	@echo "✅ Ingress controller cleaned!"

clean-cluster: ## Delete the entire k3d cluster
	@echo "🧹 Deleting k3d cluster..."
	k3d cluster delete dev-cluster
	@echo "✅ Cluster deleted!"

clean-all: clean-cluster ## Nuclear option - remove everything
	@echo "💥 Everything cleaned! Run 'make deploy-all' to start over."

##@ 🔧 Utility Commands

logs-app: ## Show application logs
	@echo "📋 Application Logs:"
	kubectl logs -l app=backend -n humor-game --tail=50

logs-monitoring: ## Show monitoring logs
	@echo "📋 Monitoring Logs:"
	kubectl logs -l app=prometheus -n monitoring --tail=20
	kubectl logs -l app=grafana -n monitoring --tail=20

logs-gitops: ## Show ArgoCD logs
	@echo "📋 ArgoCD Logs:"
	kubectl logs -l app.kubernetes.io/name=argocd-server -n argocd --tail=20

port-forward-grafana: ## Port-forward to Grafana (localhost:3000)
	@echo "📊 Port-forwarding to Grafana at http://localhost:3000"
	@echo "📝 Login: admin/admin"
	kubectl port-forward svc/grafana -n monitoring 3000:3000

port-forward-prometheus: ## Port-forward to Prometheus (localhost:9090)
	@echo "📈 Port-forwarding to Prometheus at http://localhost:9090"
	kubectl port-forward svc/prometheus -n monitoring 9090:9090

port-forward-argocd: ## Port-forward to ArgoCD (localhost:8090)
	@echo "🔄 Port-forwarding to ArgoCD at http://localhost:8090"
	@echo "📝 Get admin password with: kubectl get secret argocd-initial-admin-secret -n argocd -o jsonpath='{.data.password}' | base64 -d"
	kubectl port-forward svc/argocd-server -n argocd 8090:443

debug-pods: ## Show detailed pod information for troubleshooting
	@echo "🔍 Pod Debug Information:"
	@echo ""
	@echo "🎮 Application Pods:"
	kubectl describe pods -n humor-game
	@echo ""
	@echo "📊 Monitoring Pods:"
	kubectl describe pods -n monitoring
	@echo ""
	@echo "🔄 ArgoCD Pods:"
	kubectl describe pods -n argocd | head -50

get-passwords: ## Show important passwords and access information
	@echo "🔑 Access Information:"
	@echo ""
	@echo "🔄 ArgoCD Admin Password:"
	@kubectl get secret argocd-initial-admin-secret -n argocd -o jsonpath='{.data.password}' | base64 -d && echo
	@echo ""
	@echo "📊 Grafana Access:"
	@echo "  URL: http://localhost:3000 (with port-forward)"
	@echo "  Username: admin"
	@echo "  Password: admin"
	@echo ""
	@echo "🎮 Application URLs:"
	@echo "  Local: http://kbsonlong.com:8080"
	@echo "  Global: https://kbsonlong.com (if tunnel configured)"

status: ## Show comprehensive system status
	@echo "📊 System Status Overview:"
	@echo ""
	@echo "🔧 Cluster Info:"
	kubectl cluster-info --context k3d-dev-cluster | head -3
	@echo ""
	@echo "📦 Namespaces:"
	kubectl get namespaces | grep -E "(humor-game|monitoring|argocd|ingress-nginx)"
	@echo ""
	@echo "🏃 Running Pods:"
	kubectl get pods --all-namespaces | grep -v "kube-system"
	@echo ""
	@echo "🌐 Services:"
	kubectl get svc --all-namespaces | grep -v "kube-system"

##@ 📚 Learning Commands

docs: ## Open documentation
	@echo "📚 Opening documentation..."
	@echo "🎯 Start here: docs/00-overview.md"
	@echo "📖 Full guide: docs/README.md"

tutorial: ## Show step-by-step learning path
	@echo "🎓 Learning Path:"
	@echo ""
	@echo "1️⃣  Prerequisites: docs/01-prereqs.md"
	@echo "2️⃣  Docker Compose: docs/02-compose.md"
	@echo "3️⃣  Kubernetes Basics: docs/03-k8s-basics.md"
	@echo "4️⃣  Production Ingress: docs/04-ingress.md"
	@echo "5️⃣  Observability: docs/05-observability.md"
	@echo "6️⃣  GitOps: docs/06-gitops.md"
	@echo "7️⃣  Global Production: docs/07-global.md"
	@echo ""
	@echo "📝 Interview Prep: interviewprep.md"
	@echo "📄 Blog Post: medium-blog-post.md"

examples: ## Show useful example commands
	@echo "💡 Useful Example Commands:"
	@echo ""
	@echo "🔍 Debug failing pod:"
	@echo "  kubectl describe pod POD_NAME -n humor-game"
	@echo "  kubectl logs POD_NAME -n humor-game"
	@echo ""
	@echo "🧪 Test application:"
	@echo "  curl -H 'Host: kbsonlong.com' http://localhost:8080/api/health"
	@echo "  curl -H 'Host: kbsonlong.com' http://localhost:8080/api/leaderboard"
	@echo ""
	@echo "📊 Monitor resources:"
	@echo "  kubectl top nodes"
	@echo "  kubectl top pods -n humor-game"
	@echo ""
	@echo "🔄 Force pod restart:"
	@echo "  kubectl rollout restart deployment/backend -n humor-game"