# InstaDam Backend

Backend API server for InstaDam, an application to create ground truth pixel-wise labels for deep learning based semantic segmentation of complex shapes like mechanical/structural defects in civil infrastructure like buildings and bridges or medical images in a user friendly manner.

[![Build Status](https://travis-ci.org/ra1nty/InstaDam-backend.svg?branch=master)](https://travis-ci.org/ra1nty/InstaDam-backend)
[![codecov](https://codecov.io/gh/ra1nty/InstaDam-backend/branch/master/graph/badge.svg)](https://codecov.io/gh/ra1nty/InstaDam-backend)

## Quickstart

Start a development server (Use In-memory Sqlite) :
```
pip install -r requirements.txt 
python manage.py start
```

start a production server (PostgreSQL) :
```
python manage.py initdb --mode=production
python manage.py start --mode=production
```
