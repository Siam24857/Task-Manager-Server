from django.contrib.auth.backends import BaseBackend
from django.contrib.auth import get_user_model
from .models import AuthToken

User = get_user_model()


class TokenAuthenticationBackend(BaseBackend):
    """Custom authentication backend using MongoDB tokens"""
    
    def authenticate(self, request, token=None, **kwargs):
        """Authenticate user using token from request"""
        if token is None:
            # Try to get token from Authorization header
            auth_header = request.META.get('HTTP_AUTHORIZATION', '')
            if auth_header.startswith('Token '):
                token = auth_header[6:]  # Remove 'Token ' prefix
            elif auth_header.startswith('Bearer '):
                token = auth_header[7:]  # Remove 'Bearer ' prefix
        
        if not token:
            return None
        
        # Validate token using MongoDB
        auth_token = AuthToken.validate_token(token)
        if auth_token:
            try:
                user = User.objects.get(id=auth_token.user_id)
                return user
            except User.DoesNotExist:
                return None
        
        return None
    
    def get_user(self, user_id):
        """Get user by ID"""
        try:
            return User.objects.get(id=user_id)
        except User.DoesNotExist:
            return None
