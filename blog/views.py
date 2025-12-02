from django.shortcuts import render, get_object_or_404, redirect
from django.core.paginator import Paginator
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils.text import slugify
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from django.db.models import Q
from django.contrib.auth.models import User
from django.contrib.auth.hashers import make_password
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
def user_dashboard(request):
    """Regular user dashboard"""
    if not request.user.is_staff:
        messages.error(request, 'You need to be a staff member to access the dashboard.')
        return redirect('post_list')
    
    # If superuser, redirect to admin dashboard
    if request.user.is_superuser:
        return redirect('admin_dashboard')
    
    posts = Post.objects.filter(author=request.user).order_by('-created_at')[:10]
    stats = {
        'total_posts': Post.objects.filter(author=request.user).count(),
        'published_posts': Post.objects.filter(author=request.user, status='published').count(),
        'draft_posts': Post.objects.filter(author=request.user, status='draft').count(),
    }
    
    context = {
        'posts': posts,
        'stats': stats,
    }
    return render(request, 'blog/user_dashboard.html', context)


@login_required
def admin_dashboard(request):
    """Custom admin dashboard"""
    if not request.user.is_staff:
        return redirect('post_list')
    
    # If not superuser, redirect to user dashboard
    if not request.user.is_superuser:
        return redirect('user_dashboard')
    
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


@login_required(login_url='custom_login')
def admin_manage_posts(request):
    """Custom admin page to manage posts"""
    if not request.user.is_staff:
        return redirect('post_list')
    
    # Filter and search functionality
    status_filter = request.GET.get('status', '')
    category_filter = request.GET.get('category', '')
    search_query = request.GET.get('search', '')
    
    # Superusers see all posts, regular users see only their own
    if request.user.is_superuser:
        posts = Post.objects.all().select_related('author', 'category')
    else:
        posts = Post.objects.filter(author=request.user).select_related('author', 'category')
    
    if status_filter:
        posts = posts.filter(status=status_filter)
    if category_filter:
        posts = posts.filter(category__id=category_filter)
    if search_query:
        posts = posts.filter(
            Q(title__icontains=search_query) | 
            Q(content__icontains=search_query)
        )
    
    # Pagination
    paginator = Paginator(posts, 20)
    page_number = request.GET.get('page')
    posts = paginator.get_page(page_number)
    
    categories = Category.objects.all()
    
    context = {
        'posts': posts,
        'categories': categories,
        'status_filter': status_filter,
        'category_filter': category_filter,
        'search_query': search_query,
    }
    return render(request, 'blog/admin_manage_posts.html', context)


@login_required(login_url='custom_login')
def admin_manage_categories(request):
    """Custom admin page to manage categories"""
    if not request.user.is_superuser:
        return redirect('post_list')
    
    categories = Category.objects.all().order_by('name')
    
    # Add new category
    if request.method == 'POST' and 'add_category' in request.POST:
        name = request.POST.get('name', '').strip()
        description = request.POST.get('description', '').strip()
        
        if name:
            slug = slugify(name)
            counter = 1
            original_slug = slug
            while Category.objects.filter(slug=slug).exists():
                slug = f"{original_slug}-{counter}"
                counter += 1
            
            Category.objects.create(
                name=name,
                slug=slug,
                description=description
            )
            messages.success(request, f'Category "{name}" created successfully!')
            return redirect('admin_manage_categories')
        else:
            messages.error(request, 'Category name is required!')
    
    context = {
        'categories': categories,
    }
    return render(request, 'blog/admin_manage_categories.html', context)


@login_required(login_url='custom_login')
def admin_edit_category(request, slug):
    """Edit a category"""
    if not request.user.is_superuser:
        return redirect('post_list')
    
    category = get_object_or_404(Category, slug=slug)
    
    if request.method == 'POST':
        name = request.POST.get('name', '').strip()
        description = request.POST.get('description', '').strip()
        
        if name:
            category.name = name
            category.description = description
            # Update slug only if name changed
            if category.name != name:
                new_slug = slugify(name)
                counter = 1
                original_slug = new_slug
                while Category.objects.filter(slug=new_slug).exclude(pk=category.pk).exists():
                    new_slug = f"{original_slug}-{counter}"
                    counter += 1
                category.slug = new_slug
            
            category.save()
            messages.success(request, f'Category "{name}" updated successfully!')
            return redirect('admin_manage_categories')
        else:
            messages.error(request, 'Category name is required!')
    
    context = {
        'category': category,
    }
    return render(request, 'blog/admin_edit_category.html', context)


@login_required(login_url='custom_login')
def admin_delete_category(request, slug):
    """Delete a category"""
    if not request.user.is_superuser:
        return redirect('post_list')
    
    category = get_object_or_404(Category, slug=slug)
    
    if request.method == 'POST':
        category_name = category.name
        category.delete()
        messages.success(request, f'Category "{category_name}" deleted successfully!')
        return redirect('admin_manage_categories')
    
    context = {
        'category': category,
    }
    return render(request, 'blog/admin_delete_category.html', context)


