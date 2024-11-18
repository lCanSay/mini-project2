from rest_framework import viewsets
from .models import User
from .serializers import CustomUserSerializer, CustomUserCreateSerializer
from rest_framework.permissions import AllowAny

class CustomUserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    permission_classes = [AllowAny]

    serializer_class = CustomUserSerializer

    def get_serializer_class(self):
        if self.action == 'create':
            return CustomUserCreateSerializer
        return CustomUserSerializer 

