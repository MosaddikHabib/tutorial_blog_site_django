from django.urls import path
from . import views

urlpatterns = [
    path('login/', __import__('blog.auth_views').auth_views.custom_login, name='custom_login'),
    path('logout/', __import__('blog.auth_views').auth_views.custom_logout, name='custom_logout'),
    path('', views.post_list, name='post_list'),
    path('post/<slug:slug>/', views.post_detail, name='post_detail'),
    path('category/<slug:slug>/', views.category_posts, name='category_posts'),
    # Custom Admin URLs - using 'manage' prefix to avoid conflict with Django admin
    path('manage/', views.admin_dashboard, name='admin_dashboard'),
    path('manage/create-post/', views.admin_create_post, name='admin_create_post'),
    path('manage/edit-post/<slug:slug>/', views.admin_edit_post, name='admin_edit_post'),
    path('manage/delete-post/<slug:slug>/', views.admin_delete_post, name='admin_delete_post'),
]
