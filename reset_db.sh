#!/usr/bin/env bash

rm -r ./db.sqlite3

python manage.py migrate

python manage.py runscript deployment

python manage.py runserver