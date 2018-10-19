from views import db
from _config import DATABASE_PATH

import sqlite3
from datetime import datetime

with sqlite3.connect(DATABASE_PATH) as connection:
    cursor = connection.cursor()

    # temporarily change the name of the databse
    cursor.execute("""ALTER TABLE tasks RENAME TO old_tasks""")

    #  Create new schema
    db.create_all()

    # Retrieve data from the old tasks table
    cursor.execute("""SELECT name, due_date, priority, status
    FROM old_tasks ORDER BY task_id ASC
    """)
    task_data = [(row[0], row[1], row[2], row[3],
                  datetime.now(), 1) for row in cursor.fetchall()
                 ]
    cursor.executemany("""INSERT INTO tasks(name, due_date, priority, status,
    posted_date, user_id) VALUES (?,?,?,?,?,?)""", task_data)

    # Drop table old_tasks
    cursor.execute("""DROP TABLE IF EXISTS old_tasks""")
