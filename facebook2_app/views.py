from django.shortcuts import render, get_object_or_404
from .models import Post
from django.contrib.auth.models import User
from datetime import datetime
from django.http import HttpResponseRedirect, JsonResponse
from django.urls import reverse
from .forms import RegisterForm


def index(request):
    post_list = []
    friend_requests = []
    if request.user.is_authenticated:
        post_list_plain = []
        for friend in request.user.person.friends.all():
            post_list_plain += list(friend.post_set.all())
        post_list_plain.sort(key=lambda x: x.date, reverse=True)
        for post in post_list_plain:
            post_list += [[post, post.content.split("\r\n"), len(post.likeprofile_set.all())]]
        friend_requests = request.user.requestprofile.friend_requests.all()
    return render(request, "index.html", {
        "post_list": post_list, "friend_requests": friend_requests, "friend_requests_len": len(friend_requests)
    })


def submit_post(request):
    content = request.POST["content"]
    author = request.user.person
    date = datetime.now()
    post = Post(content=content, author=author, date=date)
    post.save()
    post.likeprofile_set.add(request.user.likeprofile)
    post.save()
    return HttpResponseRedirect(reverse("index"))


def search(request):
    original_query = request.GET.get("q")
    query = original_query.lower()
    users = User.objects.all()
    direct_username_matches = []
    direct_full_name_matches = []
    direct_last_name_matches = []
    direct_first_name_matches = []
    first_name_matches = []
    last_name_matches = []
    full_name_matches = []
    username_matches = []
    for user in users:
        if query == user.username.lower():
            direct_username_matches += [user]
        elif query == (user.first_name + ' ' + user.last_name).lower():
            direct_full_name_matches += [user]
        elif query == user.last_name.lower():
            direct_last_name_matches += [user]
        elif query == user.first_name.lower():
            direct_first_name_matches += [user]
        elif query in user.first_name.lower():
            first_name_matches += [user]
        elif query in user.last_name.lower():
            last_name_matches += [user]
        elif query in (user.first_name + ' ' + user.last_name).lower():
            full_name_matches += [user]
        elif query in user.username.lower():
            username_matches += [user]
    result = direct_username_matches + direct_full_name_matches + direct_last_name_matches + \
             direct_first_name_matches + first_name_matches + last_name_matches + full_name_matches + \
             username_matches
    return render(request, "search-results.html", {"result": result, "query": original_query})


def user(request, username):
    viewed_user = get_object_or_404(User, username=username)
    post_list = []
    post_list_plain = viewed_user.person.post_set.order_by("-date")
    for post in post_list_plain:
        post_list += [[post, post.content.split("\r\n"), len(post.likeprofile_set.all())]]
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


def friend_list(request):
    return render(request, "friend-list.html", {"friend_count": len(request.user.person.friends.all())})


def like(request):
    post_id = request.GET.get("id")
    post = get_object_or_404(Post, id=post_id)
    if request.user.likeprofile not in post.likeprofile_set.all():
        post.likeprofile_set.add(request.user.likeprofile)
    return JsonResponse({"new_likes": len(post.likeprofile_set.all())})


def dislike(request):
    post_id = request.GET.get("id")
    post = get_object_or_404(Post, id=post_id)
    if request.user.likeprofile in post.likeprofile_set.all():
        post.likeprofile_set.remove(request.user.likeprofile)
    return JsonResponse({"new_likes": len(post.likeprofile_set.all())})


def register(request):
    if request.method == 'GET':
        form = RegisterForm()
        return render(request, "registration/register.html", {"form": form})
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.username = user.username.lower()
            user.save()
            return HttpResponseRedirect(reverse("index"))
        else:
            return render(request, 'registration/register.html', {'form': form})
