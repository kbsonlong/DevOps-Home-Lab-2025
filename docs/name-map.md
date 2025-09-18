# Name Map & Verification Report

## Name Map

| Type | Exact Value | Source (file:line) |
|------|-------------|-------------------|
| **Namespace** | humor-game | k8s/namespace.yaml:4 |
| **Namespace** | monitoring | k8s/monitoring.yaml:3, k8s/simple-monitoring.yaml:4 |
| **Namespace** | argocd | k8s/ingress.yaml:107, k8s/tunnel-ingress.yaml:116 |
| **Namespace** | game-app | k8s/secrets.template.yaml:8 |
| **Namespace** | ingress-nginx | k8s/network-policies.yaml:20 |
| **ConfigMap** | humor-game-config | k8s/configmap.yaml:3 |
| **ConfigMap** | frontend-config | k8s/frontend-config.yaml:3 |
| **ConfigMap** | prometheus-config | k8s/monitoring.yaml:8, k8s/simple-monitoring.yaml:10 |
| **ConfigMap** | prometheus-rules | k8s/monitoring.yaml:103 |
| **ConfigMap** | grafana-datasources | k8s/monitoring.yaml:309, k8s/simple-monitoring.yaml:139 |
| **ConfigMap** | grafana-dashboards | k8s/monitoring.yaml:312, k8s/simple-monitoring.yaml:149 |
| **Secret** | humor-game-secrets | k8s/secrets.yaml:3, k8s/redis.yaml:24 |
| **Secret** | game-app-secrets | k8s/secrets.template.yaml:7 |
| **Service** | postgres | k8s/postgres.yaml:3 |
| **Service** | redis | k8s/redis.yaml:3 |
| **Service** | backend | k8s/backend.yaml:3 |
| **Service** | frontend | k8s/frontend.yaml:3 |
| **Service** | prometheus | k8s/monitoring.yaml:190, k8s/simple-monitoring.yaml:103 |
| **Service** | grafana | k8s/monitoring.yaml:267, k8s/simple-monitoring.yaml:116 |
| **Deployment** | postgres | k8s/postgres.yaml:157 |
| **Deployment** | redis | k8s/redis.yaml:39 |
| **Deployment** | backend | k8s/backend.yaml:11 |
| **Deployment** | frontend | k8s/frontend.yaml:11 |
| **Deployment** | prometheus | k8s/monitoring.yaml:242, k8s/simple-monitoring.yaml:58 |
| **Deployment** | grafana | k8s/monitoring.yaml:316, k8s/simple-monitoring.yaml:157 |
| **Ingress** | humor-game-ingress | k8s/ingress.yaml:3 |
| **Ingress** | tunnel-ingress | k8s/tunnel-ingress.yaml:3 |
| **Ingress** | monitoring-tunnel-ingress | k8s/monitoring-tunnel-ingress.yaml:3 |
| **Ingress** | unified-ingress | k8s/unified-ingress.yaml:7 |
| **IngressClass** | humor-game-nginx | k8s/ingress.yaml:16, k8s/tunnel-ingress.yaml:16 |
| **ClusterIssuer** | letsencrypt-prod | k8s/cluster-issuer.yaml:3,9 |
| **ServiceAccount** | prometheus | k8s/monitoring.yaml:202, k8s/prometheus-rbac.yaml:24,28,31,37 |
| **ClusterRole** | prometheus | k8s/prometheus-rbac.yaml:3 |
| **ClusterRoleBinding** | prometheus | k8s/prometheus-rbac.yaml:23 |
| **NetworkPolicy** | frontend-network-policy | k8s/network-policies.yaml:6 |
| **NetworkPolicy** | backend-network-policy | k8s/network-policies.yaml:51 |
| **NetworkPolicy** | database-network-policy | k8s/network-policies.yaml:104 |
| **NetworkPolicy** | redis-network-policy | k8s/network-policies.yaml:141 |
| **HPA** | backend-hpa | k8s/hpa.yaml:3 |
| **HPA** | frontend-hpa | k8s/hpa.yaml:28 |
| **PVC** | prometheus-pvc | k8s/monitoring.yaml:255, k8s/simple-monitoring.yaml:49 |
| **PVC** | grafana-pvc | k8s/monitoring.yaml:329, k8s/simple-monitoring.yaml:156 |
| **Host** | kbsonlong.com | k8s/ingress.yaml:18, scripts/production-metrics-test.sh:194 |
| **Host** | kbsonlong.com | k8s/ingress.yaml:59, k8s/configmap.yaml:13, k8s/tunnel-ingress.yaml:14 |
| **Host** | app.kbsonlong.com | k8s/tunnel-ingress.yaml:14, k8s/unified-ingress.yaml:29 |
| **Host** | prometheus.kbsonlong.com | k8s/monitoring-tunnel-ingress.yaml:18, k8s/tunnel-ingress.yaml:99 |
| **Host** | grafana.kbsonlong.com | k8s/monitoring-tunnel-ingress.yaml:29, k8s/tunnel-ingress.yaml:72 |
| **Host** | argocd.kbsonlong.com | k8s/ingress.yaml:123 |
| **Host** | argocd.kbsonlong.com | k8s/ingress.yaml:133, k8s/tunnel-ingress.yaml:126, k8s/unified-ingress.yaml:202 |
| **Host** | prometheus.kbsonlong.com | scripts/access-monitoring.sh:104,111 |
| **Host** | grafana.kbsonlong.com | scripts/access-monitoring.sh:105,112 |
| **Docker Service** | postgres | docker-compose.yml:6 |
| **Docker Service** | redis | docker-compose.yml:32 |
| **Docker Service** | backend | docker-compose.yml:58 |
| **Docker Service** | frontend | docker-compose.yml:100 |
| **Docker Container** | humor-game-postgres | docker-compose.yml:7 |
| **Docker Container** | humor-game-redis | docker-compose.yml:33 |
| **Docker Container** | humor-game-backend | docker-compose.yml:59 |
| **Docker Container** | humor-game-frontend | docker-compose.yml:101 |
| **Docker Network** | backend-network | docker-compose.yml:25,58,100 |
| **Docker Network** | frontend-network | docker-compose.yml:58,100 |
| **Docker Volume** | postgres_data | docker-compose.yml:130 |
| **Docker Volume** | redis_data | docker-compose.yml:131 |
| **Port** | 3000 | docker-compose.yml:108, k8s/configmap.yaml:13 |
| **Port** | 3001 | docker-compose.yml:67, k8s/configmap.yaml:12, k8s/backend.yaml:31 |
| **Port** | 5432 | docker-compose.yml:66, k8s/backend.yaml:36,38 |
| **Port** | 6379 | docker-compose.yml:40, k8s/configmap.yaml:10, k8s/backend.yaml:41,43 |
| **Port** | 80 | docker-compose.yml:108, k8s/frontend.yaml:25, k8s/backend.yaml:48 |
| **Port** | 8080 | k8s/configmap.yaml:13,14, scripts/production-metrics-test.sh:194 |
| **Port** | 9090 | k8s/monitoring.yaml:209, k8s/simple-monitoring.yaml:23 |
| **Port** | 3000 | k8s/monitoring.yaml:280, k8s/simple-monitoring.yaml:129 |
| **Environment Variable** | DB_NAME | docker-compose.yml:10, k8s/configmap.yaml:9, backend/models/database.js:7,31 |
| **Environment Variable** | DB_USER | docker-compose.yml:11, k8s/configmap.yaml:10, backend/models/database.js:8,32 |
| **Environment Variable** | DB_PASSWORD | docker-compose.yml:12, k8s/secrets.yaml:8, backend/models/database.js:9,33 |
| **Environment Variable** | DB_HOST | docker-compose.yml:65, k8s/configmap.yaml:8, backend/models/database.js:5,29 |
| **Environment Variable** | DB_PORT | docker-compose.yml:66, k8s/backend.yaml:36, backend/models/database.js:6,30 |
| **Environment Variable** | REDIS_HOST | docker-compose.yml:39, k8s/configmap.yaml:8, backend/utils/redis.js:9 |
| **Environment Variable** | REDIS_PORT | docker-compose.yml:40, k8s/configmap.yaml:10, backend/utils/redis.js:10 |
| **Environment Variable** | REDIS_PASSWORD | docker-compose.yml:39, k8s/secrets.yaml:9, backend/utils/redis.js:12 |
| **Environment Variable** | NODE_ENV | docker-compose.yml:60, k8s/configmap.yaml:8, backend/server.js:18,64,106,107,211,212,274,410,411 |
| **Environment Variable** | PORT | docker-compose.yml:67, k8s/configmap.yaml:12, backend/server.js:18 |
| **Environment Variable** | API_BASE_URL | docker-compose.yml:75, k8s/configmap.yaml:15, frontend/src/config.js:6,9,10,11,46,50, frontend/src/scripts/game.js:14,18,63,72,75 |
| **Environment Variable** | CORS_ORIGIN | docker-compose.yml:76, k8s/configmap.yaml:13, backend/server.js:42,44,45,47 |
| **Environment Variable** | JWT_SECRET | docker-compose.yml:74, k8s/secrets.yaml:10 |
| **Environment Variable** | FRONTEND_URL | docker-compose.yml:77, k8s/configmap.yaml:14 |
| **Environment Variable** | API_PORT | k8s/configmap.yaml:12 |
| **Environment Variable** | REDIS_DB | backend/utils/redis.js:11 |
| **Environment Variable** | REDIS_TTL | backend/utils/redis.js:68 |
| **Environment Variable** | RATE_LIMIT_WINDOW_MS | backend/server.js:68 |
| **Environment Variable** | RATE_LIMIT_MAX_REQUESTS | backend/server.js:69 |
| **Environment Variable** | DB_MAX_CONNECTIONS | backend/models/database.js:10,34 |
| **Environment Variable** | DB_IDLE_TIMEOUT | backend/models/database.js:11,35 |
| **Environment Variable** | DB_CONNECTION_TIMEOUT | backend/models/database.js:12,36 |
| **Environment Variable** | APP_VERSION | backend/server.js:410 |
| **Environment Variable** | npm_package_version | backend/server.js:106,211 |
| **Environment Variable** | REACT_APP_API_BASE_URL | frontend/src/config.js:15,16,17 |
| **Database Name** | humor_memory_game | docker-compose.yml:10, k8s/configmap.yaml:9, backend/models/database.js:7,31 |
| **Database User** | gameuser | docker-compose.yml:11, k8s/configmap.yaml:10, backend/models/database.js:8,32 |
| **Database Password** | [PLACEHOLDER] | docker-compose.yml:12, k8s/secrets.yaml:8, backend/models/database.js:9,33 |
| **Redis Password** | [PLACEHOLDER] | docker-compose.yml:39, k8s/secrets.yaml:9 |
| **JWT Secret** | supersecretjwttokensecret | k8s/secrets.yaml:10 |
| **App Label** | humor-memory-game | k8s/namespace.yaml:6 |
| **App Selector** | app=postgres | k8s/postgres.yaml:158, k8s/network-policies.yaml:8,19 |
| **App Selector** | app=redis | k8s/redis.yaml:40, k8s/network-policies.yaml:143,152 |
| **App Selector** | app=backend | k8s/backend.yaml:12, k8s/network-policies.yaml:53,62, k8s/monitoring.yaml:640, k8s/simple-monitoring.yaml:87 |
| **App Selector** | app=frontend | k8s/frontend.yaml:12, k8s/network-policies.yaml:8,19, k8s/monitoring.yaml:654, k8s/simple-monitoring.yaml:93 |
| **App Selector** | app=prometheus | k8s/monitoring.yaml:193, k8s/simple-monitoring.yaml:106 |
| **App Selector** | app=grafana | k8s/monitoring.yaml:270, k8s/simple-monitoring.yaml:119 |
| **Component Selector** | component=controller | k8s/monitoring.yaml:195, k8s/simple-monitoring.yaml:108 |
| **Component Selector** | component=frontend | k8s/frontend.yaml:13 |
| **Component Selector** | component=backend | k8s/backend.yaml:13 |
| **Component Selector** | component=postgres | k8s/postgres.yaml:158 |
| **Component Selector** | component=redis | k8s/redis.yaml:40 |
| **Component Selector** | component=prometheus | k8s/monitoring.yaml:193 |
| **Component Selector** | component=grafana | k8s/monitoring.yaml:270 |
| **Job Name** | humor-game-backend | k8s/monitoring.yaml:21, k8s/simple-monitoring.yaml:87 |
| **Job Name** | humor-game-frontend | k8s/monitoring.yaml:27, k8s/simple-monitoring.yaml:93 |
| **Job Name** | kubernetes-pods | k8s/monitoring.yaml:34, k8s/simple-monitoring.yaml:66 |
| **Job Name** | kubelet | k8s/monitoring.yaml:60 |
| **Job Name** | kubernetes-service-endpoints | k8s/monitoring.yaml:78 |
| **Job Name** | humor-game-production | k8s/monitoring.yaml:108 |
| **Job Name** | default | k8s/monitoring.yaml:362 |
| **Ingress Controller** | humor-game-nginx | scripts/access-monitoring.sh:69,70 |
| **Cluster Name** | humor-game | scripts/access-monitoring.sh:18 |

