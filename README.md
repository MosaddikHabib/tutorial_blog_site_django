# Django Blog Site

A simple and clean blog platform built with Django, featuring an admin dashboard for easy content management and image upload capabilities.

## Features

- **Clean Black & White Theme**: Modern, minimalist design using Bootstrap
- **Admin Dashboard**: Easy-to-use Django admin interface for managing posts and categories
- **Image Support**: Upload featured images and multiple images per post
- **Category System**: Organize posts by categories
- **Responsive Design**: Works perfectly on desktop and mobile devices
- **SEO Friendly**: Clean URLs and proper meta tags

## Installation

1. **Clone or download the project files**

2. **Create a virtual environment** (recommended):
   ```bash
   python -m venv blog_env
   ```

3. **Activate the virtual environment**:
   - Windows: `blog_env\Scripts\activate`
   - macOS/Linux: `source blog_env/bin/activate`

4. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

5. **Run migrations**:
   ```bash
   python manage.py makemigrations
   python manage.py migrate
   ```

6. **Create a superuser** (admin account):
   ```bash
   python manage.py createsuperuser
   ```

7. **Run the development server**:
   ```bash
   python manage.py runserver
   ```

8. **Access the site**:
   - Frontend: http://127.0.0.1:8000/
   - Admin Dashboard: http://127.0.0.1:8000/admin/

## Usage

### Admin Dashboard

1. Go to `/admin/` and log in with your superuser credentials
2. **Categories**: Create categories to organize your posts
3. **Posts**: 
   - Create new blog posts
   - Add featured images
   - Upload additional images within posts
   - Set post status (Draft/Published)
   - Add excerpts for post previews

### Frontend

- **Home Page**: View all published posts in a clean grid layout
- **Category Pages**: Browse posts by category
- **Post Detail**: Read full posts with images and related content
- **Responsive Navigation**: Easy access to all sections

## Project Structure

```
blog_site/
├── blog/                    # Main blog app
│   ├── models.py           # Post and Category models
│   ├── views.py            # Frontend views
│   ├── admin.py            # Admin interface configuration
│   └── urls.py             # URL patterns
├── templates/blog/         # HTML templates
│   ├── base.html           # Base template
│   ├── post_list.html      # Home page
│   ├── post_detail.html    # Individual post page
│   └── category_posts.html # Category listing page
├── static/css/             # Custom CSS
│   └── style.css           # Black & white theme styles
├── media/                  # User uploaded files (created automatically)
├── requirements.txt        # Python dependencies
└── manage.py              # Django management script
```

## Customization

### Adding New Features

1. **Models**: Add new fields to `blog/models.py`
2. **Admin**: Update `blog/admin.py` to include new fields
3. **Views**: Add new views in `blog/views.py`
4. **Templates**: Create or modify templates in `templates/blog/`
5. **URLs**: Add new URL patterns in `blog/urls.py`

### Styling

- Modify `static/css/style.css` for custom styling
- The theme uses Bootstrap 5 with custom black & white styling
- All colors and fonts can be easily customized

## Production Deployment

For production deployment:

1. Set `DEBUG = False` in `settings.py`
2. Change `SECRET_KEY` to a secure random string
3. Configure proper database (PostgreSQL recommended)
4. Set up static file serving
5. Configure media file serving
6. Use environment variables for sensitive settings

## Dependencies

- **Django 4.2.7**: Web framework
- **Pillow 10.0.1**: Image processing
- **python-decouple 3.8**: Environment variable management

## License

This project is open source and available under the MIT License.
