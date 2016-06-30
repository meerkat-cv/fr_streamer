sudo apt-get update
sudo apt-get -y install checkinstall python3-dev python3-numpy build-essential libjpeg8-dev libjasper-dev libpng12-dev libavcodec-dev libavformat-dev libswscale-dev libgtk2.0-dev
sudo apt-get -y install software-properties-common

wget https://bootstrap.pypa.io/get-pip.py
sudo python3 get-pip.py

sudo pip3 install numpy

sudo dpkg -i opencv_3.1.0-1_amd64.deb

cd fr_streamer
sudo pip3 install -r requirements.txt