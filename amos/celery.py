import os

from celery import Celery
from django.conf import settings

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'amos.settings')
app = Celery('amos', broker = "amqp://localhost/")

app.config_from_object('django.conf:settings', namespace = 'CELERY')
app.autodiscover_tasks()

@app.task(bind = True)
def debug_task(self):
    print('Request: {}'.format(self.request))