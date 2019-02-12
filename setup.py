from setuptools import setup

with open("README.md", 'r') as f:
    long_description = f.read()

setup(
   name='instadam-backend',
   version='1.0',
   description='backend for instadam project',
   long_description=long_description,
   author='',
   author_email='',
   url="",
   packages=[''], # instadam-backend 
   tests_require = [
      'pytest',
      'pytest-cov',
      'codecov',
   ],
   install_requires = [
      'flask>=1.0.2',
      'flask-sqlalchemy',
      'psycopg2',
      'flask-jwt-extended',
   ],
)
