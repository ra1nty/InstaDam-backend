FROM python:3.6-alpine

RUN adduser -D instadam

WORKDIR /home/instadam

COPY requirements requirements
RUN python -m venv venv
RUN venv/bin/pip install -r requirements/prod.txt
RUN venv/bin/pip install gunicorn

COPY instadam instadam
COPY manage.py ./

RUN chown -R instadam:instadam ./
USER instadam

EXPOSE 5000