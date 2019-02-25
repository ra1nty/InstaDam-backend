FROM python:3.6-alpine

RUN adduser -D instadam

WORKDIR /home/instadam

COPY requirements requirements
RUN \
 apk add --no-cache postgresql-libs && \
 apk add --no-cache --virtual .build-deps gcc musl-dev postgresql-dev

RUN pip install --no-cache-dir -r requirements/prod.txt
RUN pip install gunicorn

RUN apk --purge del .build-deps

COPY instadam instadam
COPY manage.py ./
COPY wsgi.py ./

RUN chown -R instadam:instadam ./
USER instadam

EXPOSE 5000
