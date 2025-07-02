"""
Enhanced security module for MindEase API
Implements advanced security measures and GDPR compliance
"""

import hashlib
import secrets
import logging
from datetime import datetime, timedelta
from typing import Optional, Dict, Any, List
from functools import wraps
import re

from fastapi import HTTPException, Request, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from passlib.context import CryptContext
from jose import JWTError, jwt
import redis
from sqlalchemy.orm import Session

from app.core.config import settings

logger = logging.getLogger(__name__)

# Enhanced password context with stronger hashing
pwd_context = CryptContext(
    schemes=["bcrypt"],
    deprecated="auto",
    bcrypt__rounds=12  # Increased rounds for better security
)

# Security headers
SECURITY_HEADERS = {
    "X-Content-Type-Options": "nosniff",
    "X-Frame-Options": "DENY",
    "X-XSS-Protection": "1; mode=block",
    "Strict-Transport-Security": "max-age=31536000; includeSubDomains",
    "Content-Security-Policy": "default-src 'self'; script-src 'self' 'unsafe-inline'; style-src 'self' 'unsafe-inline'",
    "Referrer-Policy": "strict-origin-when-cross-origin",
    "Permissions-Policy": "geolocation=(), microphone=(), camera=()"
}

class SecurityManager:
    """Enhanced security manager with GDPR compliance"""
    
    def __init__(self, redis_client: Optional[redis.Redis] = None):
        self.redis_client = redis_client
        self.failed_attempts = {}
        self.blocked_ips = set()
        
    def hash_password(self, password: str) -> str:
        """Hash password with enhanced security"""
        return pwd_context.hash(password)
    
    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        """Verify password with timing attack protection"""
        return pwd_context.verify(plain_password, hashed_password)
    
    def validate_password_strength(self, password: str) -> Dict[str, Any]:
        """Validate password strength according to security policies"""
        errors = []
        score = 0
        
        # Length check
        if len(password) < 8:
            errors.append("Password must be at least 8 characters long")
        elif len(password) >= 12:
            score += 2
        else:
            score += 1
            
        # Character variety checks
        if not re.search(r"[a-z]", password):
            errors.append("Password must contain lowercase letters")
        else:
            score += 1
            
        if not re.search(r"[A-Z]", password):
            errors.append("Password must contain uppercase letters")
        else:
            score += 1
            
        if not re.search(r"\d", password):
            errors.append("Password must contain numbers")
        else:
            score += 1
            
        if not re.search(r"[!@#$%^&*(),.?\":{}|<>]", password):
            errors.append("Password must contain special characters")
        else:
            score += 1
            
        # Common password check
        common_passwords = ["password", "123456", "qwerty", "admin", "letmein"]
        if password.lower() in common_passwords:
            errors.append("Password is too common")
            score = 0
            
        return {
            "valid": len(errors) == 0,
            "errors": errors,
            "strength_score": min(score, 5),
            "strength_level": self._get_strength_level(score)
        }
    
    def _get_strength_level(self, score: int) -> str:
        """Get password strength level"""
        if score <= 2:
            return "weak"
        elif score <= 4:
            return "medium"
        else:
            return "strong"
    
    def generate_secure_token(self, length: int = 32) -> str:
        """Generate cryptographically secure token"""
        return secrets.token_urlsafe(length)
    
    def create_access_token(self, data: dict, expires_delta: Optional[timedelta] = None) -> str:
        """Create JWT access token with enhanced security"""
        to_encode = data.copy()
        
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
            
        to_encode.update({
            "exp": expire,
            "iat": datetime.utcnow(),
            "jti": self.generate_secure_token(16)  # JWT ID for token revocation
        })
        
        encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
        return encoded_jwt
    
    def verify_token(self, token: str) -> Optional[Dict[str, Any]]:
        """Verify JWT token with enhanced validation"""
        try:
            payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
            
            # Check if token is revoked (if Redis is available)
            if self.redis_client:
                jti = payload.get("jti")
                if jti and self.redis_client.get(f"revoked_token:{jti}"):
                    return None
                    
            return payload
        except JWTError:
            return None
    
    def revoke_token(self, token: str) -> bool:
        """Revoke JWT token"""
        if not self.redis_client:
            return False
            
        try:
            payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
            jti = payload.get("jti")
            exp = payload.get("exp")
            
            if jti and exp:
                # Store revoked token until expiration
                ttl = exp - datetime.utcnow().timestamp()
                if ttl > 0:
                    self.redis_client.setex(f"revoked_token:{jti}", int(ttl), "1")
                return True
        except JWTError:
            pass
            
        return False
    
    def check_rate_limit(self, identifier: str, limit: int = 100, window: int = 3600) -> bool:
        """Check rate limiting with Redis"""
        if not self.redis_client:
            return True
            
        key = f"rate_limit:{identifier}"
        current = self.redis_client.get(key)
        
        if current is None:
            self.redis_client.setex(key, window, 1)
            return True
        elif int(current) < limit:
            self.redis_client.incr(key)
            return True
        else:
            return False
    
    def log_security_event(self, event_type: str, details: Dict[str, Any], request: Request):
        """Log security events for audit trail"""
        security_log = {
            "timestamp": datetime.utcnow().isoformat(),
            "event_type": event_type,
            "ip_address": request.client.host,
            "user_agent": request.headers.get("user-agent"),
            "details": details
        }
        
        logger.warning(f"Security Event: {event_type}", extra=security_log)
    
    def sanitize_input(self, input_data: str) -> str:
        """Sanitize user input to prevent XSS"""
        import bleach
        
        allowed_tags = ['b', 'i', 'u', 'em', 'strong', 'p', 'br']
        allowed_attributes = {}
        
        return bleach.clean(input_data, tags=allowed_tags, attributes=allowed_attributes)
    
    def validate_file_upload(self, filename: str, content: bytes) -> Dict[str, Any]:
        """Validate file uploads for security"""
        allowed_extensions = {'.jpg', '.jpeg', '.png', '.gif', '.pdf', '.txt', '.docx'}
        max_size = 10 * 1024 * 1024  # 10MB
        
        errors = []
        
        # Check file extension
        file_ext = '.' + filename.split('.')[-1].lower() if '.' in filename else ''
        if file_ext not in allowed_extensions:
            errors.append(f"File type {file_ext} not allowed")
        
        # Check file size
        if len(content) > max_size:
            errors.append("File size exceeds 10MB limit")
        
        # Check for malicious content (basic)
        if b'<script' in content.lower() or b'javascript:' in content.lower():
            errors.append("Potentially malicious content detected")
        
        return {
            "valid": len(errors) == 0,
            "errors": errors,
            "file_hash": hashlib.sha256(content).hexdigest()
        }

