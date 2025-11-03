from django.shortcuts import render, get_object_or_404, redirect
from django.core.paginator import Paginator
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils.text import slugify
from .models import Post, Category


def post_list(request):
    """Display list of published posts"""
    posts = Post.objects.filter(status='published').select_related('author', 'category')
    categories = Category.objects.all()
    
    # Pagination
    paginator = Paginator(posts, 6)  # Show 6 posts per page
    page_number = request.GET.get('page')
    posts = paginator.get_page(page_number)
    
    context = {
        'posts': posts,
        'categories': categories,
    }
    return render(request, 'blog/post_list.html', context)


def post_detail(request, slug):
    """Display individual post detail"""
    post = get_object_or_404(Post, slug=slug, status='published')
    related_posts = Post.objects.filter(
        category=post.category, 
        status='published'
    ).exclude(id=post.id)[:3]
    
    context = {
        'post': post,
        'related_posts': related_posts,
    }
    return render(request, 'blog/post_detail.html', context)


def category_posts(request, slug):
    """Display posts filtered by category"""
    category = get_object_or_404(Category, slug=slug)
    posts = Post.objects.filter(
        category=category, 
        status='published'
    ).select_related('author', 'category')
    categories = Category.objects.all()
    
    # Pagination
    paginator = Paginator(posts, 6)
    page_number = request.GET.get('page')
    posts = paginator.get_page(page_number)
    
    context = {
        'posts': posts,
        'category': category,
        'categories': categories,
    }
    return render(request, 'blog/category_posts.html', context)


# Custom Admin Views
@login_required
def admin_dashboard(request):
    """Custom admin dashboard"""
    if not request.user.is_staff:
        return redirect('post_list')
    
    posts = Post.objects.filter(author=request.user).order_by('-created_at')[:10]
    categories = Category.objects.all()
    stats = {
        'total_posts': Post.objects.filter(author=request.user).count(),
        'published_posts': Post.objects.filter(author=request.user, status='published').count(),
        'draft_posts': Post.objects.filter(author=request.user, status='draft').count(),
    }
    
    context = {
        'posts': posts,
        'categories': categories,
        'stats': stats,
    }
    return render(request, 'blog/admin_dashboard.html', context)


from django.contrib.auth.decorators import login_required

@login_required(login_url='custom_login')
def admin_create_post(request):
    """Create new post"""
    if not request.user.is_staff:
        return redirect('post_list')
    
    categories = Category.objects.all()
    
    if request.method == 'POST':
        title = request.POST.get('title')
        category_id = request.POST.get('category')
        content = request.POST.get('content')
        featured_image = request.FILES.get('featured_image')
        
        try:
            category = Category.objects.get(id=category_id)
            slug = slugify(title)
            
            # Ensure unique slug
            counter = 1
            original_slug = slug
            while Post.objects.filter(slug=slug).exists():
                slug = f"{original_slug}-{counter}"
                counter += 1
            
            post = Post.objects.create(
                title=title,
                slug=slug,
                author=request.user,
                category=category,
                content=content,
                excerpt='',  # Default empty
                status='published',  # Always publish
                youtube_url='',  # Default empty
                featured_image=featured_image,
            )
            
            messages.success(request, 'Post published successfully!')
            return redirect('admin_dashboard')
        except Exception as e:
            messages.error(request, f'Error creating post: {str(e)}')
    
    context = {
        'categories': categories,
    }
    return render(request, 'blog/admin_create_post.html', context)


@login_required(login_url='custom_login')
def admin_edit_post(request, slug):
    """Edit existing post"""
    if not request.user.is_staff:
        return redirect('post_list')
    
    post = get_object_or_404(Post, slug=slug, author=request.user)
    categories = Category.objects.all()
    
    if request.method == 'POST':
        post.title = request.POST.get('title')
        category_id = request.POST.get('category')
        post.content = request.POST.get('content')
        # Excerpt and youtube_url may be missing from the form; default to empty string
        post.excerpt = request.POST.get('excerpt') or ''
        # Determine status from action button if present
        action = request.POST.get('action')
        if action == 'publish':
            post.status = 'published'
        elif action == 'save':
            post.status = 'draft'
        else:
            post.status = request.POST.get('status') or post.status
        post.youtube_url = request.POST.get('youtube_url') or ''
        
        if request.FILES.get('featured_image'):
            post.featured_image = request.FILES.get('featured_image')
        
        try:
            post.category = Category.objects.get(id=category_id)
            post.save()
            messages.success(request, 'Post updated successfully!')
            return redirect('admin_edit_post', slug=post.slug)
        except Exception as e:
            messages.error(request, f'Error updating post: {str(e)}')
    
    context = {
        'post': post,
        'categories': categories,
    }
    return render(request, 'blog/admin_edit_post.html', context)


@login_required(login_url='custom_login')
def admin_delete_post(request, slug):
    """Delete post"""
    if not request.user.is_staff:
        return redirect('post_list')
    
    post = get_object_or_404(Post, slug=slug, author=request.user)
    
    if request.method == 'POST':
        post.delete()
        messages.success(request, 'Post deleted successfully!')
        return redirect('admin_dashboard')
    
    context = {
        'post': post,
    }
    return render(request, 'blog/admin_delete_post.html', context)
