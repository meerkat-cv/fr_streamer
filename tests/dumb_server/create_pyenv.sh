source /usr/local/bin/virtualenvwrapper.sh
mkvirtualenv -p python3 dumb_server  --system-site-packages 
workon dumb_server
pip install -r requirements.txt
echo "Setup of dumb_server python env is complete."