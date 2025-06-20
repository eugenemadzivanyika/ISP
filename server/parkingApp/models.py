from django.db import models


class VehicleLog(models.Model):
    ACTION_CHOICES = [('entry', 'Entry'), ('exit', 'Exit')]

    timestamp = models.DateTimeField(auto_now_add=True)
    action = models.CharField(max_length=5, choices=ACTION_CHOICES)

    def __str__(self):
        return f"{self.action.capitalize()} at {self.timestamp}"

