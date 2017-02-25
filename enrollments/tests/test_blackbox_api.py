import pytest
import requests

HOST = 'http://localhost:8000/api/'
COURSES_API_ROOT = HOST + 'courses/'
STUDENTS_API_ROOT = HOST + 'students/'


def path_for_course(course):
    return COURSES_API_ROOT + course['id'] + '/'


def path_for_student(student):
    return STUDENTS_API_ROOT + student['id'] + '/'


@pytest.fixture
def course():
    data = {
        'faculty': 'Computer Science',
        'subject': 'Linear Algebra',
        'description': 'Oh no',
        'year': 2017,
        'semester': '1'
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


def test_assign_a_student_to_a_course_and_grade(student, course):
    student_path = path_for_student(student)
    enrollment = {
        'course': course['id'],
        'grade': None
    }
    r = requests.post(student_path + 'enrol/', data=enrollment)
    assert r.ok

    r = requests.post(student_path + 'enrol/', data=enrollment)
    assert not r.ok

    r = requests.get(student_path)
    student = r.json()
    enrollments = student['enrollments']
    assert len(enrollments) == 1
    assert enrollments[0]['course'] == course['id']
    assert enrollments[0]['grade'] is None

    enrollment['grade'] = 92
    r = requests.post(student_path + 'grade/', data=enrollment)
    assert r.ok

    r = requests.get(student_path)
    student = r.json()
    enrollments = student['enrollments']
    assert len(enrollments) == 1
    assert enrollments[0]['course'] == course['id']
    assert enrollments[0]['grade'] is 92
