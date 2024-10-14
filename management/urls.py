from django.urls import path
from .views import TeamViewSet, TaskViewSet

team_list = TeamViewSet.as_view({
    'post': 'create_team'
})

add_member, remove_member = TeamViewSet.as_view({
    'post': 'add_member'
}), TeamViewSet.as_view({
    'post': 'remove_member'
})

task_list = TaskViewSet.as_view({
    'get': 'get_tasks',
    'post': 'create_task'
})

task_detail = TaskViewSet.as_view({
    'get': 'retrieve_task',
    'patch': 'update_task_status',
    'delete': 'destroy_task'
})

task_comment = TaskViewSet.as_view({
    'get': 'get_comments',
    'post': 'add_comment'
})

urlpatterns = [
    path('team-list/', team_list, name='team-create'),
    path('add-member/', add_member, name='add-member'),
    path('remove-member/', remove_member, name='remove-member'),

    path('task-list/', task_list, name='tasks'),
    path('task-detail/', task_detail, name='task-detail'),
    path('task-comment/', task_comment, name='task')
]
