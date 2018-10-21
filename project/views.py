import functools

from flask import Flask, render_template, session, url_for, request, redirect, flash
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.exc import IntegrityError
import datetime

from forms import AddTaskForm, RegistrationForm, LoginForm

# load config
app = Flask(__name__)
app.config.from_object('_config')
db = SQLAlchemy(app)

from models import Task, User


def login_required(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        if 'logged_in' in session:
            return func(*args, **kwargs)
        else:
            flash('You need to login first')
            return redirect(url_for('login'))
    return wrapper


@app.route('/logout/')
@login_required
def logout():
    session.pop('logged_in', None)
    session.pop('user_id', None)
    flash('Goodbye !')
    return redirect(url_for('login'))


@app.route('/', methods=['GET', 'POST'])
def login():
    error = None
    form = LoginForm(request.form)
    if request.method == 'POST':
        if form.validate_on_submit():
            user = User.query.filter_by(name=form.name.data).first()
            if user is not None and user.password == form.password.data:
                session['logged_in'] = True
                session['user_id'] = user.id
                flash('Welcome')
                return redirect(url_for('tasks'))
            else:
                error = 'Invalid credentials. Please try again.'
        else:
            error = 'Please fill all fields'
    return render_template('login.html', form=form, error=error)


# Task related endpoints and functions
# View all tasks
@app.route('/tasks/')
@login_required
def tasks():
    return render_template('tasks.html', form=AddTaskForm(request.form), open_tasks=open_tasks(),
                           closed_tasks=closed_tasks())


# Add a new task
@app.route('/add/', methods=['GET', 'POST'])
@login_required
def new_task():
    error = None
    form = AddTaskForm(request.form)
    # validate_on_submit takes care that form is submitted only on POST
    if request.method == 'POST':
        if form.validate_on_submit():
            db.session.add(Task(form.name.data,
                                form.due_date.data,
                                form.priority.data,
                                datetime.datetime.utcnow(),
                                1,
                                session['user_id']))  # Every task is mapped to usr_id 1 temporarily
            db.session.commit()
            flash('New task was successfully created.')
            return redirect(url_for('tasks'))
    return render_template('tasks.html',
                           form=form, error=error, open_tasks=open_tasks(), closed_tasks=closed_tasks())


# Mark tasks as complete
@app.route('/complete/<int:task_id>')
@login_required
def complete(task_id):
    db.session.query(Task).filter_by(task_id=task_id).update({"status": 0})
    db.session.commit()
    flash('Task marked complete.')
    return redirect(url_for('tasks'))


# Delete tasks
@app.route('/delete/<int:task_id>')
@login_required
def delete_entry(task_id):
    db.session.query(Task).filter_by(task_id=task_id).delete()
    db.session.commit()
    flash('Task deleted successfully.')
    return redirect(url_for('tasks'))


# User registration
@app.route('/register/', methods=['GET', 'POST'])
def register():
    error = None
    form = RegistrationForm(request.form)
    if form.validate_on_submit():
        try:
            db.session.add(User(form.name.data,
                                form.email.data,
                                form.password.data))
            db.session.commit()
            flash('Thanks for registering. Please login')
            return redirect(url_for('login'))
        except IntegrityError:
            error = 'Username and/or email already exists'
            return render_template('register.html', form=form, error=error)
    return render_template('register.html', form=form, error=error)


def flash_errors(form):
    for field, errors in form.errors.items():
        for error in errors:
            flash(u'Error in {} field - {} error'.
                  format(getattr(form, field).label.text), error)


# Helper functions
def open_tasks():
    return db.session.query(Task).filter_by(status=1).order_by(Task.due_date.asc())


def closed_tasks():
    return db.session.query(Task).filter_by(status=0).order_by(Task.due_date.asc())
