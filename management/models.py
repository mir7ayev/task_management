from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()

STATUS_CHOICES = [
    ('todo', 'To Do'),
    ('in_progress', 'In Progress'),
    ('done', 'Done'),
]


class Team(models.Model):
    name = models.CharField(max_length=100)
    owner = models.ForeignKey(User, related_name='owned_teams', on_delete=models.CASCADE)
    members = models.ManyToManyField(User, related_name='teams')

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name


class Task(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES)
    deadline = models.DateTimeField()
    team = models.ForeignKey(Team, related_name='tasks', on_delete=models.CASCADE)
    assignee = models.ForeignKey(User, related_name='assigned_tasks', on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title


class Comment(models.Model):
    task = models.ForeignKey(Task, related_name='comments', on_delete=models.CASCADE)
    author = models.ForeignKey(User, related_name='comments', on_delete=models.CASCADE)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Comment by {self.author} on {self.task}"
