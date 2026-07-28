# CryptoVault AI Deployment Guide

## Prerequisites

- Docker & Docker Compose
- Kubernetes cluster (for production)
- Domain name (cryptovault.ai)
- SSL certificates
- API keys for services

## Local Development

1. Clone the repository:
```bash
git clone https://github.com/your-org/cryptovault-ai.git
cd cryptovault-ai
```

2. Copy environment variables:
```bash
cp .env.example .env
# Edit .env with your values
```

3. Start services with Docker Compose:
```bash
docker-compose up -d
```

4. Access the application:
- Frontend: http://localhost:3000
- Backend API: http://localhost:4000/graphql
- ML Engine: http://localhost:5002/docs

## Production Deployment

### 1. Build Docker Images

```bash
# Build all images
docker build -t cryptovault/backend:latest ./backend
docker build -t cryptovault/frontend:latest ./frontend
docker build -t cryptovault/blockchain-service:latest ./services/blockchain
docker build -t cryptovault/ml-engine:latest ./services/ml-engine

# Push to registry
docker push cryptovault/backend:latest
docker push cryptovault/frontend:latest
docker push cryptovault/blockchain-service:latest
docker push cryptovault/ml-engine:latest
```

### 2. Create Kubernetes Secrets

```bash
kubectl create namespace cryptovault

kubectl create secret generic cryptovault-secrets \
  --from-literal=db-password=$DB_PASSWORD \
  --from-literal=redis-password=$REDIS_PASSWORD \
  --from-literal=jwt-secret=$JWT_SECRET \
  --from-literal=stripe-secret-key=$STRIPE_SECRET_KEY \
  --from-literal=database-url=$DATABASE_URL \
  --from-literal=redis-url=$REDIS_URL \
  -n cryptovault
```

### 3. Deploy to Kubernetes

```bash
kubectl apply -f infrastructure/kubernetes/deployment.yaml
```

### 4. Setup SSL with cert-manager

```bash
# Install cert-manager
kubectl apply -f https://github.com/cert-manager/cert-manager/releases/download/v1.13.0/cert-manager.yaml

# Create ClusterIssuer
kubectl apply -f infrastructure/kubernetes/cluster-issuer.yaml
```

### 5. Configure DNS

Point your domain to the Kubernetes ingress IP:
- cryptovault.ai → Ingress IP
- api.cryptovault.ai → Ingress IP

## Database Migrations

```bash
# Run migrations
kubectl exec -it deployment/backend -n cryptovault -- npm run migrate

# Create admin user
kubectl exec -it deployment/backend -n cryptovault -- npm run seed:admin
```

## Monitoring

### Prometheus & Grafana

```bash
# Install Prometheus
helm install prometheus prometheus-community/kube-prometheus-stack -n monitoring

# Access Grafana
kubectl port-forward -n monitoring svc/prometheus-grafana 3000:80
```

### Application Logs

```bash
# Backend logs
kubectl logs -f deployment/backend -n cryptovault

# ML Engine logs
kubectl logs -f deployment/ml-engine -n cryptovault
```

## Backup & Recovery

### Database Backup

```bash
# Create backup
kubectl exec -it deployment/postgres -n cryptovault -- \
  pg_dump -U cryptovault cryptovault > backup-$(date +%Y%m%d).sql

# Restore backup
kubectl exec -i deployment/postgres -n cryptovault -- \
  psql -U cryptovault cryptovault < backup-20240101.sql
```

### Automated Backups

Configure automated backups using CronJob:
```bash
kubectl apply -f infrastructure/kubernetes/backup-cronjob.yaml
```

## Scaling

### Horizontal Scaling

```bash
# Scale backend
kubectl scale deployment backend --replicas=5 -n cryptovault

# Scale ML engine
kubectl scale deployment ml-engine --replicas=3 -n cryptovault
```

### Vertical Scaling

Edit resource limits in deployment.yaml and apply:
```bash
kubectl apply -f infrastructure/kubernetes/deployment.yaml
```

## Security

### Network Policies

```bash
kubectl apply -f infrastructure/kubernetes/network-policies.yaml
```

### Security Scanning

```bash
# Scan images for vulnerabilities
trivy image cryptovault/backend:latest
trivy image cryptovault/frontend:latest
```

## Troubleshooting

### Common Issues

1. **Database Connection Issues**
   ```bash
   kubectl exec -it deployment/backend -n cryptovault -- nc -zv postgres 5432
   ```

2. **Redis Connection Issues**
   ```bash
   kubectl exec -it deployment/backend -n cryptovault -- redis-cli -h redis ping
   ```

3. **ML Model Loading Issues**
   ```bash
   kubectl exec -it deployment/ml-engine -n cryptovault -- ls -la /app/models
   ```

### Debug Mode

Enable debug logging:
```bash
kubectl set env deployment/backend LOG_LEVEL=debug -n cryptovault
kubectl set env deployment/ml-engine LOG_LEVEL=debug -n cryptovault
```

## Performance Optimization

1. **Enable Redis Caching**
   - Price data: 30s TTL
   - User sessions: 1h TTL
   - API responses: 5m TTL

2. **CDN Configuration**
   - Static assets
   - API responses (where applicable)

3. **Database Optimization**
   - Create indexes
   - Enable query caching
   - Connection pooling

## Maintenance

### Rolling Updates

```bash
# Update backend
kubectl set image deployment/backend backend=cryptovault/backend:v2.0.0 -n cryptovault

# Check rollout status
kubectl rollout status deployment/backend -n cryptovault
```

### Health Checks

```bash
# Check all pods
kubectl get pods -n cryptovault

# Check services
kubectl get svc -n cryptovault

# Check ingress
kubectl get ingress -n cryptovault
```

## Cost Optimization

1. **Use Spot Instances** for non-critical workloads
2. **Enable autoscaling** based on metrics
3. **Optimize container images** (multi-stage builds)
4. **Use persistent volume snapshots** instead of full backups

## Support

- Documentation: https://docs.cryptovault.ai
- Support Email: support@cryptovault.ai
- Status Page: https://status.cryptovault.ai