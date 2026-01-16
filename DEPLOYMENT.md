# 🚀 Deployment Guide - Production Deployment

How to deploy Incident Autopilot to production (post-hackathon).

---

## Architecture for Production

```
┌─────────────────────────────────────────────┐
│          Load Balancer (ALB/NGINX)          │
└──────────────┬──────────────────────────────┘
               │
       ┌───────┴────────┐
       │                │
┌──────▼─────┐   ┌─────▼──────┐
│  FastAPI   │   │  FastAPI   │  (Multiple instances)
│  Server 1  │   │  Server 2  │
└──────┬─────┘   └─────┬──────┘
       │               │
       └───────┬───────┘
               │
      ┌────────▼─────────┐
      │  State Store     │
      │  (Redis/Postgres)│
      └──────────────────┘
               │
      ┌────────▼─────────┐
      │  Message Queue   │
      │  (RabbitMQ/Kafka)│
      └──────────────────┘
```

---

## Prerequisites

- Kubernetes cluster (EKS, GKE, or AKS)
- PostgreSQL or Redis for state
- Prometheus for metrics
- ElasticSearch for logs
- API keys for sponsor tools

---

## 1. Docker Containerization

### Dockerfile

```dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application
COPY . .

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=3s \
  CMD curl -f http://localhost:8000/health || exit 1

# Run application
CMD ["python", "main.py", "--mode", "server", "--port", "8000"]
```

### Build and push

```bash
docker build -t incident-autopilot:latest .
docker tag incident-autopilot:latest your-registry/incident-autopilot:latest
docker push your-registry/incident-autopilot:latest
```

---

## 2. Kubernetes Deployment

### deployment.yaml

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: incident-autopilot
  namespace: monitoring
spec:
  replicas: 3
  selector:
    matchLabels:
      app: incident-autopilot
  template:
    metadata:
      labels:
        app: incident-autopilot
    spec:
      containers:
      - name: autopilot
        image: your-registry/incident-autopilot:latest
        ports:
        - containerPort: 8000
        env:
        - name: ANTHROPIC_API_KEY
          valueFrom:
            secretKeyRef:
              name: autopilot-secrets
              key: anthropic-key
        - name: RETOOL_API_KEY
          valueFrom:
            secretKeyRef:
              name: autopilot-secrets
              key: retool-key
        resources:
          requests:
            memory: "512Mi"
            cpu: "500m"
          limits:
            memory: "2Gi"
            cpu: "2000m"
        livenessProbe:
          httpGet:
            path: /health
            port: 8000
          initialDelaySeconds: 30
          periodSeconds: 10
        readinessProbe:
          httpGet:
            path: /health
            port: 8000
          initialDelaySeconds: 5
          periodSeconds: 5
---
apiVersion: v1
kind: Service
metadata:
  name: incident-autopilot
  namespace: monitoring
spec:
  selector:
    app: incident-autopilot
  ports:
  - protocol: TCP
    port: 80
    targetPort: 8000
  type: LoadBalancer
```

### secrets.yaml

```yaml
apiVersion: v1
kind: Secret
metadata:
  name: autopilot-secrets
  namespace: monitoring
type: Opaque
stringData:
  anthropic-key: "your-anthropic-key"
  retool-key: "your-retool-key"
  tinyfish-key: "your-tinyfish-key"
  tonic-key: "your-tonic-key"
  freepik-key: "your-freepik-key"
```

### Deploy

```bash
kubectl create namespace monitoring
kubectl apply -f secrets.yaml
kubectl apply -f deployment.yaml
```

---

## 3. State Store Setup

### Redis

```bash
# Install Redis via Helm
helm repo add bitnami https://charts.bitnami.com/bitnami
helm install redis bitnami/redis --namespace monitoring

# Update deployment to use Redis
env:
- name: REDIS_HOST
  value: "redis-master.monitoring.svc.cluster.local"
