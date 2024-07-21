from django.db import models
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
import re,uuid
import requests
from urllib.parse import urlparse
from django.utils import timezone
def validate_url(value):
    url_pattern = re.compile(
        r"^(?:http|https)://"  # http:// or https://
        r"(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+(?:[A-Z]{2,6}\.?|[A-Z0-9-]{2,}\.?)"  # domain...
        r"(?:/?|[/?]\S+)$",
        re.IGNORECASE,
    )
    if not re.match(url_pattern, value):
        raise ValidationError("Invalid URL format")


class Website(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=100, null=False,default="None")
    url = models.URLField(unique=True, validators=[validate_url])
    last_hash = models.TextField(default="None", null=False)
    last_checked = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.url
    def save(self, *args, **kwargs):
        if not self.name:
            self.name = urlparse(self.url).netloc
            self.name = self.name.replace("www.", "")
            self.name = self.name.title()
        super(Website, self).save(*args, **kwargs)

    def is_alive(self):
        try:
            response = requests.get(self.url, timeout=10)
            return response.status_code == 200
        except requests.RequestException:
            return False


class PasswordResetToken(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    token = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    created_at = models.DateTimeField(default=timezone.now)
    is_used = models.BooleanField(default=False)

    def is_valid(self):
        now = timezone.now()
        return not self.is_used and (now - self.created_at).total_seconds() < 3600
