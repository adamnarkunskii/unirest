from rest_framework.permissions import AllowAny
from rest_framework_mongoengine import viewsets

from enrollments.models import Course, Student
from enrollments.serializers import CourseSerializer, StudentSerializer


class CourseViewSet(viewsets.ModelViewSet):
    '''
    Information about a course
    '''
    lookup_field = 'id'
    serializer_class = CourseSerializer

    permission_classes = (AllowAny,)

    def get_queryset(self):
        return Course.objects.all()


class StudentViewSet(viewsets.ModelViewSet):
    '''
    Information about a student and their enrollments
    '''
    lookup_field = 'id'
    serializer_class = StudentSerializer

    permission_classes = (AllowAny,)

    def get_queryset(self):
        return Student.objects.all()
