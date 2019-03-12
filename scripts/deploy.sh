#!/usr/bin/env bash
rsync -e "ssh -o StrictHostKeyChecking=no" -r --delete-after --quiet $TRAVIS_BUILD_DIR $TRAVIS_SSH_USER@$TRAVIS_SSH_HOST:/tmp/$TRAVIS_BUILD_ID;
ssh -o StrictHostKeyChecking=no $TRAVIS_SSH_USER@$TRAVIS_SSH_HOST -t "sudo source ~/.bashrc;\
cd ~/InstaDam-backend;\
sudo docker-compose down;\
cd /tmp/${TRAVIS_BUILD_ID};\
sudo rm -rf ~/InstaDam-backend;\
sudo mv /tmp/${TRAVIS_BUILD_ID}/InstaDam-backend ~/;\
cd ~/InstaDam-backend;\
sudo docker-compose --verbose up --build&"
