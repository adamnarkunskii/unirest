import pytest
import requests

HOST = 'http://localhost:8000/api/'
COURSES_API_ROOT = HOST + 'courses/'
STUDENTS_API_ROOT = HOST + 'students/'


def path_for_course(course):
    return COURSES_API_ROOT + course['id'] + '/'


def path_for_student(student):
    return STUDENTS_API_ROOT + student['id'] + '/'


def get_student(student_path):
    return requests.get(student_path).json()


@pytest.fixture
def course():
    data = {
        'faculty': 'Computer Science',
        'subject': 'Linear Algebra',
        'description': 'Oh no',
        'year': 2017,
        'semester': '1',
        'points': 3
    }

    r = requests.post(COURSES_API_ROOT, data=data)
    assert r.ok
    course = r.json()

    assert course['subject'] == data['subject']
    yield course
    course_path = path_for_course(course)

    r = requests.delete(course_path)
    assert r.ok

    r = requests.get(course_path)
    assert r.status_code == 404


@pytest.fixture
def student():
    data = {
        "name": "Natalie",
        "city": "Haifa",
        "email": "aa@aa.aa",
        "year_of_birth": 1987,
        "enrollments": []
    }

    r = requests.post(STUDENTS_API_ROOT, data=data)
    assert r.ok

    student = r.json()
    student_path = path_for_student(student)
    r = requests.get(student_path)
    assert r.ok
    assert data['name'] == student['name']

    yield student
    r = requests.delete(student_path)
    assert r.ok

    r = requests.get(student_path)
    assert r.status_code == 404


def test_outstanding(student, course):
    enrol(course, student)
    grade(course, student, 88)
    r = requests.get(STUDENTS_API_ROOT + 'outstanding/')
    assert r.ok

    assert len(r.json()) == 0


    grade(course, student, 91)
    r = requests.get(STUDENTS_API_ROOT + 'outstanding/')
    assert r.ok

    assert len(r.json()) == 1


def test_bulk_enrol(student, course):
    assert_enrolled_students(course, count=0)
    r = requests.post(STUDENTS_API_ROOT + 'bulk_enrol/', params={'course': course['id'], 'name': 'Lucy'})
    assert r.ok

    assert_enrolled_students(course, count=0)
    r = requests.post(STUDENTS_API_ROOT + 'bulk_enrol/', params={'course': course['id'], 'name': 'Na'})
    assert r.ok

    assert_enrolled_students(course, count=1)


def test_get_enrolled_students(student, course):
    assert_enrolled_students(course, count=0)
    enrol(course, student)
    assert_enrolled_students(course, count=1)


def assert_enrolled_students(course, count):
    r = requests.get(STUDENTS_API_ROOT + 'enrolled/', params={'course': course['id']})
    assert r.ok
    enrolled = r.json()
    assert len(enrolled) == count


def test_student_filters(student):
    verify_filter(requests.get(STUDENTS_API_ROOT, params={'name': 'Nat'}))
    verify_filter(requests.get(STUDENTS_API_ROOT, params={'city': 'Tel'}), empty=True)
    verify_filter(requests.get(STUDENTS_API_ROOT, params={'minimal_year': '1987'}))
    verify_filter(requests.get(STUDENTS_API_ROOT, params={'minimal_year': '2000'}), empty=True)


def test_course_filters(course):
    verify_filter(requests.get(COURSES_API_ROOT, params={'minimal_points': 1}))
    verify_filter(requests.get(COURSES_API_ROOT, params={'minimal_points': 10}), empty=True)


def verify_filter(response, empty=False):
    assert response.ok
    filtered = response.json()
    if empty:
        assert len(filtered) == 0
    else:
        assert len(filtered) == 1


def test_patch_course(course):
    course_path = path_for_course(course)

    new_subject = 'Linear Algebra 2'
    r = requests.patch(course_path, data={'subject': new_subject})
    assert r.ok
    assert r.json()['subject'] == new_subject


def test_patch_student(student):
    student_path = path_for_student(student)

    new_name = 'Natalie Shk'
    r = requests.patch(student_path, data={'name': new_name})
    assert r.ok
    assert r.json()['name'] == new_name


def test_cant_enrol_twice(student, course):
    student_path = path_for_student(student)
    enrollment = {
        'course': course['id'],
        'grade': None
    }
    r = requests.post(student_path + 'enrol/', data=enrollment)
    assert r.ok

    r = requests.post(student_path + 'enrol/', data=enrollment)
    assert not r.ok


def test_basic_enrollment(student, course):
    enrol(course, student)


def enrol(course, student):
    student_path = path_for_student(student)
    enrollment_data = {
        'course': course['id'],
        'grade': None
    }
    r = requests.post(student_path + 'enrol/', data=enrollment_data)
    assert r.ok
    verify_enrollment(course, enrollment_data, student_path)


def test_assign_a_student_to_a_course_and_grade(student, course):
    student_path = path_for_student(student)
    enrollment_data = {
        'course': course['id'],
        'grade': None
    }
    r = requests.post(student_path + 'enrol/', data=enrollment_data)
    assert r.ok

    grade(course, student, 88)
    enrollment_data['grade'] = 88
    verify_enrollment(course, enrollment_data, student_path)


def grade(course, student, grade):
    enrollment_data = {
        'course': course['id'],
        'grade': grade
    }
    r = requests.post(path_for_student(student) + 'grade/', data=enrollment_data)
    assert r.ok


def verify_enrollment(course, enrollment, student_path):
    student = get_student(student_path)
    enrollments = student['enrollments']
    assert len(enrollments) == 1
    assert enrollments[0]['course'] == course['id']
    assert enrollments[0]['grade'] == enrollment['grade']
