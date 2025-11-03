from django.core.management.base import BaseCommand
from django.utils.text import slugify
from blog.models import Post


class Command(BaseCommand):
    help = 'Backfill missing slugs for existing posts by slugifying the title and ensuring uniqueness.'

    def handle(self, *args, **options):
        posts = Post.objects.filter(slug__isnull=True) | Post.objects.filter(slug='')
        total = posts.count()
        if total == 0:
            self.stdout.write(self.style.SUCCESS('No posts with missing slugs found.'))
            return

        self.stdout.write(f'Backfilling slugs for {total} posts...')
        for post in posts:
            base_slug = slugify(post.title) or 'post'
            slug = base_slug
            i = 1
            while Post.objects.filter(slug=slug).exclude(pk=post.pk).exists():
                slug = f"{base_slug}-{i}"
                i += 1
            post.slug = slug
            post.save(update_fields=['slug'])
            self.stdout.write(f'  - {post.pk}: {post.title!r} -> {post.slug}')

        self.stdout.write(self.style.SUCCESS('Done.'))
