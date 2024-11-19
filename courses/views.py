from rest_framework.generics import ListCreateAPIView, RetrieveUpdateDestroyAPIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.exceptions import PermissionDenied
from drf_yasg.utils import swagger_auto_schema
from django.core.cache import cache
from django.conf import settings
from .models import Course, Enrollment
from .serializers import CourseSerializer, EnrollmentSerializer
from logger.logging import logger

CACHE_TTL = getattr(settings, 'CACHE_TTL', 300)


class CourseListView(ListCreateAPIView):
    queryset = Course.objects.filter(is_active=True)
    serializer_class = CourseSerializer
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_summary="Get a list of courses",
        operation_description="Returns a list of active courses for students",
        responses={200: CourseSerializer(many=True)}
    )
    def list(self, request, *args, **kwargs):
        logger.info(f"Fetching course list by {request.user.username}")
        cached_courses = cache.get('course_list')

        if not cached_courses:
            courses = self.get_queryset()
            cached_courses = self.get_serializer(courses, many=True).data
            cache.set('course_list', cached_courses, timeout=CACHE_TTL)
            logger.info("Course list cached")

        return Response(cached_courses)

    @swagger_auto_schema(
        operation_summary="Add a course",
        operation_description="Creates a new course (teachers only)",
        request_body=CourseSerializer,
        responses={201: CourseSerializer}
    )
    def create(self, request, *args, **kwargs):
        if request.user.role != 'teacher':
            raise PermissionDenied("Only teachers can create courses.")

        logger.info(f"Teacher {request.user.username} creating a course")
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        course = serializer.save(instructor=request.user)

        notify_students_about_new_course.delay(
            course.name, 
            [student.user.email for student in Student.objects.all()]
        )
        logger.info(f"Course '{course.name}' created and notifications sent")
        return Response(serializer.data, status=201)


class CourseDetailView(RetrieveUpdateDestroyAPIView):
    queryset = Course.objects.all()
    serializer_class = CourseSerializer
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_summary="Change course",
        operation_description="Allows the teacher to change the course",
        request_body=CourseSerializer,
        responses={200: CourseSerializer}
    )
    def update(self, request, *args, **kwargs):
        course = self.get_object()
        if request.user.role != 'teacher' or course.instructor != request.user:
            raise PermissionDenied("You can only modify your own courses.")

        logger.info(f"Updating course {course.id} by {request.user.username}")
        serializer = self.get_serializer(course, data=request.data)
        serializer.is_valid(raise_exception=True)
        updated_course = serializer.save()

        cache.delete(f'course_{course.id}')
        cache.set(f'course_{course.id}', serializer.data, timeout=CACHE_TTL)
        logger.info(f"Course {course.id} updated and cached")
        return Response(serializer.data)


class EnrollmentListView(ListCreateAPIView):
    queryset = Enrollment.objects.all()
    serializer_class = EnrollmentSerializer
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_summary="Sign up for a course",
        operation_description="Allows students to enroll in courses",
        request_body=EnrollmentSerializer,
        responses={201: EnrollmentSerializer}
    )
    def create(self, request, *args, **kwargs):
        if request.user.role != 'student':
            raise PermissionDenied("Only students can enroll in courses.")

        logger.info(f"Student {request.user.username} enrolling in a course")
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        enrollment = serializer.save()
        logger.info(f"Student {enrollment.student.user.username} enrolled in {enrollment.course.name}")
        return Response(serializer.data, status=201)
