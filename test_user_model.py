"""User model tests."""

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


class UserModelTestCase(TestCase):
    """Test User Model"""

    def setUp(self):
        """Create test client, add sample data."""
        db.drop_all()
        db.create_all()

        u1 = User.signup("bbb", "bbb@me.com", "12345", None, 'hello', 'NY')
        uid1 = 1111
        u1.id = uid1

        u2 = User.signup("ccc", "ccc2@me.com", "09876", None, 'bye', 'LA')
        uid2 = 2222
        u2.id = uid2

        db.session.commit()

        u1 = User.query.get(uid1)
        u2 = User.query.get(uid2)

        self.u1 = u1
        self.uid1 = uid1

        self.u2 = u2
        self.uid2 = uid2

        self.client = app.test_client()

    def tearDown(self):
        res = super().tearDown()
        db.session.rollback()
        return res

    def test_user_model(self):
        """Does basic model work?"""

        u = User(
            email="test@test.com",
            username="testuser",
            password="HASHED_PASSWORD"
        )

        db.session.add(u)
        db.session.commit()

        # User should have no messages & no followers
        self.assertEqual(len(u.messages), 0)
        self.assertEqual(len(u.followers), 0)

    def test_repr(self):
        '''Testing correct representation of output'''

        return repr(User(username='bob')) == "<User: {'username': 'bob'}>"

    def test_is_following(self):
        '''Does is following detect when user1 follows user2'''

        self.u1.following.append(self.u2)
        db.session.commit()

        self.assertTrue(self.u1.is_following(self.u2))
        self.assertFalse(self.u2.is_following(self.u1))

    def test_is_followed_by(self):
        '''Does is following detect when user2 follows user1'''

        self.u1.following.append(self.u2)
        db.session.commit()

        self.assertTrue(self.u2.is_followed_by(self.u1))
        self.assertFalse(self.u1.is_followed_by(self.u2))

    def test_signup(self):
        '''Testing nullable module columns when user signs up'''

        new_user = User.signup("TestUser", "test@me.com",
                               "123456789", None, 'cat', 'PA')
        new_user_id = 9000
        new_user.id = new_user_id

        db.session.add(new_user)
        db.session.commit()

        u = User.query.get(9000)

        self.assertEqual(new_user.username, "TestUser")
        self.assertEqual(new_user.email, "test@me.com")

        fail_user = User.signup(None, "fail@me.com",
                                "888", None, 'cat', 'PA')
        fail_user_id = 2000
        fail_user.id = fail_user_id

        with self.assertRaises(exc.IntegrityError) as context:
            db.session.commit()

    def test_authenticate(self):
        '''Testing authentication of a user'''

        u = User.authenticate(self.u1.username, "password")
        self.assertIsNotNone(u)

        self.assertFalse(User.authenticate("badusername", "password"))

        self.assertFalse(User.authenticate(self.u1.username, "badpassword"))