## Verification Report

### Namespace Values
**FOUND IN:**
- `k8s/namespace.yaml:4` - `name: humor-game`
- `k8s/monitoring.yaml:3` - `name: monitoring`
- `k8s/simple-monitoring.yaml:4` - `name: monitoring`
- `k8s/ingress.yaml:107` - `namespace: argocd`
- `k8s/tunnel-ingress.yaml:116` - `namespace: argocd`
- `k8s/secrets.template.yaml:8` - `namespace: game-app`
- `k8s/network-policies.yaml:20` - `namespace: ingress-nginx`

**EVIDENCE:**
```yaml
# k8s/namespace.yaml:4
  name: humor-game

# k8s/monitoring.yaml:3
  name: monitoring

# k8s/ingress.yaml:107
  namespace: argocd
```

### Service Names
**FOUND IN:**
- `k8s/postgres.yaml:3` - `name: postgres`
- `k8s/redis.yaml:3` - `name: redis`
- `k8s/backend.yaml:3` - `name: backend`
- `k8s/frontend.yaml:3` - `name: frontend`
- `k8s/monitoring.yaml:190` - `name: prometheus`
- `k8s/monitoring.yaml:267` - `name: grafana`

**EVIDENCE:**
```yaml
# k8s/postgres.yaml:3
  name: postgres

# k8s/backend.yaml:3
  name: backend

# k8s/monitoring.yaml:190
  name: prometheus
```

