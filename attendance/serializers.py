from rest_framework import serializers
from .models import Attendance


class AttendanceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Attendance
        fields = ('id', 'student', 'course', 'date', 'status')
        read_only_fields = ('student', 'course')

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        request = self.context.get('request')
        if request and hasattr(request.user, 'role') and request.user.role == 'student':
            allowed_fields = ('id', 'date', 'status')
            representation = {key: representation[key] for key in allowed_fields}

        return representation

    def validate(self, data):
        request = self.context.get('request')
        if request and (request.user.role != 'teacher' or request.user.role != 'admin'):
            raise serializers.ValidationError("Students are not allowed to modify attendance records.")

        return data