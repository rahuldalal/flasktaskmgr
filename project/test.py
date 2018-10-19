import os
import unittest

from views import app, db
from _config import basedir
from models import User

TEST_DB = 'test.db'


class AllTests(unittest.TestCase):

    #### Setup and teardown #####
    # executed prior to each test
    def setUp(self):
        app.config['TESTING'] = True
        app.config['WTF_CSRF_ENABLED'] = False
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///'+ \
            os.path.join(os.path.abspath(basedir),TEST_DB)
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

    def test_users_can_register(self):
        new_user = User('michael', 'michael@mherman.org', 'michaelherman')
        db.session.add(new_user)
        db.session.commit()

        test = db.session.query(User).all()
        for t in test:
            assert t.name == 'michael'


if __name__ == '__main__':
    unittest.main()