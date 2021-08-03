from rest_framework import generics
from rest_framework.permissions import IsAuthenticated

from .models import Post
from .permissions import (
    IsOwnerOrReadOnly,
    IsNotOwnerAndAuthenticatedOrReadOnly,
)
from .serializers import (
    PostSerializer,
    LikeSerializer,
)


class PostList(generics.ListCreateAPIView):
    queryset = Post.objects.all()
    permission_classes = [IsAuthenticated]
    serializer_class = PostSerializer

    def perform_create(self, serializer):
        user = self.request.user
        serializer.save(owner=user)


class PostDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = Post.objects.all()
    permission_classes = [IsOwnerOrReadOnly]
    serializer_class = PostSerializer


class LikeUpdate(generics.UpdateAPIView):
    queryset = Post.objects.all()
    permission_classes = [IsNotOwnerAndAuthenticatedOrReadOnly]
    serializer_class = LikeSerializer

    def perform_update(self, serializer):
        user = self.request.user
        post = Post.objects.get(pk=self.kwargs.get('pk'))
        post.likes.add(user)


class UnLikeUpdate(generics.UpdateAPIView):
    queryset = Post.objects.all()
    permission_classes = [IsNotOwnerAndAuthenticatedOrReadOnly]
    serializer_class = LikeSerializer

    def perform_update(self, serializer, *args, **kwargs):
        user = self.request.user
        post = Post.objects.get(pk=self.kwargs.get('pk'))
        post.likes.remove(user)
