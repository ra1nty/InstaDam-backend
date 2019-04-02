#!/usr/bin/env bash
rsync -e "ssh -o StrictHostKeyChecking=no" -r --delete-after --quiet $TRAVIS_BUILD_DIR instadam@23.100.23.94:/home/instadam;
ssh -o StrictHostKeyChecking=no instadam@23.100.23.94 -t "sudo systemctl restart instadam-backendd"
