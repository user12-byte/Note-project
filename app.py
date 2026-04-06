from flask import Flask, render_template, request, redirect, url_for
import sqlite3
import os
from werkzeug.utils import secure_filename

app = Flask(__name__)

DB_PATH = 'notes.db'
UPLOAD_FOLDER = 'static/uploads'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def get_categories():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT name FROM category")
    result = [row[0] for row in c.fetchall()]
    conn.close()
    return result


def get_messages(category_name):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT id FROM category WHERE name=?", (category_name,))
    row = c.fetchone()
    if not row:
        return []
    category_id = row[0]
    c.execute("SELECT id, content FROM message WHERE category_id=? ORDER BY created_at ASC", (category_id,))
    messages = c.fetchall()
    conn.close()
    return messages


def add_message(category_name, content):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT id FROM category WHERE name=?", (category_name,))
    row = c.fetchone()
    if not row:
        conn.close()
        return
    category_id = row[0]
    c.execute("INSERT INTO message (content, category_id) VALUES (?, ?)", (content, category_id))
    conn.commit()
    conn.close()


@app.route('/')
@app.route('/category/<name>')
def home(name='日记'):
    categories = get_categories()
    messages = get_messages(name)
    return render_template('index.html',
                           categories=categories,
                           current_category=name,
                           messages=messages)


@app.route('/send/<name>', methods=['POST'])
def send(name):
    content = request.form.get('content', '').strip()
    file = request.files.get('image')

    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)
        image_path = f"/static/uploads/{filename}"
        add_message(name, image_path)

    if content:
        add_message(name, content)

    return redirect(url_for('home', name=name))


@app.route('/delete_message/<int:msg_id>/<category>')
def delete_message(msg_id, category):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("DELETE FROM message WHERE id=?", (msg_id,))
    conn.commit()
    conn.close()
    return redirect(url_for('home', name=category))


@app.route('/add_category', methods=['POST'])
def add_category():
    name = request.form.get('new_category', '').strip()
    if name:
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        c.execute("INSERT OR IGNORE INTO category (name) VALUES (?)", (name,))
        conn.commit()
        conn.close()
    return redirect(url_for('home'))


@app.route('/delete_category/<name>')
def delete_category(name):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT id FROM category WHERE name=?", (name,))
    row = c.fetchone()
    if row:
        cat_id = row[0]
        c.execute("DELETE FROM message WHERE category_id=?", (cat_id,))
        c.execute("DELETE FROM category WHERE id=?", (cat_id,))
    conn.commit()
    conn.close()
    return redirect(url_for('home'))


@app.route('/search')
def search():
    keyword = request.args.get('q', '').strip()
    results = []
    if keyword:
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        query = """
            SELECT category.name, message.content 
            FROM message 
            JOIN category ON message.category_id = category.id 
            WHERE message.content LIKE ? 
            ORDER BY message.created_at ASC
        """
        c.execute(query, (f"%{keyword}%",))
        results = c.fetchall()
        conn.close()
    return render_template('search.html', keyword=keyword, results=results)


if __name__ == '__main__':
    app.run(debug=True)

