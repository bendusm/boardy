"""Security headers middleware for HTTP responses.

Adds standard security headers recommended by OWASP:
- X-Content-Type-Options: Prevent MIME type sniffing
- X-Frame-Options: Prevent clickjacking
- X-XSS-Protection: Enable XSS filtering (legacy browsers)
- Referrer-Policy: Control referrer information
- Strict-Transport-Security: Enforce HTTPS (production only)
- Content-Security-Policy: Prevent XSS and injection attacks
"""
from urllib.parse import urlparse

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response

from app.core.config import settings


class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next) -> Response:
        response = await call_next(request)

        # Prevent MIME type sniffing
        response.headers["X-Content-Type-Options"] = "nosniff"

        # Prevent clickjacking
        response.headers["X-Frame-Options"] = "DENY"

        # Legacy XSS protection for older browsers
        response.headers["X-XSS-Protection"] = "1; mode=block"

        # Control referrer information
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"

        # Enforce HTTPS in production
        if not settings.debug:
            response.headers["Strict-Transport-Security"] = (
                "max-age=31536000; includeSubDomains"
            )

        # Prevent caching of auth pages
        if request.url.path.startswith("/auth/"):
            response.headers["Cache-Control"] = "no-store, no-cache, must-revalidate"
            response.headers["Pragma"] = "no-cache"

        # Content Security Policy - protection against XSS and injection attacks
        parsed_url = urlparse(settings.app_url)
        domain = parsed_url.netloc or parsed_url.path  # Handle URLs with/without scheme
        app_url = settings.app_url

        is_auth_path = request.url.path.startswith("/auth/")

        csp_directives = [
            "default-src 'self'",
            "script-src 'self'",
            "style-src 'self' 'unsafe-inline'",
            "img-src 'self' data: blob:",
            "font-src 'self'",
            f"connect-src 'self' wss://{domain} https://{domain}",
            "frame-ancestors 'none'",
            "base-uri 'self'",
        ]
        # Only restrict form-action on non-auth pages
        if not is_auth_path:
            csp_directives.append("form-action 'self'")

        response.headers["Content-Security-Policy"] = "; ".join(csp_directives)

        return response
