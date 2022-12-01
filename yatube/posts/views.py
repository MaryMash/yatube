from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, render
from django.shortcuts import redirect
from django.urls import reverse
from utils import paginate_page
from .models import Group, Post, User, Comment, Follow
from .constants import PER_PAGE
from .forms import PostForm, CommentForm


def index(request):
    post_list = Post.objects.select_related('group', 'author').all()
    page_obj = paginate_page(request, post_list)
    template = 'posts/index.html'
    context = {
        'page_obj': page_obj
    }
    return render(request, template, context)


def group_posts(request, slug):
    group = get_object_or_404(Group, slug=slug)
    post_list = group.posts.all()
    page_obj = paginate_page(request, post_list)
    template = 'posts/group_list.html'
    posts = group.posts.all()[:PER_PAGE]
    context = {'group': group,
               'posts': posts,
               'page_obj': page_obj
               }
    return render(request, template, context)


def profile(request, username):
    template = 'posts/profile.html'
    author = User.objects.filter(username=username).first()
    posts = author.posts.all()
    page_obj = paginate_page(request, posts)
    user = request.user
    author = User.objects.get(username=username)
    following = False
    if request.user.is_authenticated:
        following = Follow.objects.filter(user=user, author=author).exists()
    context = {'author': author,
               'page_obj': page_obj,
               'following': following
               }
    return render(request, template, context)


def post_detail(request, post_id):
    template = 'posts/post_detail.html'
    post = get_object_or_404(Post, pk=post_id)
    form = CommentForm(request.POST or None)
    comments = Comment.objects.filter(post_id=post_id)
    context = {'post': post,
               'form': form,
               'comments': comments,
               }
    return render(request, template, context)


@login_required
def post_create(request):
    groups = Group.objects.all()
    form = PostForm(request.POST or None,
                    files=request.FILES or None
                    )
    context = {'form': form,
               'groups': groups
               }

    if form.is_valid():
        post = form.save(commit=False)
        post.author = request.user
        post.save()
        return redirect('posts:profile', username=post.author)
    else:
        return render(request, 'posts/create_post.html', context)


@login_required
def post_edit(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    groups = Group.objects.all()

    if request.user != post.author:
        return redirect('posts:post_detail', post_id=post.id)
    else:
        form = PostForm(
            request.POST or None,
            files=request.FILES or None,
            instance=post
        )
        if form.is_valid():
            form.save()
            return redirect('posts:post_detail', post_id=post.id)

    context = {'form': form,
               'groups': groups,
               'post': post,
               'is_edit': True
               }

    return render(request, 'posts/create_post.html', context)


@login_required
def add_comment(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    form = CommentForm(request.POST or None)
    if form.is_valid():
        comment = form.save(commit=False)
        comment.author = request.user
        comment.post = post
        comment.save()
        return redirect('posts:post_detail', post_id=post_id)
    return render(request, 'includes/comments.html', {'form': form,
                  'post': post})


@login_required
def follow_index(request):
    posts = Post.objects.filter(author__following__user=request.user)
    page_obj = paginate_page(request, posts)
    context = {'page_obj': page_obj}
    return render(request, 'posts/follow.html', context=context)


@login_required
def profile_follow(request, username):
    user = request.user
    author = get_object_or_404(User, username=username)
    is_follower = Follow.objects.filter(user=user, author=author).exists()
    if user != author and not is_follower:
        Follow.objects.create(user=user, author=author)

    return redirect(reverse('posts:profile',
                    kwargs={'username': author.username}))


@login_required
def profile_unfollow(request, username):
    user = request.user
    author = get_object_or_404(User, username=username)
    is_follower = Follow.objects.filter(user=user, author=author).exists()
    if user != author and is_follower:
        Follow.objects.filter(user=user, author=author).delete()

    return redirect(reverse('posts:profile',
                    kwargs={'username': author.username}))
