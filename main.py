from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
from database import connect_to_mongo, close_mongo_connection
from routes import events, rsvps
from logger import logger
import time

@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Lifespan context manager.
    
    Manages the application lifecycle:
    1. Startup: Connect to MongoDB when the app starts
    2. Yield: Application runs and serves requests
    3. Shutdown: Close MongoDB connection when app shuts down
    """
    # Startup
    logger.info("=" * 70)
    logger.info("🚀 Starting Event RSVP API with Service Layer Architecture")
    logger.info("=" * 70)
    await connect_to_mongo()
    logger.info("✅ Application startup complete")
    yield
    # Shutdown
    logger.info("=" * 70)
    logger.info("👋 Shutting down Event RSVP API...")
    logger.info("=" * 70)
    await close_mongo_connection()
    logger.info("✅ Application shutdown complete")

# Create FastAPI application
app = FastAPI(
    title="Event RSVP API",
    description="A complete REST API for managing events and RSVPs with Service Layer architecture",
    version="1.0.0",
    lifespan=lifespan
)

# ==================== REQUEST LOGGING MIDDLEWARE ====================

@app.middleware("http")
async def log_requests(request: Request, call_next):
    """
    Middleware to log all HTTP requests and responses.
    Tracks: method, path, status code, duration
    """
    start_time = time.time()
    
    # Log incoming request
    logger.info(f"➡️  {request.method} {request.url.path} - Client: {request.client.host}")
    
    try:
        # Process request
        response = await call_next(request)
        
        # Calculate duration
        duration = time.time() - start_time
        
        # Log response with appropriate emoji
        if response.status_code < 400:
            status_emoji = "✅"
            log_level = logger.info
        elif response.status_code < 500:
            status_emoji = "⚠️"
            log_level = logger.warning
        else:
            status_emoji = "❌"
            log_level = logger.error
        
        log_level(
            f"{status_emoji} {request.method} {request.url.path} "
            f"- Status: {response.status_code} - Duration: {duration:.3f}s"
        )
        
        return response
    
    except Exception as e:
        duration = time.time() - start_time
        logger.error(
            f"❌ {request.method} {request.url.path} "
            f"- Exception: {str(e)} - Duration: {duration:.3f}s"
        )
        raise

# ==================== HEALTH CHECK ====================

@app.get(
    "/health",
    tags=["Health"],
    summary="Health check",
    description="Check if the API is running and database is connected"
)
async def health_check():
    """
    Health check endpoint.
    
    Why? 
    - Monitoring systems can ping this to check if API is alive
    - Load balancers use this to route traffic only to healthy instances
    - Docker/Kubernetes use this for health checks
    """
    logger.debug("Health check endpoint called")
    return JSONResponse(
        status_code=200,
        content={
            "status": "healthy",
            "message": "Event RSVP API is running",
            "version": "1.0.0"
        }
    )

# ==================== ROOT ENDPOINT ====================

@app.get(
    "/",
    tags=["Root"],
    summary="API information",
    description="Get basic information about the API and available endpoints"
)
async def root():
    """
    Root endpoint - API welcome message.
    
    Provides basic info and links to documentation.
    """
    logger.debug("Root endpoint called")
    return {
        "message": "Welcome to Event RSVP API",
        "version": "1.0.0",
        "architecture": "Service Layer Pattern",
        "documentation": {
            "swagger_ui": "/docs",
            "redoc": "/redoc"
        },
        "health_check": "/health",
        "endpoints": {
            "events": "/events",
            "rsvps": "/rsvps"
        }
    }

# ==================== INCLUDE ROUTERS ====================

# Include the event routes (Controller layer)
app.include_router(events.router)
logger.info("✅ Event routes registered")

# Include the RSVP routes (Controller layer)
app.include_router(rsvps.router)
logger.info("✅ RSVP routes registered")

# ==================== RUN THE APP ====================

if __name__ == "__main__":
    import uvicorn
    print("=" * 70)
    print("🎉 Event RSVP API with Service Layer Architecture")
    print("=" * 70)
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True  # Auto-reload on code changes (development only)
    )