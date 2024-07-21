from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Website, PasswordResetToken
from django.contrib.auth import authenticate, login, logout
import hashlib
import requests
from urllib.parse import urlparse
from django.conf import settings
from django.core.mail import send_mail
from django.contrib.auth.models import User
from django.db.models import Q


def send_alert_email(subject, message, recipient_list):
    send_mail(
        subject,
        message,
        f"Trackio Notification {settings.DEFAULT_FROM_EMAIL}",
        recipient_list,
        fail_silently=False,
    )


def fetch_content(url):
    if requests.get(url).status_code != 200:
        return None
    response = requests.get(url)
    return response.text


def hash_content(content):
    return hashlib.md5(content.encode("utf-8")).hexdigest()


# def check_website_changes():
#     websites = Website.objects.all()
#     print(websites)
#     for website in websites:
#         current_content = fetch_content(website.url)
#         # print(current_content)
#         if current_content:
#             current_hash = hash_content(current_content)
#             if current_hash != website.last_hash:
#                 website.last_hash = current_hash
#                 website.last_checked = timezone.now()
#                 website.save()
#                 print(f"Changes detected in {website.url}")

#                 # Send email alert
#                 send_alert_email(
#                     subject="Website Content Changed",
#                     message=f"The content of the website {website.url} has changed.",
#                     recipient_list=[website.user.email],
#                 )


def signup(request):
    if request.method == "POST":
        username = request.POST.get("username")
        email = request.POST.get("email")
        password = request.POST.get("password")
        if User.objects.filter(username=username).exists():
            messages.error(request, "Username is already taken.")
            return redirect("signup")
        if User.objects.filter(email=email).exists():
            messages.error(request, "Email is already taken.")
            return redirect("signup")
        user = User.objects.create_user(username=username, email=email, password=password)
        user.save()
        messages.success(request, "Account created successfully.")
        return redirect("login")
    # else:
    #     return render(request, "signup.html")
    return render(request, "signup.html")

def login_usr(request):
    if request.user.is_authenticated:
        return redirect("dashboard")
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")
        user = authenticate(username=username, password=password)
        if user:
            login(request, user)
            messages.success(request, "Logged in successfully.")
            # check_website_changes()
            return redirect("dashboard")    
        else:
            messages.error(request, "Invalid username or password.")
    return render(request, "login.html")


def logout_usr(request):
    logout(request)
    messages.success(request, "Logged out successfully.")
    return redirect("login")


@login_required
def dashboard(request):
    websites = Website.objects.filter(user=request.user)
    # check_website_changes()
    return render(request, "dashboard.html", {"websites": websites})


@login_required
def add_website(request):
    try:
        if request.method == "POST":
            name = request.POST.get("name")
            url = request.POST.get("url")
            if url:
                url = url.strip()
                if not url.startswith("http"):
                    url = f"http://{url}"
                if not name:
                    name = urlparse(url).notloc
                    name = name.replace("wwww", "").title()

                if Website.objects.filter(url=url, user=request.user).exists():
                    messages.error(request, "Website already exists.")
                    return redirect("dashboard")
                try:
                    response = requests.get(url, timeout=10)
                    if response.status_code != 200:
                        messages.error(request, "Invalid URL or website is down.")
                        return redirect("dashboard")
                except requests.RequestException:
                    messages.error(request, "Invalid URL or website is down.")
                    return redirect("add_website")
                hash = hash_content(fetch_content(url))
                if hash is None:
                    messages.error(request, "Invalid URL or website is down.")
                    return redirect("add_website")
                website = Website(url=url, user=request.user, last_hash=hash, name=name)
                website.save()
                send_mail(
                    subject="🌐 New Website Added to Your Tracking List",
                    message=(
                        f"<html><body>"
                        f"<h2>Website Added Successfully</h2>"
                        f"<p>Hello {request.user.username},</p>"
                        f"<p>We wanted to let you know that a new website has been added to your tracking list:</p>"
                        f"<p><strong>URL:</strong> {website.url}</p>"
                        f"<p>We will start monitoring this website for any changes and notify you accordingly.</p>"
                        f"<p>If you have any questions or need further assistance, please feel free to reach out to us.</p>"
                        f"<p>Thank you for using our service!</p>"
                        f"<p>Best regards,<br>Trackio</p>"
                        f"</body></html>"
                    ),
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    recipient_list=[request.user.email],
                    fail_silently=False,
                    html_message=(
                        f"<html><body>"
                        f"<h2>Website Added Successfully</h2>"
                        f"<p>Hello {request.user.username},</p>"
                        f"<p>We wanted to let you know that a new website has been added to your tracking list:</p>"
                        f"<p><strong>URL:</strong> {website.url}</p>"
                        f"<p>We will start monitoring this website for any changes and notify you accordingly.</p>"
                        f"<p>If you have any questions or need further assistance, please feel free to reach out to us.</p>"
                        f"<p>Thank you for using our service!</p>"
                        f"<p>Best regards,<br>Trackio</p>"
                        f"</body></html>"
                    ),
                )

                messages.success(request, "Website added successfully!")
                return redirect("dashboard")
            else:
                messages.error(request, "There was an error with your submission.")

        else:
            return render(request, "add_website.html")
    except Exception as e:
        messages.error(request, f"Tracking failed, Try again later. ")
    return render(request, "add_website.html")


