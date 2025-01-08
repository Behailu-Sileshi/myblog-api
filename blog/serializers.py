from rest_framework import serializers
from .models import Author, Post
from django.contrib.auth import get_user_model


class SimpleAuthorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Author
        fields = ['id', 'user', 'image']
        read_only_fields = ['user', 'image']


class AuthorSerializer(serializers.ModelSerializer): 
    followers = SimpleAuthorSerializer(source='followed_by', many=True, read_only=True)
    following = SimpleAuthorSerializer(source='follows', many=True, read_only=True)

    class Meta:
        model = Author
        fields = ['id',
                  'user',
                  'bio',
                  'image',
                  'followers',
                  'following',
                  'follower_count',
                  'following_count',
                 ]
        read_only_fields = ['user',
                            'followers',
                            'following',
                            'follower_count',
                            'following_count'
                            ]
    
    
    
class PostSerializer(serializers.ModelSerializer):
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
                  'updated_at']
        read_only_fields = ['owner']
        
    def create(self, validated_data):
        author = Author.objects.get(user_id=self.context['user_id'])
        return Post.objects.create(owner=author, **validated_data)


    
        