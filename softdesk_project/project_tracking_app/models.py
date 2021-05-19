"""Models for project tracking application.
Models contain:
"""

from django.db import models
from django.utils import timezone
from django.conf import settings  # To use User = settings.AUTH_USER_MODEL
from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()


class Project(models.Model):
    title = models.CharField(max_length=128)
    description = models.TextField(max_length=2048, blank=True)
    project_type = models.CharField(max_length=32)
    users = models.ManyToManyField(User, through='Contributor')

    def __str__(self):
        return f'Project title: {self.title}, type: {self.project_type}'


class Contributor(models.Model):
    # These fields tie to the roles!
    AUTHOR = 1
    MANAGER = 2
    CREATOR = 3

    ROLE_CHOICES = (
        (AUTHOR, 'Author'),
        (MANAGER, 'Manager'),
        (CREATOR, 'Creator')
    )

    user = models.ForeignKey(User, related_name='contributors', on_delete=models.CASCADE)
    project = models.ForeignKey(Project, related_name='contributors', on_delete=models.CASCADE)
    permission = models.PositiveSmallIntegerField(choices=ROLE_CHOICES, blank=True, null=True, default=AUTHOR)
    role = models.CharField(max_length=32) # What is this?

    def __str__(self):
        return f'Contributor: user is {self.user}, project is {self.project}'


class Issue(models.Model):
    title = models.CharField(max_length=128)
    description = models.CharField(max_length=256)
    tag = models.CharField(max_length=32)
    priority = models.CharField(max_length=32)
    status = models.CharField(max_length=32)
    author_user = models.ForeignKey(User, related_name='issues', on_delete=models.CASCADE)
    assignee_user = models.ForeignKey(User, related_name='issues', on_delete=models.CASCADE)   # ???
    project = models.ForeignKey(Project, related_name='issues', on_delete=models.CASCADE)  # ??? project_id : integer
    created_time = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'Issue: {self.title}, project is {self.project}'


class Comment(models.Model):
    description = models.TextField(max_length=2048, blank=True)
    author_user = models.ForeignKey(User, related_name='comments', on_delete=models.CASCADE)
    issue = models.ForeignKey(Issue, related_name='comments', on_delete=models.CASCADE)

    def __str__(self):
        return f'Comment: {self.description} of issue {self.issue}'

