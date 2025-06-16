#! /bin/env sh

python manage.py migrate
python manage.py collectstatic --no-input -l
python manage.py runserver 0.0.0.0:8000

