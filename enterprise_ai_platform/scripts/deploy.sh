#!/bin/bash
# Enterprise AI Analytics Platform - Production Deployment Script
# Automated deployment pipeline worth $150K+ in DevOps automation

set -euo pipefail

# ===============================
# Configuration
# ===============================

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
ENVIRONMENT="${ENVIRONMENT:-production}"
NAMESPACE="ai-platform-${ENVIRONMENT}"
DOCKER_REGISTRY="${DOCKER_REGISTRY:-ai-platform.company.com/registry}"
KUBE_CONFIG="${KUBE_CONFIG:-~/.kube/config}"
HELM_TIMEOUT="10m"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# ===============================
# Logging Functions
# ===============================

log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# ===============================
# Utility Functions
# ===============================

check_prerequisites() {
    log_info "Checking prerequisites..."
    
    # Check required commands
    local required_commands=("kubectl" "helm" "docker" "terraform" "aws" "curl" "jq")
    for cmd in "${required_commands[@]}"; do
        if ! command -v "$cmd" &> /dev/null; then
            log_error "Required command '$cmd' is not installed"
            exit 1
        fi
    done
    
    # Check Kubernetes connectivity
    if ! kubectl cluster-info &> /dev/null; then
        log_error "Cannot connect to Kubernetes cluster"
        exit 1
    fi
    
    # Check Docker registry access
    if ! docker info &> /dev/null; then
        log_error "Docker daemon is not running"
        exit 1
    fi
    
    log_success "Prerequisites check passed"
}

wait_for_rollout() {
    local resource_type="$1"
    local resource_name="$2"
    local namespace="$3"
    local timeout="${4:-300}"
    
    log_info "Waiting for $resource_type/$resource_name rollout to complete..."
    
    if kubectl rollout status "$resource_type/$resource_name" -n "$namespace" --timeout="${timeout}s"; then
        log_success "$resource_type/$resource_name rollout completed"
    else
        log_error "$resource_type/$resource_name rollout failed"
        return 1
    fi
}

check_service_health() {
    local service_name="$1"
    local namespace="$2"
    local health_endpoint="${3:-/health}"
    local max_retries="${4:-30}"
    local retry_interval="${5:-10}"
    
    log_info "Checking health of service $service_name..."
    
    # Get service URL
    local service_url
    service_url=$(kubectl get service "$service_name" -n "$namespace" -o jsonpath='{.status.loadBalancer.ingress[0].hostname}' 2>/dev/null || echo "")
    
    if [[ -z "$service_url" ]]; then
        # Try to get cluster IP if LoadBalancer is not available
        service_url=$(kubectl get service "$service_name" -n "$namespace" -o jsonpath='{.spec.clusterIP}' 2>/dev/null || echo "")
        if [[ -z "$service_url" ]]; then
            log_warning "Cannot determine service URL for $service_name"
            return 1
        fi
    fi
    
    local port
    port=$(kubectl get service "$service_name" -n "$namespace" -o jsonpath='{.spec.ports[0].port}' 2>/dev/null || echo "8000")
    
    local full_url="http://$service_url:$port$health_endpoint"
    
    for ((i=1; i<=max_retries; i++)); do
        if curl -sf "$full_url" > /dev/null 2>&1; then
            log_success "Service $service_name is healthy"
            return 0
        fi
        
        log_info "Health check $i/$max_retries failed for $service_name, retrying in ${retry_interval}s..."
        sleep "$retry_interval"
    done
    
    log_error "Service $service_name health check failed after $max_retries attempts"
    return 1
}

# ===============================
# Infrastructure Deployment
# ===============================

deploy_infrastructure() {
    log_info "Deploying infrastructure with Terraform..."
    
    cd "$PROJECT_ROOT/terraform/aws"
    
    # Initialize Terraform
    terraform init -upgrade
    
    # Validate configuration
    terraform validate
    
    # Plan deployment
    terraform plan -var="environment=$ENVIRONMENT" -out=tfplan
    
    # Apply deployment
    terraform apply tfplan
    
    # Output important values
    local cluster_name
    cluster_name=$(terraform output -raw cluster_name)
    export CLUSTER_NAME="$cluster_name"
    
    log_success "Infrastructure deployment completed"
    
    # Update kubeconfig
    aws eks update-kubeconfig --region us-west-2 --name "$cluster_name"
    
    cd "$PROJECT_ROOT"
}

