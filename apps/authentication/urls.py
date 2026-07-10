from django.urls import path
from .views import RegisterView, CustomTokenObtainPairView, CustomTokenRefreshView, LogoutView, UserProfileView

urlpatterns = [
    path('register', RegisterView.as_view(), name='register'),
    path('login', CustomTokenObtainPairView.as_view(), name='login'),
    path('refresh', CustomTokenRefreshView.as_view(), name='token_refresh'),
    path('logout', LogoutView.as_view(), name='logout'),
    path('profile', UserProfileView.as_view(), name='profile'),
]