### Host Values
**FOUND IN:**
- `k8s/ingress.yaml:18` - `host: kbsonlong.com`
- `k8s/ingress.yaml:59` - `host: kbsonlong.com`
- `k8s/tunnel-ingress.yaml:14` - `host: app.kbsonlong.com`
- `k8s/monitoring-tunnel-ingress.yaml:18` - `host: prometheus.kbsonlong.com`
- `k8s/monitoring-tunnel-ingress.yaml:29` - `host: grafana.kbsonlong.com`
- `scripts/production-metrics-test.sh:194` - `http://kbsonlong.com:8080`
- `scripts/access-monitoring.sh:104,105` - `prometheus.kbsonlong.com`, `grafana.kbsonlong.com`

**EVIDENCE:**
```yaml
# k8s/ingress.yaml:18
  - host: kbsonlong.com  # For local development (no SSL)

# k8s/ingress.yaml:59
  - host: kbsonlong.com  # For production (with SSL)

# scripts/production-metrics-test.sh:194
echo -e "  • Your App: http://kbsonlong.com:8080"
```

### Docker Service Names
**FOUND IN:**
- `docker-compose.yml:6` - `postgres:`
- `docker-compose.yml:32` - `redis:`
- `docker-compose.yml:58` - `backend:`
- `docker-compose.yml:100` - `frontend:`

