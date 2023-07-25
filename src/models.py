from django.db import models


class CustomSession(models.Model):
    session_key = models.CharField(max_length=40, primary_key=True)
    data = models.TextField()
    expire_date = models.DateTimeField()
