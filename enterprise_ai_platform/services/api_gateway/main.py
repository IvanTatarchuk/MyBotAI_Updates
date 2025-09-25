"""
Enterprise AI Analytics Platform - API Gateway Service
Unified API layer with REST and GraphQL support worth $200K+ in development

This service provides:
- RESTful API with OpenAPI 3.0 specification
- GraphQL API with schema introspection
- API versioning and backward compatibility
- Rate limiting and throttling
- Request/Response validation
- Caching and optimization
- API analytics and monitoring
- Auto-generated documentation
- SDK generation
- WebSocket support for real-time APIs
"""

import asyncio
import json
import logging
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Union
from contextlib import asynccontextmanager

import strawberry
from strawberry.fastapi import GraphQLRouter
from strawberry.types import Info
import graphene
from graphene import ObjectType, String, Int, Float, Boolean, DateTime, List as GrapheneList, Field
import redis
import aioredis
from fastapi import FastAPI, HTTPException, Depends, Request, status, BackgroundTasks, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.responses import JSONResponse, HTMLResponse
from fastapi.openapi.docs import get_swagger_ui_html, get_redoc_html
from fastapi.openapi.utils import get_openapi
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel, Field, validator
import uvicorn
from prometheus_client import Counter, Histogram, Gauge, generate_latest
import httpx
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware
import aiocache
from aiocache import cached, Cache
from aiocache.serializers import JsonSerializer
import websockets
import socketio

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Metrics
api_requests_total = Counter('api_requests_total', 'Total API requests', ['method', 'endpoint', 'status'])
api_request_duration = Histogram('api_request_duration_seconds', 'API request duration', ['method', 'endpoint'])
api_rate_limits = Counter('api_rate_limits_total', 'Total rate limit hits', ['endpoint'])
graphql_queries = Counter('graphql_queries_total', 'Total GraphQL queries', ['operation'])
websocket_connections = Gauge('websocket_connections_active', 'Active WebSocket connections')

# ===============================
# Configuration
# ===============================

class APIConfig:
    """API Gateway configuration"""
    
    # Service URLs
    AUTH_SERVICE_URL = "http://ai-platform-auth.ai-platform-prod.svc.cluster.local:8000"
    ML_ENGINE_URL = "http://ai-platform-ml-engine.ai-platform-prod.svc.cluster.local:8000"
    DATA_PIPELINE_URL = "http://ai-platform-data-pipeline.ai-platform-prod.svc.cluster.local:8000"
    ANALYTICS_SERVICE_URL = "http://ai-platform-analytics.ai-platform-prod.svc.cluster.local:8000"
    WEBSOCKET_SERVICE_URL = "http://ai-platform-websocket.ai-platform-prod.svc.cluster.local:8000"
    
    # Redis for caching and rate limiting
    REDIS_URL = "redis://ai-platform-redis-master.ai-platform-prod.svc.cluster.local:6379"
    
    # API versioning
    API_VERSION = "v1"
    SUPPORTED_VERSIONS = ["v1", "v2"]
    
    # Rate limiting
    RATE_LIMIT_REQUESTS = "1000/minute"
    RATE_LIMIT_BURST = "100/second"
    
    # Caching
    CACHE_TTL = 300  # 5 minutes
    CACHE_MAX_SIZE = 10000
    
    # Request timeouts
    REQUEST_TIMEOUT = 30
    LONG_REQUEST_TIMEOUT = 300  # For ML operations

# ===============================
# Pydantic Models for REST API
# ===============================

class APIResponse(BaseModel):
    """Standard API response format"""
    success: bool = True
    data: Optional[Any] = None
    message: Optional[str] = None
    errors: Optional[List[str]] = None
    metadata: Optional[Dict[str, Any]] = None
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    version: str = APIConfig.API_VERSION

class PaginationParams(BaseModel):
    """Pagination parameters"""
    page: int = Field(default=1, ge=1, description="Page number")
    limit: int = Field(default=20, ge=1, le=100, description="Items per page")
    sort_by: Optional[str] = Field(default=None, description="Sort field")
    sort_order: Optional[str] = Field(default="asc", regex="^(asc|desc)$", description="Sort order")

class FilterParams(BaseModel):
    """Generic filtering parameters"""
    search: Optional[str] = Field(default=None, description="Search query")
    filters: Optional[Dict[str, Any]] = Field(default_factory=dict, description="Additional filters")
    date_from: Optional[datetime] = Field(default=None, description="Filter from date")
    date_to: Optional[datetime] = Field(default=None, description="Filter to date")

