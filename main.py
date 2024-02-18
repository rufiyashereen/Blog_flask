from flask import Flask, request, redirect
from flask import url_for
from flask import render_template
from flask import session
from flask_mysqldb import MySQL
from flask import *
import yaml
app = Flask(__name__)


db = yaml.load(open('db.yaml'), Loader=yaml.SafeLoader)
app.config['MYSQL_HOST'] = db['mysql_host']
app.config['MYSQL_USER'] = db['mysql_user']
app.config['MYSQL_PASSWORD'] = db['mysql_password']
app.config['MYSQL_DB'] = db['mysql_db']

mysql = MySQL(app)


@app.route('/login', methods=['POST', 'GET'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        cur = mysql.connection.cursor()
        cur.execute(f'SELECT user_id FROM users WHERE username = "{username}"')
        userid = cur.fetchone()  # Fetch the user_id
        cur.close()
        if userid:
            return redirect(url_for('home', user_id=userid[0]))  # Pass the user_id to the home route
        else:
            return redirect(url_for('signup'))
    return render_template('login.html')


        


@app.route('/', methods=['POST', 'GET'])
def signup():
    if request.method == 'POST':
        userdetails = request.form
        fullname = userdetails['fullname']
        email = userdetails['email']
        password = userdetails['password']
        username = userdetails['username']
        bio = userdetails['bio']
        # id = userdetails['user_id']
        cur = mysql.connection.cursor()
         
        cur.execute('insert into users (full_name, username,email,passwrd,bio) values(%s, %s, %s, %s, %s)', (fullname, username, email, password, bio)) 
        mysql.connection.commit()
        user_id = cur.lastrowid
        cur.close()
        return redirect(url_for('home', user_id=user_id))    
    return render_template('signup.html')


@app.route('/home/<int:user_id>')
def home(user_id):
    cur = mysql.connection.cursor()
    cur.execute('SELECT title, content FROM posts WHERE user_id = %s', (user_id,))
    blog_posts = cur.fetchall()
    cur.close()
    cur = mysql.connection.cursor()
    cur.execute("select username from users where user_id = %s", (user_id,))
    username = cur.fetchone()[0] 
    cur.close()
    return render_template('home.html', user_id=user_id, blog_posts=blog_posts, username=username)


@app.route('/createblog/<int:user_id>', methods=['POST', 'GET'])
def createblog(user_id):
    if request.method == 'POST':
        userdetails = request.form
        userid = user_id
        title = userdetails['title']
        content = userdetails['content']
        cur = mysql.connection.cursor()
        cur.execute("insert into posts(user_id, title, content) values(%s, %s, %s)", (userid, title, content))
        mysql.connection.commit()
        cur.close()
        # Redirect to blog.html
        return redirect(url_for('home', user_id=user_id))
    # If GET request or if form submission fails, stay on the same page
    return render_template('blog.html', user_id=user_id)


if __name__ == '__main__':
    app.run(debug=True)
