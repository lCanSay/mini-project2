from rest_framework.generics import ListCreateAPIView, RetrieveUpdateDestroyAPIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from drf_yasg.utils import swagger_auto_schema
from django.core.cache import cache
from django.conf import settings
from .models import Grade
from .serializers import GradeSerializer
from grades.tasks import notify_student_about_new_grade

CACHE_TTL = getattr(settings, 'CACHE_TTL', 300)

class GradeListView(ListCreateAPIView):
    queryset = Grade.objects.all()
    serializer_class = GradeSerializer
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_summary="Get a list of grades",
        responses={200: GradeSerializer(many=True)}
    )
    def get(self, request, *args, **kwargs):
        cached_grades = cache.get('grade_list')
        if cached_grades:
            return Response(cached_grades)
        grades = self.get_queryset()
        serializer = self.get_serializer(grades, many=True)
        cache.set('grade_list', serializer.data, timeout=CACHE_TTL)
        return Response(serializer.data)

    @swagger_auto_schema(
        operation_summary="Add a grade",
        request_body=GradeSerializer,
        responses={201: GradeSerializer}
    )
    def post(self, request, *args, **kwargs):
        if not hasattr(request.user, 'role') or request.user.role != 'teacher':
            return Response({"error": "Only teachers can add grades"}, status=403)

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        grade = serializer.save(teacher=request.user)
        notify_student_about_new_grade.delay(
            grade.student.user.email,
            grade.course.name,
            grade.grade
        )
        return Response(serializer.data, status=201)


class GradeDetailView(RetrieveUpdateDestroyAPIView):
    queryset = Grade.objects.all()
    serializer_class = GradeSerializer
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_summary="Update grade data",
        request_body=GradeSerializer,
        responses={200: GradeSerializer}
    )
    def put(self, request, *args, **kwargs):
        if not hasattr(request.user, 'role') or request.user.role != 'teacher':
            return Response({"error": "Only teachers can update grades"}, status=403)

        grade = self.get_object()
        serializer = self.get_serializer(grade, data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        cache.delete(f'grade_{grade.pk}')
        cache.set(f'grade_{grade.pk}', serializer.data, timeout=CACHE_TTL)
        return Response(serializer.data)