- name: REDIS_PORT
  value: "6379"
```

### PostgreSQL

```bash
# Install PostgreSQL via Helm
helm install postgres bitnami/postgresql --namespace monitoring

# Update deployment
env:
- name: POSTGRES_HOST
  value: "postgres-postgresql.monitoring.svc.cluster.local"
- name: POSTGRES_DB
  value: "incident_autopilot"
```

---

## 4. Monitoring Integration

### Prometheus ServiceMonitor

```yaml
apiVersion: monitoring.coreos.com/v1
kind: ServiceMonitor
metadata:
  name: incident-autopilot
  namespace: monitoring
spec:
  selector:
    matchLabels:
      app: incident-autopilot
  endpoints:
  - port: http
    path: /metrics
    interval: 30s
```

### Grafana Dashboard

Import the provided dashboard JSON:

```bash
kubectl create configmap grafana-dashboard \
  --from-file=dashboard.json \
  --namespace monitoring
```

---

## 5. Integration Setup

### Kubernetes RBAC

For executor to actually perform actions on K8s:

```yaml
apiVersion: v1
kind: ServiceAccount
metadata:
  name: incident-autopilot
  namespace: monitoring
---
apiVersion: rbac.authorization.k8s.io/v1
kind: ClusterRole
metadata:
  name: incident-autopilot
rules:
- apiGroups: ["apps"]
  resources: ["deployments", "replicasets"]
  verbs: ["get", "list", "watch", "update", "patch"]
- apiGroups: [""]
  resources: ["pods"]
  verbs: ["get", "list", "watch", "delete"]
---
apiVersion: rbac.authorization.k8s.io/v1
kind: ClusterRoleBinding
metadata:
  name: incident-autopilot
roleRef:
  apiGroup: rbac.authorization.k8s.io
  kind: ClusterRole
  name: incident-autopilot
subjects:
- kind: ServiceAccount
  name: incident-autopilot
  namespace: monitoring
```

### ArgoCD Integration

For rollbacks:

```python
# In executor.py
async def apply_rollback(self, service: str, target_version: str):
    # Use ArgoCD API
    async with aiohttp.ClientSession() as session:
        await session.post(
            f"{ARGOCD_URL}/api/v1/applications/{service}/rollback",
            json={"revision": target_version},
            headers={"Authorization": f"Bearer {ARGOCD_TOKEN}"}
        )
```

---

## 6. Retool Dashboard Setup

### Create Retool App

1. Go to Retool console
2. Create new app: "Incident Control Tower"
3. Add data source: Your FastAPI endpoint
4. Import components:

```javascript
// Fetch incidents
const incidents = await api.get('/api/incidents');

// Approve button
<Button
  onClick={() => api.post(`/api/incidents/${incident.id}/approve`)}
  text="Approve Mitigation"
  loading={approvalState.loading}
/>

// Real-time updates
setInterval(() => {
  query1.trigger();
}, 5000);
```

---

## 7. Alerting Setup

### Alert on failures

```yaml
# alertmanager-config.yaml
route:
  receiver: 'incident-autopilot-failures'
  routes:
  - match:
      severity: critical
      source: incident-autopilot
    receiver: 'pagerduty'

receivers:
- name: 'incident-autopilot-failures'
  slack_configs:
  - channel: '#incidents'
    text: 'Autopilot failed to resolve incident: {{ .CommonAnnotations.summary }}'
```

---

## 8. Backup and Recovery

### Backup incident history

```bash
# Cron job to backup
apiVersion: batch/v1
kind: CronJob
metadata:
  name: backup-incidents
spec:
  schedule: "0 2 * * *"  # Daily at 2 AM
  jobTemplate:
    spec:
      template:
        spec:
          containers:
          - name: backup
            image: postgres:14
            command:
            - /bin/sh
            - -c
            - pg_dump -h $POSTGRES_HOST -U postgres incident_autopilot > /backup/incidents.sql && aws s3 cp /backup/incidents.sql s3://backups/$(date +%Y%m%d).sql
