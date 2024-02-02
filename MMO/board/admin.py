from django.contrib import admin
from .models import Post, CustomUser, Reply

admin.site.register(Post)
admin.site.register(CustomUser)  # Change "Author" to "CustomUser"
admin.site.register(Reply)
# admin.site.register(Category)