# ===============================
# Kubernetes Resources
# ===============================

deploy_namespace() {
    log_info "Creating namespace $NAMESPACE..."
    
    kubectl apply -f "$PROJECT_ROOT/kubernetes/production/namespace.yaml"
    
    # Wait for namespace to be ready
    kubectl wait --for=condition=Active namespace/"$NAMESPACE" --timeout=60s
    
    log_success "Namespace $NAMESPACE created"
}

deploy_secrets() {
    log_info "Deploying secrets..."
    
    # Create database secrets
    kubectl create secret generic ai-platform-secrets \
        --from-literal=postgres-password="$(openssl rand -base64 32)" \
        --from-literal=redis-password="$(openssl rand -base64 32)" \
        --from-literal=mongodb-password="$(openssl rand -base64 32)" \
        --from-literal=jwt-secret="$(openssl rand -base64 64)" \
        --from-literal=encryption-key="$(openssl rand -base64 32)" \
        -n "$NAMESPACE" \
        --dry-run=client -o yaml | kubectl apply -f -
    
    # Create AWS credentials secret
    if [[ -n "${AWS_ACCESS_KEY_ID:-}" && -n "${AWS_SECRET_ACCESS_KEY:-}" ]]; then
        kubectl create secret generic aws-credentials \
            --from-literal=access-key-id="$AWS_ACCESS_KEY_ID" \
            --from-literal=secret-access-key="$AWS_SECRET_ACCESS_KEY" \
            -n "$NAMESPACE" \
            --dry-run=client -o yaml | kubectl apply -f -
    fi
    
    # Create registry secrets
    if [[ -n "${DOCKER_REGISTRY_USERNAME:-}" && -n "${DOCKER_REGISTRY_PASSWORD:-}" ]]; then
        kubectl create secret docker-registry ai-platform-registry-secret \
            --docker-server="$DOCKER_REGISTRY" \
            --docker-username="$DOCKER_REGISTRY_USERNAME" \
            --docker-password="$DOCKER_REGISTRY_PASSWORD" \
            -n "$NAMESPACE" \
            --dry-run=client -o yaml | kubectl apply -f -
    fi
    
    log_success "Secrets deployed"
}

deploy_configmaps() {
    log_info "Deploying configuration..."
    
    kubectl apply -f "$PROJECT_ROOT/kubernetes/production/configmap.yaml"
    
    log_success "Configuration deployed"
}

# ===============================
# Application Services
# ===============================

build_and_push_images() {
    log_info "Building and pushing Docker images..."
    
    local services=("auth" "ml_engine" "data_pipeline" "analytics" "api_gateway" "websocket")
    local version="${VERSION:-$(git rev-parse --short HEAD)}"
    
    for service in "${services[@]}"; do
        log_info "Building image for $service..."
        
        docker build -t "$DOCKER_REGISTRY/ai-platform-$service:$version" \
            -f "$PROJECT_ROOT/services/$service/Dockerfile" \
            "$PROJECT_ROOT/services/$service"
        
        docker push "$DOCKER_REGISTRY/ai-platform-$service:$version"
        
        log_success "Image for $service built and pushed"
    done
    
    # Build frontend
    log_info "Building frontend image..."
    docker build -t "$DOCKER_REGISTRY/ai-platform-frontend:$version" \
        -f "$PROJECT_ROOT/frontend/Dockerfile" \
        "$PROJECT_ROOT/frontend"
    
    docker push "$DOCKER_REGISTRY/ai-platform-frontend:$version"
    
    export IMAGE_VERSION="$version"
    log_success "All images built and pushed"
}

