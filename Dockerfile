FROM centos:7
WORKDIR /my_blog
COPY . .
RUN yum -y update
RUN yum -y install vim
RUN yum -y install ruby
RUN gpg --keyserver hkp://keys.gnupg.net --recv-keys 409B6B1796C275462A1703113804BB82D39DC0E3 7D2BAF1CF37B13E2069D6956105BD0E739499BDB
RUN curl -sSL https://get.rvm.io | bash -s stable
RUN source /etc/profile.d/rvm.sh
RUN rvm install ruby
RUN echo "ruby installed: " $(ruby -v)
RUN gem install jekyll
RUN echo "jekyll installed: " $(jekyll -v)
RUN gem install bundler

RUN echo "now install Node"
RUN curl -sL https://rpm.nodesource.com/setup_10.x | bash -
RUN yum -y install nodejs
RUN npm install -g github-webhook-handler     # install github-webhook-handler
RUN cp deploy.sh  /usr/lib/node_modules/github-webhook-handler/
RUN cp deploy.js  /usr/lib/node_modules/github-webhook-handler/

RUN npm install forever -g  # install forever
RUN forever start -a -l  forever.log   deploy.js  # run forever