```

---

## 9. Security

### Network Policies

```yaml
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: incident-autopilot
spec:
  podSelector:
    matchLabels:
      app: incident-autopilot
  policyTypes:
  - Ingress
  - Egress
  ingress:
  - from:
    - namespaceSelector:
        matchLabels:
          name: monitoring
    ports:
    - protocol: TCP
      port: 8000
  egress:
  - to:
    - namespaceSelector: {}
    ports:
    - protocol: TCP
      port: 443  # API calls
```

### Secrets Management

Use external secrets operator:

```yaml
apiVersion: external-secrets.io/v1beta1
kind: ExternalSecret
metadata:
  name: autopilot-secrets
spec:
  secretStoreRef:
    name: aws-secrets-manager
    kind: SecretStore
  target:
    name: autopilot-secrets
  data:
  - secretKey: anthropic-key
    remoteRef:
      key: prod/incident-autopilot/anthropic
```

---

## 10. Testing in Production

### Canary Deployment

```yaml
apiVersion: flagger.app/v1beta1
kind: Canary
metadata:
  name: incident-autopilot
spec:
  targetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: incident-autopilot
  progressDeadlineSeconds: 60
  service:
    port: 80
  analysis:
    interval: 1m
    threshold: 5
    maxWeight: 50
    stepWeight: 10
    metrics:
    - name: request-success-rate
      thresholdRange:
        min: 99
      interval: 1m
```

### Chaos Testing

```bash
# Use Chaos Mesh to test resilience
kubectl apply -f - <<EOF
apiVersion: chaos-mesh.org/v1alpha1
kind: PodChaos
metadata:
  name: test-autopilot-resilience
spec:
  action: pod-failure
  mode: one
  selector:
    namespaces:
      - monitoring
    labelSelectors:
      app: incident-autopilot
  duration: "30s"
EOF
```

---

## 11. Scaling

### Horizontal Pod Autoscaler

```yaml
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: incident-autopilot
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: incident-autopilot
  minReplicas: 3
  maxReplicas: 20
  metrics:
  - type: Resource
    resource:
      name: cpu
      target:
        type: Utilization
        averageUtilization: 70
  - type: Resource
    resource:
      name: memory
      target:
        type: Utilization
        averageUtilization: 80
```

---

## 12. Cost Optimization

### LLM API Cost Management

```python
# In agents/base.py
class BaseAgent:
    def __init__(self):
        self.use_cache = True
        self.cache_ttl = 300  # 5 minutes
        
    async def call_llm(self, prompt: str):
        # Check cache first
        if cached := self.get_from_cache(prompt):
            return cached
        
        # Use smaller model for simple tasks
        model = "claude-3-haiku" if self.is_simple_task() else "claude-3-sonnet"
        
        response = await anthropic_client.messages.create(
            model=model,
            max_tokens=1000,  # Limit tokens
            messages=[{"role": "user", "content": prompt}]
        )
        
        self.save_to_cache(prompt, response)
        return response
```

---

## Production Checklist

- [ ] Docker image built and pushed
- [ ] Kubernetes deployment configured
- [ ] Secrets stored securely
- [ ] Redis/PostgreSQL set up
- [ ] RBAC configured for K8s access
- [ ] Monitoring and alerting configured
- [ ] Retool dashboard created
- [ ] Network policies applied
- [ ] Backup strategy implemented
- [ ] Disaster recovery tested
- [ ] Load testing completed
- [ ] Security audit passed
- [ ] Documentation updated
- [ ] On-call runbook created

---

## Support

For production issues:
- Check logs: `kubectl logs -n monitoring -l app=incident-autopilot`
- Check metrics: Prometheus/Grafana
- Review incidents: Retool dashboard
- Escalate: #incident-autopilot Slack channel

---

**Production-ready! 🚀**

