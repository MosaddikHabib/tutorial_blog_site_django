from django.core.management.base import BaseCommand
from blog.models import Post, Category
from django.contrib.auth.models import User


class Command(BaseCommand):
    help = 'Creates dummy blog posts for testing'

    def handle(self, *args, **kwargs):
        # Get or create a user
        user, created = User.objects.get_or_create(
            username='admin',
            defaults={
                'email': 'admin@example.com',
                'is_staff': True,
                'is_superuser': True
            }
        )
        
        # Get or create categories
        categories = []
        for cat_name in ['Technology', 'Tutorials', 'Django', 'Python', 'Web Development']:
            cat, _ = Category.objects.get_or_create(
                name=cat_name,
                defaults={'slug': cat_name.lower().replace(' ', '-')}
            )
            categories.append(cat)
        
        # Sample post data
        dummy_posts = [
            {
                'title': 'Getting Started with Django Web Development',
                'excerpt': 'Learn the basics of Django and build your first web application.',
                'content': '''
Django is a high-level Python web framework that encourages rapid development and clean, pragmatic design. It's perfect for building web applications of any size.

In this tutorial, we'll cover:

1. Setting up your Django project
2. Creating your first models
3. Building views and templates
4. Working with the admin interface

Django makes it easy to build web applications quickly. The framework includes everything you need to build production-ready applications, including authentication, database management, and security features.

Let's start by creating a new Django project and exploring its structure.
                ''',
                'category': 'Django',
                'status': 'published',
                'youtube_url': 'https://www.youtube.com/watch?v=_uQrJ0TkZlc'
            },
            {
                'title': 'Python Programming Fundamentals',
                'excerpt': 'Master the core concepts of Python programming language.',
                'content': '''
Python is one of the most popular programming languages in the world. It's known for its simplicity and readability, making it perfect for beginners and experts alike.

Key concepts covered:
- Variables and data types
- Control structures
- Functions and modules
- Object-oriented programming

Python is used in a wide variety of applications, from web development to data science and artificial intelligence. Its extensive standard library and active community make it an excellent choice for any project.
                ''',
                'category': 'Python',
                'status': 'published'
            },
            {
                'title': 'Modern Web Development Best Practices',
                'excerpt': 'Learn the latest techniques and best practices for building modern web applications.',
                'content': '''
Web development has evolved significantly over the years. Today, we have access to powerful tools and frameworks that make it easier than ever to build incredible web applications.

This post covers:

1. Responsive design principles
2. Performance optimization
3. Accessibility standards
4. Security best practices

Modern web development requires understanding of HTML, CSS, JavaScript, and various frameworks. It's also important to follow best practices for code organization, testing, and deployment.
                ''',
                'category': 'Web Development',
                'status': 'published'
            },
            {
                'title': 'Building RESTful APIs with Django',
                'excerpt': 'Create powerful and flexible APIs for your web applications.',
                'content': '''
RESTful APIs are essential for modern web applications. They allow different systems to communicate with each other efficiently.

In this tutorial, you'll learn how to:

- Design RESTful endpoints
- Handle HTTP methods properly
- Implement authentication and authorization
- Test your API endpoints

Django REST Framework makes it easy to build robust APIs. It provides powerful tools for serialization, authentication, and permissions.
                ''',
                'category': 'Technology',
                'status': 'published'
            },
            {
                'title': 'Database Design and Optimization',
                'excerpt': 'Learn how to design efficient databases and optimize your queries.',
                'content': '''
Good database design is crucial for application performance and scalability. In this comprehensive guide, we'll cover database design principles and optimization techniques.

Topics include:
- Normalization
- Indexing strategies
- Query optimization
- Database relationships

Understanding how databases work will help you build faster and more efficient applications. We'll use practical examples to illustrate key concepts.
                ''',
                'category': 'Technology',
                'status': 'published'
            },
            {
                'title': 'Understanding Git and Version Control',
                'excerpt': 'Master version control with Git and improve your development workflow.',
                'content': '''
Version control is essential for any serious development project. Git has become the standard tool for managing code versions and collaboration.

Learn about:
- Basic Git commands
- Branching and merging strategies
- Working with remote repositories
- Collaboration workflows

Git allows you to track changes, experiment with new features, and collaborate with team members effectively.
                ''',
                'category': 'Tutorials',
                'status': 'published'
            }
        ]
        
        # Create posts
        posts_created = 0
        for post_data in dummy_posts:
            category = next((cat for cat in categories if cat.name == post_data['category']), categories[0])
            
            slug = post_data['title'].lower().replace(' ', '-')[:50]
            
            # Ensure unique slug
            counter = 1
            original_slug = slug
            while Post.objects.filter(slug=slug).exists():
                slug = f"{original_slug}-{counter}"
                counter += 1
            
            Post.objects.get_or_create(
                slug=slug,
                defaults={
                    'title': post_data['title'],
                    'author': user,
                    'category': category,
                    'content': post_data['content'],
                    'excerpt': post_data['excerpt'],
                    'status': post_data['status'],
                    'youtube_url': post_data.get('youtube_url', '')
                }
            )
            posts_created += 1
        
        self.stdout.write(
            self.style.SUCCESS(f'Successfully created {posts_created} dummy posts!')
        )
