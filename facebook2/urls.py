"""facebook2 URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.views.generic.base import TemplateView

import facebook2_app.views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('accounts/', include("django.contrib.auth.urls")),
    path('accounts/register/', facebook2_app.views.register, name="register"),
    path('', facebook2_app.views.index, name="index"),
    path('create_post/', TemplateView.as_view(template_name="create-post.html"), name="create_post"),
    path('submit_post/', facebook2_app.views.submit_post, name="submit_post"),
    path('friends/', facebook2_app.views.friend_list, name="friends"),
    path('@<slug:username>/', facebook2_app.views.user, name="user"),
    path('@<slug:username>/send_request', facebook2_app.views.send_request, name="send_request"),
    path('@<slug:username>/accept_request', facebook2_app.views.accept_request, name="accept_request"),
    path('@<slug:username>/reject_request', facebook2_app.views.reject_request, name="reject_request"),
    path('@<slug:username>/end_friendship', facebook2_app.views.end_friendship, name="end_friendship"),
    path('<int:post_id>', facebook2_app.views.post_page, name="post_page"),
    path('<int:post_id>/edit', facebook2_app.views.edit_post, name="edit_post"),
    path('<int:post_id>/edit/submit', facebook2_app.views.submit_edited_post, name="submit_edited_post"),
    path('<int:post_id>/delete', facebook2_app.views.delete_post, name="delete_post"),
    path('<int:post_id>/submit_comment', facebook2_app.views.submit_comment, name="submit_comment"),
    path('like', facebook2_app.views.like, name="like"),
    path('dislike', facebook2_app.views.dislike, name="dislike"),
    path('like_comment', facebook2_app.views.like_comment, name="like_comment"),
    path('dislike_comment', facebook2_app.views.dislike_comment, name="dislike_comment"),
    path('s/', facebook2_app.views.search, name="search_results"),
    path('preferences/', TemplateView.as_view(template_name="preferences.html"), name="preferences"),
    path('notifications/', facebook2_app.views.notifications, name="notifications")
]
