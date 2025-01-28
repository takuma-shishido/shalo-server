from django.db import models
from django.contrib.auth.models import AbstractUser

class CardData(models.Model):
    id = models.CharField(max_length=100, primary_key=True)
    rank = models.IntegerField(null=True, blank=True)
    title = models.CharField(max_length=255)
    author = models.CharField(max_length=255)
    tags = models.JSONField()
    description = models.TextField()
    previewImage = models.URLField()
    url = models.URLField()
    views = models.IntegerField(default=0)
    likes = models.IntegerField(null=True, blank=True)
    dateCreated = models.DateField()

class User(AbstractUser):
    id = models.CharField(max_length=100, primary_key=True)
    email = models.EmailField(unique=True)
    name = models.CharField(max_length=255)
    avatar = models.URLField(blank=True)
    joinDate = models.DateField()
    memberNumber = models.CharField(max_length=100)
    contributions = models.IntegerField()
    bookmarks = models.IntegerField()
    location = models.CharField(max_length=255, blank=True)
    website = models.URLField(null=True, blank=True)
    github = models.CharField(max_length=255, null=True, blank=True)
    twitter = models.CharField(max_length=255, null=True, blank=True)
    bio = models.TextField(null=True, blank=True)

    bookmarksCards = models.ManyToManyField(CardData, related_name='bookmarked_by', blank=True)

    groups = models.ManyToManyField(
        'auth.Group',
        related_name='api_user_set',
        blank=True,
        help_text='The groups this user belongs to. A user will get all permissions granted to each of their groups.',
        verbose_name='groups',
    )
    user_permissions = models.ManyToManyField(
        'auth.Permission',
        related_name='api_user_set',
        blank=True,
        help_text='Specific permissions for this user.',
        verbose_name='user permissions',
    )

    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = ['email', 'password']


class CardActivity(models.Model):
    id = models.CharField(max_length=100, primary_key=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    card = models.ForeignKey(CardData, on_delete=models.CASCADE)
    activityType = models.CharField(max_length=100)
    date = models.DateField()
    time = models.TimeField()