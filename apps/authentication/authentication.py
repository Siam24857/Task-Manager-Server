from rest_framework.authentication import BaseAuthentication
from django.contrib.auth import get_user_model
from .models import AuthToken

User = get_user_model()


class MongoTokenAuthentication(BaseAuthentication):
    """Custom DRF authentication using MongoDB tokens"""
    
    def authenticate(self, request):
        """Authenticate user using token from request"""
        # Try to get token from Authorization header
        auth_header = request.META.get('HTTP_AUTHORIZATION', '')
        token = None
        
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
                return (user, auth_token)
            except User.DoesNotExist:
                return None
        
        return None
    
    def authenticate_header(self, request):
        """Return the authentication header"""
        return 'Token'
