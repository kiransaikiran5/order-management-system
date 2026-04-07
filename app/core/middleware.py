from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
import time
import logging

logger = logging.getLogger(__name__)

class PerformanceMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        start_time = time.time()
        
        # Process request
        response = await call_next(request)
        
        # Calculate execution time
        execution_time = time.time() - start_time
        
        # Log slow requests
        if execution_time > 1.0:  # More than 1 second
            logger.warning(
                f"Slow request: {request.method} {request.url.path} "
                f"took {execution_time:.2f} seconds"
            )
        
        # Add response header
        response.headers["X-Execution-Time"] = str(execution_time)
        
        return response

class QueryCountMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        from app.core.database import SessionLocal
        
        response = await call_next(request)
        
        # Log query count (useful for debugging)
        if hasattr(request.state, 'query_count'):
            logger.info(f"Query count for {request.url.path}: {request.state.query_count}")
        
        return response