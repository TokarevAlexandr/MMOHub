from allauth.account.forms import SignupForm
from django.db import models
from django.contrib.auth.models import AbstractUser, Group
from django.urls import reverse
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.conf import settings



class Post(models.Model):
    CATEGORY_CHOICES = [
        ('TK', 'Танки'),
        ('HL', 'Хилы'),
        ('DD', 'ДД'),
        ('TD', 'Торговцы'),
        ('GM', 'Гилдмастеры'),
        ('QG', 'Квестгиверы'),
        ('SM', 'Кузнецы'),
        ('TN', 'Кожевники'),
        ('HM', 'Зельевары'),
        ('WZ', 'Мастера заклинаний'),
    ]

    author = models.ForeignKey('CustomUser', on_delete=models.CASCADE)
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES, default='TK')
    post_time_in = models.DateTimeField(auto_now_add=True)
    title = models.CharField(max_length=255)
    post_text = models.TextField()
    image = models.ImageField(upload_to='post_images/', null=True, blank=True)
    video_url = models.URLField(null=True, blank=True)

    def __str__(self):
        return self.title

    def __str__(self):
        return self.category

    def get_absolute_url(self):
        return reverse('post_detail', args=[str(self.id)])


class CustomUser(AbstractUser):
    subscribed_to_newsletter = models.BooleanField(default=False)
    posts = models.ManyToManyField(Post, related_name='author_posts')

    def __str__(self):
        return self.username


class Reply(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE)
    sender = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    reply_text = models.TextField()
    approved = models.BooleanField(default=False)
    date_created = models.DateTimeField(auto_now_add=True)

    def send_notification_email(self):
        subject = 'Отклик на ваше объявление'
        message = 'Здравствуйте!\n\nНа ваше объявление "{}" появился новый отклик.\n\nС уважением,\nВаш сайт.'.format(
            self.post.title)
        from_email = settings.DEFAULT_FROM_EMAIL
        recipient_list = [self.post.author.email]

        send_mail(subject, message, from_email, recipient_list)


class CommonSignupForm(SignupForm):
    def save(self, request):
        user = super().save(request)
        common_group, created = Group.objects.get_or_create(name='common')
        common_group.user_set.add(user)
        return user