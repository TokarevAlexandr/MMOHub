import django_filters

from .models import Post

class PostFilter(django_filters.FilterSet):
    title = django_filters.CharFilter(lookup_expr='icontains', label='Title')
    category = django_filters.ChoiceFilter(choices=Post.CATEGORY_CHOICES, label='Category')

    class Meta:
        model = Post
        fields = ['title', 'category']