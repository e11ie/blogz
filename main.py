from flask import Flask, request, redirect, render_template
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://build-a-blog:build-a-blog@localhost:8889/build-a-blog'
app.config['SQLALCHEMY_ECHO'] = True
db = SQLAlchemy(app)


class Entry(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(120))
    content = db.Column(db.String(1000))

    def __init__(self, title, content):
        self.title = title
        self.content = content


@app.route('/', methods=['POST', 'GET'])
def index():

    if request.method == 'POST':
        entry_title = request.form['title']
        entry_content = request.form['content']
        new_entry = Entry(entry_title, entry_content)
        db.session.add(new_entry)
        db.session.commit()

    entries = Entry.query.all()
    return render_template('blog.html',title="Build a Blog!", 
        entries=entries)


# @app.route('/delete-entry', methods=['POST'])
# def delete_task():

#     entry_id = int(request.form['entry-id'])
#     entry = Entry.query.get(entry_id)
#     db.session.delete(entry)
#     db.session.commit()

#     return redirect('/')


if __name__ == '__main__':
    app.run()