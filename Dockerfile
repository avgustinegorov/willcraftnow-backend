# Use an official Python runtime as a parent image
FROM python:3.6-alpine
ENV PYTHONUNBUFFERED 1

# Adding backend directory to make absolute filepaths consistent across services
WORKDIR /app

# Install Python dependencies
COPY /requirements /app/requirements
COPY /requirements.txt /app

RUN apk add --no-cache --virtual .build-deps \
    ca-certificates gcc python3-dev make postgresql-dev linux-headers musl-dev \
    libffi-dev jpeg-dev zlib-dev git \
    && pip install -r requirements.txt \
    && find /usr/local \
    \( -type d -a -name test -o -name tests \) \
    -o \( -type f -a -name '*.pyc' -o -name '*.pyo' \) \
    -exec rm -rf '{}' + \
    && runDeps="$( \
    scanelf --needed --nobanner --recursive /usr/local \
    | awk '{ gsub(/,/, "\nso:", $2); print "so:" $2 }' \
    | sort -u \
    | xargs -r apk info --installed \
    | sort -u \
    )" \
    && apk add --virtual .rundeps $runDeps \
    && apk del .build-deps

# Add the rest of the code
COPY . /app

# add env files
# COPY .env /app/WillCraft/settings

RUN python3 manage.py collectstatic --noinput

# Make port 8000 available for the app
EXPOSE 8000

CMD gunicorn WillCraft.wsgi:application --access-logfile - --error-logfile - -k gevent -w 3 -b 0.0.0.0:$PORT
