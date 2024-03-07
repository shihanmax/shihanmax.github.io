# basic
yun -y install tmux
yum -y install vim
yum -y install git


# install jekyll
sudo yum -y install dnf
sudo dnf install ruby ruby-devel -y
sudo dnf group install "Development Tools" -y
yum -y install epel-release
yum -y install readline-devel zlib-devel libffi-devel libyaml-devel openssl-devel sqlite-devel
gpg2 --keyserver hkp://keyserver.ubuntu.com --recv-keys 409B6B1796C275462A1703113804BB82D39DC0E3 7D2BAF1CF37B13E2069D6956105BD0E739499BDB
curl -sSL https://get.rvm.io | bash -s stable --ruby
source /etc/profile.d/rvm.sh
rvm reload
rvm requirements run
rvm install 2.7.2
rvm use 2.7.2 --default

gem install jekyll bundler --no-document

# nginx
sudo yum -y install epel-release
sudo yum -y install nginx
sudo systemctl start nginx


sudo firewall-cmd --zone=public --add-port=8081/tcp --permanent
sudo firewall-cmd --zone=public --add-port=8082/tcp --permanent
sudo firewall-cmd --zone=public --add-port=8082/tcp --permanent
firewall-cmd --reload