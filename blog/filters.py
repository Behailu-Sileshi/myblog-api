from django_filters.filterset import FilterSet

from .models import Post


class PostFilter(FilterSet):
    class Meta:
        model = Post
        fields = {
            'published_date': ['gte', 'lte'],
            'status': ['exact']
        }