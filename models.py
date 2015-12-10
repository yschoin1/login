from django.db import models
from django.contrib.auth.models import User

# Model to store user data
class nomatUser(models.Model):
    email = models.EmailField()
    confirmationCode = models.CharField(max_length=100)
    agreeToConditions = models.BooleanField('Agree to conditions', default = False)

    def __unicode__(self):
		return self.email