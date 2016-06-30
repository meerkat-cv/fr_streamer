# it is going to see if the bucket exists, if not creates it
echo "Running gunicorn..."
exec gunicorn -k tornado --bind=0.0.0.0:4443 --workers=1 --log-level INFO --timeout=120 'fr_streamer:build_app()'