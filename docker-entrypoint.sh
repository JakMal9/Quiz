#!/bin/bash

wait-for-it "${DB_HOST}:${DB_PORT}"
python manage.py migrate &&
python manage.py runserver 0.0.0.0:8000
