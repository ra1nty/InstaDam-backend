# Endpoint Documentation

## Annotation Endpoints

Endpoints for uploading and getting project/image annotations

* Get Annotation : `GET /annotation/:label_id/:image_id/`

  Example response body
  
  ```json
  {
      "project_id": 1,
      "image_id": 4,
      "labels": [
          {
              "label_id": 1,
              "alpha": 255,
              "blue": 0,
              "ellipses": [
                  {
                      "bottom": 441.36460554371,
                      "left": 584.2217484008529,
                      "objectID": 10,
                      "right": 827.2921108742004,
                      "rotation": 0,
                      "top": 232.409381663113
                  }
              ],
              "freedraw": {
                  "objectID": 76,
                  "pixmap": "lFTkSuQmCC"
              },
              "green": 85,
              "polygons": [
                  {
                      "objectID": 34,
                      "points": [
                          942.4307036247335,
                          153.5181236673774,
                          814.498933901919,
                          196.16204690831557,
                          869.9360341151386,
                          285.7142857142857
                      ]
                  },
                  {
                      "objectID": 18,
                      "points": [
                          125.79957356076758,
                          334.7547974413646
                      ]
                  },
                  {
                      "objectID": 16,
                      "points": [
                          449.89339019189765,
                          194.02985074626866,
                          277.1855010660981,
                          275.0533049040512
                      ]
                  },
                  {
                      "objectID": 30,
                      "points": [
                          168.44349680170575,
                          635.3944562899787,
                          268.65671641791045,
                          882.72921108742
                      ]
                  }
              ],
              "rectangles": [
                  {
                      "bottom": 437.1002132196162,
                      "left": 127.9317697228145,
                      "objectID": 26,
                      "right": 127.9317697228145,
                      "rotation": 0,
                      "top": 437.1002132196162
                  },
                  {
                      "bottom": 859.2750533049041,
                      "left": 100.2132196162047,
                      "objectID": 14,
                      "right": 249.4669509594883,
                      "rotation": 0,
                      "top": 703.6247334754797
                  },
                  {
                      "bottom": 526.6524520255864,
                      "left": 89.55223880597015,
                      "objectID": 28,
                      "right": 89.55223880597015,
                      "rotation": 0,
                      "top": 526.6524520255864
                  }
              ],
              "red": 255,
              "text": "Cracks"
          }
      ]
  }
  ```

* Upload Annotation : `POST /annotation`

  Example request body:
  ```json
  {
      "project_id": 1,
      "image_id": 4,
      "labels": [
          {
              "label_id": 1,
              "alpha": 255,
              "blue": 0,
              "ellipses": [
                  {
                      "bottom": 441.36460554371,
                      "left": 584.2217484008529,
                      "objectID": 10,
                      "right": 827.2921108742004,
                      "rotation": 0,
                      "top": 232.409381663113
                  }
              ],
              "freedraw": {
                  "objectID": 76,
                  "pixmap": "lFTkSuQmCC"
              },
              "green": 85,
              "polygons": [
                  {
                      "objectID": 34,
                      "points": [
                          942.4307036247335,
                          153.5181236673774,
                          814.498933901919,
                          196.16204690831557,
                          869.9360341151386,
                          285.7142857142857
                      ]
                  },
                  {
                      "objectID": 18,
                      "points": [
                          125.79957356076758,
                          334.7547974413646
                      ]
                  },
                  {
                      "objectID": 16,
                      "points": [
                          449.89339019189765,
                          194.02985074626866,
                          277.1855010660981,
                          275.0533049040512
                      ]
                  },
                  {
                      "objectID": 30,
                      "points": [
                          168.44349680170575,
                          635.3944562899787,
                          268.65671641791045,
                          882.72921108742
                      ]
                  }
              ],
              "rectangles": [
                  {
                      "bottom": 437.1002132196162,
                      "left": 127.9317697228145,
                      "objectID": 26,
                      "right": 127.9317697228145,
                      "rotation": 0,
                      "top": 437.1002132196162
                  },
                  {
                      "bottom": 859.2750533049041,
                      "left": 100.2132196162047,
                      "objectID": 14,
                      "right": 249.4669509594883,
                      "rotation": 0,
                      "top": 703.6247334754797
                  },
                  {
                      "bottom": 526.6524520255864,
                      "left": 89.55223880597015,
                      "objectID": 28,
                      "right": 89.55223880597015,
                      "rotation": 0,
                      "top": 526.6524520255864
                  }
              ],
              "red": 255,
              "text": "Cracks"
          }
      ]
  }
  ```

