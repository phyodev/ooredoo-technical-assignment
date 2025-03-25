# Ooredoo Technical Test

## Prerequisites
- Python 3.13
- Django 5.1.7
- Django Restframework 3.15.2
- Redis (server & pip package) 5.2.1
- Celery 5.4.0

## Installation and Running Guides

## STEP - 1
Clone the project first

## STEP - 2
```shell
cd ooredoo-technical-assignment
python -m venv venv
source venv/bin/activate
which python # to ensure the environment is activated
pip install -r requirements.txt
```

## STEP - 3
```shell
cd loyalty_system
python migrate
python manage.py collectstatic
python manage.py runserver
```

## STEP - 4
Open new terminal and run:
```shell
docker run -d -p 6379:6379 redis # ignore - if you already installed redis on your host.
cd loyalty_system
celery -A loyalty_system worker --loglevel=info
```

## STEP - 5
Now we can test the APIs via `http://localhost:8000`


# Endpoints
All of the endpoints in this project
## Users
`/api/users/` - Read Only and Update Only his/her Data for customers<br>
## Products
`/api/products/` - Read Only for customers<br>
`/api/products/{product_id}/purchase/` - Purchase a product (for now payment keep as True)<br>
## Points
`/api/points/` - Read only for customers<br>
`POST /api/points/redemptions/` - to redeem product with points<br>
`POST /api/points/redemptions/{redemption_id}/redeem/` - just as third party API<br>
`GET /api/points/redemptions/{redemption_id}/`