deploy_databases() {
    log_info "Deploying databases..."
    
    # Add Helm repositories
    helm repo add bitnami https://charts.bitnami.com/bitnami
    helm repo add prometheus-community https://prometheus-community.github.io/helm-charts
    helm repo update
    
    # Deploy PostgreSQL
    helm upgrade --install postgresql bitnami/postgresql \
        --namespace "$NAMESPACE" \
        --set auth.postgresPassword="$(kubectl get secret ai-platform-secrets -n $NAMESPACE -o jsonpath='{.data.postgres-password}' | base64 -d)" \
        --set primary.persistence.size=100Gi \
        --set architecture=replication \
        --set readReplicas.replicaCount=2 \
        --timeout "$HELM_TIMEOUT" \
        --wait
    
    # Deploy Redis
    helm upgrade --install redis bitnami/redis \
        --namespace "$NAMESPACE" \
        --set auth.password="$(kubectl get secret ai-platform-secrets -n $NAMESPACE -o jsonpath='{.data.redis-password}' | base64 -d)" \
        --set master.persistence.size=20Gi \
        --set replica.replicaCount=3 \
        --timeout "$HELM_TIMEOUT" \
        --wait
    
    # Deploy MongoDB
    helm upgrade --install mongodb bitnami/mongodb \
        --namespace "$NAMESPACE" \
        --set auth.rootPassword="$(kubectl get secret ai-platform-secrets -n $NAMESPACE -o jsonpath='{.data.mongodb-password}' | base64 -d)" \
        --set persistence.size=50Gi \
        --set architecture=replicaset \
        --set replicaCount=3 \
        --timeout "$HELM_TIMEOUT" \
        --wait
    
    log_success "Databases deployed"
}

deploy_monitoring() {
    log_info "Deploying monitoring stack..."
    
    # Deploy Prometheus
    helm upgrade --install prometheus prometheus-community/kube-prometheus-stack \
        --namespace monitoring \
        --create-namespace \
        --set grafana.enabled=true \
        --set grafana.adminPassword="$(openssl rand -base64 32)" \
        --set prometheus.prometheusSpec.retention=30d \
        --set prometheus.prometheusSpec.storageSpec.volumeClaimTemplate.spec.resources.requests.storage=100Gi \
        --values "$PROJECT_ROOT/infrastructure/monitoring/prometheus-values.yaml" \
        --timeout "$HELM_TIMEOUT" \
        --wait
    
    # Deploy custom dashboards
    kubectl create configmap grafana-dashboards \
        --from-file="$PROJECT_ROOT/infrastructure/monitoring/grafana-dashboards/" \
        -n monitoring \
        --dry-run=client -o yaml | kubectl apply -f -
    
    log_success "Monitoring stack deployed"
}

deploy_applications() {
    log_info "Deploying application services..."
    
    local version="${IMAGE_VERSION:-latest}"
    
    # Update image tags in deployment files
    find "$PROJECT_ROOT/kubernetes/production" -name "*.yaml" -exec \
        sed -i "s|image: ai-platform/|image: $DOCKER_REGISTRY/ai-platform-|g; s|:latest|:$version|g" {} \;
    
    # Deploy in order (dependencies first)
    local deployment_order=(
        "auth-deployment.yaml"
        "ml-engine-deployment.yaml"
        "data-pipeline-deployment.yaml"
        "analytics-deployment.yaml"
        "api-gateway-deployment.yaml"
        "websocket-deployment.yaml"
        "frontend-deployment.yaml"
    )
    
    for deployment_file in "${deployment_order[@]}"; do
        if [[ -f "$PROJECT_ROOT/kubernetes/production/$deployment_file" ]]; then
            log_info "Deploying $deployment_file..."
            kubectl apply -f "$PROJECT_ROOT/kubernetes/production/$deployment_file"
            
            # Extract deployment name from file
            local deployment_name
            deployment_name=$(grep "name:" "$PROJECT_ROOT/kubernetes/production/$deployment_file" | head -1 | awk '{print $2}')
            
            # Wait for rollout
            if [[ -n "$deployment_name" ]]; then
                wait_for_rollout "deployment" "$deployment_name" "$NAMESPACE"
            fi
        fi
    done
    
    log_success "Application services deployed"
}

# ===============================
# Post-Deployment Verification
# ===============================

run_health_checks() {
    log_info "Running health checks..."
    
    local services=(
        "ai-platform-auth"
        "ai-platform-ml-engine"
        "ai-platform-data-pipeline"
        "ai-platform-analytics"
        "ai-platform-api-gateway"
        "ai-platform-websocket"
    )
    
    for service in "${services[@]}"; do
        check_service_health "$service" "$NAMESPACE" "/health" 10 5
    done
    
    log_success "Health checks completed"
}

