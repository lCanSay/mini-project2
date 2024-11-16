# views.py
from django.core.cache import cache
from rest_framework.response import Response
from rest_framework.views import APIView
from djoser.views import UserViewSet
from rest_framework.permissions import IsAuthenticated
from users.models import User
from .serializers import CustomUserCreateSerializer, CustomUserSerializer


class CustomUserViewSet(UserViewSet):
    queryset = User.objects.all()
    serializer_class = CustomUserSerializer
    permission_classes = [IsAuthenticated]

class UserDetailView(APIView):
    def get(self, request, pk):
        user = cache.get(f'user_{pk}')
        if not user:
            try:
                user = User.objects.get(pk=pk)
                cache.set(f'user_{pk}', user, timeout=600)
            except User.DoesNotExist:
                return Response({'detail': 'User not found'}, status=404)
        
        return Response({'username': user.username, 'role': user.role})
