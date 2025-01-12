from rest_framework import serializers
from .models import Author, Comment, Post, PostImage, PostVideo





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
                  'joined_at'
                 ]
        read_only_fields = ['user',
                            'username',
                            'first_name',
                            'last_name',
                            'follower_count',
                            'following_count'
                           ]
    def update(self, instance, validated_data):
        if 'image' in validated_data:
            instance.image = validated_data.get('image', instance.image)
        instance.bio = validated_data.get('bio', instance.bio)
        instance.save()
        return instance
   

class ReplySerializer(serializers.ModelSerializer):
    created_at = serializers.SerializerMethodField(method_name='get_time')
    
    def get_time(self, comment):
        return comment.created_at.strftime("%Y-%m-%d %H:%M:%S")
    class Meta:
        model = Comment 
        fields = ['id', 'owner', 'body', 'created_at']

class CommentSerializer(serializers.ModelSerializer):
    replies = ReplySerializer(many=True, read_only=True)
    created_at = serializers.SerializerMethodField(method_name='get_time')
    
    def get_time(self, comment):
        return comment.created_at.strftime("%Y-%m-%d %H:%M:%S")
    class Meta:
        model = Comment
        fields = [
            'id',
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
  
class PostImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = PostImage
        fields = ['id', 'image', 'caption', 'upload_at'] 
    
    
    def create(self, validated_data):
        return PostImage.objects.create(post_id=self.context.get('post_id'), **validated_data)
    
class PostVideoSerializer(serializers.ModelSerializer):
    class Meta:
        model = PostVideo
        fields = ['id', 'video', 'caption', 'upload_at'] 
    
    def create(self, validated_data):
        return PostVideo.objects.create(post_id=self.context.get('post_id'), **validated_data)
    
    
class PostSerializer(serializers.ModelSerializer):
    
    comments_count = serializers.IntegerField(read_only=True)
    images_count = serializers.IntegerField(read_only=True)
    videos_count = serializers.IntegerField(read_only=True)
    
   
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
                  'comments_count',
                  'images_count',
                  'videos_count']
        read_only_fields = ['owner']
        
    def create(self, validated_data):
        author = Author.objects.get(user_id=self.context['user_id'])
        return Post.objects.create(owner=author, **validated_data)
