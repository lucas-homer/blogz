from flask import Flask, request, redirect, render_template, session, flash
from flask_sqlalchemy import SQLAlchemy 

app = Flask(__name__)
app.config['DEBUG'] = True

# Note: the connection string after :// contains the following info:
# user:password@server:portNumber/databaseName

app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://blogz:gouda@localhost:8889/blogz'
app.config['SQLALCHEMY_ECHO'] = True
db = SQLAlchemy(app)
app.secret_key = '2bEei7qbbtbnowUnbdve'



class Blog(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120))
    entry = db.Column(db.String(240))
    owner_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    def __init__(self, name, entry, owner):
        self.name = name
        self.entry = entry 
        self.owner = owner

class User(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(120), unique=True)
    password = db.Column(db.String(120))
    blogs = db.relationship('Blog', backref='owner')

    def __init__(self, username, password):
        self.username = username
        self.password = password
        


@app.before_request
def require_login():
    allowed_routes = ['login', 'signup', 'list_blogs', 'index']

    if request.endpoint not in allowed_routes and 'username' not in session:
        return redirect('/login')


@app.route('/')
def index():
    users = User.query.all()

    return render_template('index.html', users=users)

@app.route('/blog')
def list_blogs():
    
    id_exists = request.args.get('id')
    user_exists = request.args.get('user')
    author = User.query.filter_by(id = user_exists).first

    if id_exists:
        single_blog = Blog.query.filter_by(id = id_exists).first()
        return render_template('singlepost.html', blog=single_blog)
    if user_exists:
        single_user_posts = Blog.query.filter_by(owner_id = user_exists).all()
        return render_template('singleuser.html', blogs = single_user_posts)
    else:   
        blogs = Blog.query.all()
        return render_template('blog.html', blogs=blogs)


@app.route('/newpost', methods=['POST', 'GET'])
def new_post():

    owner = User.query.filter_by(username=session['username']).first()

    if request.method == 'GET':
        return render_template('newpost.html')

    elif request.method == 'POST':
        name = request.form['name']
        entry = request.form['entry']
        name_error = ''
        entry_error = ''

        if "" == name:
            name_error = 'Title your blog'
            name = ''
        if "" == entry:
            entry_error = 'You have to write something!'
            entry = ''
    
        if name_error or entry_error:
            return render_template('newpost.html', name=name, entry=entry, name_error=name_error, entry_error=entry_error)

        else: 
            name = request.form['name']
            entry = request.form['entry']
            new_blog = Blog(name,entry,owner)
            db.session.add(new_blog)
            db.session.commit()
            blog = Blog.query.filter_by(name=name).first()
            return render_template('singlepost.html', blog=blog)

@app.route('/login', methods=['POST', 'GET'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()
        if user and user.password == password:
            session['username'] = username
            flash("Logged in")
            return redirect('/newpost')
        if not user:
            flash('Username does not exist', 'error')
        if user.password != password:
            flash('Password incorrect', 'error')

    return render_template('login.html')


def valid_input(i):
    if len(i) >= 3 and not ' ' in i:
        return True
    else:
        return False

@app.route('/signup', methods=['POST', 'GET'])
def signup():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        verify = request.form['verify']

        # todo - validate user's data

        existing_user = User.query.filter_by(username=username).first()
        if not existing_user:
            if len(username) == 0 or len(password) == 0 or len(verify) == 0:
                flash('Username, Password, and Verify Password must all be completed', 'error')
                
            elif not valid_input(username):
                flash('Username must be at least 3 characters long and contain no spaces', 'error')
                
            elif not valid_input(password):
                flash('Password must be at least 3 characters long and contain no spaces', 'error')
                
            elif verify != password:
                flash('Passwords do no match', 'error')
                return render_template('signup.html')

            else:
                new_user = User(username, password)
                db.session.add(new_user)
                db.session.commit()
                session['username'] = username
                return redirect('/newpost')

        else:
            # todo - user better response messaging
            flash('User already exists', 'error')
            return render_template('signup.html')

    return render_template('signup.html')


@app.route('/logout')
def logout():
    del session['username']
    return redirect('/blog')




if __name__ == '__main__':
    app.run()

