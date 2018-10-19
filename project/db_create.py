from views import db
from models import Task
from datetime import date

# Create the database tables
db.create_all()

#  insert data
# db.session.add(Task("Finish the tutorial", date(2018, 10, 20), 10, 1))
# db.session.add(Task("Finish the tutorial", date(2018, 10, 30), 10, 1))

# Commit the changes
db.session.commit()

