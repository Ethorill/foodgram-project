FROM python:3.8.5

WORKDIR /code
COPY . /code



RUN python -m pip install --upgrade pip && pip install -r requirements.txt && python3 manage.py collectstatic --noinput

CMD python3 manage.py makemigrations && python3 manage.py migrate && gunicorn foodgram.wsgi:application --bind 0.0.0.0:8000