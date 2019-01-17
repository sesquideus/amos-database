from celery import shared_task

from .models import Meteor

@shared_task
def createMeteor():
    meteor = Meteor.objects.createRandom() 
    meteor.save()
