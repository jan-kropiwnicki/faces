from django.shortcuts import render, get_object_or_404
from .models import Post, Person
from django.contrib.auth.models import User
from datetime import datetime
from django.http import HttpResponseRedirect
from django.urls import reverse


def index(request):
    post_list = []
    if request.user.is_authenticated:
        post_list_plain = request.user.person.post_set.order_by("-date")
        for post in post_list_plain:
            post_list += [[post, post.content.split("\r\n")]]
    return render(request, "index.html", {"post_list": post_list})


def submit_post(request):
    content = request.POST["content"]
    author = request.user.person
    date = datetime.now()
    likes = 0
    post = Post(content=content, author=author, date=date, likes=likes)
    post.save()
    return HttpResponseRedirect(reverse("index"))


def search_users(request):
    users = Person.objects.all()
    return render(request, "search-users.html", {"users": users})


def user(request, username):
    viewed_user = get_object_or_404(User, username=username)
    post_list = []
    post_list_plain = viewed_user.person.post_set.order_by("-date")
    for post in post_list_plain:
        post_list += [[post, post.content.split("\r\n")]]
    return render(request, "user.html", {"user": viewed_user, "post_list": post_list})
