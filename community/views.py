from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from .models import Review, Comment
from .forms import ReviewForm, CommentForm


# Create your views here.
def index(request):
    reviews = Review.objects.order_by('-pk')
    context = {
        'reviews': reviews
    }
    return render(request, 'community/index.html', context)

@login_required
def create(request):
    if request.method == 'POST':
        form = ReviewForm(request.POST)
        if form.is_valid():
            review = form.save(commit=False)
            review.user = request.user
            review.save()
            return redirect('community:detail', review.pk)
    else:
        form = ReviewForm()
    context = {
        'form': form
    }
    return render(request, 'community/create.html', context)

@login_required
def detail(request, review_pk):
    review = get_object_or_404(Review, pk=review_pk)
    comments = review.comment_set.order_by('-pk')
    comment_form = CommentForm()
    context = {
        'review': review,
        'comment_form': comment_form,
        'comments': comments
    }
    return render(request, 'community/detail.html', context)

@require_POST
def comments_create(request, review_pk):
    if request.user.is_authenticated:
        review = get_object_or_404(Review, pk=review_pk)
        comment_form = CommentForm(request.POST)
        if comment_form.is_valid():
            comment = comment_form.save(commit=False)
            comment.review = review
            comment.user = request.user
            comment.save()
            return redirect('community:detail', review.pk)
        context = {
            'comment_form': comment_form,
            'review': review,
        }
        return render(request, 'community/detail.html', context)
    return redirect('accounts:login')


# 좋아요를 누르면 실행되는 함수
@require_POST
def like(request, review_pk):
    # 1. 로그인을 했는지 조사
    if request.user.is_authenticated:
        review = get_object_or_404(Review, pk=review_pk)
        # 로그인 한 유저라면 (인증된 사용자라면)
        # 2번째 조사 -> 좋아요를 눌렀던 사람인지 아닌지
        if review.like.filter(pk=request.user.pk).exists():
            # 이미 좋아요 버튼을 누른 경우 -> 좋아요 취소
            review.like.remove(request.user)
        else:
            # 아닌 경우 -> 좋아요
            review.like.add(request.user)
        return redirect('community:detail', review.pk)
    # 로그인 하지 않은 user는 login으로 ...
    return redirect('accounts:login')