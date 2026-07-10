from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import get_user_model
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from .serializers import UserSerializer, CustomTokenObtainPairSerializer, RegisterSerializer

User = get_user_model()


@method_decorator(csrf_exempt, name='dispatch')
class RegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = RegisterSerializer
    permission_classes = [AllowAny]

    def options(self, request, *args, **kwargs):
        response = Response(status=status.HTTP_200_OK)
        return response

    def create(self, request, *args, **kwargs):
        try:
            import logging
            logging.info(f"Registration attempt with data: {request.data}")
            
            serializer = self.get_serializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            
            logging.info("Serializer validation passed")
            user = serializer.save()
            
            logging.info(f"User created: {user.email}")
            
            response = Response({
                'user': UserSerializer(user).data,
                'message': 'User created successfully'
            }, status=status.HTTP_201_CREATED)
            
            return response
        except Exception as exc:
            import logging
            logging.error(f"Registration error: {str(exc)}", exc_info=True)
            detail = getattr(exc, 'detail', None)
            if detail is not None:
                status_code = getattr(exc, 'status_code', status.HTTP_400_BAD_REQUEST)
                return Response(detail, status=status_code)
            return Response({'detail': str(exc)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@method_decorator(csrf_exempt, name='dispatch')
class CustomTokenObtainPairView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer
    permission_classes = [AllowAny]

    def options(self, request, *args, **kwargs):
        response = Response(status=status.HTTP_200_OK)
        return response

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        try:
            serializer.is_valid(raise_exception=True)
            data = serializer.validated_data
            
            response = Response({
                'user': data['user'],
                'message': 'Login successful'
            }, status=status.HTTP_200_OK)
            
            # Set HttpOnly cookies with error handling
            try:
                response.set_cookie(
                    settings.SIMPLE_JWT['AUTH_COOKIE'],
                    str(data['access']),
                    expires=settings.SIMPLE_JWT['ACCESS_TOKEN_LIFETIME'],
                    httponly=settings.SIMPLE_JWT['AUTH_COOKIE_HTTPONLY'],
                    secure=settings.SIMPLE_JWT['AUTH_COOKIE_SECURE'],
                    samesite=settings.SIMPLE_JWT['AUTH_COOKIE_SAMESITE'],
                    path=settings.SIMPLE_JWT['AUTH_COOKIE_PATH'],
                )
                response.set_cookie(
                    settings.SIMPLE_JWT['REFRESH_COOKIE'],
                    str(data['refresh']),
                    expires=settings.SIMPLE_JWT['REFRESH_TOKEN_LIFETIME'],
                    httponly=settings.SIMPLE_JWT['REFRESH_COOKIE_HTTPONLY'],
                    secure=settings.SIMPLE_JWT['REFRESH_COOKIE_SECURE'],
                    samesite=settings.SIMPLE_JWT['REFRESH_COOKIE_SAMESITE'],
                    path=settings.SIMPLE_JWT['REFRESH_COOKIE_PATH'],
                )
            except Exception as cookie_error:
                import logging
                logging.error(f"Cookie setting error: {cookie_error}")
            
            return response
        except Exception as exc:
            return Response({'detail': str(exc)}, status=status.HTTP_401_UNAUTHORIZED)


@method_decorator(csrf_exempt, name='dispatch')
class CustomTokenRefreshView(TokenRefreshView):
    permission_classes = [AllowAny]

    def options(self, request, *args, **kwargs):
        response = Response(status=status.HTTP_200_OK)
        return response

    def post(self, request, *args, **kwargs):
        # Get refresh token from cookie
        refresh_token = request.COOKIES.get(settings.SIMPLE_JWT['REFRESH_COOKIE'])
        
        if not refresh_token:
            return Response({'detail': 'Refresh token not found in cookies'}, 
                          status=status.HTTP_401_UNAUTHORIZED)
        
        request.data['refresh'] = refresh_token
        
        serializer = self.get_serializer(data=request.data)
        try:
            serializer.is_valid(raise_exception=True)
            data = serializer.validated_data
            
            response = Response({'message': 'Token refreshed successfully'}, 
                             status=status.HTTP_200_OK)
            
            # Update access token cookie with error handling
            try:
                response.set_cookie(
                    settings.SIMPLE_JWT['AUTH_COOKIE'],
                    str(data['access']),
                    expires=settings.SIMPLE_JWT['ACCESS_TOKEN_LIFETIME'],
                    httponly=settings.SIMPLE_JWT['AUTH_COOKIE_HTTPONLY'],
                    secure=settings.SIMPLE_JWT['AUTH_COOKIE_SECURE'],
                    samesite=settings.SIMPLE_JWT['AUTH_COOKIE_SAMESITE'],
                    path=settings.SIMPLE_JWT['AUTH_COOKIE_PATH'],
                )
            except Exception as cookie_error:
                import logging
                logging.error(f"Cookie setting error: {cookie_error}")
            
            # Update refresh token cookie if rotated
            if 'refresh' in data:
                try:
                    response.set_cookie(
                        settings.SIMPLE_JWT['REFRESH_COOKIE'],
                        str(data['refresh']),
                        expires=settings.SIMPLE_JWT['REFRESH_TOKEN_LIFETIME'],
                        httponly=settings.SIMPLE_JWT['REFRESH_COOKIE_HTTPONLY'],
                        secure=settings.SIMPLE_JWT['REFRESH_COOKIE_SECURE'],
                        samesite=settings.SIMPLE_JWT['REFRESH_COOKIE_SAMESITE'],
                        path=settings.SIMPLE_JWT['REFRESH_COOKIE_PATH'],
                    )
                except Exception as cookie_error:
                    import logging
                    logging.error(f"Cookie setting error: {cookie_error}")
            
            return response
        except Exception as exc:
            return Response({'detail': str(exc)}, status=status.HTTP_401_UNAUTHORIZED)


@method_decorator(csrf_exempt, name='dispatch')
class LogoutView(generics.GenericAPIView):
    permission_classes = [IsAuthenticated]

    def options(self, request, *args, **kwargs):
        response = Response(status=status.HTTP_200_OK)
        return response

    def post(self, request, *args, **kwargs):
        response = Response({'message': 'Logout successful'}, status=status.HTTP_200_OK)
        
        # Clear cookies
        response.delete_cookie(
            settings.SIMPLE_JWT['AUTH_COOKIE'],
            path=settings.SIMPLE_JWT['AUTH_COOKIE_PATH'],
        )
        response.delete_cookie(
            settings.SIMPLE_JWT['REFRESH_COOKIE'],
            path=settings.SIMPLE_JWT['REFRESH_COOKIE_PATH'],
        )
        
        return response


class UserProfileView(generics.RetrieveUpdateAPIView):
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        return self.request.user
