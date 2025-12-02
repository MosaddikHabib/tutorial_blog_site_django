from django.shortcuts import render, get_object_or_404, redirect
from django.core.paginator import Paginator
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils.text import slugify
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from django.db.models import Q
import json
from .models import Post, Category, HomePageContent


def post_list(request):
    """Display homepage with search and summary"""
    homepage_content = HomePageContent.get_content()
    categories = Category.objects.all()
    
    # Search functionality
    search_query = request.GET.get('search', '')
    if search_query:
        posts = Post.objects.filter(
            Q(title__icontains=search_query) | 
            Q(content__icontains=search_query) | 
            Q(excerpt__icontains=search_query),
            status='published'
        ).select_related('author', 'category')
    else:
        posts = Post.objects.filter(status='published').select_related('author', 'category')
    
    # Get recent posts for summary cards
    recent_posts = Post.objects.filter(status='published').select_related('author', 'category')[:6]
    
    # Pagination
    paginator = Paginator(posts, 9)
    page_number = request.GET.get('page')
    posts = paginator.get_page(page_number)
    
    context = {
        'homepage_content': homepage_content,
        'posts': posts,
        'recent_posts': recent_posts,
        'categories': categories,
        'search_query': search_query,
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


@login_required(login_url='custom_login')
@require_POST
def auto_save_draft(request):
    """Auto-save draft functionality"""
    if not request.user.is_staff:
        return JsonResponse({'success': False, 'error': 'Unauthorized'})
    
    try:
        data = json.loads(request.body)
        title = data.get('title', '').strip()
        content = data.get('content', '').strip()
        category_id = data.get('category', '')
        post_id = data.get('post_id', None)
        
        # Don't save if both title and content are empty
        if not title and not content:
            return JsonResponse({'success': True, 'message': 'Nothing to save'})
        
        # Use a default title if empty
        if not title:
            title = 'Untitled Draft'
        
        if post_id:
            # Update existing draft
            try:
                post = Post.objects.get(id=post_id, author=request.user, status='draft')
                post.title = title
                post.content = content
                if category_id:
                    try:
                        category = Category.objects.get(id=category_id)
                        post.category = category
                    except Category.DoesNotExist:
                        pass
                post.save()
                return JsonResponse({
                    'success': True, 
                    'message': 'Draft updated',
                    'post_id': post.id
                })
            except Post.DoesNotExist:
                pass
        
        # Create new draft
        slug = slugify(title)
        counter = 1
        original_slug = slug
        while Post.objects.filter(slug=slug).exists():
            slug = f"{original_slug}-{counter}"
            counter += 1
        
        category = None
        if category_id:
            try:
                category = Category.objects.get(id=category_id)
            except Category.DoesNotExist:
                category = Category.objects.first()  # Default to first category
        else:
            category = Category.objects.first()
        
        if not category:
            return JsonResponse({'success': False, 'error': 'No categories available'})
        
        post = Post.objects.create(
            title=title,
            slug=slug,
            author=request.user,
            category=category,
            content=content,
            excerpt='',
            status='draft',
            youtube_url='',
        )
        
        return JsonResponse({
            'success': True, 
            'message': 'Draft saved automatically',
            'post_id': post.id
        })
        
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})


@login_required(login_url='custom_login')
def get_draft_posts(request):
    """Get user's draft posts"""
    if not request.user.is_staff:
        return JsonResponse({'success': False, 'error': 'Unauthorized'})
    
    drafts = Post.objects.filter(
        author=request.user, 
        status='draft'
    ).order_by('-updated_at')[:5]
    
    draft_list = []
    for draft in drafts:
        draft_list.append({
            'id': draft.id,
            'title': draft.title,
            'updated_at': draft.updated_at.strftime('%Y-%m-%d %H:%M'),
            'edit_url': f'/manage/edit-post/{draft.slug}/' if draft.slug else '#'
        })
    
    return JsonResponse({'success': True, 'drafts': draft_list})
