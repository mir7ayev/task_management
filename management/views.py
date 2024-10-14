from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from .models import Team, Task, Comment
from .serializers import (
    TeamSerializer, TaskSerializer, CommentSerializer,
)
from django.shortcuts import get_object_or_404

from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from .tasks import check_deadline_and_notify
from django.utils import timezone


class TeamViewSet(viewsets.ModelViewSet):
    queryset = Team.objects.all()

    # permission_classes = (IsAuthenticated,)

    @swagger_auto_schema(
        operation_description="Create a new team",
        request_body=TeamSerializer,
        responses={
            201: TeamSerializer,
            400: "Bad Request"
        },
        tags=['Team List']
    )
    @action(detail=True, methods=['post'])
    def create_team(self, request):
        serializer = TeamSerializer(data=request.data)
        if serializer.is_valid():
            team = serializer.save(owner=request.user)
            team.members.add(request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @swagger_auto_schema(
        method='post',
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'member_id': openapi.Schema(type=openapi.TYPE_INTEGER),
                'team_id': openapi.Schema(type=openapi.TYPE_INTEGER),
            },
            required=['member_id', 'team_id'],
        ),
        responses={200: 'Member added successfully.', 400: 'Member ID is required.'},
        tags=['Team Members']
    )
    @action(detail=True, methods=['post'])
    def add_member(self, request):
        member_id = request.data.get('member_id')
        if not member_id:
            return Response({'detail': 'Member ID is required.'}, status=status.HTTP_400_BAD_REQUEST)

        team_id = request.data.get('team_id')
        team = get_object_or_404(Team, pk=team_id)

        team.members.add(member_id)
        return Response({'detail': 'Member added successfully.'}, status=status.HTTP_200_OK)

    @swagger_auto_schema(
        method='post',
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'member_id': openapi.Schema(type=openapi.TYPE_INTEGER),
                'team_id': openapi.Schema(type=openapi.TYPE_INTEGER),
            },
            required=['member_id', 'team_id'],
        ),
        responses={200: 'Member removed successfully.', 400: 'Member ID is required.'},
        tags=['Team Members']
    )
    @action(detail=True, methods=['post'])
    def remove_member(self, request):
        member_id = request.data.get('member_id')
        if not member_id:
            return Response({'detail': 'Member ID is required.'}, status=status.HTTP_400_BAD_REQUEST)

        team_id = request.data.get('team_id')
        team = get_object_or_404(Team, pk=team_id)

        if member_id == team.owner.id:
            return Response({'Can not remove owner'}, status=status.HTTP_400_BAD_REQUEST)

        team.members.remove(member_id)
        return Response({'detail': 'Member removed successfully.'}, status=status.HTTP_200_OK)


class TaskViewSet(viewsets.ModelViewSet):
    # permission_classes = (IsAuthenticated,)

    serializer_class = TaskSerializer  # Add the serializer_class here

    @swagger_auto_schema(request_body=TaskSerializer, responses={201: TaskSerializer()}, tags=['Task List'])
    def create_task(self, request):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            task = serializer.save()
            if task.deadline:
                check_deadline_and_notify.delay(task.id, task.deadline)

            return Response(serializer.data, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @swagger_auto_schema(responses={200: TaskSerializer(many=True)}, tags=['Task List'])
    def get_tasks(self, request):
        tasks = Task.objects.all()
        serializer = self.serializer_class(tasks, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @swagger_auto_schema(
        manual_parameters=[
            openapi.Parameter('task_id', openapi.IN_QUERY, description="Task ID", type=openapi.TYPE_INTEGER)
        ],
        responses={200: TaskSerializer()},
        tags=['Task Detail']
    )
    def retrieve_task(self, request):
        task_id = request.query_params.get('task_id')
        if not task_id:
            return Response({'error': 'Task ID is required.'}, status=status.HTTP_400_BAD_REQUEST)

        task = get_object_or_404(Task, id=task_id)
        serializer = self.serializer_class(task)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @swagger_auto_schema(
        manual_parameters=[
            openapi.Parameter('task_id', openapi.IN_QUERY, description="Task ID", type=openapi.TYPE_INTEGER)
        ],
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'status': openapi.Schema(type=openapi.TYPE_STRING, description='New status', example='completed')
            }
        ),
        responses={200: 'Task status updated successfully'},
        tags=['Task Detail']
    )
    def update_task_status(self, request):
        task_id = request.query_params.get('task_id')
        if not task_id:
            return Response({'error': 'Task ID is required.'}, status=status.HTTP_400_BAD_REQUEST)

        task = get_object_or_404(Task, id=task_id)
        new_status = request.data.get('status')

        if not new_status:
            return Response({'error': 'Status is required.'}, status=status.HTTP_400_BAD_REQUEST)

        if new_status not in ['todo', 'in_progress', 'done']:
            return Response({'error': 'Invalid status'}, status=status.HTTP_400_BAD_REQUEST)

        task.status = new_status
        task.save(update_fields=['status'])

        return Response({'message': 'Task status updated successfully'}, status=status.HTTP_200_OK)

    @swagger_auto_schema(
        manual_parameters=[
            openapi.Parameter('task_id', openapi.IN_QUERY, description="Task ID", type=openapi.TYPE_INTEGER)
        ],
        responses={204: 'Task deleted successfully'},
        tags=['Task Detail']
    )
    def destroy_task(self, request):
        task_id = request.query_params.get('task_id')
        if not task_id:
            return Response({'error': 'Task ID is required.'}, status=status.HTTP_400_BAD_REQUEST)

        task = get_object_or_404(Task, id=task_id)
        task.delete()
        return Response({'message': 'Task deleted successfully'}, status=status.HTTP_204_NO_CONTENT)

    @swagger_auto_schema(
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'task_id': openapi.Schema(type=openapi.TYPE_INTEGER, description='Task ID'),
                'comment': openapi.Schema(type=openapi.TYPE_STRING, description='Comment text'),
            },
            required=['task_id', 'comment']
        ),
        responses={201: 'Comment added successfully'},
        tags=['Task Comments']
    )
    def add_comment(self, request):
        task_id = request.data.get('task_id')
        if not task_id:
            return Response({'error': 'Task ID is required.'}, status=status.HTTP_400_BAD_REQUEST)

        task = get_object_or_404(Task, id=task_id)
        comment_text = request.data.get('comment')
        if not comment_text:
            return Response({'error': 'Comment text is required.'}, status=status.HTTP_400_BAD_REQUEST)

        comment = Comment.objects.create(task=task, content=comment_text, author=request.user)
        return Response({'message': 'Comment added successfully'}, status=status.HTTP_201_CREATED)

    @swagger_auto_schema(
        manual_parameters=[
            openapi.Parameter('task_id', openapi.IN_QUERY, description="Task ID", type=openapi.TYPE_INTEGER)
        ],
        responses={200: CommentSerializer(many=True)},
        tags=['Task Comments']
    )
    def get_comments(self, request):
        task_id = request.query_params.get('task_id')
        if not task_id:
            return Response({'error': 'Task ID is required.'}, status=status.HTTP_400_BAD_REQUEST)

        task = get_object_or_404(Task, id=task_id)
        comments = task.comments.all()  # Assuming a related_name='comments' on the Comment model
        serializer = CommentSerializer(comments, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