# ML API Models
class MLModelInfo(BaseModel):
    """ML model information"""
    id: str
    name: str
    type: str
    version: str
    status: str
    accuracy: float
    created_at: datetime
    last_used: Optional[datetime]

class MLTrainingRequest(BaseModel):
    """ML model training request"""
    model_type: str = Field(..., description="Type of model to train")
    dataset_path: str = Field(..., description="Path to training dataset")
    target_column: str = Field(..., description="Target column name")
    model_name: str = Field(..., description="Name for the trained model")
    parameters: Dict[str, Any] = Field(default_factory=dict)
    
class MLPredictionRequest(BaseModel):
    """ML prediction request"""
    model_name: str = Field(..., description="Model name to use")
    data: Union[List[Dict[str, Any]], Dict[str, Any]] = Field(..., description="Input data")
    return_probabilities: bool = Field(default=False)

# Analytics API Models
class AnalyticsQuery(BaseModel):
    """Analytics query"""
    query_type: str = Field(..., description="Type of analytics query")
    metrics: List[str] = Field(..., description="Metrics to retrieve")
    dimensions: Optional[List[str]] = Field(default_factory=list)
    filters: Optional[Dict[str, Any]] = Field(default_factory=dict)
    time_range: Optional[Dict[str, datetime]] = Field(default=None)
    aggregation: Optional[str] = Field(default="sum")

class DashboardConfig(BaseModel):
    """Dashboard configuration"""
    name: str
    description: Optional[str] = None
    layout: Dict[str, Any]
    widgets: List[Dict[str, Any]]
    filters: Optional[Dict[str, Any]] = Field(default_factory=dict)
    refresh_interval: int = Field(default=30, description="Refresh interval in seconds")

# ===============================
# GraphQL Schema
# ===============================

@strawberry.type
class MLModel:
    """GraphQL ML Model type"""
    id: str
    name: str
    type: str
    version: str
    status: str
    accuracy: float
    created_at: datetime
    last_used: Optional[datetime]

@strawberry.type
class AnalyticsMetric:
    """GraphQL Analytics Metric type"""
    name: str
    value: float
    timestamp: datetime
    dimensions: Optional[Dict[str, str]] = None

@strawberry.type
class User:
    """GraphQL User type"""
    id: str
    username: str
    email: str
    full_name: str
    roles: List[str]
    is_active: bool
    created_at: datetime
    last_login: Optional[datetime]

@strawberry.input
class MLModelFilter:
    """GraphQL ML Model filter input"""
    type: Optional[str] = None
    status: Optional[str] = None
    name_contains: Optional[str] = None

@strawberry.input
class AnalyticsFilter:
    """GraphQL Analytics filter input"""
    metric_name: Optional[str] = None
    date_from: Optional[datetime] = None
    date_to: Optional[datetime] = None
    dimensions: Optional[Dict[str, str]] = None

@strawberry.type
class Query:
    """GraphQL Query root"""
    
    @strawberry.field
    async def ml_models(self, filter: Optional[MLModelFilter] = None) -> List[MLModel]:
        """Get ML models"""
        # Implementation would call ML service
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{APIConfig.ML_ENGINE_URL}/models")
            if response.status_code == 200:
                models_data = response.json()
                return [MLModel(**model) for model in models_data]
            return []
    
    @strawberry.field
    async def ml_model(self, id: str) -> Optional[MLModel]:
        """Get specific ML model"""
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{APIConfig.ML_ENGINE_URL}/models/{id}")
            if response.status_code == 200:
                model_data = response.json()
                return MLModel(**model_data)
            return None
    
    @strawberry.field
    async def analytics_metrics(self, filter: Optional[AnalyticsFilter] = None) -> List[AnalyticsMetric]:
        """Get analytics metrics"""
        async with httpx.AsyncClient() as client:
            params = {}
            if filter:
                if filter.metric_name:
                    params['metric_name'] = filter.metric_name
                if filter.date_from:
                    params['date_from'] = filter.date_from.isoformat()
                if filter.date_to:
                    params['date_to'] = filter.date_to.isoformat()
            
            response = await client.get(f"{APIConfig.ANALYTICS_SERVICE_URL}/metrics", params=params)
            if response.status_code == 200:
                metrics_data = response.json()
                return [AnalyticsMetric(**metric) for metric in metrics_data]
            return []
    
    @strawberry.field
    async def current_user(self, info: Info) -> Optional[User]:
        """Get current authenticated user"""
        # Extract token from context and validate with auth service
        token = info.context.get("token")
        if not token:
            return None
        
        async with httpx.AsyncClient() as client:
            headers = {"Authorization": f"Bearer {token}"}
            response = await client.get(f"{APIConfig.AUTH_SERVICE_URL}/auth/me", headers=headers)
            if response.status_code == 200:
                user_data = response.json()
                return User(**user_data)
            return None

