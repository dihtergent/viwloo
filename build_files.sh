python3 -m pip install -r requirements.txt --break-system-packages
python3 manage.py collectstatic --noinput
mkdir -p staticfiles_build/static
touch staticfiles_build/static/placeholder.txt