## Auth Endpoints

Endpoints for registering and logging in user via username and password

* Login : `POST /login`

  Example request body:
  ```json
  {
      "username": "admin",
      "password": "AdminPassword0"
  }
  ```
* Signup : `POST /register` 

  Example request body:
  ```json
  {
      "username": "User1",
      "password": "Password1234",
      "email": "user1@illinois.edu"
  }
  ```

* Logout : `DELETE /logout`

## Image Endpoints

Endpoints for getting and uploading images to project

* List Image: `GET /projects/:project_id/images`

  Example response body:
  
  ```json
  {
      "project_images": [
          {
              "id": 1,
              "is_annotated": false,
              "name": "evilgeniuses.jpg",
              "path": "static/1/b268235e-37c6-4863-805e-77175a574647.jpg",
              "project_id": 1
          }
      ]
  } 
  ```
* Get Image Thumbnail: `GET /image/:image_id/thumbnail`

  Parameters:
  
  | Name   | Type | Description                 |
  |--------|------|-----------------------------|
  | size_w | int  | Max width of the thumbnail  |
  | size_h | int  | Max height of the thumbnail |

  Example response body:
  ```json
  {
      "base64_image": "iVBORw0KGgoAAAANSUhE...rkJggg==",
      "format": "png",
      "image_id": 1
  }
  ```
* Upload Image: `POST /image/upload/:project_id`
  
  Body of the request has format `form-data`, with key `image` and binary file as value.
  
* Upload Zip File of Images: `POST /image/upload/zip/:project_id`

  Body of the request has format `form-data`, with key `zip` and binary file as value.

## Project Endpoints

Endpoints for creating projects and loading info 

* Create Project : `POST /project`

  Example request body:
  ```json
  {
      "project_name": "Project"
  }
  ```
* Get List of Projects : `GET /projects`
  
  Example response body:
  ```json
  [
      {
          "id": 1,
          "is_admin": true,
          "name": "First Project"
      }
  ]
  ```
* Get Unannotated Images of Project : `GET /projects/:project_id/unannotated`
  
  Example response body:
  ```json
  {
      "unannotated_images": [
          {
              "id": 1,
              "name": "sree0.PNG",
              "path": "static/1/33492042-52b9-439c-93ae-9158450dd27e.png",
              "project_id": 1
          }
      ]
  } 
  ```
* Get Images of Project : `GET /projects/:project_id/images`

  Example response body:
  ```json
  {
      "project_images": [
          {
              "id": 1,
              "is_annotated": false,
              "name": "sree0.PNG",
              "path": "static/1/33492042-52b9-439c-93ae-9158450dd27e.png",
              "project_id": 1
          }
      ]
  } 
  ```
* Add Label to Project : `POST /project/<project_id>/labels`

  Example request body:
  ```json
  {
      "label_text": "first label",
      "label_color": "#12345"
  } 
  ```
* Add user to Project : `PUT /project/:project_id/permissions`

  Example request body:
  ```json
  {
      "access_type": "rw",
      "username": "User1"
  }
  ```
* Delete Project : `DELETE /project/:project_id`
* List All Users of Project : `GET /project/:project_id/users`
  ```json
  [
      {
          "access_type": "AccessTypeEnum.READ_WRITE",
          "user": {
              "created_at": "2019-04-02 01:01:53.859822",
              "email": "admin@default.com",
              "privileges": "PrivilegesEnum.ADMIN",
              "username": "admin"
          }
      }
  ]
  ```

## User Endpoints

* Search for Users : `GET /users/search`

  Parameters:
  
  | Name   | Type   | Description                   |
  |--------|--------|-------------------------------|
  | q      | string | substring of user name, email |
  
  Example response body:
  ```json
  {
      "users": [
          {
              "created_at": "2019-04-02 01:38:57.017910",
              "email": "user1@illinois.edu",
              "privileges": "PrivilegesEnum.ADMIN",
              "username": "User1"
          }
      ]
  } 
  ```
