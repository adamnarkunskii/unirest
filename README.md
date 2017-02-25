# UNIREST

## Setup:
Start server:
```shell
$ git clone git@github.com:wat-izz/unirest.git
$ cd unirest
# create a virtualenv and activate it
$ pip install -r requirements.txt
$ vim unirest/settings.py # change mongo connection details
$ ./manage.py runserver
```
Server is running at `http://localhost:8000`

## Test:

Run integration tests (server must be up at `http://localhost:8000`):
```
$ py.test
```
## Documentation
View documentation at `/docs`: <http://localhost:8000/docs>






