from django.core.management.base import BaseCommand
from tracker.tasks import WebsiteChecker, handle_exit
import signal


class Command(BaseCommand):
    help = "Start the website checker"

    def handle(self, *args, **kwargs):
        checker = WebsiteChecker()
        signal.signal(signal.SIGINT, handle_exit)
        signal.signal(signal.SIGTERM, handle_exit)
        checker.start()
        self.stdout.write(self.style.SUCCESS("Website checker started"))
