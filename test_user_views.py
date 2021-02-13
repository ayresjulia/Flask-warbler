"""Message View tests."""

from app import app, CURR_USER_KEY
import os
from unittest import TestCase

from models import db, connect_db, Message, User, Follows


os.environ['DATABASE_URL'] = "postgresql:///warbler-test"

db.create_all()

# Don't have WTForms use CSRF at all, since it's a pain to test

app.config['WTF_CSRF_ENABLED'] = False


class MessageViewTestCase(TestCase):
    """Test views for messages."""

    def setUp(self):
        """Create test client, add sample data."""

        User.query.delete()
        Message.query.delete()

        self.client = app.test_client()

        self.testuser = User.signup(username="testuser",
                                    email="test@test.com",
                                    password="testuser",
                                    image_url=None,
                                    bio='bio',
                                    location='location')
        self.testuser_id = 567
        self.testuser.id = self.testuser_id

        self.u1 = User.signup("abc", "test1@test.com",
                              "password", None, 'hjdf', 'NY')
        self.u1_id = 778
        self.u1.id = self.u1_id

        self.u2 = User.signup("efg", "test2@test.com",
                              "password", None, 'ghjk', 'MA')
        self.u2_id = 884
        self.u2.id = self.u2_id

        db.session.commit()

    def test_add_message(self):
        """Adding a message"""

        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testuser.id

            resp = c.post("/messages/new", data={"text": "TestMessage"})

            self.assertEqual(resp.status_code, 302)

            msg = Message.query.one()
            self.assertEqual(msg.text, "TestMessage")

    def test_messages_show(self):
        '''Show message on user page'''

        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testuser.id

            resp = c.post("/messages/new", data={"text": "TestMessage"})
            msg = Message.query.one()

            res = c.get(f'/users/{self.testuser.id}')
            html = res.get_data(as_text=True)

            self.assertIn('TestMessage', html)

    def test_see_follower(self):
        '''See Following, Followers and Likes on the page'''

        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testuser.id

            res = c.get(f'/users/{self.testuser.id}')
            html = res.get_data(as_text=True)

            self.assertIn('Following', html)
            self.assertIn('Followers', html)
            self.assertIn('Likes', html)

    def test_delete_message(self):
        '''Delete message'''

        m = Message(id=1234, text='test message', user_id=self.testuser_id)

        db.session.add(m)
        db.session.commit()

        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testuser.id

            resp = c.post("/messages/1234/delete", follow_redirects=True)
            self.assertEqual(resp.status_code, 200)
            m = Message.query.get(1234)

            self.assertIsNone(m)

    def setup_followers(self):
        f1 = Follows(user_being_followed_id=self.u1_id,
                     user_following_id=self.testuser_id)
        f2 = Follows(user_being_followed_id=self.u2_id,
                     user_following_id=self.testuser_id)

        db.session.add_all([f1, f2])
        db.session.commit()

    def test_unauthorized_following_page_access(self):
        self.setup_followers()
        with self.client as c:

            resp = c.get(
                f"/users/{self.testuser_id}/following", follow_redirects=True)
            self.assertEqual(resp.status_code, 200)
            self.assertNotIn("@abc", str(resp.data))
            self.assertIn("Access unauthorized", str(resp.data))
