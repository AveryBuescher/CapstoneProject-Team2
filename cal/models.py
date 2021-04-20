from django.db import models
from django.urls import reverse
from django.contrib.auth.models import User
from cal.gcal_sync.format_datetime import format_datetime

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
    gcal_id = models.TextField(max_length=1024, null=True, blank=True)

    @property
    def get_html_url(self):
        url = reverse('cal:event_edit', args=(self.id,))
        return f'<a href="{url}"> {self.title} </a>'

    @property
    def to_gcal_body(self):
        return {
            "kind": "calendar#event",
            "start": {"dateTime": format_datetime(
                self.start_time)},
            "end": {
                "dateTime": format_datetime(self.end_time)},
            "summary": self.title,
            "description": self.description
        }


class Token(models.Model):
    token = models.TextField()
    refresh_token = models.TextField()
    token_uri = models.TextField()
    client_id = models.TextField()
    client_secret = models.TextField()
    scopes = models.TextField()
    expiry = models.TextField()
    the_user = models.ForeignKey(User, on_delete=models.CASCADE,
                                 null=False, blank=False)

    @property
    def to_dict(self):
        return {
            "token": self.token,
            "refresh_token": self.refresh_token,
            "token_uri": self.token_uri,
            "client_id": self.client_id,
            "client_secret": self.client_secret,
            "scopes": self.scopes,
            "expiry": self.expiry,
            "the_user": self.the_user
        }