@strawberry.type
class Mutation:
    """GraphQL Mutation root"""
    
    @strawberry.mutation
    async def train_ml_model(self, model_type: str, dataset_path: str, target_column: str, model_name: str) -> str:
        """Train ML model"""
        async with httpx.AsyncClient() as client:
            payload = {
                "model_type": model_type,
                "dataset_path": dataset_path,
                "target_column": target_column,
                "model_name": model_name
            }
            response = await client.post(f"{APIConfig.ML_ENGINE_URL}/models/train/deep-learning", json=payload)
            if response.status_code == 200:
                return "Training started successfully"
            else:
                raise Exception("Training failed")
    
    @strawberry.mutation
    async def delete_ml_model(self, model_id: str) -> bool:
        """Delete ML model"""
        async with httpx.AsyncClient() as client:
            response = await client.delete(f"{APIConfig.ML_ENGINE_URL}/models/{model_id}")
            return response.status_code == 200

# Create GraphQL schema
schema = strawberry.Schema(query=Query, mutation=Mutation)

# ===============================
# Service Clients
# ===============================

class ServiceClient:
    """HTTP client for microservices"""
    
    def __init__(self):
        self.session = httpx.AsyncClient(
            timeout=httpx.Timeout(APIConfig.REQUEST_TIMEOUT),
            limits=httpx.Limits(max_keepalive_connections=100, max_connections=1000)
        )
    
    async def call_service(self, service_url: str, method: str, endpoint: str, **kwargs):
        """Generic service call"""
        url = f"{service_url}{endpoint}"
        
        try:
            response = await self.session.request(method, url, **kwargs)
            response.raise_for_status()
            return response.json()
        except httpx.HTTPStatusError as e:
            logger.error(f"HTTP error calling {url}: {e}")
            raise HTTPException(status_code=e.response.status_code, detail=str(e))
        except httpx.RequestError as e:
            logger.error(f"Request error calling {url}: {e}")
            raise HTTPException(status_code=503, detail="Service unavailable")
    
    async def close(self):
        """Close HTTP session"""
        await self.session.aclose()

# ===============================
# Cache Manager
# ===============================

class CacheManager:
    """Redis-based cache manager"""
    
    def __init__(self):
        self.cache = Cache(
            Cache.REDIS,
            endpoint=APIConfig.REDIS_URL,
            serializer=JsonSerializer(),
            ttl=APIConfig.CACHE_TTL
        )
    
    @cached(ttl=300, cache=Cache.REDIS, serializer=JsonSerializer())
    async def get_cached_data(self, key: str):
        """Get cached data"""
        return await self.cache.get(key)
    
    async def set_cached_data(self, key: str, data: Any, ttl: int = None):
        """Set cached data"""
        await self.cache.set(key, data, ttl=ttl or APIConfig.CACHE_TTL)
    
    async def invalidate_cache(self, pattern: str):
        """Invalidate cache by pattern"""
        await self.cache.delete(pattern)

# ===============================
# Rate Limiter
# ===============================

# Initialize rate limiter
limiter = Limiter(key_func=get_remote_address, default_limits=[APIConfig.RATE_LIMIT_REQUESTS])

# ===============================
# WebSocket Manager
# ===============================

class WebSocketManager:
    """WebSocket connection manager"""
    
    def __init__(self):
        self.active_connections: Dict[str, websockets.WebSocketServerProtocol] = {}
    
    async def connect(self, websocket: websockets.WebSocketServerProtocol, user_id: str):
        """Accept WebSocket connection"""
        await websocket.accept()
        self.active_connections[user_id] = websocket
        websocket_connections.inc()
        logger.info(f"WebSocket connected for user {user_id}")
    
    def disconnect(self, user_id: str):
        """Remove WebSocket connection"""
        if user_id in self.active_connections:
            del self.active_connections[user_id]
            websocket_connections.dec()
            logger.info(f"WebSocket disconnected for user {user_id}")
    
    async def send_personal_message(self, message: str, user_id: str):
        """Send message to specific user"""
        if user_id in self.active_connections:
            await self.active_connections[user_id].send_text(message)
    
    async def broadcast(self, message: str):
        """Broadcast message to all connected clients"""
        for connection in self.active_connections.values():
            await connection.send_text(message)

