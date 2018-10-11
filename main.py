from flask import Flask, request, redirect, render_template, session, flash
from flask_sqlalchemy import SQLAlchemy
import cgi

app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://build-a-blog:build-a-blog@localhost:8889/build-a-blog'
app.config['SQLALCHEMY_ECHO'] = True
db = SQLAlchemy(app)
app.secret_key = 'j23oiIlkjAFcR'


class Entry(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(120))
    content = db.Column(db.String(1000))

    def __init__(self, title, content):
        self.title = title
        self.content = content


@app.route('/blog')
def index():

    entries = Entry.query.all()
    return render_template('blog.html',title="Build a Blog!", 
        entries=entries)


@app.route('/newpost', methods=['POST', 'GET'])
def newpost():

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

        new_entry = Entry(entry_title, entry_content)
        db.session.add(new_entry)
        db.session.commit()

        return redirect('/blog')

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