script_path = $(pwd)

# ===== install anaconda
wget https://mirrors.tuna.tsinghua.edu.cn/anaconda/archive/Anaconda3-2019.03-Linux-x86_64.sh
bash Anaconda3-2019.03-Linux-x86_64.sh -b -p $HOME/miniconda


# ===== install tmux
# Install tmux 2.8 on Centos
# install deps
yum install gcc kernel-devel make ncurses-devel
# DOWNLOAD SOURCES FOR LIBEVENT AND MAKE AND INSTALL
curl -LOk https://github.com/libevent/libevent/releases/download/release-2.1.8-stable/libevent-2.1.8-stable.tar.gz
tar -xf libevent-2.1.8-stable.tar.gz
cd libevent-2.1.8-stable
./configure --prefix=/usr/local
make
make install
# DOWNLOAD SOURCES FOR TMUX AND MAKE AND INSTALL
curl -LOk https://github.com/tmux/tmux/releases/download/2.8/tmux-2.8.tar.gz
tar -xf tmux-2.8.tar.gz
cd tmux-2.8
LDFLAGS="-L/usr/local/lib -Wl,-rpath=/usr/local/lib" ./configure --prefix=/usr/local
make
make install
# pkill tmux
# close your terminal window (flushes cached tmux executable)
# open new shell and check tmux version
tmux -V


# ====== install vim, ruby, jekyll, nodejs, forever, bounder
yum -y update
yum -y install vim
yum -y install ruby
gpg --keyserver hkp://keys.gnupg.net --recv-keys 409B6B1796C275462A1703113804BB82D39DC0E3 7D2BAF1CF37B13E2069D6956105BD0E739499BDB
curl -sSL https://get.rvm.io | bash -s stable
source /etc/profile.d/rvm.sh
rvm install ruby 2.4.3
echo "ruby installed: " $(ruby -v)
gem install jekyll
echo "jekyll installed: " $(jekyll -v)
gem install bundler 2.2.6

echo "now install Node"
curl -sL https://rpm.nodesource.com/setup_10.x | bash -
yum -y install nodejs
npm install -g github-webhook-handler     # install github-webhook-handler

cd script_path
cp deploy.sh  /usr/lib/node_modules/github-webhook-handler/
cp deploy.js  /usr/lib/node_modules/github-webhook-handler/

npm install forever -g  # install forever
forever start -a -l  forever.log   deploy.js  # run forever

# ===== install BBR
wget --no-check-certificate https://github.com/teddysun/across/raw/master/bbr.sh
chmod +x bbr.sh
# bash bbr.sh  # need reboot