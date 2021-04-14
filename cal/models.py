from django.db import models
from django.urls import reverse
from django.contrib.auth.models import User

# Create your models here.

class Event(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField()
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    CATEGORY_CHOICES = [("Important", "Important"), ("Tentative", "Tentative"), ("Recurrent", "Recurrent"), ("Normal", "Normal")]
    category = models.CharField(max_length=40, choices=CATEGORY_CHOICES, default="NORMAL")
    COLOR_CHOICES = [("dddddd","WHITE"),("ff4444","RED"), ("44ff44", "GREEN"), ("4444ff", "BLUE")]
    color = models.CharField(max_length=40, choices=COLOR_CHOICES, default="WHITE")
    the_user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)

    @property
    def get_html_url(self):
        url = reverse('cal:event_edit', args=(self.id,))
        return f'<a href="{url}"> {self.title} </a>'
