import sqlite3

from flask import Flask, render_template, \
    session, url_for, request, redirect, flash

import functools

# load config
app = Flask(__name__)
app.config.from_object('_config')


# helper functions
def connect_db():
    return sqlite3.connect(app.config['DATABASE_PATH'])

def login_required(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        if 'logged_in' in session:
            return func(*args, **kwargs)
        else:
            flash('You need to login first')
            redirect(url_for('login'))
    return wrapper


@app.route('/logout')
def logout():
    session.pop('logged_in')
    flash('Goodbye !')
    return redirect(url_for('login'))


@app.route('/', methods=['GET', 'POST'])
def login():
    if request.method=='POST':
        if request.form['username'] != app.config['USERNAME and'] or request.form['password'] != app.config['PASSWORD']:
            error = 'Invalid credentials. Please try again.'
            return render_template('login.html', error=error)
        else:
            session['logged_in'] = True
            flash('Welcome')
            redirect(url_for('tasks'))
    return render_template('login.html')

