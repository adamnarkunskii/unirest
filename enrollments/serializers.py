from rest_framework_mongoengine.serializers import DocumentSerializer, EmbeddedDocumentSerializer

from enrollments.models import Course, Student, Enrollment


class EnrollmentSerializer(EmbeddedDocumentSerializer):
    class Meta:
        model = Enrollment
        fields = '__all__'


class CourseSerializer(DocumentSerializer):
    class Meta:
        model = Course
        fields = '__all__'


class StudentSerializer(DocumentSerializer):
    class Meta:
        model = Student
        fields = '__all__'
