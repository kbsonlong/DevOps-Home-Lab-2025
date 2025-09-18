#!/bin/bash

echo "🌐 Setting up Monitoring Ingress Access..."

# Apply the monitoring ingress
echo "📋 Applying monitoring ingress configuration..."
kubectl apply -f k8s/monitoring-ingress.yaml

# Wait for ingress to be ready
echo "⏳ Waiting for ingress to be ready..."
sleep 5

# Add local DNS entries to /etc/hosts
echo "📝 Adding local DNS entries to /etc/hosts..."

# Check if entries already exist
if ! grep -q "prometheus.kbsonlong.com" /etc/hosts; then
    echo "127.0.0.1 prometheus.kbsonlong.com" | sudo tee -a /etc/hosts
    echo "✅ Added prometheus.kbsonlong.com to /etc/hosts"
else
    echo "ℹ️  prometheus.kbsonlong.com already exists in /etc/hosts"
fi

if ! grep -q "grafana.kbsonlong.com" /etc/hosts; then
    echo "127.0.0.1 grafana.kbsonlong.com" | sudo tee -a /etc/hosts
    echo "✅ Added grafana.kbsonlong.com to /etc/hosts"
else
    echo "ℹ️  grafana.kbsonlong.com already exists in /etc/hosts"
fi

# Check ingress status
echo "🔍 Checking ingress status..."
kubectl get ingress -n monitoring

echo ""
echo "🎉 Monitoring ingress setup complete!"
echo ""
echo "📊 Access your monitoring services:"
echo "   Prometheus: http://prometheus.kbsonlong.com:8080"
echo "   Grafana:   http://grafana.kbsonlong.com:8080"
echo ""
echo "🔐 Grafana credentials:"
echo "   Username: admin"
echo "   Password: admin123"
echo ""
echo "💡 Note: Make sure your k3d cluster is configured to expose port 8080"
echo "   Run: k3d cluster create --port 8080:80@loadbalancer"
