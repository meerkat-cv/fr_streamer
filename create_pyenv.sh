source /usr/local/bin/virtualenvwrapper.sh
mkvirtualenv -p python3 fr_streamer --system-site-packages 
workon fr_streamer
pip install -r requirements.txt
echo "Setup of fr_streamer python env is complete."