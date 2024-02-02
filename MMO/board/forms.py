from django import forms
from .models import Post, Reply

class PostForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        category_choices = kwargs.pop('category_choices', None)
        super().__init__(*args, **kwargs)
        if category_choices:
            self.fields['category'].queryset = category_choices


    image = forms.ImageField(required=False)
    video_url = forms.URLField(required=False)

    class Meta:
        model = Post
        fields = ['category', 'title', 'post_text', 'image', 'video_url']

class ReplyForm(forms.ModelForm):
    class Meta:
        model = Reply
        fields = ['reply_text']