# n8n 安装指南

## clone n8n-hosting
```bash
git clone https://github.com/n8n-io/n8n-hosting.git
```

## install n8n

```bash
cd n8n-hosting
kubectl apply -f kubernetes/namespace.yaml
kubectl apply -f kubernetes
```

## install mcp-server

```bash
cd ../
kubectl apply -f k8s/mcp-server.yaml
```

## install ollama

注意ollama 模型是否支持tools, https://ollama.com/search?c=tools

## workflow

import from file Demo workflow.json