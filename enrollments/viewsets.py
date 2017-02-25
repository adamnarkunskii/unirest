import functools

from rest_framework import status
from rest_framework.decorators import detail_route, list_route
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

    def destroy(self, request, *args, **kwargs):
        
        super(CourseViewSet, self).destroy(*args, **kwargs)


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

    def get_outstanding_students(self, minimum_score=0):
        def calc_score(student):
            sum = 0
            points = 0
            for enrollment in student.enrollments:
                sum += enrollment.grade * enrollment.course.points
                points += enrollment.course.points
            return student, sum / points

        student_scores = map(calc_score, self.get_queryset())
        high_student_scores = filter(lambda student_scores: student_scores[1] >= minimum_score, student_scores)
        high_student_scores = sorted(high_student_scores, key=lambda x: x[1], reverse=True)
        just_high_students = map(lambda student_score: student_score[0], high_student_scores)
        return just_high_students

    @list_route(permission_classes=[AllowAny])
    def outstanding(self, request):
        outstanding_students = self.get_outstanding_students(minimum_score=90)
        return Response(self.get_serializer(outstanding_students, many=True).data)

    @list_route(permission_classes=[AllowAny])
    def valedictorian(self, request):
        outstanding_students = self.get_outstanding_students()
        valedict = outstanding_students[0]
        return Response(self.get_serializer(valedict).data)

    @list_route(methods=['post'], permission_classes=[AllowAny])
    def bulk_enrol(self, request, **kwargs):
        course_id = request.query_params.get('course')
        try:
            course = Course.objects.get(id=course_id)
        except Exception as e:
            return Response(data={'error': 'Invalid course_id %s' % course_id, 'details': e.message},
                            status=status.HTTP_400_BAD_REQUEST)

        def enrol_and_save(student):
            student.enrol(course)
            student.save()

        map(enrol_and_save, self.get_queryset())

        return Response(self.get_serializer(self.get_queryset(), many=True).data)

    @list_route(permission_classes=[AllowAny])
    def enrolled(self, request, **kwargs):
        course_id = request.query_params.get('course')
        try:
            course = Course.objects.get(id=course_id)
        except Exception as e:
            return Response(data={'error': 'Invalid course_id %s' % course_id, 'details': e.message},
                            status=status.HTTP_400_BAD_REQUEST)

        enrolled_students = filter(lambda student: course in student.enrolled_courses(),
                                   self.get_queryset())

        serializer = self.get_serializer(enrolled_students, many=True)
        return Response(serializer.data)

    @detail_route(methods=['post'], permission_classes=[AllowAny], url_path='enrol')
    def enrol(self, request, id=None):
        student = self.get_object()

        course_id = request.data.get('course')
        try:
            course = Course.objects.get(id=course_id)
        except Exception as e:
            return Response(data={'error': 'Invalid course_id %s' % course_id, 'details': e.message},
                            status=status.HTTP_400_BAD_REQUEST)

        if course in student.enrolled_courses():
            return Response(data={'error': 'Student already enrolled to course %s' % course_id, 'details': ''},
                            status=status.HTTP_400_BAD_REQUEST)

        student.enrol(course)
        student.save()
        return Response(self.get_serializer(student).data)

    @detail_route(methods=['post'], permission_classes=[AllowAny], url_path='grade')
    def grade(self, request, id=None):
        student = self.get_object()
        course_id = request.data.get('course')
        try:
            course = Course.objects.get(id=course_id)
        except Exception as e:
            return Response(data={'error': 'Invalid course_id %s' % course_id, 'details': e.message},
                            status=status.HTTP_400_BAD_REQUEST)

        if course not in student.enrolled_courses():
            return Response(data={'error': 'Student not enrolled to course %s' % course_id, 'details': ''},
                            status=status.HTTP_400_BAD_REQUEST)

        enrollment = filter(lambda enrollment: enrollment.course == course, student.enrollments)[0]
        enrollment.grade = request.data.get('grade')
        student.save()
        return Response(self.get_serializer(student).data)
