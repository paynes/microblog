from datetime import datetime, timedelta
import unittest

from app import app, db
from app.models import User, Post


class UserModelCase(unittest.TestCase):

	def setUp(self):
		app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite://'
		db.create_all()

	def tearDown(self):
		db.session.remove()
		db.drop_all()

	def test_password_hashing(self):
		u = User(username='Test')
		u.set_password('test')

		self.assertFalse(u.check_password('password'))
		self.assertTrue(u.check_password('test'))

	def test_avatar(self):
		u = User(username='test', email='test@test.cz')
		self.assertEqual(u.avatar(128), ('https://www.gravatar.com/avatar/'
										'32dc008f58672e97fd61b77ad4510331'
										'?d=identicon&s=128'))

	def test_follow(self):
		u1 = User(username='john', email='john@email.com')
		u2 = User(username='susan', email='susan@email.com')
		db.session.add_all([u1, u2])
		db.session.commit()

		self.assertEqual(u1.followed.all(), [])
		self.assertEqual(u2.followed.all(), [])

		u1.follow(u2)
		db.session.commit()

		self.assertTrue(u1.is_following(u2))
		self.assertEqual(u1.followed.count(), 1)
		self.assertEqual(u1.followed.first().username, 'susan')
		self.assertEqual(u2.followers.count(), 1)
		self.assertEqual(u2.followers.first().username, 'john')

		u1.unfollow(u2)
		db.session.commit()
		self.assertFalse(u1.is_following(u2))
		self.assertEqual(u1.followed.count(), 0)
		self.assertEqual(u2.followers.count(), 0)


	def test_follow_posts(self):
		u1 = User(username='john', email='john@email.com')
		u2 = User(username='susan', email='susan@email.com')
		u3 = User(username='mary', email='mary@email.com')
		u4 = User(username='david', email='david@email.com')
		db.session.add_all([u1, u2, u3, u4])

		now = datetime.now()

		p1 = Post(body='post from john', timestamp=now + timedelta(seconds=1), author=u1)
		p2 = Post(body='post from susan', timestamp=now + timedelta(seconds=4), author=u2)
		p3 = Post(body='post from mary', timestamp=now + timedelta(seconds=3), author=u3)
		p4 = Post(body='post from david', timestamp=now + timedelta(seconds=2), author=u4)
		db.session.add_all([p1, p2, p3, p4])
		db.session.commit()

		u1.follow(u2)
		u1.follow(u4)
		u2.follow(u3)
		u3.follow(u4)
		db.session.commit()

		f1 = u1.followed_posts().all()
		f2 = u2.followed_posts().all()
		f3 = u3.followed_posts().all()
		f4 = u4.followed_posts().all()

		self.assertEqual(f1, [p2, p4, p1])
		self.assertEqual(f2, [p2, p3])
		self.assertEqual(f3, [p3, p4])
		self.assertEqual(f4, [p4])


if __name__ == '__main__':
    unittest.main(verbosity=2)