#! /home/b51816/localpython/python3/bin/python3
import sqlite3
import os
from flask import  Flask, request, session, g, redirect, url_for, abort, render_template, flash
from contextlib import closing
# configuration

PROJECT_ROOT = os.path.dirname(os.path.realpath(__file__))
DATABASE = os.path.join(PROJECT_ROOT,'db','jay_flaskr.db')
DEBUG = True
SECRET_KEY = 'wait for select'
USERNAME = 'Jay'
PASSWORD = 'b51816'

# create app
app = Flask(__name__)
app.config.from_object(__name__)


def connect_db():
   print("Try to connect to database {0}".format(app.config['DATABASE']))
   return sqlite3.connect(app.config['DATABASE'])

def init_db():
   with closing(connect_db()) as db:
      with app.open_resource('jay_schema.sql',mode='r') as f:
         db.cursor().executescript(f.read())
      db.commit()

@app.before_request
def before_request():
   g.db = connect_db()

@app.teardown_request
def teardown_request(exception):
   db = getattr(g,'db',None)
   if db is not None:
      db.close()

@app.route('/')
def show_entries():
   cur = g.db.execute('select title, bom, description,explanation,solution,status from entries order by id desc')
   entries = [dict(title=row[0],bom=row[1],desc=row[2],expl=row[3],solu=row[4],status=row[5]) for row in cur.fetchall()]
   return render_template('show_entries.html',entries=entries)

@app.route('/add',methods=['POST'])
def add_entry():
   print("adding entry")
   if not session.get('logged_in'):
      abort(401)
   print(type(g))
   g.db.execute('insert into entries (title,bom,description,explanation, solution,status) values (?,?,?,?,?,?)',[request.form['title'],request.form['bom'],request.form['description'],request.form['explanation'], request.form['solution'],request.form['status']])
   g.db.commit()
   flash("New entry was successfully posted")
   return redirect(url_for('show_entries'))

@app.route('/login',methods=['GET','POST'])
def login():
   error = None
   if request.method == 'POST':
      if request.form['username'] != app.config['USERNAME']:
         error = 'Invalid username'
      elif request.form['password'] != app.config['PASSWORD']:
         error = 'Invalid password'
      else:
         session['logged_in'] = True
         flash('Successfully Logged in')
         return redirect(url_for('show_entries'))
   return render_template('login.html',error=error)

@app.route('/logout')
def logout():
   session.pop('logged_in',None)
   flash('Logged Out')
   return redirect(url_for('show_entries'))

if __name__ =='__main__':
   app.run(debug=app.config['DEBUG'],host='0.0.0.0')
   

