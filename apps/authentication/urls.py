from django.urls import path
from .views import RegisterView, CustomTokenObtainPairView, CustomTokenRefreshView, UserProfileView

urlpatterns = [
    path('register', RegisterView.as_view(), name='register'),
    path('login', CustomTokenObtainPairView.as_view(), name='login'),
    path('login/refresh', CustomTokenRefreshView.as_view(), name='token_refresh'),
    path('profile', UserProfileView.as_view(), name='profile'),
]
