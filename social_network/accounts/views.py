from rest_framework import (
    generics,
    status,
)
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

import accounts.data_enrichment
from .user_serializer import UserSerializer
from .models import User


class Account(APIView):
    def post(self, request):
        username = request.data['username']
        email = request.data['email']
        password = request.data['password']
        user_serializer = UserSerializer(data=request.data)

        if accounts.data_enrichment.is_valid_email(email):
            if user_serializer.is_valid():
                ip = request.META['REMOTE_ADDR']
                user = User.objects.create_user(username, email, password, ip=ip)
                return Response({'id': user.id, 'username': user.username, 'email': user.email},
                                status=status.HTTP_201_CREATED)
            return Response(user_serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response({'error': 'The email format is not valid'},
                            status=status.HTTP_400_BAD_REQUEST)


class UserData(generics.RetrieveAPIView):
    queryset = User.objects.all()
    permission_classes = [IsAuthenticated]
    serializer_class = UserSerializer
