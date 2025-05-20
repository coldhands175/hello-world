import unittest
from app import create_app, db
from app.models import User
from config import TestConfig

class AuthTestCase(unittest.TestCase):
    def setUp(self):
        self.app = create_app(TestConfig)
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()
        self.client = self.app.test_client()

        # Create a test user for login/logout tests
        self.test_user = User(username='testuser', email='test@example.com')
        self.test_user.set_password('password123')
        db.session.add(self.test_user)
        db.session.commit()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    # Registration Tests
    def test_get_registration_page(self):
        response = self.client.get('/register')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Register', response.data)

    def test_register_user_success(self):
        response = self.client.post('/register', data={
            'username': 'newuser',
            'email': 'new@example.com',
            'password': 'password123',
            'password2': 'password123'
        }, follow_redirects=True)
        self.assertEqual(response.status_code, 200) # Should redirect to login
        self.assertIn(b'Congratulations, you are now a registered user!', response.data)
        user = User.query.filter_by(username='newuser').first()
        self.assertIsNotNone(user)
        self.assertEqual(user.email, 'new@example.com')

    def test_register_user_existing_username(self):
        # First, create the user that will cause the conflict
        existing_user = User(username='testuser1', email='test1@example.com')
        existing_user.set_password('password')
        db.session.add(existing_user)
        db.session.commit()

        response = self.client.post('/register', data={
            'username': 'testuser1', # Existing username
            'email': 'new2@example.com',
            'password': 'password123',
            'password2': 'password123'
        }, follow_redirects=True)
        self.assertEqual(response.status_code, 200) # Stays on register page
        self.assertIn(b'Please use a different username.', response.data)

    def test_register_user_existing_email(self):
        # First, create the user that will cause the conflict
        existing_user = User(username='testuser2', email='test2@example.com')
        existing_user.set_password('password')
        db.session.add(existing_user)
        db.session.commit()

        response = self.client.post('/register', data={
            'username': 'newuser3',
            'email': 'test2@example.com', # Existing email
            'password': 'password123',
            'password2': 'password123'
        }, follow_redirects=True)
        self.assertEqual(response.status_code, 200) # Stays on register page
        self.assertIn(b'Please use a different email address.', response.data)

    def test_register_password_mismatch(self):
        response = self.client.post('/register', data={
            'username': 'newuser4',
            'email': 'new4@example.com',
            'password': 'password123',
            'password2': 'password456' # Mismatched password
        }, follow_redirects=True)
        self.assertEqual(response.status_code, 200) # Stays on register page
        self.assertIn(b'Passwords must match.', response.data)

    # Login Tests
    def test_get_login_page(self):
        response = self.client.get('/login')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Sign In', response.data)

    def test_login_user_success(self):
        response = self.client.post('/login', data={
            'username': 'testuser',
            'password': 'password123'
        }, follow_redirects=True)
        self.assertEqual(response.status_code, 200) # Redirects to index
        self.assertIn(b'Welcome to My App!', response.data) # Assuming index shows this
        self.assertIn(b'Hi, testuser!', response.data) # Check for username in nav/body

    def test_login_user_invalid_username(self):
        response = self.client.post('/login', data={
            'username': 'wronguser',
            'password': 'password123'
        }, follow_redirects=True)
        self.assertEqual(response.status_code, 200) # Stays on login page (or redirects to it)
        self.assertIn(b'Invalid username or password', response.data)

    def test_login_user_invalid_password(self):
        response = self.client.post('/login', data={
            'username': 'testuser',
            'password': 'wrongpassword'
        }, follow_redirects=True)
        self.assertEqual(response.status_code, 200) # Stays on login page
        self.assertIn(b'Invalid username or password', response.data)

    # Logout Test
    def test_logout_user(self):
        # First, log in the user
        self.client.post('/login', data={
            'username': 'testuser',
            'password': 'password123'
        }, follow_redirects=True)
        
        # Then, log out
        response = self.client.get('/logout', follow_redirects=True)
        self.assertEqual(response.status_code, 200) # Redirects to index
        self.assertIn(b'Login', response.data) # Should see Login link again
        self.assertNotIn(b'Hi, testuser!', response.data)
        self.assertNotIn(b'Logout', response.data)

    # Protected Route Access Tests
    def test_access_index_not_logged_in(self):
        response = self.client.get('/', follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Sign In', response.data) # Should be redirected to login

    def test_access_profile_not_logged_in(self):
        response = self.client.get('/user/testuser', follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Sign In', response.data) # Should be redirected to login

    # Authenticated User Redirect Tests
    def test_authenticated_user_redirect_from_login(self):
        # Log in the user
        self.client.post('/login', data={
            'username': 'testuser',
            'password': 'password123'
        }, follow_redirects=True)
        
        # Try to access login page again
        response = self.client.get('/login', follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Welcome to My App!', response.data) # Should be on index
        self.assertNotIn(b'Sign In', response.data) # Should not see login form

    def test_authenticated_user_redirect_from_register(self):
        # Log in the user
        self.client.post('/login', data={
            'username': 'testuser',
            'password': 'password123'
        }, follow_redirects=True)

        # Try to access register page
        response = self.client.get('/register', follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Welcome to My App!', response.data) # Should be on index
        self.assertNotIn(b'Register', response.data) # Should not see register form


if __name__ == '__main__':
    unittest.main()
