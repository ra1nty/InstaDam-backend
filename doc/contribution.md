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
