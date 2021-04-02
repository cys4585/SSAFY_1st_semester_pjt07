from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import login as auth_login, logout as auth_logout
from django.contrib.auth import get_user_model
from django.views.decorators.http import require_POST, require_safe
from .forms import CustomUserCreationForm

User = get_user_model()
# Create your views here.
def signup(request):
    # request.user가 인증된 유저인가? 조사
    if request.user.is_authenticated:
        return redirect('community:index')
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            auth_login(request, user)
            return redirect('community:index')
    else:
        form = CustomUserCreationForm()
    context = {
        'form': form
    }
    return render(request, 'accounts/signup.html', context)

def login(request):
    if request.method == "POST":
        form = AuthenticationForm(request, request.POST)
        if form.is_valid():
            auth_login(request, form.get_user())
            return redirect(request.GET.get('next') or 'community:index')
    else:
        form = AuthenticationForm()
    context = {
        'form': form
    }
    return render(request, 'accounts/login.html', context)

@require_POST
def logout(request):
    auth_logout(request)
    return redirect('community:index')

@require_safe
def profile(request, user_id):
    person = get_object_or_404(User, pk=user_id)
    context = {
        'person': person,
    }
    return render(request, 'accounts/profile.html', context)

@require_POST
def follow(request, user_id):
    # 로그인 했는지 조사
    if request.user.is_authenticated:
        # 로그인 했다면
        person = get_object_or_404(User, pk=user_id)
        # 요청한 user 와 person이 달라야죠 (팔로우를 하려면)
        if request.user != person:
            # 이미 팔로우 한 유저인지 아닌지 조사
            if person.followers.filter(pk=request.user.pk).exists():
                person.followers.remove(request.user)
            else:
                person.followers.add(request.user)
        return redirect('accounts:profile', person.pk)
    return redirect('accounts:login')