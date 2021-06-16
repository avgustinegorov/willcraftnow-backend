#!/usr/bin/env bash

DJANGO_SETTINGS_MODULE=WillCraft.settings coverage run \
    --source 'assets,billing,content,core,history,lastrites,lawyer_services,lawyer_admin,partners,persons,powers,utils,willcraft_auth,services/will_generator' \
    --omit '*/tests.py,*/apps.py,*/migrations/*,*/tests/*,*/admin.py,*/urls.py' \
    manage.py test assets billing content core lastrites lawyer_services partners persons powers willcraft_auth
# manage.py test $1 $2 $3 $4 $5 $6 $7 $8 $9
coverage report -m
#coverage html
