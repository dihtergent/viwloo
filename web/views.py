from django.shortcuts import render, redirect
from django.contrib.auth import login, logout, authenticate, update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib import messages
from django.views.decorators.http import require_POST
from .models import UserProfile, Post

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


# ---------- Feed ----------

@login_required(login_url='/')
def page_view(request):
    """Main feed — masonry grid of posts with optional tab filtering."""
    tab = request.GET.get('tab', 'all')

    if tab and tab != 'all':
        posts = Post.objects.filter(category=tab).select_related('author', 'author__profile')
    else:
        posts = Post.objects.all().select_related('author', 'author__profile')

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
    """Handle post creation via AJAX or normal form submit."""
    if request.method == 'POST':
        title = request.POST.get('title', '').strip()
        body = request.POST.get('body', '').strip()
        category = request.POST.get('category', 'recommended')
        image_file = request.FILES.get('image')

        if not title:
            messages.error(request, 'Title is required.')
            return redirect('page')

        post = Post(author=request.user, title=title, body=body, category=category)

        if image_file:
            upload_result = cloudinary.uploader.upload(image_file)
            post.image = upload_result.get('public_id')

        post.save()
        messages.success(request, 'Post created!')
        return redirect('page')

    return redirect('page')


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
