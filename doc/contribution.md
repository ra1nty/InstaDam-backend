# How to change the code

## Project directory structure
  * Root directory
    * .gitignore: Gitignore file
    * .travis.yml: Travis config
    * Dockerfile: Docker configuration
    * README.md: The default readme
    * deploy_rsa.enc: Encrypted ssh key to access production server
    * doc.sh: Script to generate Python doc
    * docker-compose.yml: Docker configuration
    * manage.py: Manage database. Run `python3 manage.py --help` for details
    * setup.py: Python package installation
    * uwsgi.ini: Config for UWSGI
    * wsgi.py: Entry point for wsgi server
    * conf.d: Nginx config
    * instadam: Source code directory
      * annotation.py: Annotation related end points
        * Save annotation
        * Get annotation
      * app.py: Registration of blueprints and creation of the application instance
      * auth.py: Auth related end points
        * Login
        * Register
        * Logout
      * config.py: File of configurations
      * error_handlers.py: Registered handlers to convert `abort` message to json response
      * image.py: Image related endpoints
        * Upload image
        * Upload zip
        * Get image
        * Get thumbnail
      * project.py: Project related endpoints
        * Create project
        * List project of the user
        * Get unannotated images of a project
        * Get all images of a project
        * Add label
        * Get labels
        * Add user to project
        * Delete project
        * List user of a project
      * search_users.py: Endpoint for searching user
      * user.py: Change user privilege (deprecated)
      * model: Contains model for database. Note that the relationship between 
        * annotation.py: Model for annotation
        * image.py: Model for image
        * label.py: Model for label
        * project.py: Model for project
        * project_permission.py: Model for user access permission. Used to implement many to many mapping between user and project
        * revoked_token.py: Save revoked tokens when user log out
        * user.py: Model for user

## Set up development environment
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