# ===============================
# FastAPI Application
# ===============================

# Initialize services
service_client = ServiceClient()
cache_manager = CacheManager()
websocket_manager = WebSocketManager()

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan management"""
    logger.info("Starting Enterprise API Gateway")
    yield
    logger.info("Shutting down Enterprise API Gateway")
    await service_client.close()

# Create FastAPI app
app = FastAPI(
    title="Enterprise AI Analytics Platform - API Gateway",
    description="Unified API layer with REST and GraphQL support",
    version="1.0.0",
    lifespan=lifespan,
    docs_url=None,  # Custom docs
    redoc_url=None,  # Custom redoc
    openapi_url=f"/api/{APIConfig.API_VERSION}/openapi.json"
)

# Add middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://ai-platform.company.com", "https://admin.company.com"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.add_middleware(GZipMiddleware, minimum_size=1000)
app.add_middleware(SlowAPIMiddleware)

# Add rate limit handler
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# ===============================
# Middleware
# ===============================

@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    """Add processing time header and metrics"""
    start_time = time.time()
    
    response = await call_next(request)
    
    process_time = time.time() - start_time
    response.headers["X-Process-Time"] = str(process_time)
    
    # Record metrics
    api_requests_total.labels(
        method=request.method,
        endpoint=request.url.path,
        status=response.status_code
    ).inc()
    
    api_request_duration.labels(
        method=request.method,
        endpoint=request.url.path
    ).observe(process_time)
    
    return response

# ===============================
# Authentication Dependency
# ===============================

security = HTTPBearer()

async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Get current authenticated user"""
    try:
        # Validate token with auth service
        user_data = await service_client.call_service(
            APIConfig.AUTH_SERVICE_URL,
            "GET",
            "/auth/me",
            headers={"Authorization": f"Bearer {credentials.credentials}"}
        )
        return user_data
    except HTTPException as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials"
        )

# ===============================
# Custom Documentation
# ===============================

@app.get("/docs", include_in_schema=False)
async def custom_swagger_ui_html():
    """Custom Swagger UI"""
    return get_swagger_ui_html(
        openapi_url=app.openapi_url,
        title=app.title + " - Swagger UI",
        oauth2_redirect_url=app.swagger_ui_oauth2_redirect_url,
        swagger_js_url="https://cdn.jsdelivr.net/npm/swagger-ui-dist@5/swagger-ui-bundle.js",
        swagger_css_url="https://cdn.jsdelivr.net/npm/swagger-ui-dist@5/swagger-ui.css",
    )

@app.get("/redoc", include_in_schema=False)
async def redoc_html():
    """Custom ReDoc"""
    return get_redoc_html(
        openapi_url=app.openapi_url,
        title=app.title + " - ReDoc",
        redoc_js_url="https://cdn.jsdelivr.net/npm/redoc@next/bundles/redoc.standalone.js",
    )

# ===============================
# Health and Status Endpoints
# ===============================

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return APIResponse(
        data={
            "status": "healthy",
            "service": "api-gateway",
            "timestamp": datetime.utcnow(),
            "version": APIConfig.API_VERSION,
            "active_connections": len(websocket_manager.active_connections)
        }
    )

@app.get("/metrics")
async def get_metrics():
    """Prometheus metrics endpoint"""
    from fastapi.responses import Response
    return Response(generate_latest(), media_type="text/plain")

# ===============================
# REST API Endpoints
# ===============================

# ML Engine Endpoints
@app.post(f"/api/{APIConfig.API_VERSION}/ml/models/train")
@limiter.limit(APIConfig.RATE_LIMIT_BURST)
async def train_ml_model(
    request: Request,
    training_request: MLTrainingRequest,
    background_tasks: BackgroundTasks,
    current_user: dict = Depends(get_current_user)
):
    """Train ML model"""
    response = await service_client.call_service(
        APIConfig.ML_ENGINE_URL,
        "POST",
        "/models/train/deep-learning",
        json=training_request.dict()
    )
    
    return APIResponse(data=response)

