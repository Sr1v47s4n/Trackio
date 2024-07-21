import hashlib
import requests
from bs4 import BeautifulSoup
from django.core.mail import send_mail
from django.conf import settings
from .models import Website
import threading
import signal
import sys


def fetch_content(url):
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        return response.text
    except requests.RequestException as e:
        print(f"Error fetching content from {url}: {e}")
        return None


def extract_static_content(html):
    soup = BeautifulSoup(html, "html.parser")

    # Remove unwanted tags
    for tag in soup(["script", "style"]):
        tag.decompose()

    # Get the text from the remaining content
    static_content = soup.get_text(separator=" ", strip=True)

    return static_content


def hash_content(content):
    return hashlib.md5(content.encode("utf-8")).hexdigest() if content else None


class WebsiteChecker:

    def __init__(self, interval=60):  # Default interval set to 24 hours
        self.interval = interval
        self.thread = threading.Thread(target=self.run)
        self.stop_event = threading.Event()

    def start(self):
        print("Starting Website Checker...")
        self.thread.start()

    def stop(self):
        print("Stopping Website Checker...")
        self.stop_event.set()
        self.thread.join()

    def run(self):
        while not self.stop_event.is_set():
            print("Checking websites...")
            self.check_websites()
            print(f"Sleeping for {self.interval} seconds...")
            self.stop_event.wait(self.interval)

    def check_websites(self):
        websites = Website.objects.all()
        for website in websites:
            current_content = fetch_content(website.url)
            if current_content:
                static_content = extract_static_content(current_content)
                current_hash = hash_content(static_content)
                print(f"Current Hash for {website.url}: {current_hash}")
                print(f"Last Hash for {website.url}: {website.last_hash}")
                if current_hash != website.last_hash:
                    website.last_hash = current_hash
                    website.save()
                    self.send_notification(website)
                    print(f"Changes detected in {website.url}")

    def send_notification(self, website):
        send_mail(
            subject="🚨 Website Content Updated!",
            message="A change has been detected on a website you are tracking.",
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[website.user.email],
            fail_silently=False,
            html_message=(
                f"<html><body>"
                f"<h2>Website Content Update</h2>"
                f"<p>Hello {website.user.username},</p>"
                f"<p>Good news! The website <strong>{website.url}</strong> has been updated.</p>"
                f"<p>We noticed a change since our last check. Please review the updated content by clicking the button below:</p>"
                f"<p><a href='{website.url}' style='display: inline-block; padding: 10px 20px; font-size: 16px; color: #fff; background-color: #007bff; text-decoration: none; border-radius: 5px;'>View Website</a></p>"
                f"<p>Thank you for using our service!</p>"
                f"<p>Best regards,<br>Trackio</p>"
                f"</body></html>"
            ),
        )


checker = WebsiteChecker()


def handle_exit(signum, frame):
    print("Shutting down...")
    checker.stop()
    sys.exit(0)


signal.signal(signal.SIGINT, handle_exit)
signal.signal(signal.SIGTERM, handle_exit)

checker.start()
