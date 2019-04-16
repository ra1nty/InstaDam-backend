# Endpoint Documentation

## Annotation Endpoints

Endpoints for uploading and getting project/image annotations

* Get Annotation : `GET /annotation/<label_id>/<image_id>`
* Upload Annotation : `POST /annotation`

## Auth Endpoints

Endpoints for registering and logging in user via username and password

* Login : `POST /login`
* Signup : `POST /signup` 
* Logout : `DELETE /logout`

## Image Endpoints

Endpoints for getting and uploading images to project

* Get Image : `GET /image/<image_id>`
* Get Image Thumbnail : `GET /image/<image_id>/thumbnail`
* Upload Image : `POST /image/upload/<project_id>`
* Upload Zip File of Images: `POST /image/upload/zip/<project_id>`

## Project Endpoints

Endpoints for creating projects and loading info 

* Create Project : `POST /project`
* Get List of Projects : `GET /projects`
* Get Unannotated Images of Project : `GET /project/<project_id>/unannotated`
* Get Images of Project : `GET /project/<project_id>/images`
* Add Labels to Project : `POST /project/<project_id>/labels`
* Update User Permissions for Project : `PUT /project/<project_id>/permissions`
* Delete Project : `DELETE /project/<project_id>`
* List All Users of Project : `GET /project/<project_id>/users`

## User Endpoints

* Search for Users : `GET /users/search`
* Change User Privilege : `PUT /user/privilege`
