import sqlite3

from flask import Flask, render_template, \
    session, url_for, request, redirect, flash, g

from forms import AddTaskForm

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


@app.route('/logout/')
def logout():
    session.pop('logged_in')
    flash('Goodbye !')
    return redirect(url_for('login'))


@app.route('/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        if request.form['username'] != app.config['USERNAME'] or request.form['password'] != app.config['PASSWORD']:
            error = 'Invalid credentials. Please try again.'
            return render_template('login.html', error=error)
        else:
            session['logged_in'] = True
            flash('Welcome')
            return redirect(url_for('tasks'))
    return render_template('login.html')


# Task related endpoints and functions
# View all tasks
@app.route('/tasks/')
@login_required
def tasks():
    g.db = connect_db()
    cursor = g.db.execute("""SELECT name, due_date, priority, task_id 
    FROM tasks WHERE status=1""")
    open_tasks = [{'name': row[0],
                   'due_date': row[1],
                   'priority': row[2],
                   'task_id': row[3]}
                  for row in cursor.fetchall()]
    cursor = g.db.execute("""SELECT name, due_date, priority, task_id 
       FROM tasks WHERE status=0""")
    closed_tasks = [{'name': row[0],
                     'due_date': row[1],
                     'priority': row[2],
                     'task_id': row[3]} for row in cursor.fetchall()
                    ]
    g.db.close()
    return render_template('tasks.html', form=AddTaskForm(request.form), open_tasks=open_tasks, closed_tasks=closed_tasks )


# Add a new task
@app.route('/add/', methods=['POST'])
@login_required
def new_task():
    g.db = connect_db()
    name = request.form['name']
    due_date = request.form['due_date']
    priority = int(request.form['priority'])
    if not name or not due_date or not priority:
        flash('All fields are compulsory')
        return redirect(url_for('tasks'))
    else:
        g.db.execute('INSERT INTO tasks(name, due_date, priority, status) VALUES (?,?,?,1)',
                     (name, due_date, priority)) # parameterized insertion to prevent sql injection
        g.db.commit()
        g.db.close()
        flash('New task created successfully.')
        return redirect(url_for('tasks'))


# Mark tasks as complete
@app.route('/complete/<int:task_id>')
@login_required
def complete(task_id):
    print('taskid {}'.format(task_id))
    g.db = connect_db()
    g.db.execute('UPDATE tasks SET status = 0 where task_id ='+str(task_id))
    g.db.commit()
    g.db.close()
    flash('Task marked complete')
    return redirect(url_for('tasks'))


# Delete tasks
@app.route('/delete/<int:task_id>')
@login_required
def delete_entry(task_id):
    g.db = connect_db()
    g.db.execute('DELETE FROM tasks WHERE task_id ='+str(task_id))
    g.db.commit()
    g.db.close()
    flash('Task deleted successfully.')
    return redirect(url_for('tasks'))
