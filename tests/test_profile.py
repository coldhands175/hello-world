import unittest
from app import create_app, db
from app.models import User
from config import TestConfig

class ProfileTestCase(unittest.TestCase):
    def setUp(self):
        self.app = create_app(TestConfig)
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()
        self.client = self.app.test_client()

        # Create and log in a test user
        self.test_user = User(username='testuser', email='test@example.com', first_name='Test', last_name='User', bio='Test bio')
        self.test_user.set_password('password123')
        db.session.add(self.test_user)
        db.session.commit()
        
        # Log in the user
        self.client.post('/login', data={
            'username': 'testuser',
            'password': 'password123'
        }, follow_redirects=True)

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    # Profile Viewing Tests
    def test_get_own_profile_page(self):
        response = self.client.get('/user/testuser')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'testuser', response.data) # Username
        self.assertIn(b'Test User', response.data) # First and Last name (assuming they are displayed)
        self.assertIn(b'Test bio', response.data)  # Bio
        self.assertIn(b'Edit Profile', response.data) # Should see edit link for own profile

    def test_get_other_user_profile_page(self):
        # Create another user
        other_user = User(username='otheruser', email='other@example.com')
        other_user.set_password('password456')
        db.session.add(other_user)
        db.session.commit()

        response = self.client.get('/user/otheruser')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'otheruser', response.data)
        self.assertNotIn(b'Edit Profile', response.data) # Should not see edit link for other's profile

    def test_get_nonexistent_user_profile_page(self):
        response = self.client.get('/user/nonexistentuser')
        self.assertEqual(response.status_code, 404)

    # Profile Editing Tests
    def test_get_edit_profile_page(self):
        response = self.client.get('/edit_profile')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Edit Profile', response.data)
        self.assertIn(b'testuser', response.data) # Username should be pre-filled and readonly
        self.assertIn(b'test@example.com', response.data) # Email should be pre-filled and readonly
        self.assertIn(b'Test', response.data) # first_name
        self.assertIn(b'User', response.data) # last_name
        self.assertIn(b'Test bio', response.data) # bio

    def test_edit_profile_success(self):
        response = self.client.post('/edit_profile', data={
            'first_name': 'UpdatedFirst',
            'last_name': 'UpdatedLast',
            'bio': 'This is an updated bio.'
        }, follow_redirects=True)
        self.assertEqual(response.status_code, 200) # Should redirect to profile view
        self.assertIn(b'Your changes have been saved.', response.data)
        
        # Verify data on the profile page
        self.assertIn(b'UpdatedFirst', response.data)
        self.assertIn(b'UpdatedLast', response.data)
        self.assertIn(b'This is an updated bio.', response.data)

        # Verify data in the database
        user = User.query.filter_by(username='testuser').first()
        self.assertEqual(user.first_name, 'UpdatedFirst')
        self.assertEqual(user.last_name, 'UpdatedLast')
        self.assertEqual(user.bio, 'This is an updated bio.')

    def test_edit_profile_empty_fields_allowed(self):
        response = self.client.post('/edit_profile', data={
            'first_name': '',
            'last_name': '',
            'bio': ''
        }, follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Your changes have been saved.', response.data)
        user = User.query.filter_by(username='testuser').first()
        self.assertEqual(user.first_name, '')
        self.assertEqual(user.last_name, '')
        self.assertEqual(user.bio, '')

    def test_edit_profile_max_length_validation(self):
        # Assuming first_name, last_name max_length is 64 and bio is 500
        long_string65 = 'a' * 65
        long_string501 = 'b' * 501
        
        response = self.client.post('/edit_profile', data={
            'first_name': long_string65,
            'last_name': 'ValidLastName',
            'bio': 'Valid Bio'
        }, follow_redirects=True)
        self.assertEqual(response.status_code, 200) # Stays on edit_profile page due to validation error
        self.assertIn(b'Field must be between 0 and 64 characters long.', response.data) # Check for WTForms Length validator message

        response = self.client.post('/edit_profile', data={
            'first_name': 'ValidFirstName',
            'last_name': long_string65,
            'bio': 'Valid Bio'
        }, follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Field must be between 0 and 64 characters long.', response.data)

        response = self.client.post('/edit_profile', data={
            'first_name': 'ValidFirstName',
            'last_name': 'ValidLastName',
            'bio': long_string501
        }, follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Field must be between 0 and 500 characters long.', response.data)

if __name__ == '__main__':
    unittest.main()
