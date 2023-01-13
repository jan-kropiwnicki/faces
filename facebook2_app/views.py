from django.shortcuts import render, get_object_or_404
from .models import Post, Person
from django.contrib.auth.models import User
from datetime import datetime
from django.http import HttpResponseRedirect
from django.urls import reverse


def index(request):
    post_list = []
    friend_requests = []
    if request.user.is_authenticated:
        post_list_plain = []
        for friend in request.user.person.friends.all():
            post_list_plain += list(friend.post_set.all())
        post_list_plain.sort(key=lambda x: x.date, reverse=True)
        for post in post_list_plain:
            post_list += [[post, post.content.split("\r\n")]]
        friend_requests = request.user.requestprofile.friend_requests.all()
    return render(request, "index.html", {
        "post_list": post_list, "friend_requests": friend_requests, "friend_requests_len": len(friend_requests)
    })


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
    return render(request, "user.html", {"viewed_user": viewed_user, "post_list": post_list})


def send_request(request, username):
    get_object_or_404(User, username=username).requestprofile.friend_requests.add(request.user.person)
    return HttpResponseRedirect(reverse("user", args=[username]))


def accept_request(request, username):
    accepted_user = get_object_or_404(User, username=username)
    if accepted_user.person in request.user.requestprofile.friend_requests.all():
        request.user.person.friends.add(accepted_user.person)
    for person in request.user.requestprofile.friend_requests.all():
        if person.user.username == username:
            request.user.requestprofile.friend_requests.remove(person)
            break
    return HttpResponseRedirect(reverse("index"))


def reject_request(request, username):
    for person in request.user.requestprofile.friend_requests.all():
        if person.user.username == username:
            request.user.requestprofile.friend_requests.remove(person)
            break
    return HttpResponseRedirect(reverse("index"))


def end_friendship(request, username):
    for person in request.user.person.friends.all():
        if person.user.username == username:
            request.user.person.friends.remove(person)
            break
    return HttpResponseRedirect(reverse("user", args=[username]))


def edit_post(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    if post.author.user == request.user:
        return render(request, "edit-post.html", {"post": post})
    return HttpResponseRedirect(reverse("user", args=[request.user.username]))


def submit_edited_post(request, post_id):
    content = request.POST["content"]
    post = get_object_or_404(Post, id=post_id)
    if post.author.user == request.user:
        post.content = content
        post.save()
    return HttpResponseRedirect(reverse("user", args=[request.user.username]))


def delete_post(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    if post.author.user == request.user:
        post.delete()
    return HttpResponseRedirect(reverse("user", args=[request.user.username]))
