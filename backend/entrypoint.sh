set -e 
 
echo "Applying migrations..." 
python manage.py migrate --noinput 
 
echo "Collecting static files..." 
python manage.py collectstatic --noinput 
 
echo "Copying static files to shared volume..." 
cp -r /app/collected_static/. /backend_static/static/ 
 
exec "$@"