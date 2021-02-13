"""Message model tests."""

# run these tests like:
#
#    python -m unittest test_user_model.py


from app import app
import os
from unittest import TestCase
from models import db, User, Message, Follows
from sqlalchemy import exc

os.environ['DATABASE_URL'] = "postgresql:///warbler-test"


db.create_all()


class MessageModelTestCase(TestCase):
    """Test Message Mdodel"""

    def setUp(self):
        db.drop_all()
        db.create_all()

        u = User.signup("testing", "testing@test.com",
                        "password", None, 'bio', 'location')
        self.uid = 7777
        u.id = self.uid
        db.session.commit()

        self.u = User.query.get(self.uid)

        self.client = app.test_client()

    def tearDown(self):
        res = super().tearDown()
        db.session.rollback()
        return res

    def test_create_message(self):
        '''Testing nullable module columns when user signs up'''
        new_message = Message(text='Text', user_id=self.uid)

        db.session.add(new_message)
        db.session.commit()

        msg = Message.query.get(1)

        self.assertEqual(len(self.u.messages), 1)
