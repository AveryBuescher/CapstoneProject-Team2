from django.db import models
from django.urls import reverse
from django.contrib.auth.models import User

# Create your models here.

class Event(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField()
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    the_user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    #category = models.TextField() #String representing event type (let users type category or use drop down list?)

    @property
    def get_html_url(self):
        url = reverse('cal:event_edit', args=(self.id,))
        return f'<a href="{url}"> {self.title} </a>'