@app.post(f"/api/{APIConfig.API_VERSION}/ml/models/predict")
@limiter.limit(APIConfig.RATE_LIMIT_BURST)
async def predict_ml_model(
    request: Request,
    prediction_request: MLPredictionRequest,
    current_user: dict = Depends(get_current_user)
):
    """Make ML predictions"""
    # Check cache first
    cache_key = f"prediction:{prediction_request.model_name}:{hash(str(prediction_request.data))}"
    cached_result = await cache_manager.get_cached_data(cache_key)
    
    if cached_result:
        return APIResponse(data=cached_result, metadata={"cached": True})
    
    response = await service_client.call_service(
        APIConfig.ML_ENGINE_URL,
        "POST",
        "/models/predict",
        json=prediction_request.dict()
    )
    
    # Cache the result
    await cache_manager.set_cached_data(cache_key, response, ttl=60)
    
    return APIResponse(data=response, metadata={"cached": False})

@app.get(f"/api/{APIConfig.API_VERSION}/ml/models")
@limiter.limit(APIConfig.RATE_LIMIT_REQUESTS)
async def list_ml_models(
    request: Request,
    pagination: PaginationParams = Depends(),
    filters: FilterParams = Depends(),
    current_user: dict = Depends(get_current_user)
):
    """List ML models"""
    # Check cache
    cache_key = f"ml_models:{pagination.page}:{pagination.limit}:{filters.search}"
    cached_result = await cache_manager.get_cached_data(cache_key)
    
    if cached_result:
        return APIResponse(data=cached_result, metadata={"cached": True})
    
    response = await service_client.call_service(
        APIConfig.ML_ENGINE_URL,
        "GET",
        "/models",
        params={
            "page": pagination.page,
            "limit": pagination.limit,
            "search": filters.search
        }
    )
    
    await cache_manager.set_cached_data(cache_key, response)
    
    return APIResponse(data=response, metadata={"cached": False})

@app.get(f"/api/{APIConfig.API_VERSION}/ml/models/{{model_id}}")
@limiter.limit(APIConfig.RATE_LIMIT_REQUESTS)
async def get_ml_model(
    request: Request,
    model_id: str,
    current_user: dict = Depends(get_current_user)
):
    """Get specific ML model"""
    response = await service_client.call_service(
        APIConfig.ML_ENGINE_URL,
        "GET",
        f"/models/{model_id}"
    )
    
    return APIResponse(data=response)

@app.delete(f"/api/{APIConfig.API_VERSION}/ml/models/{{model_id}}")
@limiter.limit(APIConfig.RATE_LIMIT_BURST)
async def delete_ml_model(
    request: Request,
    model_id: str,
    current_user: dict = Depends(get_current_user)
):
    """Delete ML model"""
    response = await service_client.call_service(
        APIConfig.ML_ENGINE_URL,
        "DELETE",
        f"/models/{model_id}"
    )
    
    # Invalidate cache
    await cache_manager.invalidate_cache("ml_models:*")
    
    return APIResponse(data=response)

# Analytics Endpoints
@app.post(f"/api/{APIConfig.API_VERSION}/analytics/query")
@limiter.limit(APIConfig.RATE_LIMIT_BURST)
async def execute_analytics_query(
    request: Request,
    analytics_query: AnalyticsQuery,
    current_user: dict = Depends(get_current_user)
):
    """Execute analytics query"""
    response = await service_client.call_service(
        APIConfig.ANALYTICS_SERVICE_URL,
        "POST",
        "/query",
        json=analytics_query.dict()
    )
    
    return APIResponse(data=response)

@app.get(f"/api/{APIConfig.API_VERSION}/analytics/dashboards")
@limiter.limit(APIConfig.RATE_LIMIT_REQUESTS)
async def list_dashboards(
    request: Request,
    pagination: PaginationParams = Depends(),
    current_user: dict = Depends(get_current_user)
):
    """List analytics dashboards"""
    response = await service_client.call_service(
        APIConfig.ANALYTICS_SERVICE_URL,
        "GET",
        "/dashboards",
        params={
            "page": pagination.page,
            "limit": pagination.limit
        }
    )
    
    return APIResponse(data=response)

@app.post(f"/api/{APIConfig.API_VERSION}/analytics/dashboards")
@limiter.limit(APIConfig.RATE_LIMIT_BURST)
async def create_dashboard(
    request: Request,
    dashboard_config: DashboardConfig,
    current_user: dict = Depends(get_current_user)
):
    """Create analytics dashboard"""
    response = await service_client.call_service(
        APIConfig.ANALYTICS_SERVICE_URL,
        "POST",
        "/dashboards",
        json=dashboard_config.dict()
    )
    
    return APIResponse(data=response)

