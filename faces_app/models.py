from django.contrib.auth.models import User
from django.db import models
from django.dispatch import receiver
from django.db.models.signals import post_save
import random


class Person(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    friends = models.ManyToManyField("self")
    notifications = models.JSONField()
    unread = models.PositiveIntegerField()
    bio = models.TextField(max_length=300, default="")

    # post visibility
    POST_VIS_FRIENDS = '0'
    POST_VIS_FRIENDS_FRIENDS = '1'
    POST_VIS_EVERYONE = '2'
    POST_VIS_CHOICES = [
        (POST_VIS_FRIENDS, "Friends"),
        (POST_VIS_FRIENDS_FRIENDS, "Friends' friends"),
        (POST_VIS_EVERYONE, "Everyone"),
    ]
    post_vis = models.PositiveIntegerField(
        choices=POST_VIS_CHOICES,
        default=POST_VIS_FRIENDS
    )


class RequestProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    friend_requests = models.ManyToManyField(Person)


class ProfilePicture(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    url = models.URLField()


@receiver(post_save, sender=User)
def user_is_created(sender, instance, created, **kwargs):
    if created:
        Person.objects.create(user=instance, notifications=[], unread=0)
        RequestProfile.objects.create(user=instance)
        LikeProfile.objects.create(user=instance)
        ProfilePicture.objects.create(
            user=instance, url='img/profiles/' + ['blue.png', 'green.png', 'red.png', 'yellow.png', 'violet.png'][random.randrange(5)]
        )
    else:
        instance.person.save()


class Post(models.Model):
    content = models.TextField()
    author = models.ForeignKey(Person, on_delete=models.CASCADE)
    date = models.DateTimeField()
    image = models.CharField(max_length=512, default="")


class Comment(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE)
    author = models.ForeignKey(Person, on_delete=models.CASCADE)
    content = models.TextField()
    date = models.DateTimeField()


class LikeProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    liked_posts = models.ManyToManyField(Post)
    liked_comments = models.ManyToManyField(Comment)
