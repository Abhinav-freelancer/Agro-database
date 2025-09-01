from fastapi import FastAPI, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp
import time
from typing import Callable, List
import os

class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """
    Middleware to add security headers to responses.
    """
    def __init__(self, app: ASGIApp):
        super().__init__(app)

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        response = await call_next(request)
        
        # Add security headers
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
        response.headers["Content-Security-Policy"] = "default-src 'self'; img-src 'self' data:; style-src 'self' 'unsafe-inline'; script-src 'self' 'unsafe-inline'; connect-src 'self' https://api.mapbox.com; font-src 'self' data:;"
        
        return response

class RateLimitMiddleware(BaseHTTPMiddleware):
    """
    Middleware to implement rate limiting.
    """
    def __init__(self, app: ASGIApp, requests_limit: int = 100, window_seconds: int = 60):
        super().__init__(app)
        self.requests_limit = requests_limit
        self.window_seconds = window_seconds
        self.requests = {}

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        # Get client IP
        client_ip = request.client.host if request.client else "unknown"
        
        # Check if client is in requests dict
        if client_ip not in self.requests:
            self.requests[client_ip] = []
        
        # Clean old requests
        current_time = time.time()
        self.requests[client_ip] = [req_time for req_time in self.requests[client_ip] 
                                  if current_time - req_time < self.window_seconds]
        
        # Check if client has exceeded rate limit
        if len(self.requests[client_ip]) >= self.requests_limit:
            return Response(
                content="Rate limit exceeded. Please try again later.",
                status_code=429,
                media_type="text/plain"
            )
        
        # Add current request time
        self.requests[client_ip].append(current_time)
        
        # Process request
        response = await call_next(request)
        
        # Add rate limit headers
        response.headers["X-RateLimit-Limit"] = str(self.requests_limit)
        response.headers["X-RateLimit-Remaining"] = str(self.requests_limit - len(self.requests[client_ip]))
        response.headers["X-RateLimit-Reset"] = str(int(current_time + self.window_seconds))
        
        return response

class RequestLoggingMiddleware(BaseHTTPMiddleware):
    """
    Middleware to log requests.
    """
    def __init__(self, app: ASGIApp):
        super().__init__(app)

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        start_time = time.time()
        
        # Process request
        response = await call_next(request)
        
        # Calculate processing time
        process_time = time.time() - start_time
        
        # Log request
        print(f"{request.method} {request.url.path} {response.status_code} {process_time:.4f}s")
        
        return response

def setup_security(app: FastAPI, allowed_origins: List[str] = None):
    """
    Set up security middleware for the FastAPI application.
    
    Args:
        app: FastAPI application
        allowed_origins: List of allowed CORS origins
    """
    # Set up CORS
    if allowed_origins is None:
        allowed_origins = ["http://localhost:3000", "http://localhost:8000"]
        
        # Add production origin if defined
        production_origin = os.getenv("PRODUCTION_ORIGIN")
        if production_origin:
            allowed_origins.append(production_origin)
    
    app.add_middleware(
        CORSMiddleware,
        allow_origins=allowed_origins,
        allow_credentials=True,
        allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
        allow_headers=["*"],
    )
    
    # Add security headers middleware
    app.add_middleware(SecurityHeadersMiddleware)
    
    # Add rate limiting middleware
    requests_limit = int(os.getenv("RATE_LIMIT", "100"))
    window_seconds = int(os.getenv("RATE_LIMIT_WINDOW", "60"))
    app.add_middleware(RateLimitMiddleware, requests_limit=requests_limit, window_seconds=window_seconds)
    
    # Add request logging middleware
    app.add_middleware(RequestLoggingMiddleware)