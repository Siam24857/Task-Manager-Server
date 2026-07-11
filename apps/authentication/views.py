from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from django.contrib.auth import get_user_model, authenticate
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
import logging
from .serializers import UserSerializer, RegisterSerializer
from .models import AuthToken

logger = logging.getLogger(__name__)

User = get_user_model()


class CsrfExemptMixin:
    @method_decorator(csrf_exempt, name='dispatch')
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)

    def options(self, request, *args, **kwargs):
        return Response(status=status.HTTP_200_OK)


class RegisterView(CsrfExemptMixin, generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = RegisterSerializer
    permission_classes = [AllowAny]

    def create(self, request, *args, **kwargs):
        try:
            serializer = self.get_serializer(data=request.data)
            if not serializer.is_valid():
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

            user = serializer.save()

            try:
                auth_token = AuthToken.generate_token(user)
                token = auth_token.token
            except Exception as token_err:
                logger.error("Token generation failed: %s", str(token_err))
                token = None

            return Response({
                'user': UserSerializer(user).data,
                'token': token,
                'message': 'User created successfully'
            }, status=status.HTTP_201_CREATED)

        except Exception as exc:
            logger.exception("Registration error: %s", str(exc))
            detail = getattr(exc, 'detail', None)
            if detail is not None:
                status_code = getattr(exc, 'status_code', status.HTTP_400_BAD_REQUEST)
                return Response(detail, status_code)
            return Response(
                {'detail': str(exc) or 'Registration failed. Please try again.'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class LoginView(CsrfExemptMixin, generics.GenericAPIView):
    permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs):
        try:
            email = request.data.get('email')
            password = request.data.get('password')

            if not email or not password:
                return Response(
                    {'detail': 'Email and password are required'},
                    status=status.HTTP_400_BAD_REQUEST
                )

            user = authenticate(request, username=email, password=password)

            if user is None:
                return Response(
                    {'detail': 'Invalid credentials'},
                    status=status.HTTP_401_UNAUTHORIZED
                )

            try:
                auth_token = AuthToken.generate_token(user)
                token = auth_token.token
            except Exception as token_err:
                logger.error("Token generation failed for login: %s", str(token_err))
                return Response(
                    {'detail': 'Login succeeded but token generation failed.'},
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )

            return Response({
                'user': UserSerializer(user).data,
                'token': token,
                'message': 'Login successful'
            }, status=status.HTTP_200_OK)

        except Exception as exc:
            logger.exception("Login error: %s", str(exc))
            return Response(
                {'detail': str(exc) or 'Login failed. Please try again.'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class LogoutView(CsrfExemptMixin, generics.GenericAPIView):
    permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs):
        auth_header = request.META.get('HTTP_AUTHORIZATION', '')
        token = None
        if auth_header.startswith('Token '):
            token = auth_header[6:]
        elif auth_header.startswith('Bearer '):
            token = auth_header[7:]

        if token:
            try:
                auth_token = AuthToken.objects.get(token=token, is_active=True)
                auth_token.is_active = False
                auth_token.save()
            except AuthToken.DoesNotExist:
                pass

        return Response(
            {'message': 'Logged out successfully'},
            status=status.HTTP_200_OK
        )


class ProfileView(CsrfExemptMixin, generics.RetrieveAPIView):
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        return self.request.user
