import pytest
import requests

HOST = 'http://localhost:8000/api/'
COURSES_API_ROOT = HOST + 'courses/'
STUDENTS_API_ROOT = HOST + 'students/'


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
    assert r.json()['subject'] == data['subject']

    yield r.json()

    course_path = COURSES_API_ROOT + r.json()['id'] + '/'

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

    student_path = STUDENTS_API_ROOT + r.json()['id'] + '/'
    r = requests.get(student_path)
    assert r.ok
    assert data['name'] == r.json()['name']

    yield r.json()
    r = requests.delete(student_path)
    assert r.ok

    r = requests.get(student_path)
    assert r.status_code == 404


def test_patch_course(course):
    course_path = COURSES_API_ROOT + course['id'] + '/'

    new_subject = 'Linear Algebra 2'
    r = requests.patch(course_path, data={'subject': new_subject})
    assert r.ok
    assert r.json()['subject'] == new_subject


def test_patch_student(student):
    student_path = STUDENTS_API_ROOT + student['id'] + '/'

    new_name = 'Natalie Shk'
    r = requests.patch(student_path, data={'name': new_name})
    assert r.ok
    assert r.json()['name'] == new_name
