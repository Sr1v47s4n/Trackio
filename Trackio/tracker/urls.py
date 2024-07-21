from django.urls import path
from django.contrib.auth import views as auth_views
from tracker import views

urlpatterns = [
    path("", views.home, name="home"),
    path("dashboard/", views.dashboard, name="dashboard"),
    path("add_website/", views.add_website, name="add_website"),
    path("profile/", views.profile, name="profile"),
    path("login/", views.login_usr, name="login"),
    path("password_reset", views.reset_password, name="password_reset"),
    path(
        "reset-password/<token>/",
        views.reset_password_confirmation,
        name="reset_password_confirmation",
    ),
    path("logout/", views.logout_usr, name="logout"),
    path("signup/", views.signup, name="signup"),
    path("search", views.search, name="search"),
    path("delete/<int:id>", views.delete_website, name="delete_website"),
]