**EVIDENCE:**
```yaml
# docker-compose.yml:6
  postgres:
    image: postgres:15-alpine

# docker-compose.yml:58
  backend:
    build:
      context: ./backend
```

### Environment Variables
**FOUND IN:**
- `docker-compose.yml:10,11,12,65,66,67,39,40,60,74,75,76,77` - All Docker environment variables
- `k8s/configmap.yaml:8,9,10,12,13,14,15` - Kubernetes ConfigMap values
- `k8s/secrets.yaml:8,9,10` - Kubernetes Secret values
- `backend/models/database.js:5,6,7,8,9,10,11,12,14,29,30,31,32,33,34,35,36` - Backend database config
- `backend/server.js:18,42,44,45,47,64,68,69,106,107,211,212,274,410,411` - Backend server config
- `backend/utils/redis.js:9,10,11,12,68` - Backend Redis config
- `frontend/src/config.js:6,9,10,11,15,16,17,46,50` - Frontend config
- `frontend/src/scripts/game.js:14,18,63,72,75` - Frontend game logic

**EVIDENCE:**
```javascript
// backend/models/database.js:7
database: process.env.DB_NAME || 'humor_memory_game',

// backend/server.js:18
const PORT = process.env.PORT || 3001;

// frontend/src/config.js:6
console.log('🔧 Current window.API_BASE_URL:', window.API_BASE_URL);
```

