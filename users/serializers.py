from djoser.serializers import UserCreateSerializer, UserSerializer
from rest_framework import serializers
from .models import User

class CustomUserCreateSerializer(UserCreateSerializer):
    username = serializers.CharField(help_text="The user's username.")
    email = serializers.EmailField(help_text="The user's email address.")
    password = serializers.CharField(write_only=True, help_text="The user's password.")
    role = serializers.CharField(help_text="The role of the user (e.g., 'student', 'teacher', 'admin').")

    class Meta(UserCreateSerializer.Meta):
        model = User
        fields = ('id', 'email', 'username', 'password', 'role')

class CustomUserSerializer(UserSerializer):
    username = serializers.CharField(help_text="The user's username.")
    email = serializers.EmailField(help_text="The user's email address.")
    role = serializers.CharField(help_text="The role of the user (e.g., 'student', 'teacher', 'admin').")

    class Meta(UserSerializer.Meta):
        model = User
        fields = ('id', 'email', 'username', 'role')