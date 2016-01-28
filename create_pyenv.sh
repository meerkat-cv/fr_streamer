source /usr/local/bin/virtualenvwrapper.sh
mkvirtualenv -p python3 fr_on_premise --system-site-packages 
workon fr_on_premise
pip install -r requirements.txt
echo "Setup of fr_on_premise python env is complete."