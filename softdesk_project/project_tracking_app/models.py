"""Models for project tracking application.
Models contain:
"""
from django.contrib.auth import get_user_model
from django.db import models

User = get_user_model()

class Project(models.Model):
    # objects = None
    title = models.CharField(max_length=128)
    description = models.TextField(max_length=2048, blank=True)
    project_type = models.CharField(max_length=32)  # type (back-end, front-end, iOS ou Android),
    users = models.ManyToManyField(User, through='Contributor', related_name='projects')

    def __str__(self):
        return f'Project title: {self.title}, type: {self.project_type}'


class Contributor(models.Model):

    ROLE_CHOICES = (
        ('AUTHOR', 'Author'),
        ('MANAGER', 'Manager'),
        ('CREATOR', 'Creator')
    )

    user = models.ForeignKey(User, related_name='contributors', on_delete=models.CASCADE)
    project = models.ForeignKey(Project, related_name='contributors', on_delete=models.CASCADE)

    permission = models.CharField(max_length=10, choices=ROLE_CHOICES)
    role = models.CharField(max_length=32) # What is this?

    class Meta:
        unique_together = ('user', 'project',)

    def __str__(self):
        return f'id = {self.id}, Contributor: user is {self.user}, project is {self.project}'


class Issue(models.Model):
    TAG_CHOICES = (
        ('BUG', 'Bug'),
        ('IMPROVEMENT', 'Improvement'),
        ('TASK', 'Task')
    )

    PRIORITY_CHOICES = (
        ('LOW', 'Low'),
        ('MEDIUM', 'Medium'),
        ('HIGH', 'High')
    )

    STATUS_CHOICES = (
        ('TODO', 'To Do'),
        ('IN_PR', 'In Progress'),
        ('COMPLETED', 'Completed')
    )

    title = models.CharField(max_length=128)
    description = models.CharField(max_length=256)
    tag = models.CharField(max_length=16, choices=TAG_CHOICES, blank=True)  # tag (BUG, IMPROVEMENT or TASK)
    priority = models.CharField(max_length=16, choices=PRIORITY_CHOICES, blank=True)  # priority (LOW, MEDIUM or HIGH)
    status = models.CharField(max_length=16, choices=STATUS_CHOICES, blank=True) # status (To do, In progress or Completed)
    author_user = models.ForeignKey(User, related_name='issues', on_delete=models.CASCADE)
    assignee_user = models.ForeignKey(User, related_name='assignee_issues', default=author_user, on_delete=models.CASCADE)
    project = models.ForeignKey(Project, related_name='issues', on_delete=models.CASCADE)  # ??? project_id : integer
    created_time = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'Issue: {self.title}, project is {self.project}, Author is {self.author_user}'


class Comment(models.Model):
    description = models.TextField(max_length=2048, blank=True)
    author_user = models.ForeignKey(User, related_name='comments', on_delete=models.CASCADE)
    issue = models.ForeignKey(Issue, related_name='comments', on_delete=models.CASCADE)

    def __str__(self):
        return f'Comment: {self.description} of issue {self.issue} by author {self.author_user}'

