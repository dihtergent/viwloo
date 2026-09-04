from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .models import images

def home(request):
    img_list = images.objects.all().order_by('-created_at', '-id')
    return render(request, 'index.html', {'images': img_list})

@login_required(login_url='login')
def create_post(request):
    if request.method == 'POST':
        title = request.POST.get('title', '').strip()
        description = request.POST.get('description', '').strip()
        image_file = request.FILES.get('image')

        if not title:
            messages.error(request, 'กรุณาระบุหัวข้อโพสต์')
            return render(request, 'create_post.html', {'title': title, 'description': description})

        if not image_file:
            messages.error(request, 'กรุณาเลือกรูปภาพสำหรับโพสต์')
            return render(request, 'create_post.html', {'title': title, 'description': description})

        try:
            new_post = images.objects.create(
                user=request.user,
                title=title,
                description=description,
                image=image_file
            )
            messages.success(request, 'โพสต์รูปภาพสำเร็จแล้ว!')
            return redirect('home')
        except Exception as e:
            messages.error(request, f'เกิดข้อผิดพลาดในการอัปโหลดรูปภาพ: {str(e)}')
            return render(request, 'create_post.html', {'title': title, 'description': description})

    return render(request, 'create_post.html')

@login_required(login_url='login')
def delete_post(request, pk):
    post = get_object_or_404(images, pk=pk)
    if post.user == request.user or request.user.is_superuser:
        post.delete()
        messages.success(request, 'ลบโพสต์เรียบร้อยแล้ว')
    else:
        messages.error(request, 'คุณไม่มีสิทธิ์ลบโพสต์นี้')
    return redirect('home')

def login_view(request):
    if request.user.is_authenticated:
        return redirect('home')

    if request.method == 'POST':
        identifier = request.POST.get('username', '').strip()
        password_input = request.POST.get('password', '')
        remember_me = request.POST.get('remember_me')

        if not identifier or not password_input:
            messages.error(request, 'กรุณากรอกชื่อผู้ใช้และรหัสผ่าน')
            return render(request, 'login.html', {'username': identifier})

        # Allow login with either username or email
        username = identifier
        if '@' in identifier:
            user_obj = User.objects.filter(email__iexact=identifier).first()
            if user_obj:
                username = user_obj.username

        user = authenticate(request, username=username, password=password_input)
        if user is not None:
            login(request, user)

            # Handle Remember Me
            if remember_me:
                request.session.set_expiry(1209600)  # 2 weeks
            else:
                request.session.set_expiry(0)  # On browser close

            messages.success(request, f'ยินดีต้อนรับกลับ, {user.username}!')
            next_url = request.GET.get('next') or request.POST.get('next')
            if next_url:
                return redirect(next_url)
            return redirect('home')
        else:
            if User.objects.count() == 0:
                messages.warning(request, 'ยังไม่มีบัญชีผู้ใช้ในระบบ กรุณาสมัครสมาชิกก่อนเข้าสู่ระบบ')
            else:
                messages.error(request, 'ชื่อผู้ใช้หรือรหัสผ่านไม่ถูกต้อง')
            return render(request, 'login.html', {'username': identifier})

    return render(request, 'login.html')

def register_view(request):
    if request.user.is_authenticated:
        return redirect('home')

    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, f'สมัครสมาชิกสำเร็จ! ยินดีต้อนรับ {user.username}')
            return redirect('home')
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, error)
    else:
        form = UserCreationForm()

    return render(request, 'register.html', {'form': form})

def logout_view(request):
    logout(request)
    messages.info(request, 'ออกจากระบบเรียบร้อยแล้ว')
    return redirect('login')