@login_required(login_url='custom_login')
def admin_manage_users(request):
    """Custom admin page to manage all users"""
    if not request.user.is_superuser:
        return redirect('post_list')
    
    # Filter and search functionality
    search_query = request.GET.get('search', '')
    role_filter = request.GET.get('role', '')
    
    users = User.objects.all().order_by('-date_joined')
    
    if role_filter == 'admin':
        users = users.filter(is_superuser=True)
    elif role_filter == 'user':
        users = users.filter(is_superuser=False)
    
    if search_query:
        users = users.filter(
            Q(username__icontains=search_query) | 
            Q(email__icontains=search_query) |
            Q(first_name__icontains=search_query) |
            Q(last_name__icontains=search_query)
        )
    
    # Pagination
    paginator = Paginator(users, 20)
    page_number = request.GET.get('page')
    users = paginator.get_page(page_number)
    
    context = {
        'users': users,
        'search_query': search_query,
        'role_filter': role_filter,
    }
    return render(request, 'blog/admin_manage_users.html', context)


@login_required(login_url='custom_login')
def admin_create_user(request):
    """Create a new user"""
    if not request.user.is_superuser:
        return redirect('post_list')
    
    if request.method == 'POST':
        username = request.POST.get('username', '').strip()
        email = request.POST.get('email', '').strip()
        password = request.POST.get('password', '').strip()
        first_name = request.POST.get('first_name', '').strip()
        last_name = request.POST.get('last_name', '').strip()
        is_superuser = request.POST.get('is_superuser') == 'on'
        
        # Validation
        if not username or not password:
            messages.error(request, 'Username and password are required!')
            return redirect('admin_create_user')
        
        if User.objects.filter(username=username).exists():
            messages.error(request, f'Username "{username}" already exists!')
            return redirect('admin_create_user')
        
        if email and User.objects.filter(email=email).exists():
            messages.error(request, f'Email "{email}" is already registered!')
            return redirect('admin_create_user')
        
        # Create user
        user = User.objects.create(
            username=username,
            email=email,
            first_name=first_name,
            last_name=last_name,
            is_superuser=is_superuser,
            is_staff=True,  # All users are staff (can access dashboard and create posts)
            password=make_password(password)
        )
        
        role = "Admin" if is_superuser else "User"
        messages.success(request, f'{role} "{username}" created successfully!')
        return redirect('admin_manage_users')
    
    return render(request, 'blog/admin_create_user.html')


@login_required(login_url='custom_login')
def admin_edit_user(request, user_id):
    """Edit a user"""
    if not request.user.is_superuser:
        return redirect('post_list')
    
    user = get_object_or_404(User, id=user_id)
    
    if request.method == 'POST':
        username = request.POST.get('username', '').strip()
        email = request.POST.get('email', '').strip()
        first_name = request.POST.get('first_name', '').strip()
        last_name = request.POST.get('last_name', '').strip()
        is_superuser = request.POST.get('is_superuser') == 'on'
        new_password = request.POST.get('new_password', '').strip()
        
        if not username:
            messages.error(request, 'Username is required!')
            return redirect('admin_edit_user', user_id=user_id)
        
        # Check username uniqueness
        if User.objects.filter(username=username).exclude(id=user_id).exists():
            messages.error(request, f'Username "{username}" already exists!')
            return redirect('admin_edit_user', user_id=user_id)
        
        # Check email uniqueness
        if email and User.objects.filter(email=email).exclude(id=user_id).exists():
            messages.error(request, f'Email "{email}" is already registered!')
            return redirect('admin_edit_user', user_id=user_id)
        
        # Update user
        user.username = username
        user.email = email
        user.first_name = first_name
        user.last_name = last_name
        user.is_superuser = is_superuser
        user.is_staff = True  # All users are staff (can access dashboard and create posts)
        
        # Update password if provided
        if new_password:
            user.password = make_password(new_password)
        
        user.save()
        messages.success(request, f'User "{username}" updated successfully!')
        return redirect('admin_manage_users')
    
    context = {
        'edited_user': user,
    }
    return render(request, 'blog/admin_edit_user.html', context)


@login_required(login_url='custom_login')
def admin_delete_user(request, user_id):
    """Delete a user"""
    if not request.user.is_superuser:
        return redirect('post_list')
    
    user = get_object_or_404(User, id=user_id)
    
    # Prevent deleting yourself
    if user.id == request.user.id:
        messages.error(request, 'You cannot delete your own account!')
        return redirect('admin_manage_users')
    
    if request.method == 'POST':
        username = user.username
        user.delete()
        messages.success(request, f'User "{username}" deleted successfully!')
        return redirect('admin_manage_users')
    
    context = {
        'deleted_user': user,
    }
    return render(request, 'blog/admin_delete_user.html', context)
    return render(request, 'blog/admin_delete_category.html', context)
