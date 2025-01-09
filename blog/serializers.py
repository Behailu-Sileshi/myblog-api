from rest_framework import serializers
from .models import Author, Comment, Post
from django.contrib.auth import get_user_model


class SimpleAuthorSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source='user.username')
    class Meta:
        model = Author
        fields = ['id', 'user_id', 'username', 'image']
        read_only_fields = ['user', 'username', 'image']


class AuthorSerializer(serializers.ModelSerializer): 
    username = serializers.CharField(source='user.username')
    first_name = serializers.CharField(source='user.first_name')
    last_name = serializers.CharField(source='user.last_name')
    

    class Meta:
        model = Author
        fields = ['id',
                  'user_id',
                  'username',
                  'first_name',
                  'last_name',
                  'bio',
                  'image',
                  'follower_count',
                  'following_count',
                 ]
        read_only_fields = ['user',
                            'follower_count',
                            'following_count'
                           ]
   

class ReplySerializer(serializers.ModelSerializer):
    created_at = serializers.SerializerMethodField(method_name='get_time')
    
    def get_time(self, comment):
        return comment.created_at.strftime("%Y-%m-%d %H:%M:%S")
    class Meta:
        model = Comment 
        fields = ['id', 'owner', 'body', 'created_at']


class CommentSerializer(serializers.ModelSerializer):
    replies = ReplySerializer(many=True)
    created_at = serializers.SerializerMethodField(method_name='get_time')
    
    def get_time(self, comment):
        return comment.created_at.strftime("%Y-%m-%d %H:%M:%S")
    class Meta:
        model = Comment
        fields = [
            'owner',
            'post',
            'body',
            'created_at',
            'parent',
            'replies'
                 
        ]
        read_only_fields = ['post', 'owner']
        
    def create(self, validated_data):
        author = Author.objects.get(user_id=self.context['user_id'])
        return Comment.objects.create(owner=author, post_id=self.context['post_id'], **validated_data)
  
    
    
class PostSerializer(serializers.ModelSerializer):
    comments = CommentSerializer(many=True)
    class Meta:
        model = Post
        fields = ['id',
                  'title',
                  'slug',
                  'body',
                  'owner',
                  'status',
                  'published_date',
                  'created_at',
                  'updated_at',
                  'comments']
        read_only_fields = ['owner']
        
    def create(self, validated_data):
        author = Author.objects.get(user_id=self.context['user_id'])
        return Post.objects.create(owner=author, **validated_data)
