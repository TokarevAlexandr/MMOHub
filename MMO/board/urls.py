from django.urls import path
from .views import PostList, PostDetail, PostCreate, PostUpdate, PostDelete, ReplyCreate
from . import views

urlpatterns = [
    path('', PostList.as_view(), name='posts'),
    path('<int:pk>/', PostDetail.as_view(), name='post_detail'),
    path('create/', PostCreate.as_view(), name='post_create'),
    path('<int:pk>/update/', PostUpdate.as_view(), name='post_update'),
    path('<int:pk>/delete/', PostDelete.as_view(), name='post_delete'),
    path('<int:pk>/create_reply/', ReplyCreate.as_view(), name='create_reply'),
    path('private_replies/', views.private_replies, name='private_replies'),
    path('delete_reply/<int:pk>/', views.delete_reply, name='delete_reply'),
    path('accept_reply/<int:pk>/', views.accept_reply, name='accept_reply'),
    path('send-newsletter/', views.send_newsletter, name='send_newsletter'),
]