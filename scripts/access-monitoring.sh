#!/bin/bash

# Monitoring Access Script for Humor Game
# This script helps you access Prometheus and Grafana without port-forwarding

set -e

echo "🔍 Setting up monitoring access for Humor Game..."

# Check if kubectl is available
if ! command -v kubectl &> /dev/null; then
    echo "❌ kubectl not found. Please install kubectl first."
    exit 1
fi

# Check if k3d is running
if ! kubectl cluster-info &> /dev/null; then
    echo "❌ Kubernetes cluster not accessible. Please start your cluster first."
    echo "   Run: k3d cluster start humor-game"
    exit 1
fi

# Function to check if service is ready
check_service() {
    local namespace=$1
    local service=$2
    local port=$3
    
    echo "⏳ Waiting for $service in $namespace namespace..."
    kubectl wait --for=condition=ready pod -l app=$service -n $namespace --timeout=120s
    
    if [ $? -eq 0 ]; then
        echo "✅ $service is ready!"
        return 0
    else
        echo "❌ $service failed to become ready"
        return 1
    fi
}

# Function to add local DNS entry
add_local_dns() {
    local hostname=$1
    local ip=$2
    
    if [[ "$OSTYPE" == "darwin"* ]]; then
        # macOS
        if ! grep -q "$hostname" /etc/hosts; then
            echo "📝 Adding $hostname to /etc/hosts..."
            echo "$ip $hostname" | sudo tee -a /etc/hosts
        else
            echo "ℹ️  $hostname already exists in /etc/hosts"
        fi
    elif [[ "$OSTYPE" == "linux-gnu"* ]]; then
        # Linux
        if ! grep -q "$hostname" /etc/hosts; then
            echo "📝 Adding $hostname to /etc/hosts..."
            echo "$ip $hostname" | sudo tee -a /etc/hosts
        else
            echo "ℹ️  $hostname already exists in /etc/hosts"
        fi
    else
        echo "⚠️  Unsupported OS. Please manually add to your hosts file:"
        echo "   $ip $hostname"
    fi
}

# Get ingress controller IP
echo "🔍 Getting ingress controller IP..."
INGRESS_IP=$(kubectl get svc -n ingress-nginx humor-game-nginx-controller -o jsonpath='{.status.loadBalancer.ingress[0].ip}' 2>/dev/null || \
              kubectl get svc -n ingress-nginx humor-game-nginx-controller -o jsonpath='{.spec.clusterIP}' 2>/dev/null || \
              kubectl get nodes -o jsonpath='{.items[0].status.addresses[?(@.type=="InternalIP")].address}' 2>/dev/null)

if [ -z "$INGRESS_IP" ]; then
    echo "❌ Could not determine ingress IP. Using localhost..."
    INGRESS_IP="127.0.0.1"
else
    echo "✅ Ingress IP: $INGRESS_IP"
fi

# Check if monitoring namespace exists
if ! kubectl get namespace monitoring &> /dev/null; then
    echo "📦 Creating monitoring namespace..."
    kubectl create namespace monitoring
fi

# Apply monitoring configuration
echo "📋 Applying monitoring configuration..."
kubectl apply -f k8s/monitoring.yaml
kubectl apply -f k8s/monitoring-auth.yaml

# Wait for services to be ready
check_service "monitoring" "prometheus" "9090"
check_service "monitoring" "grafana" "3000"

# Apply ingress configuration
echo "🌐 Applying ingress configuration..."
kubectl apply -f k8s/ingress.yaml

# Wait for ingress to be ready
echo "⏳ Waiting for ingress to be ready..."
sleep 10

# Add local DNS entries (use localhost for k3d port mapping)
add_local_dns "prometheus.kbsonlong.com" "127.0.0.1"
add_local_dns "grafana.kbsonlong.com" "127.0.0.1"

echo ""
echo "🎉 Monitoring setup complete!"
echo ""
echo "📊 Access your monitoring services:"
echo "   Prometheus: http://prometheus.kbsonlong.com:8080"
echo "   Grafana:   http://grafana.kbsonlong.com:8080"
echo ""
echo "🔐 Default credentials:"
echo "   Username: admin"
echo "   Password: admin123"
echo ""
echo "💡 If you can't access the services:"
echo "   1. Check if your cluster is running: k3d cluster list"
echo "   2. Verify ingress is working: kubectl get ingress -A"
echo "   3. Check service status: kubectl get pods -n monitoring"
echo ""
echo "🚀 For production, update your DNS to point to:"
echo "   prometheus.kbsonlong.com -> $INGRESS_IP"
echo "   grafana.kbsonlong.com -> $INGRESS_IP"
