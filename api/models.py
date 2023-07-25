from django.db import models


class TwoFactorAuth(models.Model):
    user_id = models.IntegerField()
    code = models.CharField(max_length=6)
