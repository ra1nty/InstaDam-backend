FROM python:3.6-alpine

RUN mkdir -p /home/flaskapp/src
WORKDIR /home/flaskapp

COPY requirements/prod.txt requirements.txt
RUN \
 apk add --no-cache postgresql-libs && \
 apk add --no-cache --virtual .build-deps gcc musl-dev postgresql-dev

RUN pip install --no-cache-dir -r requirements.txt
RUN pip install gunicorn
RUN apk --purge del .build-deps

COPY instadam /home/flaskapp/instadam
COPY manage.py /home/flaskapp

EXPOSE 5000
