from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from django.utils.text import slugify
from django.urls import reverse


class HomePageContent(models.Model):
    """Model to store homepage editable content"""
    hero_title = models.CharField(max_length=200, default="Welcome to The Daily Learning")
    hero_subtitle = models.TextField(max_length=500, default="Discover insights, tutorials, and knowledge across various topics")
    about_section = models.TextField(default="We share quality content to help you learn and grow. Explore our categories and find what interests you.")
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Homepage Content"
        verbose_name_plural = "Homepage Content"

    def __str__(self):
        return "Homepage Content"

    @classmethod
    def get_content(cls):
        """Get or create homepage content"""
        obj, created = cls.objects.get_or_create(pk=1)
        return obj


class Category(models.Model):
    name = models.CharField(max_length=100)
    slug = models.SlugField(unique=True)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name_plural = "Categories"

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('category_posts', kwargs={'slug': self.slug})


class Post(models.Model):
    STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('published', 'Published'),
    ]

    title = models.CharField(max_length=200)
    slug = models.SlugField(unique=True)
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='posts')
    content = models.TextField(help_text="You can add images, videos, and YouTube links here")
    excerpt = models.TextField(max_length=500, blank=True, help_text="Brief description of the post")
    featured_image = models.ImageField(upload_to='blog_images/', blank=True, null=True)
    youtube_url = models.CharField(max_length=200, blank=True, help_text="YouTube URL (e.g., https://www.youtube.com/watch?v=VIDEO_ID)")
    video_file = models.FileField(upload_to='blog_videos/', blank=True, null=True, help_text="Upload video file")
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='draft')
    is_trashed = models.BooleanField(default=False)
    trashed_at = models.DateTimeField(null=True, blank=True)
    trashed_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='trashed_posts')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    published_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('post_detail', kwargs={'slug': self.slug})
    
    def get_youtube_embed_url(self):
        """Extract YouTube video ID and return embed URL"""
        if self.youtube_url:
            import re
            video_id = None
            # Handle various YouTube URL formats
            patterns = [
                r'(?:youtube\.com\/watch\?v=|youtu\.be\/)([a-zA-Z0-9_-]+)',
                r'youtube\.com\/embed\/([a-zA-Z0-9_-]+)',
            ]
            for pattern in patterns:
                match = re.search(pattern, self.youtube_url)
                if match:
                    video_id = match.group(1)
                    break
            if video_id:
                return f"https://www.youtube.com/embed/{video_id}"
        return None

    def save(self, *args, **kwargs):
        # Auto-generate a slug from the title when missing and ensure uniqueness
        if not self.slug:
            base_slug = slugify(self.title) or 'post'
            slug = base_slug
            i = 1
            # Ensure uniqueness (exclude self when updating)
            while self.__class__.objects.filter(slug=slug).exclude(pk=getattr(self, 'pk', None)).exists():
                slug = f"{base_slug}-{i}"
                i += 1
            self.slug = slug

        if self.status == 'published' and not self.published_at:
            self.published_at = timezone.now()

        super().save(*args, **kwargs)


class PostImage(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='images')
    image = models.ImageField(upload_to='blog_images/')
    caption = models.CharField(max_length=200, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Image for {self.post.title}"
