from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, authenticate, update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib import messages
from django.views.decorators.http import require_POST
from .models import UserProfile, Post, Comment

from django.db import models
import cloudinary.uploader


# ---------- Auth ----------

def index(request):
    """Landing page with login/signup. Redirects to /page/ if already logged in."""
    if request.user.is_authenticated:
        return redirect('page')

    if request.method == 'POST':
        action = request.POST.get('action')

        if action == 'login':
            username = request.POST.get('username', '').strip()
            password = request.POST.get('password', '')
            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)
                return redirect('page')
            else:
                messages.error(request, 'Invalid username or password.')

        elif action == 'signup':
            username = request.POST.get('username', '').strip()
            email = request.POST.get('email', '').strip()
            password = request.POST.get('password', '')
            password2 = request.POST.get('password2', '')

            if password != password2:
                messages.error(request, 'Passwords do not match.')
            elif User.objects.filter(username=username).exists():
                messages.error(request, 'Username already taken.')
            elif User.objects.filter(email=email).exists():
                messages.error(request, 'Email already in use.')
            else:
                user = User.objects.create_user(username=username, email=email, password=password)
                UserProfile.objects.create(user=user, display_name=username)
                login(request, user)
                return redirect('page')

    return render(request, 'index.html')


@require_POST
def logout_view(request):
    logout(request)
    return redirect('index')


# ---------- Expiration Helper ----------

from datetime import timedelta
from django.utils import timezone

def purge_expired_posts():
    """Purge posts older than 100 days."""
    cutoff = timezone.now() - timedelta(days=100)
    Post.objects.filter(created_at__lt=cutoff).delete()


# ---------- Feed ----------

@login_required(login_url='/')
def page_view(request):
    """Main feed — masonry grid of posts with Interknot & Proxy tabs."""
    purge_expired_posts()
    tab = request.GET.get('tab', 'interknot')

    if tab == 'proxy':
        posts = Post.objects.filter(category='proxy').select_related('author', 'author__profile')
    else:
        # Default 'interknot' tab includes interknot & legacy categories
        posts = Post.objects.filter(
            models.Q(category='interknot') | models.Q(category__in=['recommended', 'itinerary', 'route'])
        ).select_related('author', 'author__profile')

    # Ensure current user has a profile
    profile, _ = UserProfile.objects.get_or_create(
        user=request.user,
        defaults={'display_name': request.user.username}
    )

    context = {
        'posts': posts,
        'profile': profile,
        'current_tab': tab,
    }
    return render(request, 'page.html', context)


# ---------- Create Post ----------

@login_required(login_url='/')
def create_post(request):
    """Handle post creation with optional GPS location and double post protection."""
    if request.method == 'POST':
        title = request.POST.get('title', '').strip()
        body = request.POST.get('body', '').strip()
        category = request.POST.get('category', 'interknot')
        if category not in ['interknot', 'proxy']:
            category = 'interknot'

        image_file = request.FILES.get('image')
        location_name = request.POST.get('location_name', '').strip()
        lat = request.POST.get('latitude', '').strip()
        lng = request.POST.get('longitude', '').strip()

        if not title:
            messages.error(request, 'Title is required.')
            return redirect('page')

        # Double post submission guard (5-second debounce)
        recent_cutoff = timezone.now() - timedelta(seconds=5)
        if Post.objects.filter(author=request.user, title=title, created_at__gte=recent_cutoff).exists():
            messages.info(request, 'Post already created!')
            return redirect('page')

        post = Post(author=request.user, title=title, body=body, category=category)
        post.location_name = location_name

        if lat and lng:
            try:
                post.latitude = float(lat)
                post.longitude = float(lng)
            except (ValueError, TypeError):
                pass

        if image_file:
            upload_result = cloudinary.uploader.upload(image_file)
            post.image = upload_result.get('public_id')

        post.save()
        messages.success(request, 'Post created!')
        return redirect('page')

    return redirect('page')


# ---------- Post Detail ----------

@login_required(login_url='/')
def post_detail(request, pk):
    """Single post view with comments."""
    post = get_object_or_404(
        Post.objects.select_related('author', 'author__profile'),
        pk=pk
    )
    # Increment view count
    Post.objects.filter(pk=pk).update(views_count=models.F('views_count') + 1)

    comments = post.comments.select_related('author', 'author__profile')

    profile, _ = UserProfile.objects.get_or_create(
        user=request.user,
        defaults={'display_name': request.user.username}
    )

    context = {
        'post': post,
        'comments': comments,
        'profile': profile,
    }
    return render(request, 'post_detail.html', context)


