web: gunicorn barraca.wsgi:application --log-file -
worker: celery -A barraca worker --loglevel=info
beat: celery -A barraca beat --loglevel=info --scheduler django_celery_beat.schedulers:DatabaseScheduler