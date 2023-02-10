from django.shortcuts import render, get_object_or_404
from .models import Post, Comment, Person
from django.contrib.auth.models import User
from datetime import datetime
from django.http import HttpResponseRedirect, JsonResponse
from django.urls import reverse
from .forms import RegisterForm
from django.templatetags.static import static
from django.core.validators import URLValidator
from django.core.exceptions import ValidationError
import requests


def index(request):
    post_list = []
    friend_requests = []
    new_people_you_may_know = []
    if request.user.is_authenticated:
        post_list_plain = []
        for friend in request.user.person.friends.all():
            post_list_plain += list(friend.post_set.all())
        post_list_plain.sort(key=lambda x: x.date, reverse=True)
        for post in post_list_plain:
            post_list += [[post, post.content.split("\r\n"), len(post.likeprofile_set.all()),
                           len(post.comment_set.all())]]
        friend_requests = request.user.requestprofile.friend_requests.all()
        people_you_may_know = []
        for friend in request.user.person.friends.all():
            people_you_may_know += friend.friends.all()
        for person in people_you_may_know:
            if person != request.user.person and person not in request.user.person.friends.all():
                mutual_friends = 0
                for friend in request.user.person.friends.all():
                    if friend in person.friends.all():
                        mutual_friends += 1
                new_people_you_may_know += [{"object": person, "mutual_friends": mutual_friends}]
        new_people_you_may_know.sort(key=lambda x: x["mutual_friends"], reverse=True)
    return render(request, "index.html", {
        "post_list": post_list, "friend_requests": friend_requests, "friend_requests_len": len(friend_requests),
        "people_you_may_know": new_people_you_may_know
    })


def submit_post(request):
    content = request.POST["content"]
    author = request.user.person
    date = datetime.now()
    image = request.POST["image"]
    if image != '':
        val = URLValidator()
        try:
            val(image)
        except ValidationError:
            # TODO: add a danger message "The image URL is not a valid URL!"
            return HttpResponseRedirect(reverse("index"))
        else:
            image_response = requests.head(image)
            if image_response.headers.get("content-type")[:5] != "image":
                # TODO: add a danger message "The image URL is not a valid image!"
                return HttpResponseRedirect(reverse("index"))
    post = Post(content=content, author=author, date=date, image=image)
    post.save()
    post.likeprofile_set.add(request.user.likeprofile)
    post.save()
    for friend in request.user.person.friends.all():
        friend.notifications += [
            {"type": "new_post", "user": {
                "first_name": request.user.first_name, "last_name": request.user.last_name,
                "username": request.user.username, "url": reverse("user", args=[request.user.username]),
                "profile_picture": static(request.user.profilepicture.url)
            }, "id": post.id, "see_more": reverse("post_page", args=[post.id]), "date": str(datetime.now().date())}
        ]
        friend.unread += 1
        friend.save()
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
        post_list += [[post, post.content.split("\r\n"), len(post.likeprofile_set.all()), len(post.comment_set.all())]]
    mutual_friends = []
    viewed_user_friends = viewed_user.person.friends.all()
    for friend in request.user.person.friends.all():
        if friend in viewed_user_friends:
            mutual_friends += [friend]
    return render(request, "user.html", {"viewed_user": viewed_user, "post_list": post_list, "mutual_friends":
                  mutual_friends, "mutual_friend_count": len(mutual_friends)})


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
    accepted_user.person.notifications += [{
        "type": "accept_request",
        "user": {
            "first_name": request.user.first_name, "last_name": request.user.last_name,
            "username": request.user.username, "url": reverse("user", args=[request.user.username]),
            "profile_picture": static(request.user.profilepicture.url)
        },
        "date": str(datetime.now().date())
    }]
    accepted_user.person.unread += 1
    accepted_user.person.save()
    return HttpResponseRedirect(reverse("index"))