# ---------- Edit Post ----------

@login_required(login_url='/')
def edit_post(request, pk):
    """Edit an existing post (owner only)."""
    post = get_object_or_404(Post, pk=pk)
    if post.author != request.user:
        messages.error(request, 'You are not authorized to edit this post.')
        return redirect('post_detail', pk=pk)

    if request.method == 'POST':
        title = request.POST.get('title', '').strip()
        body = request.POST.get('body', '').strip()
        category = request.POST.get('category', 'recommended')
        image_file = request.FILES.get('image')
        location_name = request.POST.get('location_name', '').strip()
        lat = request.POST.get('latitude', '').strip()
        lng = request.POST.get('longitude', '').strip()
        clear_loc = request.POST.get('clear_location') == '1'

        if not title:
            messages.error(request, 'Title is required.')
            return redirect('edit_post', pk=pk)

        post.title = title
        post.body = body
        post.category = category
        post.location_name = location_name

        if clear_loc:
            post.latitude = None
            post.longitude = None
            post.location_name = ''
        elif lat and lng:
            try:
                post.latitude = float(lat)
                post.longitude = float(lng)
            except (ValueError, TypeError):
                pass

        if image_file:
            upload_result = cloudinary.uploader.upload(image_file)
            post.image = upload_result.get('public_id')

        post.save()
        messages.success(request, 'Post updated successfully!')
        return redirect('post_detail', pk=pk)

    profile, _ = UserProfile.objects.get_or_create(
        user=request.user,
        defaults={'display_name': request.user.username}
    )

    context = {
        'post': post,
        'profile': profile,
    }
    return render(request, 'edit_post.html', context)


# ---------- Delete Post ----------

@login_required(login_url='/')
@require_POST
def delete_post(request, pk):
    """Delete a post (owner only)."""
    post = get_object_or_404(Post, pk=pk)
    if post.author != request.user:
        messages.error(request, 'You are not authorized to delete this post.')
        return redirect('post_detail', pk=pk)

    post.delete()
    messages.success(request, 'Post deleted successfully.')
    return redirect('page')


# ---------- Add Comment ----------

@login_required(login_url='/')
@require_POST
def add_comment(request, pk):
    """Add a comment to a post."""
    post = get_object_or_404(Post, pk=pk)
    text = request.POST.get('text', '').strip()

    if text:
        Comment.objects.create(post=post, author=request.user, text=text)
        messages.success(request, 'Comment added!')
    else:
        messages.error(request, 'Comment cannot be empty.')

    return redirect('post_detail', pk=pk)


# ---------- Account Settings ----------

@login_required(login_url='/')
def account_settings(request):
    """Edit profile and change password."""
    profile, _ = UserProfile.objects.get_or_create(
        user=request.user,
        defaults={'display_name': request.user.username}
    )

    if request.method == 'POST':
        section = request.POST.get('section', 'profile')

        if section == 'profile':
            display_name = request.POST.get('display_name', '').strip()
            bio = request.POST.get('bio', '').strip()
            avatar_file = request.FILES.get('avatar')

            if display_name:
                profile.display_name = display_name
            profile.bio = bio

            if avatar_file:
                upload_result = cloudinary.uploader.upload(avatar_file)
                profile.avatar = upload_result.get('public_id')

            profile.save()
            messages.success(request, 'Profile updated!')

        elif section == 'password':
            current_password = request.POST.get('current_password', '')
            new_password = request.POST.get('new_password', '')
            confirm_password = request.POST.get('confirm_password', '')

            if not request.user.check_password(current_password):
                messages.error(request, 'Current password is incorrect.')
            elif new_password != confirm_password:
                messages.error(request, 'New passwords do not match.')
            elif len(new_password) < 8:
                messages.error(request, 'Password must be at least 8 characters.')
            else:
                request.user.set_password(new_password)
                request.user.save()
                update_session_auth_hash(request, request.user)
                messages.success(request, 'Password changed!')

        return redirect('account_settings')

    context = {
        'profile': profile,
    }
    return render(request, 'account_setting.html', context)
