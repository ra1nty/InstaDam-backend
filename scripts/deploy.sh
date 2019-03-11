#!/usr/bin/env bash
rsync -e "ssh -o StrictHostKeyChecking=no" -r --delete-after --quiet $TRAVIS_BUILD_DIR $TRAVIS_SSH_USER@$TRAVIS_SSH_HOST:/tmp/$TRAVIS_BUILD_ID;
ssh -o StrictHostKeyChecking=no $TRAVIS_SSH_USER@$TRAVIS_SSH_HOST -t\
 "cd ~/instadam/InstaDam-backend;\
docker-compose down;\
cd /tmp/${TRAVIS_BUILD_ID};\
sudo rm -rf ~/instadam;\
mkdir -p ~/instadam;\
sudo mv /tmp/${TRAVIS_BUILD_ID}/InstaDam-backend ~/instadam;\
cd ~/instadam/InstaDam-backend;\
source ~/.bashrc;\
docker-compose up --build"