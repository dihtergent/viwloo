python -m pip install --upgrade pip --break-system-packages
pip install -r requirements.txt --break-system-packages
python manage.py collectstatic --noinput
pip install cloudinary --break-system-packages
