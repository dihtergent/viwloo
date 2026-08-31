python3 -m pip install -r requirements.txt --break-system-packages
python3 manage.py collectstatic --noinput
mkdir -p staticfiles_build
touch staticfiles_build/placeholder.txt


