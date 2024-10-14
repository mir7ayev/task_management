from django.contrib import admin
from .models import Team, Task, Comment


@admin.register(Team)
class TeamAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'owner', 'created_at')
    list_display_links = ('id', 'name', 'owner')
    list_filter = ('id', 'name', 'owner', 'created_at')


@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    list_display = ('id', 'title', 'status', 'team', 'assignee', 'deadline')
    list_display_links = ('id', 'title', 'status')
    list_filter = ('id', 'title', 'status', 'team', 'assignee', 'deadline')


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ('id', 'task', 'author', 'created_at')
    list_display_links = ('id', 'task', 'author')
    list_filter = ('id', 'task', 'author', 'created_at')
