from flask import Flask, request, redirect, render_template, session, flash
from flask_sqlalchemy import SQLAlchemy
import cgi

app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://blogz:blogz@localhost:8889/blogz'
app.config['SQLALCHEMY_ECHO'] = True
db = SQLAlchemy(app)
app.secret_key = 'j23oiIlkjAFcR'


class Entry(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(120))
    content = db.Column(db.String(1000))
    owner_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    def __init__(self, title, content, owner):
        self.title = title
        self.content = content
        self.owner = owner

class User(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True)
    password = db.Column(db.String(120))
    entries = db.relationship('Entry', backref='owner')

    def __init__(self, email, password):
        self.email = email
        self.password = password


@app.before_request
def require_login():
    allowed_routes = ['login', 'register', 'index', 'blog']
    if request.endpoint not in allowed_routes and 'email' not in session:
        return redirect('/login')

@app.route('/login', methods=['POST', 'GET'])
def login():

    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        user = User.query.filter_by(email=email).first()
        if user and user.password == password:
            session['email'] = email
            flash("Logged in")
            print(session)
            return redirect('/blog')
        else: 
            flash('User password is incorrect, or user does not exsist', 'error')

    #if request.method == 'GET':

    return render_template('login.html')


@app.route('/register', methods=['POST', 'GET'])
def register():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        verify = request.form['verify-password']

        # TODO - validate user's data

        existing_user = User.query.filter_by(email=email).first()
        if not existing_user:
            new_user = User(email, password)
            db.session.add(new_user)
            db.session.commit()
            session['email'] = email
            return redirect('/blog')
        else:
            # TODO - user better response messaging
            return "<h1>Duplicate user</h1>"

    return render_template('register.html')


@app.route('/logout')
def logout():
    del session['email']
    return redirect('/blog')


@app.route('/blog', methods=['GET'])
def blog():

    entry_id = request.args.get("id")
    if entry_id != None and int(entry_id) > 0:
        entry_id = int(entry_id)
        entry = Entry.query.filter_by(id=entry_id).first()
        return render_template('post.html',title="Blogz!", 
        entry=entry)

    user_id = request.args.get("user")
    if user_id != None and int(user_id) > 0:
        user_id = int(user_id)
        owner = User.query.filter_by(id=user_id).first()
        entries = Entry.query.filter_by(owner=owner).all()
        return render_template('singleUser.html',title="Blogz!", owner=owner, 
        entries=entries)

    entries = Entry.query.all()
    return render_template('blog.html',title="Blogz!", 
        entries=entries)

@app.route('/', methods=['GET'])
def index():
    
    usernames = User.query.all()

    return render_template('index.html',title="Blogz!", 
        usernames=usernames)


@app.route('/newpost', methods=['POST', 'GET'])
def newpost():

    #owner = User.query.filter_by(email=session['email']).first()
    owner = User.query.first()

    if request.method == 'POST':
        entry_title = request.form['title']
        entry_content = request.form['content']

        # Validate: make sure no fields are left empty
        if not entry_title or not entry_content:
            error_str = 'entry_title=' + entry_title + '&entry_content=' + entry_content
            if not entry_title: 
                error_str = error_str + '&error_title=Please fill in the title'
            if not entry_content:
                error_str = error_str + '&error_content=Please fill in the body'
            return redirect('/newpost?' + error_str)

        new_entry = Entry(entry_title, entry_content, owner)
        db.session.add(new_entry)
        db.session.commit()

        return redirect('/blog?id=' + str(new_entry.id))

    if not request.args.get("error_title") and not request.args.get("error_content"):
        return render_template('newpost.html')
    else:
        error_title = ''
        error_content = ''
        entry_title = ''
        entry_content = ''
        if request.args.get("error_title") != None:
            error_title = request.args.get("error_title")
            entry_content = request.args.get("entry_content")
        if request.args.get("error_content") != None:
            error_content = request.args.get("error_content")
            entry_title = request.args.get("entry_title")
        return render_template('newpost.html',
            error_title=error_title and cgi.escape(error_title, quote=True),
            error_content=error_content and cgi.escape(error_content, quote=True),
            entry_title=entry_title and cgi.escape(entry_title, quote=True),
            entry_content=entry_content and cgi.escape(entry_content, quote=True))

    return render_template('newpost.html')



# @app.route('/delete-entry', methods=['POST'])
# def delete_task():

#     entry_id = int(request.form['entry-id'])
#     entry = Entry.query.get(entry_id)
#     db.session.delete(entry)
#     db.session.commit()

#     return redirect('/')


if __name__ == '__main__':
    app.run()