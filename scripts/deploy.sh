rsync -e "ssh -o StrictHostKeyChecking=no" -r --delete-after --quiet $TRAVIS_BUILD_DIR $TRAVIS_SSH_USER@$TRAVIS_SSH_HOST:/tmp/$TRAVIS_BUILD_ID;
ssh -o StrictHostKeyChecking=no $TRAVIS_SSH_USER@$TRAVIS_SSH_HOST -t "cd /tmp/$TRAVIS_BUILD_ID; bash --login"
rm -rf ~/instadam
cp -r $(pwd) ~/instadam
cd ~/instadam
docker-compose up -d app --build
exit
