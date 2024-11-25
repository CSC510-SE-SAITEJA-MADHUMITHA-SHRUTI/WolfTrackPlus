import unittest
from flask import Flask
from flask_testing import TestCase
from flask_login import LoginManager
from flask_sqlalchemy import SQLAlchemy
from your_flask_app import create_app, db
import io

class TestFlaskApp(TestCase):

    def create_app(self):
        app = create_app()
        app.config['TESTING'] = True
        app.config['WTF_CSRF_ENABLED'] = False  # Disable CSRF for testing
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'  # Use in-memory database
        app.config['LOGIN_DISABLED'] = True  # Disable login for testing

        return app

    def setUp(self):
        db.create_all()

    def tearDown(self):
        db.session.remove()
        db.drop_all()

    def test_login(self):
        response = self.client.get('/login')
        self.assert200(response)
        self.assert_template_used('login.html')

    def test_login_with_valid_credentials(self):
        tester = self.client
        response = tester.post('/loginUser', data={"username": "test@example.com", "password": "correctpassword"})
        self.assertRedirects(response, '/auth')

    def test_login_invalid_email_format(self):
        tester = self.client
        response = tester.post('/loginUser', data={"username": "invalidemail", "password": "password"})
        self.assert200(response)
        self.assertTemplateUsed('login.html')
        self.assertIn(b'Invalid email format', response.data)

    def test_login_page_content(self):
        tester = self.client
        response = tester.get('/login')
        self.assertEqual(response.content_type, "text/html; charset=utf-8")

    def test_otp_generation(self):
        tester = self.client
        response = tester.post('/loginUser', data={"username": "test@example.com", "password": "correctpassword"})
        self.assert200(response)
        self.assertIn(b"Your OTP for logging into WolfTrack++ is:", response.data)

    def test_otp_verification_correct(self):
        tester = self.client
        response = tester.post('/verify_otp', data={"otp": "123456"})
        self.assertRedirects(response, '/auth')

    def test_otp_verification_incorrect(self):
        tester = self.client
        response = tester.post('/verify_otp', data={"otp": "000000"})
        self.assert200(response)
        self.assertIn(b"Invalid OTP", response.data)

    def test_signup(self):
        tester = self.client
        response = tester.post('/signup', data={
            "name": "Test User",
            "email": "testuser@example.com",
            "password": "password",
            "gender": "Female",
            "location": "Test City"
        })
        self.assertRedirects(response, '/login')
        self.assertIn(b'Successfully registered', response.data)

    def test_signup_empty_form(self):
        tester = self.client
        response = tester.post('/signup', data={})
        self.assert200(response)
        self.assertIn(b"Please fill in all required fields", response.data)

    def test_application_submission_without_resume(self):
        tester = self.client
        response = tester.post('/add_new_application', data={
            "companyName": "Test Company",
            "location": "Test Location",
            "jobProfile": "Test Job",
            "salary": 100000,
            "securityQuestion": "What is your pet's name?",
            "securityAnswer": "Fluffy",
            "dateApplied": "2024-01-01",
            "notes": "Test application",
            "username": "testuser@example.com",
            "password": "password123"
        })
        self.assert200(response)
        self.assertIn(b"Resume is required for job application", response.data)

    def test_application_update(self):
        tester = self.client
        response = tester.post('/edit_application', data={
            "companyName": "Updated Company",
            "location": "Updated Location",
            "jobProfile": "Updated Job",
            "salary": 110000,
            "securityQuestion": "New Security Question",
            "securityAnswer": "New Answer",
            "dateApplied": "2024-02-01",
            "notes": "Updated notes",
            "username": "testuser@example.com",
            "password": "password123"
        })
        self.assert200(response)
        self.assertIn(b"Application updated successfully", response.data)

    def test_user_profile_retrieval(self):
        tester = self.client
        response = tester.get('/profile')
        self.assert200(response)
        self.assertTemplateUsed('profile.html')

    def test_multiple_applications(self):
        tester = self.client
        response = tester.post('/add_new_application', data={
            "companyName": "Company 1",
            "location": "Location 1",
            "jobProfile": "Job 1",
            "salary": 50000,
            "securityQuestion": "Question 1",
            "securityAnswer": "Answer 1",
            "dateApplied": "2024-01-01",
            "notes": "First application",
            "username": "testuser@example.com",
            "password": "password123"
        })
        self.assert200(response)

        response = tester.post('/add_new_application', data={
            "companyName": "Company 2",
            "location": "Location 2",
            "jobProfile": "Job 2",
            "salary": 60000,
            "securityQuestion": "Question 2",
            "securityAnswer": "Answer 2",
            "dateApplied": "2024-02-01",
            "notes": "Second application",
            "username": "testuser@example.com",
            "password": "password123"
        })
        self.assert200(response)

if __name__ == "__main__":
    unittest.main()
