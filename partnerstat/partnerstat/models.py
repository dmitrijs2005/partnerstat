from django.contrib.auth.models import User
from django.db import models

ALL = 0
ETVNET = 1
RIDNETV = 6
ACTAVA = 8

DOMAIN_CHOICES = (
    (ETVNET, 'etvnet'),
    (RIDNETV, 'ridnetv'),
    (ACTAVA, 'actava')
)

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    domain = models.IntegerField(
        default=ETVNET,
        choices=DOMAIN_CHOICES
    )