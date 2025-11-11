
pip install -r requirements.txt
python manage.py collectstatic --noinput
mkdir -p media/alertas
mkdir -p staticfiles
python manage.py migrate