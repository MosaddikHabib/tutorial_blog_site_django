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
]
