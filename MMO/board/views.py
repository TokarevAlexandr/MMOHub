from django.contrib.auth.decorators import login_required, user_passes_test
from django import forms
from django.utils import timezone
from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from .models import Post, Reply, CustomUser
from .forms import PostForm, ReplyForm
from .filters import PostFilter
from django.core.mail import EmailMessage
from django.template.loader import render_to_string
from django.urls import reverse_lazy
from django.contrib import messages
from django.utils.html import strip_tags
from django.views.generic.edit import FormMixin
from django.urls import reverse
from django.http import HttpResponseRedirect


class PostList(LoginRequiredMixin, ListView):
    model = Post
    ordering = '-post_time_in'
    template_name = 'posts.html'
    context_object_name = 'posts'
    paginate_by = 10

    def get_queryset(self):
        queryset = super().get_queryset()
        self.filterset = PostFilter(self.request.GET, queryset)
        return self.filterset.qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['filterset'] = self.filterset
        context['time_now'] = timezone.now()
        return context

class PostDetail(FormMixin, DetailView):
    model = Post
    template_name = 'post_detail.html'
    form_class = ReplyForm

    def get_success_url(self):
        return reverse('post_detail', kwargs={'pk': self.object.pk})

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = self.get_form()
        context['category'] = self.object.category
        return context

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        form = self.get_form()
        if form.is_valid():
            reply = form.save(commit=False)
            reply.post = self.object
            reply.sender = self.request.user  # Assuming you have a custom user model
            reply.save()
            return self.form_valid(form)
        else:
            return self.form_invalid(form)

class PostCreate(LoginRequiredMixin, CreateView):
    model = Post
    form_class = PostForm
    template_name = 'post_edit.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['time_now'] = timezone.now()
        return context

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['category_choices'] = Post.CATEGORY_CHOICES  # Получить все доступные категории
        return kwargs

    def form_valid(self, form):
        post = form.save(commit=False)
        post.author, created = CustomUser.objects.get_or_create(id=self.request.user.id)
        post.category = form.cleaned_data['category']
        post.save()
        return redirect('post_detail', pk=post.pk)


class PostUpdate(LoginRequiredMixin, PermissionRequiredMixin, UpdateView):
    model = Post
    form_class = PostForm
    template_name = 'post_edit.html'
    context_object_name = 'post'
    permission_required = 'board.post_edit'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return context

class PostDelete(LoginRequiredMixin, PermissionRequiredMixin, DeleteView):
    model = Post
    template_name = 'post_confirm_delete.html'
    context_object_name = 'post'
    success_url = '/posts/'
    permission_required = 'board.post_edit'

class ReplyCreate(LoginRequiredMixin, CreateView):
    model = Reply
    form_class = ReplyForm
    template_name = 'reply_create.html'

    def form_valid(self, form):
        reply = form.save(commit=False)
        reply.post = Post.objects.get(pk=self.kwargs['pk'])
        reply.sender = self.request.user
        reply.save()
        reply.send_notification_email()
        return redirect('post_detail', pk=reply.post.pk)


@login_required
def private_replies(request):
    user = request.user
    user_posts = user.post_set.all()  # Получить все объявления пользователя
    selected_post_id = request.GET.get('post')  # Получить выбранное объявление из параметров запроса

    # Фильтровать отклики по выбранному объявлению, если оно указано
    replies = Reply.objects.filter(post__author=user)
    if selected_post_id:
        replies = replies.filter(post__id=selected_post_id)

    # Вам также нужно добавить код для обработки формы фильтрации, когда пользователь отправляет ее.
    if request.method == 'GET':
        selected_post_id = request.GET.get('post')
        if selected_post_id:
            replies = replies.filter(post__id=selected_post_id)

    return render(request, 'private_replies.html', {'replies': replies, 'user_posts': user_posts, 'selected_post_id': selected_post_id})

@login_required
def accept_reply(request, pk):
    reply = get_object_or_404(Reply, pk=pk)
    if request.method == 'POST':
        reply.approved = True
        reply.save()
        reply.send_notification_email()
        return HttpResponseRedirect(reverse('post_detail', args=[reply.post.pk]))
    return HttpResponseRedirect(reverse('post_detail', args=[reply.post.pk]))


def delete_reply(request, pk):
    reply = get_object_or_404(Reply, pk=pk)
    if request.method == 'POST':
        reply.delete()
        return redirect('post_detail', pk=reply.post.pk)
    return render(request, 'reply_confirm_delete.html', {'reply': reply})
@login_required
def send_newsletter(request):
    if request.method == 'POST':
        subject = request.POST['subject']
        message = request.POST['message']
        # Assuming there is an email field in the User model, send the newsletter to all subscribed users
        subscribed_users = CustomUser.objects.filter(subscribed_to_newsletter=True)
        email_list = [user.email for user in subscribed_users if user.email]
        if email_list:
            html_message = render_to_string('email/newsletter.html', {'message': message})
            plain_message = strip_tags(html_message)
            email = EmailMessage(subject, plain_message, to=email_list)
            email.attach_alternative(html_message, "text/html")
            email.send()
            messages.success(request, 'Newsletter sent successfully.')
        else:
            messages.error(request, 'No subscribed users found.')
        return redirect('send_newsletter')
    return render(request, 'send_newsletter.html')

