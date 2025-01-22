from django.db import models
import uuid





#Creating base model or class to use everywhere as a base model It's an helper model

"""This is base model and it will be inherited by all classes and models"""
class BaseModel(models.Model):
    uid = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    create_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


    #To make sure it's not a model it's just a class to django
    class Meta:
        abstract = True