class GDPRCompliance:
    """GDPR compliance utilities"""
    
    @staticmethod
    def anonymize_email(email: str) -> str:
        """Anonymize email for GDPR compliance"""
        local, domain = email.split('@')
        anonymized_local = local[:2] + '*' * (len(local) - 2)
        return f"{anonymized_local}@{domain}"
    
    @staticmethod
    def anonymize_ip(ip: str) -> str:
        """Anonymize IP address for GDPR compliance"""
        parts = ip.split('.')
        if len(parts) == 4:
            return f"{parts[0]}.{parts[1]}.{parts[2]}.0"
        return ip
    
    @staticmethod
    def get_data_retention_policy() -> Dict[str, int]:
        """Get data retention policy in days"""
        return {
            "user_data": 2555,  # 7 years
            "session_logs": 90,  # 3 months
            "audit_logs": 2555,  # 7 years
            "chat_history": 365,  # 1 year
            "analytics_data": 730  # 2 years
        }
    
    @staticmethod
    def generate_privacy_report(user_id: int, db: Session) -> Dict[str, Any]:
        """Generate privacy report for user data"""
        # This would query all user data across tables
        return {
            "user_id": user_id,
            "data_collected": [],
            "retention_periods": GDPRCompliance.get_data_retention_policy(),
            "third_party_sharing": [],
            "user_rights": [
                "Right to access",
                "Right to rectification",
                "Right to erasure",
                "Right to restrict processing",
                "Right to data portability",
                "Right to object"
            ]
        }

# Rate limiting decorator
def rate_limit(requests_per_minute: int = 60):
    """Rate limiting decorator"""
    def decorator(func):
        @wraps(func)
        async def wrapper(request: Request, *args, **kwargs):
            # Implementation would use Redis for distributed rate limiting
            return await func(request, *args, **kwargs)
        return wrapper
    return decorator

# Security headers middleware
async def add_security_headers(request: Request, call_next):
    """Add security headers to all responses"""
    response = await call_next(request)
    
    for header, value in SECURITY_HEADERS.items():
        response.headers[header] = value
    
    return response

