#!/bin/bash
cd /root/myblog/blog/
echo start pull from github 
pwd
git pull
echo start build..
bundle exec jekyll build

