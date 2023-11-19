from django.db import models

class Log(models.Model):
    level = models.CharField(max_length=255)
    message = models.CharField(max_length=255)
    resourceId = models.CharField(max_length=255)
    timestamp = models.DateTimeField()
    traceId = models.CharField(max_length=255)
    spanId = models.CharField(max_length=255)
    commit = models.CharField(max_length=255)
    metadata = models.JSONField(max_length=255)

