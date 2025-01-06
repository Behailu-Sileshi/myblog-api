from rest_framework import serializers

from .models import Post

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
        return Post.objects.create(owner=self.request.user, **validated_data)
    
        