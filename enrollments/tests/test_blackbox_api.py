import requests

HOST = 'http://localhost:8000/api/'
COURSES_API_ROOT = HOST + 'courses/'
STUDENTS_API_ROOT = HOST + 'students/'


def test_create_get_delete_course():
    data = {
        'faculty': 'Computer Science',
        'subject': 'Linear Algebra',
        'description': 'Oh no',
        'year': 2017,
        'semester': '1'
    }

    r = requests.post(COURSES_API_ROOT, data=data)
    assert r.ok
    course_id = r.json()['id']

    r = requests.get(COURSES_API_ROOT + course_id + '/')
    assert r.ok
    assert r.json()['subject'] == data['subject']

    r = requests.delete(COURSES_API_ROOT + course_id + '/')
    assert r.ok

    r = requests.get(COURSES_API_ROOT + course_id + '/')
    assert r.status_code == 404


def test_create_get_delete_student():
    data = {
        "name": "Natalie",
        "city": "Haifa",
        "email": "aa@aa.aa",
        "year_of_birth": 1987,
        "enrollments": []
    }

    r = requests.post(STUDENTS_API_ROOT, data=data)
    assert r.ok
    student_id = r.json()['id']

    r = requests.get(STUDENTS_API_ROOT + student_id + '/')
    assert r.ok
    assert data['name'] == r.json()['name']

    r = requests.delete(STUDENTS_API_ROOT + student_id + '/')
    assert r.ok

    r = requests.get(STUDENTS_API_ROOT + student_id + '/')
    assert r.status_code == 404
