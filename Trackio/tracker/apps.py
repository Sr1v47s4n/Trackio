# tracker/apps.py
from django.apps import AppConfig


class TrackerAppConfig(AppConfig):
    name = "tracker"

    def ready(self):
        import tracker.signals  # Import the signals to ensure they're registered
