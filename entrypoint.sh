#!/bin/bash
echo "starting django"

# python myproject/manage.py makemigrations
python manage.py migrate
python manage.py runserver 0.0.0.0:8000