FROM python:3.6-alpine

RUN adduser -D instadam

WORKDIR /home/instadam

COPY requirements requirements
RUN \
 apk add --no-cache postgresql-libs && \
 apk add --no-cache --virtual .build-deps gcc musl-dev postgresql-dev
RUN python -m venv venv
RUN venv/bin/pip install -r requirements/prod.txt
RUN venv/bin/pip install gunicorn
RUN apk --purge del .build-deps
COPY instadam instadam
COPY manage.py ./

RUN chown -R instadam:instadam ./
USER instadam

EXPOSE 5000
