from django.shortcuts import render
from rest_framework.response import Response
from rest_framework import status
from .models import Feed,Comment
from rest_framework import generics
from .serializers import ProjectCreateSerializer,ProjectSerializer,FeedLikeUnlikeSerializer,CommentCreateSerializer,PostCreateSerializer,PostSerializer
from api.pagination import MyCustomPagination
from api.permissions import IsOwnerOrReadOnly
from rest_framework.permissions import IsAuthenticatedOrReadOnly,IsAuthenticated
from django.core.cache import cache
import hashlib  
from django.db import transaction

# Create your views here.
class UserProjectsListView(generics.ListAPIView):
    serializer_class = ProjectSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return Feed.objects.filter(user=self.request.user,project=True)

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        page = self.paginate_queryset(queryset)
        
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True,context={'request': request})
        return Response(serializer.data)


class ProjectListCreateView(generics.ListCreateAPIView):
    queryset = Feed.objects.filter(project=True)
    pagination_class = MyCustomPagination
    
    def get_serializer_class(self):
        if self.request.method == 'GET':
            return ProjectSerializer
        return ProjectCreateSerializer
    
    def create(self, request):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            instance = serializer.save(user=request.user,project=True)
            
            cache_key = f'feed_views_{instance.id}'
            cache.set(cache_key, 1)
            
            return Response({"message":"Your Project has been created successfully"},status=status.HTTP_201_CREATED)
        else:
            return Response({"message":"Error Uploading Your Project"}, status=status.HTTP_400_BAD_REQUEST)
        
    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        page = self.paginate_queryset(queryset)

        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True,context={'request': request})
        return Response(serializer.data)
    
    def get_queryset(self):
        queryset = self.queryset

        tag_id = self.request.query_params.get('community', None)

        if tag_id:
            queryset = queryset.filter(tag__id=tag_id)
            
        # if self.request.user.is_authenticated:
        #     queryset = queryset.exclude(user=self.request.user)
            
        return queryset
    
class ProjectRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Feed.objects.filter(project=True)
    permission_classes = [IsAuthenticatedOrReadOnly,IsOwnerOrReadOnly]
    
    def get_serializer_class(self):
        # Use ProjectCreateSerializer for create, update, and delete actions
        if self.request.method in ('POST', 'PUT', 'PATCH', 'DELETE'):
            return ProjectCreateSerializer
        return ProjectSerializer
    
    def update(self, request,*args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=True)
        if serializer.is_valid(raise_exception=True):
            instance = serializer.save()
            updated_instance = self.queryset.get(id=instance.id)
            serializer = ProjectSerializer(updated_instance)
            return Response(serializer.data,status=status.HTTP_200_OK)
        else:
            return Response({"message:An Error Occurred"})
        
    
    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        cache_key = f'feed_views_{instance.id}'

        
        views_count = cache.get(cache_key)

        if views_count is None:
            # View count not found in cache, fetch it from the database
            views_count = instance.views_count

            # Set the view count in cache for future requests
            cache.set(cache_key, views_count, 60 * 15)  # Cache for 15 minutes

        user_cache_key = None

        if request.user.is_authenticated:
            # Authenticated user: Use their user ID to distinguish views
            user_cache_key = f'user_view_{instance.id}_{request.user.id}'
        else:
            # Unauthenticated user: Use their IP address to distinguish views
            user_ip = hashlib.md5(request.META['REMOTE_ADDR'].encode()).hexdigest()
            user_cache_key = f'user_view_{instance.id}_{user_ip}'

        if not cache.get(user_cache_key):
            cache.set(user_cache_key, 1, 60 * 3)
            cache.incr(cache_key) 

            with transaction.atomic():
                instance.views_count += 1
                instance.save()

        return super().retrieve(request, *args, **kwargs)


