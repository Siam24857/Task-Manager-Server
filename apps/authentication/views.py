from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from django.contrib.auth import get_user_model
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from .serializers import UserSerializer, RegisterSerializer

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
            if not serializer.is_valid():
                logging.error(f"Validation errors: {serializer.errors}")
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
            
            logging.info("Serializer validation passed")
            user = serializer.save()
            
            logging.info(f"User created: {user.email}")
            
            # Auto-login after registration
            login(request, user)
            
            response = Response({
                'user': UserSerializer(user).data,
                'message': 'User created successfully'
            }, status=status.HTTP_201_CREATED)
            
            return response
        except Exception as exc:
            import logging
            import traceback
            logging.error(f"Registration error: {str(exc)}")
            logging.error(f"Traceback: {traceback.format_exc()}")
            detail = getattr(exc, 'detail', None)
            if detail is not None:
                status_code = getattr(exc, 'status_code', status.HTTP_400_BAD_REQUEST)
                return Response(detail, status=status_code)
            return Response({'detail': str(exc)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@method_decorator(csrf_exempt, name='dispatch')
class LoginView(generics.GenericAPIView):
    permission_classes = [AllowAny]

    def options(self, request, *args, **kwargs):
        response = Response(status=status.HTTP_200_OK)
        return response

    def post(self, request, *args, **kwargs):
        email = request.data.get('email')
        password = request.data.get('password')
        
        if not email or not password:
            return Response({'detail': 'Email and password are required'}, 
                          status=status.HTTP_400_BAD_REQUEST)
        
        # Authenticate user
        user = authenticate(request, username=email, password=password)
        
        if user is None:
            return Response({'detail': 'Invalid credentials'}, 
                          status=status.HTTP_401_UNAUTHORIZED)
        
        # # Login using Django session
        # login(request, user)
        
        response = Response({
            'user': UserSerializer(user).data,
            'message': 'Login successful'
        }, status=status.HTTP_200_OK)
        
        return response


@method_decorator(csrf_exempt, name='dispatch')
class LogoutView(generics.GenericAPIView):
    permission_classes = [IsAuthenticated]

    def options(self, request, *args, **kwargs):
        response = Response(status=status.HTTP_200_OK)
        return response

    def post(self, request, *args, **kwargs):
        # Logout using Django session
        logout(request)
        
        response = Response({'message': 'Logged out successfully'}, 
                         status=status.HTTP_200_OK)
        return response


@method_decorator(csrf_exempt, name='dispatch')
class ProfileView(generics.RetrieveAPIView):
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]

    def options(self, request, *args, **kwargs):
        response = Response(status=status.HTTP_200_OK)
        return response

    def get_object(self):
        return self.request.user