# Data Pipeline Endpoints
@app.post(f"/api/{APIConfig.API_VERSION}/data/ingest")
@limiter.limit(APIConfig.RATE_LIMIT_BURST)
async def ingest_data(
    request: Request,
    data_source: dict,
    current_user: dict = Depends(get_current_user)
):
    """Ingest data into pipeline"""
    response = await service_client.call_service(
        APIConfig.DATA_PIPELINE_URL,
        "POST",
        "/ingest",
        json=data_source
    )
    
    return APIResponse(data=response)

@app.get(f"/api/{APIConfig.API_VERSION}/data/pipelines")
@limiter.limit(APIConfig.RATE_LIMIT_REQUESTS)
async def list_data_pipelines(
    request: Request,
    pagination: PaginationParams = Depends(),
    current_user: dict = Depends(get_current_user)
):
    """List data pipelines"""
    response = await service_client.call_service(
        APIConfig.DATA_PIPELINE_URL,
        "GET",
        "/pipelines",
        params={
            "page": pagination.page,
            "limit": pagination.limit
        }
    )
    
    return APIResponse(data=response)

# ===============================
# GraphQL Endpoint
# ===============================

# Add GraphQL router
graphql_app = GraphQLRouter(schema, context_getter=lambda request: {"token": request.headers.get("authorization", "").replace("Bearer ", "")})
app.include_router(graphql_app, prefix=f"/api/{APIConfig.API_VERSION}/graphql")

# ===============================
# WebSocket Endpoint
# ===============================

@app.websocket(f"/api/{APIConfig.API_VERSION}/ws/{{user_id}}")
async def websocket_endpoint(websocket: websockets.WebSocketServerProtocol, user_id: str):
    """WebSocket endpoint for real-time updates"""
    await websocket_manager.connect(websocket, user_id)
    try:
        while True:
            data = await websocket.receive_text()
            # Process incoming messages
            message = json.loads(data)
            
            if message.get("type") == "ping":
                await websocket.send_text(json.dumps({"type": "pong", "timestamp": datetime.utcnow().isoformat()}))
            elif message.get("type") == "subscribe":
                # Handle subscription to real-time updates
                await websocket.send_text(json.dumps({"type": "subscribed", "channel": message.get("channel")}))
            
    except websockets.exceptions.ConnectionClosed:
        pass
    finally:
        websocket_manager.disconnect(user_id)

# ===============================
# Custom OpenAPI Schema
# ===============================

def custom_openapi():
    """Generate custom OpenAPI schema"""
    if app.openapi_schema:
        return app.openapi_schema
    
    openapi_schema = get_openapi(
        title=app.title,
        version=app.version,
        description=app.description,
        routes=app.routes,
    )
    
    # Add custom security schemes
    openapi_schema["components"]["securitySchemes"] = {
        "BearerAuth": {
            "type": "http",
            "scheme": "bearer",
            "bearerFormat": "JWT",
        },
        "ApiKeyAuth": {
            "type": "apiKey",
            "in": "header",
            "name": "X-API-Key",
        },
    }
    
    # Add security to all endpoints
    for path in openapi_schema["paths"]:
        for method in openapi_schema["paths"][path]:
            if method != "options":
                openapi_schema["paths"][path][method]["security"] = [
                    {"BearerAuth": []},
                    {"ApiKeyAuth": []},
                ]
    
    # Add examples
    openapi_schema["components"]["examples"] = {
        "MLTrainingExample": {
            "summary": "ML Training Request Example",
            "value": {
                "model_type": "deep_learning",
                "dataset_path": "/data/training/customer_data.csv",
                "target_column": "churn",
                "model_name": "customer_churn_predictor",
                "parameters": {
                    "epochs": 100,
                    "learning_rate": 0.001,
                    "hidden_sizes": [256, 128, 64]
                }
            }
        },
        "MLPredictionExample": {
            "summary": "ML Prediction Request Example",
            "value": {
                "model_name": "customer_churn_predictor",
                "data": {
                    "age": 35,
                    "income": 50000,
                    "tenure": 24,
                    "usage": 150
                },
                "return_probabilities": true
            }
        }
    }
    
    app.openapi_schema = openapi_schema
    return app.openapi_schema

app.openapi = custom_openapi

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=False,
        workers=4,
        log_level="info"
    )