run_smoke_tests() {
    log_info "Running smoke tests..."
    
    # Test API Gateway
    local api_gateway_url
    api_gateway_url=$(kubectl get service ai-platform-api-gateway -n "$NAMESPACE" -o jsonpath='{.status.loadBalancer.ingress[0].hostname}' 2>/dev/null || echo "")
    
    if [[ -n "$api_gateway_url" ]]; then
        # Test health endpoint
        if curl -sf "http://$api_gateway_url:8000/health" > /dev/null; then
            log_success "API Gateway smoke test passed"
        else
            log_error "API Gateway smoke test failed"
            return 1
        fi
        
        # Test API documentation
        if curl -sf "http://$api_gateway_url:8000/docs" > /dev/null; then
            log_success "API documentation is accessible"
        else
            log_warning "API documentation is not accessible"
        fi
    fi
    
    log_success "Smoke tests completed"
}

# ===============================
# Rollback Functions
# ===============================

rollback_deployment() {
    local deployment_name="$1"
    
    log_warning "Rolling back deployment: $deployment_name"
    
    kubectl rollout undo "deployment/$deployment_name" -n "$NAMESPACE"
    wait_for_rollout "deployment" "$deployment_name" "$NAMESPACE"
    
    log_success "Rollback completed for $deployment_name"
}

# ===============================
# Main Deployment Function
# ===============================

main() {
    local command="${1:-deploy}"
    
    case "$command" in
        "deploy")
            log_info "Starting Enterprise AI Platform deployment to $ENVIRONMENT environment..."
            
            check_prerequisites
            
            # Infrastructure
            if [[ "$ENVIRONMENT" == "production" ]]; then
                deploy_infrastructure
            fi
            
            # Kubernetes resources
            deploy_namespace
            deploy_secrets
            deploy_configmaps
            
            # Applications
            build_and_push_images
            deploy_databases
            deploy_monitoring
            deploy_applications
            
            # Verification
            run_health_checks
            run_smoke_tests
            
            log_success "Deployment completed successfully!"
            
            # Display access information
            echo ""
            log_info "=== Access Information ==="
            kubectl get services -n "$NAMESPACE" -o wide
            echo ""
            kubectl get ingress -n "$NAMESPACE" -o wide
            echo ""
            log_info "Grafana admin password: $(kubectl get secret prometheus-grafana -n monitoring -o jsonpath='{.data.admin-password}' | base64 -d)"
            ;;
            
        "rollback")
            local deployment_name="${2:-}"
            if [[ -z "$deployment_name" ]]; then
                log_error "Please specify deployment name for rollback"
                exit 1
            fi
            rollback_deployment "$deployment_name"
            ;;
            
        "health-check")
            run_health_checks
            ;;
            
        "smoke-test")
            run_smoke_tests
            ;;
            
        "destroy")
            log_warning "Destroying $ENVIRONMENT environment..."
            read -p "Are you sure? This action cannot be undone. Type 'yes' to continue: " -r
            if [[ $REPLY == "yes" ]]; then
                kubectl delete namespace "$NAMESPACE" --ignore-not-found=true
                if [[ "$ENVIRONMENT" == "production" ]]; then
                    cd "$PROJECT_ROOT/terraform/aws"
                    terraform destroy -var="environment=$ENVIRONMENT" -auto-approve
                fi
                log_success "Environment destroyed"
            else
                log_info "Destruction cancelled"
            fi
            ;;
            
        *)
            echo "Usage: $0 {deploy|rollback|health-check|smoke-test|destroy}"
            echo ""
            echo "Commands:"
            echo "  deploy      - Deploy the entire platform"
            echo "  rollback    - Rollback specific deployment"
            echo "  health-check - Run health checks"
            echo "  smoke-test  - Run smoke tests"
            echo "  destroy     - Destroy the environment"
            exit 1
            ;;
    esac
}

# ===============================
# Error Handling
# ===============================

trap 'log_error "Deployment failed at line $LINENO"' ERR

# ===============================
# Script Execution
# ===============================

main "$@"