class LikeUnlikeFeedView(generics.CreateAPIView):
    queryset = Feed.objects.all()
    serializer_class = FeedLikeUnlikeSerializer
    
    def create(self, request,*args, **kwargs):
        user = self.request.user
        # 
        serializer = self.serializer_class(data=request.data,context={'request': request})
        if serializer.is_valid():
            feed_id = serializer.validated_data["feed_id"]
        
            try:
                feed = Feed.objects.get(pk=feed_id)
            except Feed.DoesNotExist:
                return Response({"message": "Feed not found."}, status=status.HTTP_404_NOT_FOUND)
            
            if feed.likes.filter(id=user.id).exists():
                feed.likes.remove(user)
                feed.total_likes -= 1
            else:
                feed.likes.add(user)
                feed.total_likes += 1

            feed.save()

            serializer = PostSerializer(feed,context={'request': request})
            return Response(serializer.data, status=status.HTTP_200_OK)
        
        else:
            return Response({"message":"An Error Occurred"},status=status.HTTP_400_BAD_REQUEST)
        
    
class PostListCreateView(generics.ListCreateAPIView):
    queryset = Feed.objects.filter()
    pagination_class = MyCustomPagination
    
    def get_serializer_class(self):
        if self.request.method == 'GET':
            return PostSerializer
        return PostCreateSerializer
    
    def create(self, request):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            title = serializer.validated_data["description"][:30]
            instance = serializer.save(user=request.user,post=True,tag=request.user.community,title=title)
            
            cache_key = f'feed_views_{instance.id}'
            cache.set(cache_key, 1)
            
            return Response({"message":"Your Project has been created successfully"},status=status.HTTP_201_CREATED)
        else:
            return Response({"message":"Error Uploading Your Project"}, status=status.HTTP_400_BAD_REQUEST)
        
    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        page = self.paginate_queryset(queryset)

        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True,context={'request': request})
        return Response(serializer.data)
    
    def get_queryset(self):
        queryset = self.queryset
        # if self.request.user.is_authenticated:
        #     queryset = queryset.exclude(user=self.request.user)
            
        return queryset
        

class PostRetrieveDestroyView(generics.RetrieveDestroyAPIView):
    queryset = Feed.objects.filter()
    permission_classes = [IsAuthenticatedOrReadOnly,IsOwnerOrReadOnly]
    
    def get_serializer_class(self):
        # Use ProjectCreateSerializer for create, update, and delete actions
        if self.request.method in ('POST', 'PUT', 'PATCH', 'DELETE'):
            return PostCreateSerializer
        return PostSerializer
    
    # def update(self, request,*args, **kwargs):
    #     instance = self.get_object()
    #     serializer = self.get_serializer(instance, data=request.data, partial=True)
    #     if serializer.is_valid(raise_exception=True):
    #         instance = serializer.save()
    #         updated_instance = self.queryset.get(id=instance.id)
    #         serializer = ProjectSerializer(updated_instance)
    #         return Response(serializer.data,status=status.HTTP_200_OK)
    #     else:
    #         return Response({"message:An Error Occurred"})
        
    
    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        cache_key = f'feed_views_{instance.id}'

        
        views_count = cache.get(cache_key)

        if views_count is None:
            views_count = instance.views_count

            # Set the view count in cache for future requests
            cache.set(cache_key, views_count, 60 * 15)  # Cache for 15 minutes

        user_cache_key = None

        if request.user.is_authenticated:
            # Authenticated user: Use their user ID to distinguish views
            user_cache_key = f'user_view_{instance.id}_{request.user.id}'
        else:
            # Unauthenticated user: Use their IP address to distinguish views
            user_ip = hashlib.md5(request.META['REMOTE_ADDR'].encode()).hexdigest()
            user_cache_key = f'user_view_{instance.id}_{user_ip}'

        if not cache.get(user_cache_key):
            cache.set(user_cache_key, 1, 60 * 3)
            cache.incr(cache_key) 

            with transaction.atomic():
                instance.views_count += 1
                instance.save()

        return super().retrieve(request, *args, **kwargs)
    
class CommentCreateView(generics.CreateAPIView):
    queryset = Comment.objects.all()
    serializer_class = CommentCreateSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
    