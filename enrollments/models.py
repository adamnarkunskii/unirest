from mongoengine import Document, EmbeddedDocument, fields

SEMESTERS = (('1', 'Fall'),
             ('2', 'Spring'),
             ('3', 'Summer'),)


class Course(Document):
    faculty = fields.StringField(required=True)
    subject = fields.StringField(required=True)
    description = fields.StringField(required=True, null=True)

    year = fields.IntField(required=True)
    semester = fields.StringField(max_length=1, choices=SEMESTERS)

    points = fields.IntField(required=True, default=4)

    def __repr__(self):
        return '<Course %s %s:%s>' % (self.subject, self.year, self.semester)


class Enrollment(EmbeddedDocument):
    course = fields.ReferenceField(Course)
    grade = fields.IntField(null=True, blank=True)
    is_deleted = fields.BooleanField(defult=False)

    def __repr__(self):
        deleted = " XXX " if self.is_deleted else ""
        return '<Enrollment %s (%s)%s>' % (self.course.subject, self.grade, deleted)


class Student(Document):
    name = fields.StringField(required=True)
    city = fields.StringField(required=True)
    email = fields.EmailField(required=True, unique=True)
    year_of_birth = fields.IntField(required=True)

    enrollments = fields.EmbeddedDocumentListField('Enrollment')

    def __repr__(self):
        return '<Student %s %s (%s enrollments)>' % (self.name, self.email, len(self.enrollments))

    def enrolled_courses(self):
        return map(lambda enrollment: enrollment.course, self.enrollments)

    def enrol(self, course, grade=None):
        self.enrollments.append(Enrollment(course=course, grade=grade))
