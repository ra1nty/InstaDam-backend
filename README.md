# InstaDam Backend 

Backend API server for InstaDam, an application to create ground truth pixel-wise labels for deep learning based semantic segmentation of complex shapes like mechanical/structural defects in civil infrastructure like buildings and bridges or medical images in a user friendly manner.

[![Build Status](https://travis-ci.org/ra1nty/InstaDam-backend.svg?branch=master)](https://travis-ci.org/ra1nty/InstaDam-backend)
[![codecov](https://codecov.io/gh/ra1nty/InstaDam-backend/branch/master/graph/badge.svg)](https://codecov.io/gh/ra1nty/InstaDam-backend)

## Quickstart

Start a development server (Use In-memory Sqlite) :
* Install the dependencies in requirements/dev.txt  
  `pip install -r requirements/dev.txt`
* The development mode utilize in-memory Sqlite database for fast-prototyping and development,
  make sure you have Sqlite installed in your development environment.  
  Start the server:  
`python3 manage.py start --mode=development`

## Deploy with Docker & docker-compose
  * Set necessary environment variables for deployment: 
      - DB_USERNAME: Database username.
      - DB_PASSWORD: Database password.
      - DB_NAME: Database name for InstaDam app.
      - SECRETE_KEY: User supplied secrete key for the app.
  * Run ```docker-compose up``` in project root folder

## Deploy in custom environment
  * First, you should have a PostgreSQL instance up and running on your server.
  * Then you need to set the corresponding environment variables for the InstaDam app:
      - _DB_USERNAME: Database username.
      - _DB_PASSWORD: Database password.
      - _DB_HOSTNAME: Databse hostname
      - _DB_NAME: Database name for InstaDam app.
      - _SECRETE_KEY: User supplied secrete key for the app.  
   The default admin username and password is 'admin/AdminPassword0', you can change it in
    ```instadam/config.py``` before deployment.
  * Deploy a production server:  
  `python3 manage.py deploy`  
    The default behavior is to delete all previous data/table structure in the given database
    and reinitialize from ground up.  
    
  * Alternatively, you can reuse the previous data by using  
  `python3 manage.py start --mode=production`

## Developer's Guide

[Project Structure](doc/contribution.md)

[Project Endpoints](doc/endpoints.md)

Run below command to generate HTML documentation via Pydoc:
```
sh doc.sh
```

## Contributors
Nishanth Salinamakki: nishanthrs

Zonglin Li: zli117

Yu Tang: ra1nty

Wanxian Yang: Louise15926