@login_required
def profile(request):
    return render(request, "profile.html")


def home(request):
    return render(request, "home.html")

def reset_password(request):
    if request.method == "POST":
        email = request.POST.get("email")
        try:
            user = User.objects.get(email=email)

            token = PasswordResetToken.objects.create(user=user)
            reset_link = request.build_absolute_uri(f'/reset-password/{token.token}/')
            print("User",user.username," Link",reset_link)

            send_mail(
            subject="🔑 Password Reset Request",
            message=(
                f"<html><body>"
                f"<h2>Reset Your Password</h2>"
                f"<p>Hello {request.user.username},</p>"
                f"<p>We received a request to reset the password for your account.</p>"
                f"<p>You can reset your password by clicking the button below:</p>"
                f"<p><a href='{reset_link}' style='display: inline-block; padding: 10px 20px; font-size: 16px; color: #fff; background-color: #007bff; text-decoration: none; border-radius: 5px;'>Reset Password</a></p>"
                f"<p>If you did not request a password reset, please ignore this email.</p>"
                f"<p>Thank you,<br>Trackio</p>"
                f"</body></html>"
            ),
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[user.email],
            fail_silently=False,
            html_message=(
                f"<html><body>"
                f"<h2>Reset Your Password</h2>"
                f"<p>Hello {request.user.username},</p>"
                f"<p>We received a request to reset the password for your account.</p>"
                f"<p>You can reset your password by clicking the button below:</p>"
                f"<p><a href='{reset_link}' style='display: inline-block; padding: 10px 20px; font-size: 16px; color: #fff; background-color: #007bff; text-decoration: none; border-radius: 5px;'>Reset Password</a></p>"
                f"<p>If you did not request a password reset, please ignore this email.</p>"
                f"<p>Thank you,<br>Trackio</p>"
                f"</body></html>"
            )
        )
            messages.success(request, 'A password reset link has been sent to your email.')
            return redirect('login')
        except Exception as e:
            print(f"Error: {e}")
            messages.error(request, 'No user is associated with this email address.')
            return redirect('login')
    return render(request, "reset_password.html")

def reset_password_confirmation(request,token):
    try:
        token = PasswordResetToken.objects.get(token=token)
        if request.method == "POST":
            password = request.POST.get("password")
            password1 = request.POST.get("password1")
            if password != password1:
                messages.error(request, 'Passwords do not match.')
                return render(request, "reset_password_confirmation.html")
            user = token.user
            user.set_password(password)
            user.save()
            token.delete()
            messages.success(request, 'Password reset successful. You can now login with your new password.')
            return redirect('login')
        return render(request, "reset_password_confirmation.html")
    except:
        messages.error(request, 'Invalid or expired token.')
        return redirect('login')

def search(request):
    query = request.GET.get("query", "")
    if query:
        websites = Website.objects.filter(
            Q(url__icontains=query) | Q(name__icontains=query)
        )
    else:
        websites = Website.objects.all()
    return render(request, "dashboard.html", {"websites": websites})


def delete_website(request, id):
    website = Website.objects.get(id=id)
    if website.user != request.user:
        messages.error(request, "You are not authorized to delete this website.")
        return redirect("dashboard")
    website.delete()
    send_mail(
        subject="🗑️ Website Removed from Your Tracking List",
        message=(
            f"<html><body>"
            f"<h2>Website Removed Successfully</h2>"
            f"<p>Hello {request.user.username},</p>"
            f"<p>We wanted to inform you that the following website has been removed from your tracking list:</p>"
            f"<p><strong>URL:</strong> {website.url}</p>"
            f"<p>If this was done in error or if you need any assistance, please contact us immediately.</p>"
            f"<p>Thank you for using our service!</p>"
            f"<p>Best regards,<br>Trackio</p>"
            f"</body></html>"
        ),
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[request.user.email],
        fail_silently=False,
        html_message=(
            f"<html><body>"
            f"<h2>Website Removed Successfully</h2>"
            f"<p>Hello {request.user.username},</p>"
            f"<p>We wanted to inform you that the following website has been removed from your tracking list:</p>"
            f"<p><strong>URL:</strong> {website.url}</p>"
            f"<p>If this was done in error or if you need any assistance, please contact us immediately.</p>"
            f"<p>Thank you for using our service!</p>"
            f"<p>Best regards,<br>Trackio</p>"
            f"</body></html>"
        ),
    )

    messages.success(request, "Website deleted successfully.")
    return redirect("dashboard")

# Schedule the task (e.g., when the user logs in or adds a website)\
