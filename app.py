import os
import json
from flask import Flask, render_template, request, redirect, url_for, flash
from werkzeug.utils import secure_filename
from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, FileField, SelectField
from wtforms.validators import DataRequired
from config import Config
import re

app = Flask(__name__)
app.config.from_object(Config)
app.secret_key = 'secret'

# Formulario para crear o editar blogs
class BlogForm(FlaskForm):
    title = StringField('Title', validators=[DataRequired()])
    content = TextAreaField('Content', validators=[DataRequired()])
    image = FileField('Image')
    video = FileField('Video')
    text_color = SelectField('Text Color', choices=[('black', 'Black'), ('white', 'White'), ('red', 'Red'), ('blue', 'Blue')])
    background_color = SelectField('Background Color', choices=[('white', 'White'), ('black', 'Black'), ('yellow', 'Yellow'), ('green', 'Green')])

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']

def generate_slug(title):
    # Convertir a minúsculas
    slug = title.lower()
    # Reemplazar espacios por guiones
    slug = re.sub(r'\s+', '-', slug)
    # Eliminar caracteres que no sean letras, números o guiones
    slug = re.sub(r'[^\w\-]', '', slug)
    return slug

# Función para guardar un blog en la carpeta 'sites/'
def save_blog_as_html(blog, blog_id):
    filename = secure_filename(blog['title']) + ".html"
    filepath = os.path.join('sites', filename)

    # Crear el archivo HTML con el contenido del blog
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(render_template('blog_template.html', blog=blog, blog_id=blog_id))

# Ruta principal
@app.route('/')
def home():
    with open('blogs.json', 'r') as f:
        blogs = json.load(f)
    return render_template('home.html', blogs=blogs)

@app.route('/blog/<string:slug>')
def view_blog(slug):
    with open('blogs.json', 'r') as f:
        blogs = json.load(f)
    
    # Buscar el blog por su slug
    blog = next((blog for blog in blogs if blog['slug'] == slug), None)
    
    if blog is None:
        flash('Blog not found!')
        return redirect(url_for('home'))
    
    return render_template('blog_template.html', blog=blog)

@app.route('/new', methods=['GET', 'POST'])
def new_blog():
    form = BlogForm()
    if form.validate_on_submit():
        slug = generate_slug(form.title.data)
        new_blog = {
            "title": form.title.data,
            "slug": slug,  # Guardar el slug
            "content": form.content.data,
            "text_color": form.text_color.data,
            "background_color": form.background_color.data,
            "image": None,
            "video": None
        }

        if form.image.data and allowed_file(form.image.data.filename):
            filename = secure_filename(form.image.data.filename)
            form.image.data.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            new_blog['image'] = filename

        if form.video.data and allowed_file(form.video.data.filename):
            filename = secure_filename(form.video.data.filename)
            form.video.data.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            new_blog['video'] = filename

        with open('blogs.json', 'r+') as f:
            blogs = json.load(f)
            blogs.append(new_blog)
            blog_id = len(blogs)
            f.seek(0)
            json.dump(blogs, f)

        # Guardar el blog como archivo HTML en la carpeta 'sites/'
        save_blog_as_html(new_blog, blog_id)

        flash('Blog created successfully!')
        return redirect(url_for('home'))
    return render_template('new_blog.html', form=form)

# Editar un blog existente
@app.route('/edit/<int:blog_id>', methods=['GET', 'POST'])
def edit_blog(blog_id):
    form = BlogForm()
    with open('blogs.json', 'r') as f:
        blogs = json.load(f)
    blog = blogs[blog_id - 1]

    if request.method == 'GET':
        form.title.data = blog['title']
        form.content.data = blog['content']
        form.text_color.data = blog['text_color']
        form.background_color.data = blog['background_color']

    if form.validate_on_submit():
        blog['title'] = form.title.data
        blog['content'] = form.content.data
        blog['text_color'] = form.text_color.data
        blog['background_color'] = form.background_color.data

        if form.image.data and allowed_file(form.image.data.filename):
            filename = secure_filename(form.image.data.filename)
            form.image.data.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            blog['image'] = filename

        if form.video.data and allowed_file(form.video.data.filename):
            filename = secure_filename(form.video.data.filename)
            form.video.data.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            blog['video'] = filename

        with open('blogs.json', 'w') as f:
            json.dump(blogs, f)

        # Guardar los cambios en el archivo HTML correspondiente
        save_blog_as_html(blog, blog_id)

        flash('Blog updated successfully!')
        return redirect(url_for('home'))
    return render_template('edit_blog.html', form=form, blog_id=blog_id)

if __name__ == '__main__':
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    os.makedirs('sites', exist_ok=True)  # Crear la carpeta 'sites' si no existe
    app.run(debug=True)
