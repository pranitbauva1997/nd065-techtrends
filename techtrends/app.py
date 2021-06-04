import sqlite3

from flask import Flask, jsonify, json, render_template, request, url_for, redirect, flash
from werkzeug.exceptions import abort

class DB:
    def __init__(self):
        self.DB_NAME = 'database.db'
        self.no_of_connections = 0

    # Function to get a database connection.
    # This function connects to database with the name `database.db`
    def new_db_connection(self):
        connection = sqlite3.connect(self.DB_NAME)
        connection.row_factory = sqlite3.Row
        self.no_of_connections = self.no_of_connections + 1
        print(self.no_of_connections)
        return connection

    # Function to close a database connection
    def close_db_connection(self, connection):
        connection.close()
        self.no_of_connections = self.no_of_connections - 1

    # Function to get database metrics which include no of posts
    # and no of concurrent database connections
    def get_db_metrics(self):
        connection = self.new_db_connection()
        post_count = connection.execute('SELECT COUNT(id) FROM posts').fetchone()
        self.close_db_connection(connection)
        return post_count['COUNT(id)'], self.no_of_connections

    # Function to get a post using its ID from database
    def get_post(self, post_id):
        connection = self.new_db_connection()
        post = connection.execute('SELECT * FROM posts WHERE id = ?',
                        (post_id,)).fetchone()
        self.close_db_connection(connection)
        return post

    # Function to get all posts from database
    def get_all_posts(self):
        connection = self.new_db_connection()
        posts = connection.execute('SELECT * FROM posts').fetchall()
        self.close_db_connection(connection)
        return posts

    # Function to insert a post (title, content) into database
    def insert_post(self, title, content):
        connection = self.new_db_connection()
        connection.execute('INSERT INTO posts (title, content) VALUES (?, ?)',
                         (title, content))
        connection.commit()
        self.close_db_connection()


# Define the Flask application
app = Flask(__name__)
app.config['SECRET_KEY'] = 'your secret key'
db = DB()

# Define healthcheck endpoint
@app.route('/healthz')
def healthz():
    return {"result": "OK - healthy"}

@app.route('/metrics')
def metrics():
    post_count, db_connection_count = db.get_db_metrics()
    response = {
        'post_count': post_count,
        'db_connection_count': db_connection_count,
    }
    return response

# Define the main route of the web application 
@app.route('/')
def index():
    posts = db.get_all_posts()
    return render_template('index.html', posts=posts)

# Define how each individual article is rendered 
# If the post ID is not found a 404 page is shown
@app.route('/<int:post_id>')
def post(post_id):
    post = db.get_post(post_id)
    if post is None:
      return render_template('404.html'), 404
    else:
      return render_template('post.html', post=post)

# Define the About Us page
@app.route('/about')
def about():
    return render_template('about.html')

# Define the post creation functionality 
@app.route('/create', methods=('GET', 'POST'))
def create():
    if request.method == 'POST':
        title = request.form['title']
        content = request.form['content']

        if not title:
            flash('Title is required!')
        else:
            db.insert_post(title, content)
            return redirect(url_for('index'))

    return render_template('create.html')

# start the application on port 3111
if __name__ == "__main__":
   app.run(host='0.0.0.0', port='3111')