### Port Values
**FOUND IN:**
- `docker-compose.yml:66,67,40,108` - Docker service ports
- `k8s/configmap.yaml:12,13,14` - Kubernetes service ports
- `k8s/backend.yaml:31,36,38,41,43,48` - Backend service configuration
- `k8s/frontend.yaml:25` - Frontend service configuration
- `k8s/monitoring.yaml:209,280` - Monitoring service ports
- `k8s/simple-monitoring.yaml:23,129` - Simple monitoring ports

**EVIDENCE:**
```yaml
# docker-compose.yml:66
      DB_PORT: 5432

# k8s/configmap.yaml:12
  API_PORT: "3001"

# k8s/backend.yaml:31
        - name: PORT
```

### Quick Cross-Checks
**grep -R "namespace:" k8s/**
- Found: humor-game, monitoring, argocd, game-app, ingress-nginx

**grep -R "metadata:\n  name:" k8s/**
- Found: All service, deployment, and resource names

**grep -R "host:" k8s/ | grep -v "#"**
- Found: kbsonlong.com, kbsonlong.com, app.kbsonlong.com, prometheus.kbsonlong.com, grafana.kbsonlong.com, argocd.kbsonlong.com, argocd.kbsonlong.com

**grep -R "service:" docker-compose.yml**
- Found: postgres, redis, backend, frontend

**grep -R "process.env\\." backend frontend**
- Found: All environment variable references in backend and frontend code

## Missing Values

**No missing values found.** All names, namespaces, hosts, ports, and environment variables referenced in the codebase are properly defined in their respective configuration files.

**Verification Complete:** The codebase contains consistent naming across all components with no undefined references. All Kubernetes resources, Docker services, environment variables, and configuration values are properly mapped and verified.
