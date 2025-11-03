# Blog Site - Complete Setup Guide ✅

## 🎯 What's Been Fixed & Improved

### ✅ Virtual Environment Created
- Virtual environment: `venv_blog`
- Clean installation ready

### ✅ Content Editor Improvements
- **Fixed height**: 500px content box (no resizing)
- **MS Word-like controls**: Full toolbar with all formatting options
- **Image upload IN content**: Upload images directly in the editor
- **Rich text formatting**: Bold, italic, colors, fonts, sizes, alignment, lists, tables

### ✅ Simplified Post Creation
- **Only 2 upload options**:
  1. **Cover/Banner Photo**: Upload button for post cover image
  2. **Content Box**: Upload images inside content using the editor
- **YouTube URL**: Optional field for video embeds
- **No video file upload**: Removed to keep it simple

## 📦 Setup Instructions

### 1. Activate Virtual Environment

**Windows:**
```bash
venv_blog\Scripts\activate
```

**Mac/Linux:**
```bash
source venv_blog/bin/activate
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

Or install packages manually:
```bash
pip install Django==5.2.1 Pillow==11.1.0 django-ckeditor==6.7.0 django-js-asset==3.1.2
```

### 3. Run Migrations

```bash
python manage.py migrate
```

### 4. Create Admin User (if not exists)

```bash
python manage.py createsuperuser
```

### 5. Start Server

```bash
python manage.py runserver
```

## 🎨 Content Editor Features

### MS Word-like Controls:
- ✅ **Bold, Italic, Underline, Strike**
- ✅ **Fonts & Font Sizes**
- ✅ **Text Colors & Background Colors**
- ✅ **Text Alignment** (Left, Center, Right, Justify)
- ✅ **Lists** (Numbered & Bulleted)
- ✅ **Links**
- ✅ **Images** (Upload directly in content)
- ✅ **Tables**
- ✅ **Undo/Redo**
- ✅ **Copy, Paste, Cut**
- ✅ **Find & Replace**

## 📝 How to Create Posts

1. Go to **http://127.0.0.1:8000/manage/create-post/**
2. Fill in **Title** and **Category**
3. Write **Excerpt** (brief description)
4. **Content Box**: Click and type to get MS Word-like toolbar
5. **Upload Cover Photo**: Use the "Cover Photo / Banner" button
6. **Add YouTube Video** (optional): Paste URL if needed
7. Set **Status** (Draft/Published)
8. Click **Create Post**

### Tips:
- **Images in content**: Click "Image" button in editor → Browse Server → Upload
- **Format text**: Select text → Choose bold, italic, colors, etc.
- **Cover photo**: Use the "Cover Photo" upload button (not in content editor)

## 🔗 URLs

- **Frontend**: http://127.0.0.1:8000/
- **Custom Admin**: http://127.0.0.1:8000/manage/
- **Django Admin**: http://127.0.0.1:8000/admin/
- **Create Post**: http://127.0.0.1:8000/manage/create-post/

## 🎉 Features

- ✅ Virtual environment ready
- ✅ Fixed-size content editor (500px height)
- ✅ MS Word-like rich text editing
- ✅ Image upload in content editor
- ✅ Cover/banner photo upload
- ✅ YouTube video embeds
- ✅ Clean, simple interface

Enjoy your professional blog site! 🚀
