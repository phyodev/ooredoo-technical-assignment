# Ooredoo Technical Test

## Prerequisites
- Python 3.13
- Django 5.1.7
- Django Restframework 3.15.2
- Redis (server & pip package) 5.2.1
- Celery 5.4.0

## Installation and Running Guides

## Step - 1
Clone the project first

## Step - 2
```shell
cd ooredoo-technical-assignment
python -m venv venv
source venv/bin/activate
which python # to ensure the environment is activated
pip install -r requirements.txt
```

## Step - 3
```shell
python migrate
python manage.py runserver
```

## Step - 4
now we can test the APIs via `http://localhost:8000`