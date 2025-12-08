from django.urls import path
from . import views

urlpatterns = [
    # Authentication
    path('login/', __import__('blog.auth_views').auth_views.custom_login, name='custom_login'),
    path('logout/', __import__('blog.auth_views').auth_views.custom_logout, name='custom_logout'),
    
    # Public URLs
    path('', views.post_list, name='post_list'),
    path('post/<slug:slug>/', views.post_detail, name='post_detail'),
    path('category/<slug:slug>/', views.category_posts, name='category_posts'),
    
    # User Dashboard
    path('dashboard/', views.user_dashboard, name='user_dashboard'),
    
    # Custom Admin URLs - using 'manage' prefix to avoid conflict with Django admin
    path('manage/', views.admin_dashboard, name='admin_dashboard'),
    path('manage/create-post/', views.admin_create_post, name='admin_create_post'),
    path('manage/edit-post/<slug:slug>/', views.admin_edit_post, name='admin_edit_post'),
    path('manage/delete-post/<slug:slug>/', views.admin_delete_post, name='admin_delete_post'),
    path('manage/posts/', views.admin_manage_posts, name='admin_manage_posts'),
    path('manage/categories/', views.admin_manage_categories, name='admin_manage_categories'),
    path('manage/category/edit/<slug:slug>/', views.admin_edit_category, name='admin_edit_category'),
    path('manage/category/delete/<slug:slug>/', views.admin_delete_category, name='admin_delete_category'),
    
    # User Management URLs (Admin only)
    path('manage/users/', views.admin_manage_users, name='admin_manage_users'),
    path('manage/users/create/', views.admin_create_user, name='admin_create_user'),
    path('manage/users/edit/<int:user_id>/', views.admin_edit_user, name='admin_edit_user'),
    path('manage/users/delete/<int:user_id>/', views.admin_delete_user, name='admin_delete_user'),
    
    # Auto-save draft functionality
    path('api/auto-save-draft/', views.auto_save_draft, name='auto_save_draft'),
    path('api/get-drafts/', views.get_draft_posts, name='get_draft_posts'),
    
    # CKEditor image upload
    path('api/ckeditor-upload/', views.ckeditor_upload_image, name='ckeditor_upload_image'),
    
    # Trash Management URLs
    path('manage/trash/', views.admin_trash, name='admin_trash'),
    path('manage/trash/view/<slug:slug>/', views.admin_view_trashed_post, name='admin_view_trashed_post'),
    path('manage/trash/restore/<slug:slug>/', views.admin_restore_post, name='admin_restore_post'),
    path('manage/trash/restore-multiple/', views.admin_restore_multiple, name='admin_restore_multiple'),
    path('manage/trash/delete/<slug:slug>/', views.admin_delete_permanently, name='admin_delete_permanently'),
    path('manage/trash/delete-multiple/', views.admin_delete_multiple, name='admin_delete_multiple'),
    path('manage/trash/empty/', views.admin_empty_trash, name='admin_empty_trash'),
]
