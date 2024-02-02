from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import Group
from .models import Post, CustomUser

@receiver(post_save, sender=Post)
def add_author_to_group(sender, instance, created, **kwargs):
    if created:
        author = instance.author
        author_group, created = Group.objects.get_or_create(name='authors')  # Use get_or_create to ensure the group exists
        author_group.user_set.add(author)