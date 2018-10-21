import os
import unittest

from views import app, db
from _config import basedir
from models import User, Task

TEST_DB = 'test.db'


class AllTests(unittest.TestCase):

    #### Setup and teardown #####
    # executed prior to each test
    def setUp(self):
        app.config['TESTING'] = True
        app.config['WTF_CSRF_ENABLED'] = False
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + \
                                                os.path.join(os.path.abspath(basedir), TEST_DB)
        self.app = app.test_client()
        db.create_all()

    # executed after each test
    def tearDown(self):
        db.session.remove()
        db.drop_all()

    # def test_user_setup(self):
    #     new_user = User('michael', 'michael@mherman.org', 'michaelherman')
    #     db.session.add(new_user)
    #     db.session.commit()

    # User data can be saved in db user in SQLAlchemy
    def test_users_can_register(self):
        new_user = User('michael', 'michael@mherman.org', 'michaelherman')
        db.session.add(new_user)
        db.session.commit()
        test = db.session.query(User).all()
        for t in test:
            assert t.name == 'michael'

    ### Login ###
    # user form is present
    def test_login_form_is_present(self):
        response = self.app.get('/')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Please sign in to access your task list', response.data)

    # Modularize login test functionality
    def login(self, name, password):
        return self.app.post('/', data=dict(name=name, password=password),
                             follow_redirects=True)

    # Non registered users cannot login
    def test_users_cannot_login_unless_registered(self):
        response = self.login('foo', 'baar')
        self.assertIn(b'Invalid credentials. Please try again.', response.data)
        self.login('rahuld', '123456')
        self.assertIn(b'Invalid credentials. Please try again.', response.data)

    # Registered users can login
    def test_registered_users_can_login(self):
        response = self.login('rahuldalal', '123456')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Welcome', response.data)

    ### Register users ###

    # Register new user
    def register(self, name, email, password, confirm):
        return self.app.post('/register/', data=dict(name=name, email=email, password=password,
                                                     confirm=confirm), follow_redirects=True)

    def register_form_is_present_on_register_page(self):
        response = self.app.get('/register/')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Please register to access the task list.', response.data)

    def test_register_new_user(self):
        response = self.register('test_user', 'test@xyz.com', 'test123', 'test123')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Thanks for registering. Please login', response.data)

    # Newly registered user should be able to login
    def test_new_registered_user_can_login(self):
        self.register('test_user', 'test@xyz.com', 'test123', 'test123')
        response = self.login('test_user', 'test123')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Welcome', response.data)

    # Invalid form data should give errors
    def test_invalid_username(self):
        response = self.register('test', 'test@xyz.com', '123456', '123456')
        self.assertIn(b'Field must be between 6 and 25 characters long.', response.data)

    def test_invalid_email_1(self):
        response = self.register('test_user', 'testxyz.com', '123456', '123456')
        self.assertIn(b'Invalid email address.', response.data)

    def test_invalid_email_2(self):
        response = self.register('test_user', 'testxyzcom', '123456', '123456')
        self.assertIn(b'Invalid email address.', response.data)

    def test_invalid_email_3(self):
        response = self.register('test_user', 'testxyz.com', '123456', '123456')
        self.assertIn(b'Invalid email address.', response.data)

    def test_invalid_password(self):
        response = self.register('test_user', 'test@xyz.com', '12345', '12345')
        self.assertIn(b'Field must be between 6 and 40 characters long.', response.data)

    def test_pwd_dont_match(self):
        response = self.register('test_user', 'test@xyz.com', '123456', '1234567')
        self.assertIn(b'Passwords must match', response.data)

    def test_registered_user_get_registration_error(self):
        self.register('michael', 'michael@realpython.com', '123456', '123456')
        response = self.register('michael', 'michael@realpython.com', '123456', '123456')
        self.assertIn(b'Username and/or email already exists', response.data)

    # ---Logout--- #
    def logout(self):
        return self.app.get('/logout/', follow_redirects=True)

    def test_logged_in_users_can_logout(self):
        self.register('test_user', 'test@xyz.com', 'test123', 'test123')
        self.login('test_user', 'test123')
        response = self.logout()
        self.assertIn(b'Goodbye !', response.data)

    def test_not_logged_in_users_cannot_logout(self):
        response = self.logout()
        self.assertNotIn(b'Goodbye !', response.data)

    # ---Access task list--- #
    def test_logged_in_users_can_access_tasks_page(self):
        self.register('test_user', 'test@xyz.com', '123456', '123456')
        response = self.login('test_user', 'test@xyz.com')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Welcome to FlaskTaskr', response.data)

    def test_not_logged_in_users_cannot_access_tasks_page(self):
        response = self.app.get('/tasks/', follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'You need to login first', response.data)

    # ---CRUD for tasks --- #
    # No need to register from the endpoint as it is already tested
    def create_user(self, name, email, password):
        db.session.add(User(name, email, password))
        db.session.commit()

    # Helper function to create task
    def create_task(self, name, due_date, priority):
        return self.app.post('/add/', data=dict(
            name=name,
            due_date=due_date,
            priority=priority), follow_redirects=True)

    # Assume user is logged in as that can be tested separately
    def test_users_add_create_task(self):
        self.create_user('test_user', 'test@xyz.com', '123456')
        self.login('test_user', '123456')
        response = self.create_task('Go to the bank', '10/08/2019', '1')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'New task was successfully created.', response.data)

    # TODO Write test case with invalid arguments for each field
    def test_users_cannot_add_tasks_when_error(self):
        self.create_user('test_user', 'test@xyz.com', '123456')
        self.login('test_user', '123456')
        response = self.create_task('Go to the bank', '', '1')
        self.assertEqual(response.status_code, 200)
        self.assertNotIn(b'New task was successfully created.', response.data)

    # Users can complete tasks
    def test_users_can_complete_tasks(self):
        self.create_user('test_user', 'test@xyz.com', '123456')
        self.login('test_user', '123456')
        self.create_task('Go to the bank', '10/08/2019', '1')
        response = self.app.get('/complete/1', follow_redirects=True)
        self.assertIn(b'Task marked complete', response.data)
        task = db.session.query(Task).filter_by(task_id=1).first()
        self.assertEqual(task.status, 0)

    # Users can delete tasks
    def test_users_can_delete_tasks(self):
        self.create_user('test_user', 'test@xyz.com', '123456')
        self.login('test_user', '123456')
        self.create_task('Go to the bank', '10/08/2019', '1')
        response = self.app.get('delete/1', follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Task deleted successfully.', response.data)
        task = db.session.query(Task).filter_by(task_id=1).first()
        self.assertIsNone(task)

    def test_users_cannot_complete_tasks_that_are_not_created_by_them(self):
        self.create_user('micheal', 'michael@xyz.com', '123456')
        self.login('michael', '123456')
        self.create_task('task created by michael', '10/08/2019', '1')
        self.logout()
        self.create_user('fletcher', 'fletcher@xyz.com', 'test123')
        self.login('fletcher', 'test123')
        response = self.app.get('/complete/1', follow_redirects=True)
        self.assertNotIn(b'Task marked complete', response.data)
        task = db.session.query(Task).filter_by(task_id=1).first()
        self.assertEqual(task.status, 0)


if __name__ == '__main__':
    unittest.main()
