# tracker/signals.py
from django.apps import AppConfig
import atexit
from .tasks import checker


class TrackerAppConfig(AppConfig):
    name = "tracker"

    def ready(self):
        if not checker.thread.is_alive():
            checker.start()

        atexit.register(checker.stop)