def reject_request(request, username):
    for person in request.user.requestprofile.friend_requests.all():
        if person.user.username == username:
            request.user.requestprofile.friend_requests.remove(person)
            person.notifications += [{
                "type": "reject_request",
                "user": {
                    "first_name": request.user.first_name, "last_name": request.user.last_name,
                    "username": request.user.username, "url": reverse("user", args=[request.user.username]),
                    "profile_picture": static(request.user.profilepicture.url)
                },
                "date": str(datetime.now().date())}]
            person.unread += 1
            person.save()
            break
    return HttpResponseRedirect(reverse("index"))


def end_friendship(request, username):
    for person in request.user.person.friends.all():
        if person.user.username == username:
            request.user.person.friends.remove(person)
            person.notifications += [{
                "type": "end_friendship",
                "user": {
                    "first_name": request.user.first_name, "last_name": request.user.last_name,
                    "username": request.user.username, "url": reverse("user", args=[request.user.username]),
                    "profile_picture": static(request.user.profilepicture.url)
                },
                "date": str(datetime.now().date())
            }]
            person.unread += 1
            person.save()
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


def post_page(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    return render(request, 'post-page.html', {"post": post, "post_content": post.content.split("\r\n"), "like_count":
                  len(post.likeprofile_set.all()), "comment_count": len(post.comment_set.all()),
                                              "comments": [{"object": x, "like_count": len(x.likeprofile_set.all())}
                                                           for x in post.comment_set.all()]})


def submit_comment(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    content = request.POST["comment"]
    author = request.user.person
    date = datetime.now()
    comment = Comment(post=post, content=content, author=author, date=date)
    comment.save()
    comment.likeprofile_set.add(request.user.likeprofile)
    comment.save()
    post.author.notifications += [{
        "type": "new_comment",
        "user": {
            "first_name": request.user.first_name, "last_name": request.user.last_name,
            "username": request.user.username, "url": reverse("user", args=[request.user.username]),
            "profile_picture": static(request.user.profilepicture.url)
        },
        "id": post_id, "see_more": reverse("post_page", args=[post_id]), "date": str(datetime.now().date())}]
    post.author.unread += 1
    post.author.save()
    return HttpResponseRedirect(reverse("post_page", args=[post_id]))


def like_comment(request):
    comment_id = request.GET.get("id")
    comment = get_object_or_404(Comment, id=comment_id)
    if request.user.is_authenticated:
        comment.likeprofile_set.add(request.user.likeprofile)
    return JsonResponse({"new_likes": len(comment.likeprofile_set.all())})


def dislike_comment(request):
    comment_id = request.GET.get("id")
    comment = get_object_or_404(Comment, id=comment_id)
    if request.user.is_authenticated:
        comment.likeprofile_set.remove(request.user.likeprofile)
    return JsonResponse({"new_likes": len(comment.likeprofile_set.all())})


def e404(request):
    return render(request, '404.html', {})


def notifications(request):
    p = request.user.person
    p.unread = 0
    p.save()
    return render(request, "notifications.html", {"notifications": request.user.person.notifications[::-1]})


def preferences(request):
    return render(request, "preferences.html", {})


def change_profile_picture(request):
    color = request.POST["color"]
    profile_picture = request.user.profilepicture
    profile_picture.url = f"img/profiles/{color}.png"
    profile_picture.save()
    return HttpResponseRedirect(reverse("preferences"))


def change_post_visibility(request):
    choice = request.POST["post_vis"]
    person = request.user.person
    if choice == "friends":
        person.post_vis = Person.POST_VIS_FRIENDS
    elif choice == "friends-friends":
        person.post_vis = Person.POST_VIS_FRIENDS_FRIENDS
    elif choice == "everyone":
        person.post_vis = Person.POST_VIS_EVERYONE
    person.save()
    return HttpResponseRedirect(reverse("preferences"))


def get_notification(request):
    p = request.user.person
    if p.unread:
        p.unread = 0
        p.save()
        return JsonResponse({"notification": p.notifications[-1]})
    return JsonResponse({"notification": False})


def edit_bio(request):
    bio = request.POST["bio"]
    p = request.user.person
    p.bio = bio
    p.save()
    return HttpResponseRedirect(reverse("user", args=[request.user.username]))
