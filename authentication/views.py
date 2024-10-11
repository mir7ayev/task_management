from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import ViewSet
from django.contrib.auth import get_user_model

User = get_user_model()


class AuthenticationViewSet(ViewSet):
    # permission_classes = (IsAuthenticated,)

    def register(self, request):
        username = request.data.get('username')
        if username is None:
            return Response('Username is required', status=status.HTTP_404_NOT_FOUND)

        password = request.data.get('password')
        if password is None:
            return Response('Password is required', status=status.HTTP_404_NOT_FOUND)

        if User.objects.filter(username=username).exists():
            return Response('User already exists', status=status.HTTP_400_BAD_REQUEST)

        user = User.objects.create_user(username=username, password=password)

        return Response('User created', status=status.HTTP_201_CREATED)
