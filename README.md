# Project 10
## 1. About the project 10
This project is realized with Django REST framework in order to create an API for tracking projects.

[comment]: <> (The main goal of this application is to:)

[comment]: <> (* Allow users to post theirs requests of reviews about a book or theirs reviews. )

[comment]: <> (* Follow the other users.)
## 2. About main structure
* Project: softdesk_project
* Application: users
* Application:  project_tracking_app
## 3. Main code organization
```
├── db.sqlite3
├── manage.py
├── project_tracking_app/
│   ├── admin.py
│   ├── apps.py
│   ├── __init__.py
│   ├── migrations/
│   ├── models.py
│   ├── permissions.py
│   ├── serializers.py
│   ├── tests.py
│   ├── urls.py
│   └── views.py
├── softdesk_project/
│   ├── asgi.py
│   ├── __init__.py
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
└── users/
    ├── admin.py
    ├── apps.py
    ├── __init__.py
    ├── managers.py
    ├── migrations/
    ├── models.py
    ├── serializers.py
    ├── tests.py
    ├── urls.py
    └── views.py

```
## 4. Process
1. Clone and launch the project:
```
git clone  https://github.com/ThiHieuLUU/OCProject10.git
cd OCProject10/

python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt 

cd softdesk_project/
python manage.py makemigrations
python manage.py migrate
python manage.py runserver
```
Then go to http://127.0.0.1:8000/ and send request for different endpoints.

2. Check code with flake8
* See flake8 configuration in "setup.cfg" file.
* Check code in reviews application
```bash
cd reviews
flake8 --format=html --htmldir=flake8-rapport
```
* Result:
```bash
firefox flake8-rapport/index.html &
```

## 5. Postman documentation
See [here](https://www.postman.com/hieuluu/workspace/project-tracking-app/collection/15764425-c96c0004-74be-45c0-8dc8-9938049e756a?ctx=documentation) for Postman documentation of this API.