from django.contrib.auth.models import User
from django.db import models
from django.dispatch import receiver
from django.db.models.signals import post_save


class Person(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    friends = models.ManyToManyField("self")


class RequestProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    friend_requests = models.ManyToManyField(Person)


@receiver(post_save, sender=User)
def user_is_created(sender, instance, created, **kwargs):
    if created:
        Person.objects.create(user=instance)
        RequestProfile.objects.create(user=instance)
        LikeProfile.objects.create(user=instance)
    else:
        instance.person.save()


class Post(models.Model):
    content = models.TextField()
    author = models.ForeignKey(Person, on_delete=models.CASCADE)
    date = models.DateTimeField()


class LikeProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    liked_posts = models.ManyToManyField(Post)
