from rest_framework import serializers

from .models import Author, Post

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
    
        