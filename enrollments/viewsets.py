import functools

from rest_framework import status
from rest_framework.decorators import detail_route
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework_mongoengine import viewsets

from enrollments.models import Course, Student, Enrollment
from enrollments.serializers import CourseSerializer, StudentSerializer


class CourseViewSet(viewsets.ModelViewSet):
    '''
    Information about a course
    '''
    lookup_field = 'id'
    serializer_class = CourseSerializer

    permission_classes = (AllowAny,)

    def get_queryset(self):
        queryset = Course.objects.all()
        minimal_points = self.request.query_params.get('minimal_points', None)
        if minimal_points is not None:
            queryset = queryset.filter(points__gte=minimal_points)

        return queryset

    @detail_route(methods=['get'], permission_classes=[AllowAny], url_path='enrolled')
    def enrol(self, request, id=None):
        course = self.get_object()


class StudentViewSet(viewsets.ModelViewSet):
    '''
    Information about a student and their enrollments
    '''
    lookup_field = 'id'
    serializer_class = StudentSerializer

    permission_classes = (AllowAny,)

    def get_queryset(self):
        queryset = Student.objects.all()
        name = self.request.query_params.get('name', None)
        if name is not None:
            queryset = queryset.filter(name__contains=name)
        city = self.request.query_params.get('city', None)
        if city is not None:
            queryset = queryset.filter(city__contains=city)

        minimal_year = self.request.query_params.get('minimal_year', None)
        if minimal_year is not None:
            queryset = queryset.filter(year_of_birth__gte=minimal_year)

        return queryset

    @detail_route(methods=['post'], permission_classes=[AllowAny], url_path='enrol')
    def enrol(self, request, id=None):
        student = self.get_object()

        course_id = request.data.get('course')
        try:
            course = Course.objects.get(id=course_id)
        except Exception as e:
            return Response(data={'error': 'Invalid course_id %s' % course_id, 'details': e.message},
                            status=status.HTTP_400_BAD_REQUEST)

        existing_courses = map(lambda enrollment: enrollment.course, student.enrollments)
        if course in existing_courses:
            return Response(data={'error': 'Student already enrolled to course %s' % course_id, 'details': ''},
                            status=status.HTTP_400_BAD_REQUEST)

        student.enrollments.append(Enrollment(course=course, grade=None))
        student.save()
        return Response()

    @detail_route(methods=['post'], permission_classes=[AllowAny], url_path='grade')
    def grade(self, request, id=None):
        student = self.get_object()
        course_id = request.data.get('course')
        try:
            course = Course.objects.get(id=course_id)
        except Exception as e:
            return Response(data={'error': 'Invalid course_id %s' % course_id, 'details': e.message},
                            status=status.HTTP_400_BAD_REQUEST)

        existing_courses = map(lambda enrollment: enrollment.course, student.enrollments)
        if course not in existing_courses:
            return Response(data={'error': 'Student not enrolled to course %s' % course_id, 'details': ''},
                            status=status.HTTP_400_BAD_REQUEST)

        enrollment = filter(lambda enrollment: enrollment.course == course, student.enrollments)[0]
        enrollment.grade = request.data.get('grade')
        student.save()
        return Response()
