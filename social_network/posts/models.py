from django.db import models

from accounts.models import User


# Create your models here.
class Post(models.Model):
    title = models.CharField(max_length=400)
    body = models.TextField()
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='post_owner')
    likes = models.ManyToManyField(User, related_name='post_likes')

    def __str__(self):
        return f'{self.owner}- {self.title}'
