web: gunicorn barraca.wsgi:application --log-file -
worker: celery -A barraca worker --loglevel=info