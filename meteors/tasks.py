from celery import shared_task

from .models import Meteor

@shared_task
def createMeteor():
    meteor = Meteor.objects.create_random()
    meteor.save()
